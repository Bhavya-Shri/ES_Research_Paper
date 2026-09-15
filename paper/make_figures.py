"""Build IEEE-width result figures and a per-clip LaTeX table from experiment.csv.

Does not re-run the DSP. Reads results/tables/comparison.csv and ablation.csv.
"""

from __future__ import annotations

import csv
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TABLES = ROOT / "results" / "tables"
SRC_FIGS = ROOT / "results" / "figures"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    ("529808__logicogonist__bass-loop-and-drums-130-bpm", "Bass+drums 130", "Bass"),
    ("541260__bertsz__drum-and-bass-loop", "Drum and bass", "Bass"),
    ("628213__josefpres__bass-loops-033-with-drums-long-loop-120-bpm", "Bass loop 120", "Bass"),
    ("629137__holizna__funky-lofi-drum-loop-88-bpm", "Lofi drums", "Bass"),
    ("629139__holizna__boombap-drums-90-bpm", "Boombap", "Bass"),
    ("735157__jadis0x__simple-music-loop-bass-keys-drums", "Bass/keys/drums", "Bass"),
    ("bass_heavy", "Synth bass", "Synth"),
    ("mixed", "Synth mixed", "Synth"),
    ("179270__speedenza__poem-statue-of-jupiter-voice", "Spoken poem", "Speech"),
    ("380303__evanboyerman__various-male-command-voice-lines-mixed", "Male commands", "Speech"),
    ("431525__evanboyerman__british-soldiers-monologue-voice-actingmalevoice-over", "Monologue", "Speech"),
    ("speech_like", "Synth speech", "Synth"),
    ("189635__klankbeeld__choir-amen-130525_14", "Choir amen", "Vocal"),
    ("479941__liezen3__men-choir", "Men choir", "Vocal"),
    ("627643__asiilanna__female-vocal", "Female vocal", "Vocal"),
    ("657761__kevp888__221029_2225_fr_malechoir", "Male choir", "Vocal"),
    ("739037__acoustiangel__acoustiangel", "Acoustic", "Vocal"),
    ("165523__zemidlo__snare-roll-hit-crash", "Snare/crash", "Drums"),
    ("269906__theriavirra__02_crash_loud_cymbals__snares", "Cymbals", "Drums"),
    ("transient", "Synth transients", "Synth"),
]

# Display order: bass first (where the effect lives), then speech/vocal/drums/synth.
ORDER = [c[0] for c in CLIPS]
LABEL = {c[0]: c[1] for c in CLIPS}
GROUP = {c[0]: c[2] for c in CLIPS}

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 8,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "legend.fontsize": 8,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 8,
        "figure.dpi": 160,
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.alpha": 0.28,
        "axes.axisbelow": True,
    }
)


def _load(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _f(row: dict, key: str) -> float:
    v = row.get(key, "")
    return float(v) if v not in ("", None) else float("nan")


def index_rows(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {(r["clip"], r["system"]): r for r in rows}


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)


def copy_verification() -> None:
    for name in (
        "crossover_reconstruction.png",
        "harmonic_coverage.png",
        "aweighting_response.png",
        "weighting_ratio.png",
    ):
        src = SRC_FIGS / name
        if src.exists():
            shutil.copy2(src, OUT / name)


def plot_matched_loudness_delta(by: dict) -> list[dict]:
    labels, deltas, groups = [], [], []
    recs = []
    for clip in ORDER:
        p = by[(clip, "proposed")]
        g = by[(clip, "gain_matched_loudness")]
        d = _f(p, "laeq_proxy") - _f(g, "laeq_proxy")
        labels.append(LABEL[clip])
        deltas.append(d)
        groups.append(GROUP[clip])
        recs.append({"clip": clip, "label": LABEL[clip], "group": GROUP[clip], "dlaeq": d})

    colors = {"Bass": "#c44e52", "Speech": "#4c72b0", "Vocal": "#55a868", "Drums": "#8172b2", "Synth": "#ccb974"}
    fig, ax = plt.subplots(figsize=(7.16, 3.6))
    x = np.arange(len(labels))
    ax.bar(x, deltas, color=[colors[g] for g in groups], edgecolor="none")
    ax.axhline(0.0, color="k", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right")
    ax.set_ylabel(r"$\Delta L_{Aeq}$ (dB)")
    ax.set_title("Exposure proxy at matched LUFS (proposed minus flat gain)")
    ax.set_xlim(-0.6, len(labels) - 0.4)
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=colors[k], label=k)
        for k in ("Bass", "Speech", "Vocal", "Drums", "Synth")
    ]
    ax.set_ylim(-0.45, 5.35)
    ax.legend(handles=handles, ncol=5, loc="upper right", frameon=True)
    save(fig, "matched_loudness_delta.png")
    return recs


