"""Nonparametric tests on matched-LUFS ΔLAeq (proposed minus flat gain).

Positive Δ means the processor has a *higher* digital A-weighted proxy than
frequency-flat gain at the same LUFS (H2 rejected). Reads existing CSVs;
does not re-run DSP.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats as spstats

from .paths import TABLES, ensure_dirs

SYNTH_CLIPS = frozenset({"bass_heavy", "mixed", "speech_like", "transient"})
BASS_CLIPS = frozenset(
    {
        "529808__logicogonist__bass-loop-and-drums-130-bpm",
        "541260__bertsz__drum-and-bass-loop",
        "628213__josefpres__bass-loops-033-with-drums-long-loop-120-bpm",
        "629137__holizna__funky-lofi-drum-loop-88-bpm",
        "629139__holizna__boombap-drums-90-bpm",
        "735157__jadis0x__simple-music-loop-bass-keys-drums",
    }
)
RNG_SEED = 0
N_BOOT = 10000


def _f(row: dict[str, str], key: str) -> float:
    v = row.get(key, "")
    return float(v) if v not in ("", None) else float("nan")


def load_comparison(path: Path | None = None) -> list[dict[str, str]]:
    path = path or (TABLES / "comparison.csv")
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def matched_lufs_dlaeq(
    rows: list[dict[str, str]],
    proposed_system: str = "proposed",
    flat_system: str = "gain_matched_loudness",
) -> dict[str, float]:
    by: dict[tuple[str, str], dict[str, str]] = {(r["clip"], r["system"]): r for r in rows}
    out: dict[str, float] = {}
    clips = sorted({r["clip"] for r in rows})
    for clip in clips:
        p = by.get((clip, proposed_system))
        g = by.get((clip, flat_system))
        if p is None or g is None:
            continue
        out[clip] = _f(p, "laeq_proxy") - _f(g, "laeq_proxy")
    return out


def bootstrap_mean_ci(
    values: np.ndarray,
    n_boot: int = N_BOOT,
    seed: int = RNG_SEED,
    alpha: float = 0.05,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    draws = rng.choice(values, size=(n_boot, n), replace=True).mean(axis=1)
    lo, hi = np.quantile(draws, [alpha / 2.0, 1.0 - alpha / 2.0])
    return float(lo), float(hi)


def rank_biserial(values: np.ndarray) -> float:
    """Matched-pairs rank-biserial correlation (Kerby 2014). Positive → Δ > 0."""
    x = np.asarray(values, dtype=float)
    x = x[x != 0.0]
    if x.size == 0:
        return float("nan")
    ranks = spstats.rankdata(np.abs(x))
    r_plus = float(ranks[x > 0].sum())
    r_minus = float(ranks[x < 0].sum())
    denom = r_plus + r_minus
    return float((r_plus - r_minus) / denom) if denom else float("nan")


def summarise_deltas(values: list[float] | np.ndarray, label: str) -> dict[str, Any]:
    x = np.asarray(values, dtype=float)
    n = int(x.size)
    mean = float(np.mean(x)) if n else float("nan")
    median = float(np.median(x)) if n else float("nan")
    std = float(np.std(x, ddof=1)) if n > 1 else float("nan")
    cohens_d = float(mean / std) if n > 1 and std > 0 else float("nan")
    ci_lo, ci_hi = bootstrap_mean_ci(x) if n > 1 else (float("nan"), float("nan"))

    if n >= 6:
        # H2 predicted Δ < 0. One-sided p near 1 means H2 is not supported.
        w_less = spstats.wilcoxon(x, zero_method="wilcox", alternative="less", mode="auto")
        w_two = spstats.wilcoxon(x, zero_method="wilcox", alternative="two-sided", mode="auto")
        wilcox = {
            "one_sided_h2_less_statistic": float(w_less.statistic),
            "one_sided_h2_less_p": float(w_less.pvalue),
            "two_sided_statistic": float(w_two.statistic),
            "two_sided_p": float(w_two.pvalue),
        }
    else:
        wilcox = {
            "one_sided_h2_less_statistic": None,
            "one_sided_h2_less_p": None,
            "two_sided_statistic": None,
            "two_sided_p": None,
        }

    return {
        "label": label,
        "n": n,
        "mean_dlaeq_db": mean,
        "median_dlaeq_db": median,
        "std_dlaeq_db": std,
        "bootstrap_95ci_lo": ci_lo,
        "bootstrap_95ci_hi": ci_hi,
        "cohens_d": cohens_d,
        "rank_biserial": rank_biserial(x) if n else float("nan"),
        "n_positive_gt_0p05": int(np.sum(x > 0.05)),
        "n_negative_lt_m0p05": int(np.sum(x < -0.05)),
        "n_tie_within_0p05": int(np.sum(np.abs(x) <= 0.05)),
        **wilcox,
    }


def stats_from_deltas(deltas: dict[str, float], system: str = "proposed") -> dict[str, Any]:
    all_clips = list(deltas.keys())
    real = [c for c in all_clips if c not in SYNTH_CLIPS]
    bass = [c for c in all_clips if c in BASS_CLIPS]
    non_bass_real = [c for c in real if c not in BASS_CLIPS]
    return {
        "system": system,
        "metric": "dlaeq_at_matched_lufs",
        "sign": "positive means processor worse than flat gain on digital LAeq",
        "n20": summarise_deltas([deltas[c] for c in all_clips], "all_20"),
        "n16_real": summarise_deltas([deltas[c] for c in real], "real_16"),
        "bass_6": summarise_deltas([deltas[c] for c in bass], "bass_6"),
        "non_bass_real": summarise_deltas([deltas[c] for c in non_bass_real], "non_bass_real"),
        "per_clip": {k: float(v) for k, v in sorted(deltas.items())},
        "bootstrap": {"n_boot": N_BOOT, "seed": RNG_SEED, "method": "percentile"},
    }


def run_s1_stats(csv_path: Path | None = None, out_path: Path | None = None) -> dict[str, Any]:
    ensure_dirs()
    rows = load_comparison(csv_path)
    deltas = matched_lufs_dlaeq(rows, "proposed", "gain_matched_loudness")
    payload = stats_from_deltas(deltas, system="proposed")
    out_path = out_path or (TABLES / "stats_s1.json")
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["path"] = str(out_path)
    return payload


def run_s2_stats(csv_path: Path | None = None, out_path: Path | None = None) -> dict[str, Any]:
    ensure_dirs()
    rows = load_comparison(csv_path)
    deltas = matched_lufs_dlaeq(rows, "aligned", "aligned_gain_matched_loudness")
    payload = stats_from_deltas(deltas, system="aligned")
    out_path = out_path or (TABLES / "stats_s2.json")
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["path"] = str(out_path)
    return payload


def interpret_s2_mean(mean_db: float) -> dict[str, str]:
    """Step 7 decision gate. Do not retune mid_target_dba after seeing this."""
    if mean_db < -0.2:
        story = "reversal"
        sentence = (
            "S1 loses at matched LUFS; S2 reverses the sign, so attenuation spent "
            "where w_A is large beats flat gain on the digital LAeq proxy."
        )
    elif mean_db > 0.2:
        story = "unexpected_positive"
        sentence = (
            "S2 is also worse than flat gain at matched LUFS; debug engagement "
            "before writing, and do not p-hack mid_target_dba on all 20 clips."
        )
    else:
        story = "cannot_game"
        sentence = (
            "S1 hurts A-weighted dose by cutting bass; S2 mid-cut does not beat "
            "flat gain either, so these two operational meters are too aligned in the midrange to game."
        )
    return {"story": story, "sentence": sentence, "mean_dlaeq_s2": f"{mean_db:.4f}"}
