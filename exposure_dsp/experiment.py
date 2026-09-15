"""Matched-exposure / matched-loudness comparison and ablation study."""

from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .io import load_mono, save_wav
from .limiter import BroadbandExposureLimiter
from .metrics import clip_metrics, laeq_proxy, lufs
from .paths import AUDIO_IN, TABLES, WAVS, ensure_dirs, savefig
from .proposed import ProposedConfig, ProposedProcessor, make_ablation
from .signals import synthetic_corpus

import matplotlib.pyplot as plt


def match_gain(
    x: np.ndarray,
    fs: float,
    target_value: float,
    metric: str,
) -> dict[str, Any]:
    """Frequency-flat gain: the actual 'turn everything down' baseline.

    A-weighting is linear, so LAeq(G x) = LAeq(x) + 20 log10(G).
    LUFS is close to that; we apply one correction pass for gating.
    """
    current = laeq_proxy(x, fs) if metric == "laeq" else lufs(x, fs)
    g = 10.0 ** ((target_value - current) / 20.0)
    y = np.asarray(x, dtype=float) * g
    got = laeq_proxy(y, fs) if metric == "laeq" else lufs(y, fs)
    if abs(got - target_value) > 0.05:
        g *= 10.0 ** ((target_value - got) / 20.0)
        y = np.asarray(x, dtype=float) * g
        got = laeq_proxy(y, fs) if metric == "laeq" else lufs(y, fs)
    return {"y": y, "gain": float(g), "value": float(got), "error": float(abs(got - target_value))}


def _limiter_at(x: np.ndarray, fs: float, target_dba: float, ratio: float) -> np.ndarray:
    return BroadbandExposureLimiter(fs=fs, target_dba=target_dba, ratio=ratio).process(x)


def match_limiter(
    x: np.ndarray,
    fs: float,
    target_value: float,
    metric: str,
    ratio: float = 4.0,
    tol: float = 0.2,
    lo: float = 48.0,
    hi: float = 96.0,
    iters: int = 18,
) -> dict[str, Any]:
    measure: Callable[[np.ndarray], float] = (
        (lambda y: laeq_proxy(y, fs)) if metric == "laeq" else (lambda y: lufs(y, fs))
    )
    best: dict[str, Any] | None = None
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        y = _limiter_at(x, fs, mid, ratio)
        val = measure(y)
        err = abs(val - target_value)
        if best is None or err < best["error"]:
            best = {"y": y, "target_dba": mid, "value": val, "error": err}
        if val > target_value:
            hi = mid
        else:
            lo = mid
        if err <= tol:
            break
    assert best is not None
    return best


def _list_user_wavs() -> list[Path]:
    if not AUDIO_IN.exists():
        return []
    return sorted(p for p in AUDIO_IN.iterdir() if p.suffix.lower() in {".wav", ".flac"})


def load_corpus(fs: float = 48000.0, duration_s: float = 8.0) -> dict[str, np.ndarray]:
    clips = synthetic_corpus(fs, duration_s)
    for path in _list_user_wavs():
        x, _ = load_mono(path, target_fs=fs)
        clips[path.stem] = x
    return clips


