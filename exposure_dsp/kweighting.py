"""ITU-R BS.1770 K-weighting magnitude (the LUFS pre-filter).

Stage 1 is a high-frequency shelf (~+4 dB above ~2 kHz).
Stage 2 is the RLB second-order highpass (fc ≈ 38.1 Hz).
Neither stage dumps 40 Hz the way IEC A-weighting does (~−35 dB).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import signal

from .aweighting import a_weight_db_iec

# ITU-R BS.1770-4 analog / bilinear design constants.
K_SHELF_HZ = 1681.974450955533
K_SHELF_Q = 0.7071752369554196
K_SHELF_GAIN_DB = 3.999843853973347
K_HP_HZ = 38.13547087602444
K_HP_Q = 0.5003270373238773

# BS.1770-4 Table 1, 48 kHz (same cascade as metrics._k_weighted_ungated).
_K_B1_48K = np.array([1.53512485958697, -2.69169618940638, 1.19839281085285])
_K_A1_48K = np.array([1.0, -1.69065929318241, 0.73248077421585])
_K_B2_48K = np.array([1.0, -2.0, 1.0])
_K_A2_48K = np.array([1.0, -1.99004745483398, 0.99007225036621])

MARKER_HZ = (40.0, 300.0, 1000.0, 4000.0)


def k_weight_db_analog(freq_hz: np.ndarray | float) -> np.ndarray:
    """Analytic K-weighting in dB from the BS.1770 analog prototypes."""
    f = np.asarray(freq_hz, dtype=float)
    s = 1j * 2.0 * np.pi * f

    w_hp = 2.0 * np.pi * K_HP_HZ
    h_hp = (s ** 2) / (s ** 2 + (w_hp / K_HP_Q) * s + w_hp ** 2)

    a_gain = 10.0 ** (K_SHELF_GAIN_DB / 20.0)
    w_sh = 2.0 * np.pi * K_SHELF_HZ
    sn = s / w_sh
    sqa = np.sqrt(a_gain)
    # High shelf: H(0)=1, H(∞)=A (~+4 dB). The extra leading A would make +8 dB.
    h_sh = (a_gain * sn ** 2 + (sqa / K_SHELF_Q) * sn + 1.0) / (
        sn ** 2 + (1.0 / (sqa * K_SHELF_Q)) * sn + 1.0
    )
    mag = np.abs(h_hp * h_sh)
    return 20.0 * np.log10(np.maximum(mag, 1e-30))


def digital_k_weighting_sos(fs: float = 48000.0) -> np.ndarray:
    """Two-biquad K-weighting SOS. At 48 kHz uses the ITU table exactly."""
    fs = float(fs)
    if abs(fs - 48000.0) < 1.0:
        sos1 = np.array([*_K_B1_48K, *_K_A1_48K], dtype=float)
        sos2 = np.array([*_K_B2_48K, *_K_A2_48K], dtype=float)
        return np.vstack([sos1, sos2])

    # RBJ bilinear high-shelf + highpass at other rates (pyloudnorm recipe).
    g_db = K_SHELF_GAIN_DB
    q_s = K_SHELF_Q
    k = np.tan(np.pi * K_SHELF_HZ / fs)
    vh = 10.0 ** (g_db / 20.0)
    vb = vh ** 0.4996667741545416
    a0 = 1.0 + k / q_s + k * k
    b0 = (vh + vb * k / q_s + k * k) / a0
    b1 = 2.0 * (k * k - vh) / a0
    b2 = (vh - vb * k / q_s + k * k) / a0
    a1 = 2.0 * (k * k - 1.0) / a0
    a2 = (1.0 - k / q_s + k * k) / a0
    sos_shelf = np.array([b0, b1, b2, 1.0, a1, a2], dtype=float)

    q_h = K_HP_Q
    k = np.tan(np.pi * K_HP_HZ / fs)
    a0 = 1.0 + k / q_h + k * k
    b0 = 1.0 / a0
    b1 = -2.0 / a0
    b2 = 1.0 / a0
    a1 = 2.0 * (k * k - 1.0) / a0
    a2 = (1.0 - k / q_h + k * k) / a0
    sos_hp = np.array([b0, b1, b2, 1.0, a1, a2], dtype=float)
    return np.vstack([sos_shelf, sos_hp])


def k_weight_db_digital(freq_hz: np.ndarray | float, fs: float = 48000.0) -> np.ndarray:
    """Digital K-weighting magnitude in dB via freqz of the BS.1770 SOS."""
    f = np.asarray(freq_hz, dtype=float)
    sos = digital_k_weighting_sos(fs)
    _, h = signal.sosfreqz(sos, worN=f, fs=fs)
    return 20.0 * np.log10(np.maximum(np.abs(h), 1e-30))


def weighting_curves(
    freq_hz: np.ndarray | None = None,
    fs: float = 48000.0,
) -> dict[str, np.ndarray]:
    """A (IEC), K (analog + digital), and A/K ratio in dB."""
    if freq_hz is None:
        freq_hz = np.logspace(np.log10(20.0), np.log10(20000.0), 2048)
    f = np.asarray(freq_hz, dtype=float)
    a_db = a_weight_db_iec(f)
    k_db = k_weight_db_digital(f, fs=fs)
    k_ana = k_weight_db_analog(f)
    return {
        "freq_hz": f,
        "a_db": a_db,
        "k_db": k_db,
        "k_analog_db": k_ana,
        "k_digital_db": k_db,
        "ratio_db": a_db - k_db,
    }


def marker_table(fs: float = 48000.0) -> list[dict[str, float]]:
    rows = []
    for f in MARKER_HZ:
        a = float(a_weight_db_iec(f))
        k = float(k_weight_db_analog(f))
        kd = float(k_weight_db_digital(f, fs=fs))
        rows.append(
            {
                "freq_hz": f,
                "a_db": a,
                "k_analog_db": k,
                "k_digital_db": kd,
                "ratio_a_over_k_db": a - kd,
            }
        )
    return rows


def plot_weighting_ratio(path: Path | None = None) -> Path:
    """Two-panel IEEE-style figure: A and K, then W_A/W_K in dB."""
    import matplotlib.pyplot as plt
    from .paths import FIGURES, ensure_dirs, savefig

    curves = weighting_curves()
    f = curves["freq_hz"]
    markers = marker_table()

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
        }
    )
    fig, axes = plt.subplots(2, 1, figsize=(3.5, 4.55), sharex=True)

    ax = axes[0]
    ax.semilogx(f, curves["a_db"], color="#4c72b0", lw=1.6, label="A-weighting (IEC 61672)")
    ax.semilogx(f, curves["k_db"], color="#dd8452", lw=1.6, label="K-weighting (BS.1770)")
    ax.set_xlim(20, 20000)
    ax.set_ylim(-50, 8)
    ax.set_ylabel("Magnitude (dB)")
    ax.set_title("A-weighting versus BS.1770 K-weighting")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="lower right", fontsize=7)

    ax = axes[1]
    ax.semilogx(f, curves["ratio_db"], color="#55a868", lw=1.6, label=r"$W_A/W_K$")
    ax.axhline(0.0, color="k", lw=0.6)
    ax.set_xlim(20, 20000)
    ax.set_ylim(-45, 8)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel(r"$20\log_{10}(|W_A|/|W_K|)$ (dB)")
    ax.set_title(r"Ratio $W_A/W_K$")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="lower right", fontsize=7)

    for ax in axes:
        for m in markers:
            ax.axvline(m["freq_hz"], color="0.55", ls=":", lw=0.8)
        ax.set_xticks([20, 100, 1000, 10000, 20000])
        ax.set_xticklabels(["20", "100", "1k", "10k", "20k"])

    m40 = markers[0]
    axes[1].annotate(
        f"40 Hz: A {m40['a_db']:+.1f} dB\nK {m40['k_digital_db']:+.1f} dB",
        xy=(40.0, m40["ratio_a_over_k_db"]),
        xytext=(70.0, -18.0),
        fontsize=7,
        arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"),
    )

    if path is None:
        out = savefig("weighting_ratio.png")
    else:
        ensure_dirs()
        fig.tight_layout()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        # Keep a copy under results/figures as well.
        ensure_dirs()
        fig_copy = FIGURES / "weighting_ratio.png"
        if path.resolve() != fig_copy.resolve():
            import shutil

            shutil.copy2(path, fig_copy)
        out = path
        return out
    return out