def plot_matched_loudness_s1_s2(by: dict) -> list[dict]:
    """Grouped bars: S1−S0 and S2−S0 at matched LUFS (the three-system figure)."""
    labels, d1, d2 = [], [], []
    recs = []
    for clip in ORDER:
        p = by[(clip, "proposed")]
        g1 = by[(clip, "gain_matched_loudness")]
        a = by[(clip, "aligned")]
        g2 = by[(clip, "aligned_gain_matched_loudness")]
        s1 = _f(p, "laeq_proxy") - _f(g1, "laeq_proxy")
        s2 = _f(a, "laeq_proxy") - _f(g2, "laeq_proxy")
        labels.append(LABEL[clip])
        d1.append(s1)
        d2.append(s2)
        recs.append(
            {
                "clip": clip,
                "label": LABEL[clip],
                "group": GROUP[clip],
                "dlaeq_s1": s1,
                "dlaeq_s2": s2,
            }
        )

    x = np.arange(len(labels))
    w = 0.38
    fig, ax = plt.subplots(figsize=(7.16, 3.7))
    ax.bar(x - w / 2, d1, w, label="S1 bass-first", color="#c44e52", edgecolor="none")
    ax.bar(x + w / 2, d2, w, label="S2 aligned", color="#55a868", edgecolor="none")
    ax.axhline(0.0, color="k", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right")
    ax.set_ylabel(r"$\Delta L_{Aeq}$ (dB)")
    ax.set_title("Exposure proxy at matched LUFS (processor minus flat gain)")
    ax.set_xlim(-0.6, len(labels) - 0.4)
    ax.set_ylim(-1.45, 5.35)
    ax.legend(loc="upper right", ncol=2, frameon=True)
    save(fig, "matched_loudness_s1_s2.png")
    return recs


def plot_matched_exposure(by: dict) -> None:
    """S1 loudness and LSD at matched LAeq (kept so the dual-matching figure still regenerates)."""
    labels = [LABEL[c] for c in ORDER]
    p_lufs, g_lufs, p_lsd, g_lsd = [], [], [], []
    for clip in ORDER:
        p = by[(clip, "proposed")]
        g = by[(clip, "gain_matched_exposure")]
        p_lufs.append(_f(p, "lufs"))
        g_lufs.append(_f(g, "lufs"))
        p_lsd.append(_f(p, "lsd_vs_ref"))
        g_lsd.append(_f(g, "lsd_vs_ref"))

    x = np.arange(len(labels))
    w = 0.38
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.55))
    axes[0].bar(x - w / 2, g_lufs, w, label="Flat gain", color="#4c72b0")
    axes[0].bar(x + w / 2, p_lufs, w, label="Proposed", color="#dd8452")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=40, ha="right")
    axes[0].set_ylabel("LUFS")
    axes[0].set_title("Loudness at matched $L_{Aeq}$ proxy")
    axes[0].legend(loc="lower right")

    axes[1].bar(x - w / 2, g_lsd, w, label="Flat gain", color="#4c72b0")
    axes[1].bar(x + w / 2, p_lsd, w, label="Proposed", color="#dd8452")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=40, ha="right")
    axes[1].set_ylabel("Log-spectral distance (dB)")
    axes[1].set_title("Spectral distance at matched $L_{Aeq}$")
    axes[1].legend()
    save(fig, "matched_exposure_lsd.png")