def _row(clip: str, system: str, x: np.ndarray, y: np.ndarray | None, fs: float, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    m = clip_metrics(x, y, fs)
    out = {"clip": clip, "system": system, **m}
    if extra:
        out.update(extra)
    return out


def _append_matched_gains(
    rows: list[dict[str, Any]],
    name: str,
    x: np.ndarray,
    processed: dict[str, Any],
    fs: float,
    exposure_system: str,
    loudness_system: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Match frequency-flat G to a processed clip on LAeq and on LUFS."""
    extra_base = {"matched_to": processed["system"]}
    gain_exp = match_gain(x, fs, processed["laeq_proxy"], metric="laeq")
    rows.append(
        _row(
            name,
            exposure_system,
            gain_exp["y"],
            x,
            fs,
            extra={
                **extra_base,
                "gain": gain_exp["gain"],
                "match_error": gain_exp["error"],
                "match_metric": "laeq",
            },
        )
    )
    gain_loud = match_gain(x, fs, processed["lufs"], metric="lufs")
    rows.append(
        _row(
            name,
            loudness_system,
            gain_loud["y"],
            x,
            fs,
            extra={
                **extra_base,
                "gain": gain_loud["gain"],
                "match_error": gain_loud["error"],
                "match_metric": "lufs",
            },
        )
    )
    return gain_exp, gain_loud


def run_comparison(fs: float = 48000.0, duration_s: float = 8.0, save_audio: bool = True) -> list[dict[str, Any]]:
    ensure_dirs()
    cfg_s1 = ProposedConfig(fs=fs)
    cfg_s2 = replace(ProposedConfig.aligned(), fs=fs)
    clips = load_corpus(fs, duration_s)
    rows: list[dict[str, Any]] = []
    n_todo = sum(1 for n in clips if n != "six_tone_debug")
    done = 0
    for name, x in clips.items():
        if name == "six_tone_debug":
            continue
        done += 1
        print(f"[{done}/{n_todo}] {name} ({len(x) / fs:.1f} s)", flush=True)
        proposed = ProposedProcessor(cfg_s1).process(x)
        aligned = ProposedProcessor(cfg_s2).process(x)
        orig_m = _row(name, "original", x, None, fs)
        prop_m = _row(name, "proposed", proposed, x, fs)
        aln_m = _row(name, "aligned", aligned, x, fs)
        rows.append(orig_m)
        rows.append(prop_m)
        rows.append(aln_m)

        gain_exp, gain_loud = _append_matched_gains(
            rows, name, x, prop_m, fs, "gain_matched_exposure", "gain_matched_loudness"
        )
        aln_exp, aln_loud = _append_matched_gains(
            rows,
            name,
            x,
            aln_m,
            fs,
            "aligned_gain_matched_exposure",
            "aligned_gain_matched_loudness",
        )

        matched_exp = match_limiter(x, fs, prop_m["laeq_proxy"], metric="laeq", ratio=cfg_s1.mid_ratio)
        rows.append(
            _row(
                name,
                "limiter_matched_exposure",
                matched_exp["y"],
                x,
                fs,
                extra={
                    "limiter_target_dba": matched_exp["target_dba"],
                    "match_error": matched_exp["error"],
                    "match_metric": "laeq",
                },
            )
        )
        matched_loud = match_limiter(x, fs, prop_m["lufs"], metric="lufs", ratio=cfg_s1.mid_ratio)
        rows.append(
            _row(
                name,
                "limiter_matched_loudness",
                matched_loud["y"],
                x,
                fs,
                extra={
                    "limiter_target_dba": matched_loud["target_dba"],
                    "match_error": matched_loud["error"],
                    "match_metric": "lufs",
                },
            )
        )

        if save_audio:
            save_wav(WAVS / f"{name}_original.wav", x, fs)
            save_wav(WAVS / f"{name}_proposed.wav", proposed, fs)
            save_wav(WAVS / f"{name}_aligned.wav", aligned, fs)
            save_wav(WAVS / f"{name}_gain_matched_exposure.wav", gain_exp["y"], fs)
            save_wav(WAVS / f"{name}_gain_matched_loudness.wav", gain_loud["y"], fs)
            save_wav(WAVS / f"{name}_aligned_gain_matched_exposure.wav", aln_exp["y"], fs)
            save_wav(WAVS / f"{name}_aligned_gain_matched_loudness.wav", aln_loud["y"], fs)
    return rows


def run_ablation(fs: float = 48000.0, duration_s: float = 8.0) -> list[dict[str, Any]]:
    clips = load_corpus(fs, duration_s)
    names = ["crossover_only", "mid_only", "mid_low", "mid_high", "full"]
    rows: list[dict[str, Any]] = []
    for clip_name, x in clips.items():
        if clip_name == "six_tone_debug":
            continue
        rows.append(_row(clip_name, "original", x, None, fs))
        lim = BroadbandExposureLimiter(fs=fs, target_dba=78.0, ratio=4.0).process(x)
        rows.append(_row(clip_name, "broadband_limiter", lim, x, fs))
        for abl in names:
            y = make_ablation(abl).process(x)
            rows.append(_row(clip_name, f"ablation_{abl}", y, x, fs))
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    keys = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def _plot_matched_loudness(rows: list[dict[str, Any]]) -> None:
    clips = sorted({r["clip"] for r in rows})
    prop, lim = [], []
    labels = []
    for clip in clips:
        p = next((r for r in rows if r["clip"] == clip and r["system"] == "proposed"), None)
        l = next((r for r in rows if r["clip"] == clip and r["system"] == "gain_matched_loudness"), None)
        if p and l:
            labels.append(clip)
            prop.append(p["laeq_proxy"])
            lim.append(l["laeq_proxy"])
    if not labels:
        return
    x = np.arange(len(labels))
    w = 0.35
    plt.figure(figsize=(8.4, 4.4))
    plt.bar(x - w / 2, lim, w, label="Broadband gain")
    plt.bar(x + w / 2, prop, w, label="Proposed")
    plt.xticks(x, labels, rotation=20, ha="right")
    plt.ylabel("Digital LAeq proxy (dB)")
    plt.title("Exposure proxy at matched LUFS")
    plt.legend()
    plt.grid(True, axis="y", alpha=0.3)
    savefig("matched_loudness_exposure.png")


def _plot_matched_exposure(rows: list[dict[str, Any]]) -> None:
    clips = sorted({r["clip"] for r in rows})
    prop_lufs, lim_lufs, prop_lsd, lim_lsd = [], [], [], []
    labels = []
    for clip in clips:
        p = next((r for r in rows if r["clip"] == clip and r["system"] == "proposed"), None)
        l = next((r for r in rows if r["clip"] == clip and r["system"] == "gain_matched_exposure"), None)
        if p and l:
            labels.append(clip)
            prop_lufs.append(p["lufs"])
            lim_lufs.append(l["lufs"])
            prop_lsd.append(p.get("lsd_vs_ref", np.nan))
            lim_lsd.append(l.get("lsd_vs_ref", np.nan))
    if not labels:
        return
    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.2))
    ax[0].bar(x - w / 2, lim_lufs, w, label="Broadband gain")
    ax[0].bar(x + w / 2, prop_lufs, w, label="Proposed")
    ax[0].set_xticks(x, labels, rotation=20, ha="right")
    ax[0].set_ylabel("LUFS")
    ax[0].set_title("Loudness at matched exposure proxy")
    ax[0].legend()
    ax[0].grid(True, axis="y", alpha=0.3)
    ax[1].bar(x - w / 2, lim_lsd, w, label="Broadband gain")
    ax[1].bar(x + w / 2, prop_lsd, w, label="Proposed")
    ax[1].set_xticks(x, labels, rotation=20, ha="right")
    ax[1].set_ylabel("Log-spectral distance (dB)")
    ax[1].set_title("Spectral distance at matched exposure")
    ax[1].legend()
    ax[1].grid(True, axis="y", alpha=0.3)
    savefig("matched_exposure_quality.png")


def _plot_ablation(rows: list[dict[str, Any]]) -> None:
    systems = [
        "broadband_limiter",
        "ablation_crossover_only",
        "ablation_mid_only",
        "ablation_mid_low",
        "ablation_mid_high",
        "ablation_full",
    ]
    labels = ["Limiter", "Crossover", "+ Mid", "+ Mid/Low", "+ Mid/High", "Full"]
    clips = sorted({r["clip"] for r in rows})
    means = []
    for sys in systems:
        vals = [r["laeq_proxy"] for r in rows if r["system"] == sys]
        means.append(float(np.mean(vals)) if vals else np.nan)
    plt.figure(figsize=(8.4, 4.2))
    plt.bar(labels, means)
    plt.ylabel("Mean digital LAeq proxy (dB)")
    plt.title(f"Ablation exposure proxy (mean over {len(clips)} clips)")
    plt.grid(True, axis="y", alpha=0.3)
    savefig("ablation_exposure.png")


def _processor_deltas(
    rows: list[dict[str, Any]],
    processed_system: str,
    loudness_flat: str,
    exposure_flat: str,
) -> dict[str, Any]:
    clips = sorted({r["clip"] for r in rows if r["system"] == processed_system})
    dlaeq, dlufs_at_exp, per_clip = [], [], []
    for clip in clips:
        p = next(r for r in rows if r["clip"] == clip and r["system"] == processed_system)
        l_loud = next(r for r in rows if r["clip"] == clip and r["system"] == loudness_flat)
        l_exp = next(r for r in rows if r["clip"] == clip and r["system"] == exposure_flat)
        d_laeq = p["laeq_proxy"] - l_loud["laeq_proxy"]
        d_lufs = p["lufs"] - l_exp["lufs"]
        dlaeq.append(d_laeq)
        dlufs_at_exp.append(d_lufs)
        per_clip.append({"clip": clip, "dlaeq_matched_lufs": d_laeq, "dlufs_matched_laeq": d_lufs})
    return {
        "n_clips": len(clips),
        "mean_dlaeq_at_matched_lufs": float(np.mean(dlaeq)) if dlaeq else None,
        "mean_dlufs_at_matched_laeq": float(np.mean(dlufs_at_exp)) if dlufs_at_exp else None,
        "per_clip": per_clip,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    s1 = _processor_deltas(rows, "proposed", "gain_matched_loudness", "gain_matched_exposure")
    has_s2 = any(r["system"] == "aligned" for r in rows)
    s2 = (
        _processor_deltas(
            rows, "aligned", "aligned_gain_matched_loudness", "aligned_gain_matched_exposure"
        )
        if has_s2
        else None
    )
    out: dict[str, Any] = {
        "n_clips": s1["n_clips"],
        "mean_dlaeq_at_matched_lufs": s1["mean_dlaeq_at_matched_lufs"],
        "mean_dlufs_at_matched_laeq": s1["mean_dlufs_at_matched_laeq"],
        "s1": {k: v for k, v in s1.items() if k != "per_clip"},
        "note": (
            "Negative mean_dlaeq_at_matched_lufs means that processor has a lower "
            "digital exposure proxy than frequency-flat gain at matched LUFS."
        ),
        "s2_knobs": {"sub_atten_db": 0.0, "harmonic_mix": 0.0, "mid_target_dba": 72.0},
    }
    if s2 is not None:
        out["s2"] = {k: v for k, v in s2.items() if k != "per_clip"}
        out["mean_dlaeq_aligned_at_matched_lufs"] = s2["mean_dlaeq_at_matched_lufs"]
        out["mean_dlufs_aligned_at_matched_laeq"] = s2["mean_dlufs_at_matched_laeq"]
    return out


def write_s1_s2_csv(rows: list[dict[str, Any]], path: Path | None = None) -> Path:
    """One row per clip: S1 and S2 ΔLAeq at matched LUFS (and the dual)."""
    path = path or (TABLES / "comparison_s1_s2.csv")
    s1 = _processor_deltas(rows, "proposed", "gain_matched_loudness", "gain_matched_exposure")
    s2 = _processor_deltas(
        rows, "aligned", "aligned_gain_matched_loudness", "aligned_gain_matched_exposure"
    )
    s2_by = {r["clip"]: r for r in s2["per_clip"]}
    out_rows = []
    for r in s1["per_clip"]:
        a = s2_by.get(r["clip"], {})
        out_rows.append(
            {
                "clip": r["clip"],
                "dlaeq_s1_matched_lufs": r["dlaeq_matched_lufs"],
                "dlaeq_s2_matched_lufs": a.get("dlaeq_matched_lufs"),
                "dlufs_s1_matched_laeq": r["dlufs_matched_laeq"],
                "dlufs_s2_matched_laeq": a.get("dlufs_matched_laeq"),
            }
        )
    _write_csv(path, out_rows)
    return path


def run_experiment(
    fs: float = 48000.0,
    duration_s: float = 8.0,
    include_ablation: bool = True,
) -> dict[str, Any]:
    ensure_dirs()
    comparison = run_comparison(fs, duration_s)
    _write_csv(TABLES / "comparison.csv", comparison)
    write_s1_s2_csv(comparison)
    _plot_matched_loudness(comparison)
    _plot_matched_exposure(comparison)
    ablation: list[dict[str, Any]] = []
    if include_ablation:
        ablation = run_ablation(fs, duration_s)
        _write_csv(TABLES / "ablation.csv", ablation)
        _plot_ablation(ablation)
    summary = summarize(comparison)
    payload = {"summary": summary, "comparison": comparison, "ablation": ablation}
    (TABLES / "experiment.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return payload