def plot_metric_mismatch(by: dict) -> None:
    """Why H2 fails: proposed vs original, LUFS drop vs LAeq drop."""
    fig, ax = plt.subplots(figsize=(3.5, 3.35))
    colors = {"Bass": "#c44e52", "Speech": "#4c72b0", "Vocal": "#55a868", "Drums": "#8172b2", "Synth": "#ccb974"}
    seen = set()
    for clip in ORDER:
        o = by[(clip, "original")]
        p = by[(clip, "proposed")]
        d_lufs = _f(o, "lufs") - _f(p, "lufs")  # positive = quieter
        d_laeq = _f(o, "laeq_proxy") - _f(p, "laeq_proxy")
        g = GROUP[clip]
        ax.scatter(
            d_lufs,
            d_laeq,
            c=colors[g],
            s=28,
            zorder=3,
            label=g if g not in seen else None,
        )
        seen.add(g)
    lim = 5.4
    ax.plot([0, lim], [0, lim], "k--", lw=0.8, label="Equal drop")
    ax.set_xlim(-0.15, lim)
    ax.set_ylim(-0.15, 2.2)
    ax.set_xlabel("LUFS drop vs original (dB)")
    ax.set_ylabel(r"$L_{Aeq}$ proxy drop vs original (dB)")
    ax.set_title("A-weighting vs loudness on the proposed output")
    ax.legend(loc="upper left", fontsize=7)
    save(fig, "metric_mismatch.png")


def plot_ablation(rows: list[dict]) -> None:
    systems = [
        ("broadband_limiter", "Default DRC"),
        ("ablation_crossover_only", "Crossover"),
        ("ablation_mid_only", "Mid only"),
        ("ablation_mid_high", "Mid+high"),
        ("ablation_mid_low", "Mid+low"),
        ("ablation_full", "Full"),
    ]
    by_sys = defaultdict(list)
    orig = defaultdict(list)
    for r in rows:
        if r["system"] == "original":
            orig[r["clip"]].append(r)
        else:
            by_sys[r["system"]].append(r)

    dlaeq, dlufs, labels = [], [], []
    for key, lab in systems:
        dA, dL = [], []
        for r in by_sys[key]:
            o = orig[r["clip"]][0]
            dA.append(_f(r, "laeq_proxy") - _f(o, "laeq_proxy"))
            dL.append(_f(r, "lufs") - _f(o, "lufs"))
        dlaeq.append(float(np.mean(dA)))
        dlufs.append(float(np.mean(dL)))
        labels.append(lab)

    x = np.arange(len(labels))
    w = 0.38
    fig, ax = plt.subplots(figsize=(3.5, 2.9))
    ax.bar(x - w / 2, dlaeq, w, label=r"Mean $\Delta L_{Aeq}$", color="#4c72b0")
    ax.bar(x + w / 2, dlufs, w, label=r"Mean $\Delta$LUFS", color="#dd8452")
    ax.axhline(0.0, color="k", lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Change vs original (dB)")
    ax.set_title("Ablation, mean over 20 clips")
    ax.legend(fontsize=7)
    save(fig, "ablation_delta.png")


def write_table(by: dict) -> dict:
    """S1-only summary (kept so the old Fig. 5 numbers still regenerate)."""
    dlaeqs, dlufss, lsd_p, lsd_g = [], [], [], []
    for clip in ORDER:
        p = by[(clip, "proposed")]
        gl = by[(clip, "gain_matched_loudness")]
        ge = by[(clip, "gain_matched_exposure")]
        dlaeqs.append(_f(p, "laeq_proxy") - _f(gl, "laeq_proxy"))
        dlufss.append(_f(p, "lufs") - _f(ge, "lufs"))
        lsd_p.append(_f(p, "lsd_vs_ref"))
        lsd_g.append(_f(ge, "lsd_vs_ref"))
    real = [d for d, c in zip(dlaeqs, ORDER) if GROUP[c] != "Synth"]
    bass = [d for d, c in zip(dlaeqs, ORDER) if GROUP[c] == "Bass"]
    voice = [d for d, c in zip(dlaeqs, ORDER) if GROUP[c] in ("Speech", "Vocal", "Drums")]
    return {
        "n": len(dlaeqs),
        "mean_dlaeq_matched_lufs": float(np.mean(dlaeqs)),
        "median_dlaeq_matched_lufs": float(np.median(dlaeqs)),
        "mean_dlufs_matched_laeq": float(np.mean(dlufss)),
        "mean_lsd_proposed": float(np.mean(lsd_p)),
        "mean_lsd_flat": float(np.mean(lsd_g)),
        "mean_dlaeq_real16": float(np.mean(real)),
        "mean_dlaeq_bass": float(np.mean(bass)),
        "mean_dlaeq_voice_drums": float(np.mean(voice)),
        "n_proposed_higher": int(sum(d > 0.05 for d in dlaeqs)),
        "n_proposed_lower": int(sum(d < -0.05 for d in dlaeqs)),
        "n_tie": int(sum(abs(d) <= 0.05 for d in dlaeqs)),
        "bass_min": float(min(bass)),
        "bass_max": float(max(bass)),
    }


def write_s1_s2_table(by: dict) -> dict:
    """Per-clip LaTeX: S1 and S2 ΔLAeq at matched LUFS (and the dual ΔLUFS)."""
    lines = [
        r"\begin{table*}[!t]",
        r"\centering",
        r"\caption{Per-clip $\Delta L_{Aeq}$ at matched LUFS (processor minus flat gain; positive: higher digital exposure proxy) and the dual $\Delta$LUFS at matched $L_{Aeq}$. S1 is the bass-first heuristic; S2 is the metric-aligned mid cut.}",
        r"\label{tab:perclip}",
        r"\renewcommand{\arraystretch}{1.08}",
        r"\begin{tabular}{l l r r r r}",
        r"\hline",
        r"Clip & Type & $\Delta L_{Aeq}$ S1 & $\Delta L_{Aeq}$ S2 & $\Delta$LUFS S1 & $\Delta$LUFS S2 \\",
        r"\hline",
    ]
    s1_a, s2_a, s1_l, s2_l = [], [], [], []
    for clip in ORDER:
        p = by[(clip, "proposed")]
        g1l = by[(clip, "gain_matched_loudness")]
        g1e = by[(clip, "gain_matched_exposure")]
        a = by[(clip, "aligned")]
        g2l = by[(clip, "aligned_gain_matched_loudness")]
        g2e = by[(clip, "aligned_gain_matched_exposure")]
        dA1 = _f(p, "laeq_proxy") - _f(g1l, "laeq_proxy")
        dA2 = _f(a, "laeq_proxy") - _f(g2l, "laeq_proxy")
        dL1 = _f(p, "lufs") - _f(g1e, "lufs")
        dL2 = _f(a, "lufs") - _f(g2e, "lufs")
        s1_a.append(dA1)
        s2_a.append(dA2)
        s1_l.append(dL1)
        s2_l.append(dL2)
        typ = GROUP[clip]
        lines.append(
            f"{LABEL[clip]} & {typ} & {dA1:+.2f} & {dA2:+.2f} & {dL1:+.2f} & {dL2:+.2f} \\\\"
        )
    lines.append(r"\hline")
    lines.append(
        f"Mean ($n$=20) &  & {float(np.mean(s1_a)):+.2f} & {float(np.mean(s2_a)):+.2f} "
        f"& {float(np.mean(s1_l)):+.2f} & {float(np.mean(s2_l)):+.2f} \\\\"
    )
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    (OUT.parent / "perclip_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "mean_dlaeq_s1": float(np.mean(s1_a)),
        "mean_dlaeq_s2": float(np.mean(s2_a)),
        "mean_dlufs_s1": float(np.mean(s1_l)),
        "mean_dlufs_s2": float(np.mean(s2_l)),
    }


def plot_weighting_ratio_figure() -> None:
    from exposure_dsp.kweighting import plot_weighting_ratio

    plot_weighting_ratio(OUT / "weighting_ratio.png")


def main() -> None:
    by = index_rows(_load(TABLES / "comparison.csv"))
    copy_verification()
    plot_weighting_ratio_figure()
    plot_matched_loudness_delta(by)
    plot_matched_loudness_s1_s2(by)
    plot_matched_exposure(by)
    plot_metric_mismatch(by)
    plot_ablation(_load(TABLES / "ablation.csv"))
    summary = write_table(by)
    s1s2 = write_s1_s2_table(by)
    print({**summary, **s1s2})


if __name__ == "__main__":
    main()
