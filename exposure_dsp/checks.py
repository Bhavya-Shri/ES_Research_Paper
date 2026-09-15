"""Verification experiments for crossover, harmonics, A-weighting, and streaming."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import signal

from .aweighting import a_weight_db_iec, digital_a_weighting_ba
from .cweighting import c_weight_db_iec, digital_c_weighting_ba
from .crossover import LinkwitzRileyCrossover3Way
from .kweighting import marker_table, plot_weighting_ratio
from .limiter import BroadbandExposureLimiter, PeakCeilingLimiter
from .paths import savefig
from .proposed import ProposedConfig, ProposedProcessor
from .signals import sine, six_tone_plus_noise

import matplotlib.pyplot as plt


def _naive_butterworth_sum(x: np.ndarray, fs: float) -> np.ndarray:
    nyq = 0.5 * fs
    b_low, a_low = signal.butter(4, 300 / nyq, btype="low")
    b_mid, a_mid = signal.butter(4, [300 / nyq, 4000 / nyq], btype="band")
    b_high, a_high = signal.butter(4, 4000 / nyq, btype="high")
    return (
        signal.lfilter(b_low, a_low, x)
        + signal.lfilter(b_mid, a_mid, x)
        + signal.lfilter(b_high, a_high, x)
    )


def _reconstruction_mag_db(recon_fn, fs: float, n: int = 65536) -> tuple[np.ndarray, np.ndarray]:
    x = np.zeros(n)
    x[0] = 1.0
    y = recon_fn(x)
    mag = 20.0 * np.log10(np.abs(np.fft.rfft(y)) + 1e-15)
    f = np.fft.rfftfreq(n, 1.0 / fs)
    return f, mag


def check_crossover(fs: float = 48000.0) -> dict[str, Any]:
    xo = LinkwitzRileyCrossover3Way(fs)

    def lr_recon(x):
        xo.reset()
        return xo.reconstruct(x)

    f, mag_lr = _reconstruction_mag_db(lr_recon, fs)
    f_n, mag_naive = _reconstruction_mag_db(lambda x: _naive_butterworth_sum(x, fs), fs)
    band = (f >= 100.0) & (f <= 10000.0)
    lr_err = float(np.max(np.abs(mag_lr[band])))
    naive_err = float(np.max(np.abs(mag_naive[(f_n >= 100) & (f_n <= 10000)])))

    tone = sine(440.0, fs, 1.0, amp=0.01)
    xo.reset()
    y_lr = xo.reconstruct(tone)
    y_naive = _naive_butterworth_sum(tone, fs)
    peak_in = float(np.max(np.abs(tone)))
    peak_lr = float(np.max(np.abs(y_lr[int(0.2 * fs) :])))
    peak_naive = float(np.max(np.abs(y_naive[int(0.2 * fs) :])))

    plt.figure(figsize=(8.2, 4.2))
    plt.semilogx(f, mag_lr, label="Linkwitz–Riley 3-way (this work)")
    plt.semilogx(f_n, mag_naive, label="Independent Butterworth (old draft)", alpha=0.85)
    plt.axhline(0.5, color="k", ls="--", lw=0.8)
    plt.axhline(-0.5, color="k", ls="--", lw=0.8, label="±0.5 dB")
    plt.xlim(20, 20000)
    plt.ylim(-6, 6)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Reconstructed magnitude (dB)")
    plt.title("Crossover reconstruction")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    fig = savefig("crossover_reconstruction.png")

    passed = lr_err < 0.5 and abs(peak_lr / peak_in - 1.0) < 0.05
    return {
        "passed": passed,
        "lr_max_abs_err_db_100_10k": lr_err,
        "naive_max_abs_err_db_100_10k": naive_err,
        "quiet_tone_in_peak": peak_in,
        "quiet_tone_lr_peak": peak_lr,
        "quiet_tone_naive_peak": peak_naive,
        "quiet_tone_lr_boost_pct": 100.0 * (peak_lr / peak_in - 1.0),
        "quiet_tone_naive_boost_pct": 100.0 * (peak_naive / peak_in - 1.0),
        "figure": str(fig),
    }


def _bin_mag(x: np.ndarray, fs: float, freq: float) -> float:
    n = len(x)
    spec = np.abs(np.fft.rfft(x * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / fs)
    idx = int(np.argmin(np.abs(freqs - freq)))
    return float(spec[idx])


def check_harmonics(fs: float = 48000.0) -> dict[str, Any]:
    cfg = ProposedConfig(fs=fs, use_mid=False, use_high=False, harmonic_mode="wide", mid_target_dba=96.0)
    rows = []
    plt.figure(figsize=(8.2, 4.6))
    for f0 in (40.0, 50.0, 60.0, 80.0):
        x = sine(f0, fs, 2.0, amp=0.3)
        proc = ProposedProcessor(cfg)
        y = proc.process(x)
        skip = int(0.3 * fs)
        xs, ys = x[skip:], y[skip:]
        m_f0_in = _bin_mag(xs, fs, f0)
        m_f0_out = _bin_mag(ys, fs, f0)
        m_2 = _bin_mag(ys, fs, 2.0 * f0)
        m_3 = _bin_mag(ys, fs, 3.0 * f0)
        reduction_db = 20.0 * np.log10((m_f0_out + 1e-12) / (m_f0_in + 1e-12))
        rows.append(
            {
                "f0": f0,
                "fundamental_reduction_db": reduction_db,
                "h2_over_out_f0_db": 20.0 * np.log10((m_2 + 1e-12) / (m_f0_out + 1e-12)),
                "h3_over_out_f0_db": 20.0 * np.log10((m_3 + 1e-12) / (m_f0_out + 1e-12)),
                "h2_present": bool(m_2 > 0.03 * m_f0_in),
                "h3_present": bool(m_3 > 0.01 * m_f0_in),
            }
        )
        nfft = 16384
        spec = 20.0 * np.log10(np.abs(np.fft.rfft(ys[:nfft] * np.hanning(nfft))) + 1e-12)
        freqs = np.fft.rfftfreq(nfft, 1.0 / fs)
        plt.semilogx(freqs, spec, label=f"{f0:.0f} Hz in")

    plt.xlim(20, 800)
    plt.ylim(-80, 20)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB, arbitrary)")
    plt.title("Low-band output spectra for bass tones (wide harmonic band 80–400 Hz)")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    fig = savefig("harmonic_coverage.png")
    passed = all(r["h2_present"] and r["fundamental_reduction_db"] < -3.0 for r in rows)
    return {"passed": passed, "tones": rows, "figure": str(fig)}


def check_aweighting(fs: float = 48000.0) -> dict[str, Any]:
    b, a = digital_a_weighting_ba(fs)
    w, h = signal.freqz(b, a, worN=4096, fs=fs)
    h_db = 20.0 * np.log10(np.abs(h) + 1e-15)
    # Normalize digital filter to 0 dB at 1 kHz so EA matches IEC definition.
    h1000 = np.interp(1000.0, w, h_db)
    h_db = h_db - h1000
    ref = a_weight_db_iec(w)
    freqs = np.array([100, 500, 1000, 3150, 4000, 8000, 16000, 20000], dtype=float)
    rows = []
    for f in freqs:
        d = float(np.interp(f, w, h_db) - a_weight_db_iec(f))
        rows.append({"freq": float(f), "in_mid_band": bool(300 <= f <= 4000), "EA_db": d})

    plt.figure(figsize=(8.2, 4.2))
    plt.semilogx(w, ref, label="IEC analytic")
    plt.semilogx(w, h_db, label="Digital IIR (normalized at 1 kHz)", ls="--")
    plt.xlim(20, 20000)
    plt.ylim(-60, 10)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("A-weighting (dB)")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    fig = savefig("aweighting_response.png")
    mid = [r["EA_db"] for r in rows if r["in_mid_band"]]
    passed = max(abs(v) for v in mid) < 0.2
    return {"passed": passed, "points": rows, "figure": str(fig)}


def check_cweighting(fs: float = 48000.0) -> dict[str, Any]:
    b, a = digital_c_weighting_ba(fs)
    w, h = signal.freqz(b, a, worN=4096, fs=fs)
    h_db = 20.0 * np.log10(np.abs(h) + 1e-15)
    h1000 = np.interp(1000.0, w, h_db)
    h_db = h_db - h1000
    ref = c_weight_db_iec(w)
    freqs = np.array([31.5, 40.0, 100.0, 500.0, 1000.0, 4000.0, 8000.0], dtype=float)
    rows = []
    for f in freqs:
        d = float(np.interp(f, w, h_db) - c_weight_db_iec(f))
        rows.append({"freq": float(f), "EA_db": d, "c_db": float(np.interp(f, w, h_db))})

    plt.figure(figsize=(8.2, 4.2))
    plt.semilogx(w, ref, label="IEC analytic")
    plt.semilogx(w, h_db, label="Digital IIR (normalized at 1 kHz)", ls="--")
    plt.xlim(20, 20000)
    plt.ylim(-15, 5)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("C-weighting (dB)")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    fig = savefig("cweighting_response.png")
    c40 = float(np.interp(40.0, w, h_db))
    a40 = float(a_weight_db_iec(40.0))
    mid_err = [r["EA_db"] for r in rows if 100.0 <= r["freq"] <= 4000.0]
    passed = (max(abs(v) for v in mid_err) < 0.3) and (c40 > a40 + 20.0)
    return {
        "passed": passed,
        "points": rows,
        "c_40hz_db": c40,
        "a_40hz_db": a40,
        "figure": str(fig),
    }


def check_weighting_ratio(fs: float = 48000.0) -> dict[str, Any]:
    """A at ~40 Hz ≈ −35 dB; K is much less severe there. Writes weighting_ratio.png."""
    from pathlib import Path

    paper_fig = Path(__file__).resolve().parent.parent / "paper" / "figures" / "weighting_ratio.png"
    fig = plot_weighting_ratio(paper_fig)
    markers = marker_table(fs)
    m40 = next(m for m in markers if abs(m["freq_hz"] - 40.0) < 1e-9)
    a40 = m40["a_db"]
    k40 = m40["k_digital_db"]
    passed = (-40.0 <= a40 <= -30.0) and (k40 > a40 + 15.0)
    return {
        "passed": bool(passed),
        "markers": markers,
        "a_40hz_db": a40,
        "k_40hz_db": k40,
        "ratio_40hz_db": m40["ratio_a_over_k_db"],
        "figure": str(fig),
    }


def check_streaming(fs: float = 48000.0) -> dict[str, Any]:
    x = six_tone_plus_noise(fs, 2.0)
    proc = ProposedProcessor(ProposedConfig(fs=fs))
    y_whole = proc.process(x, block_size=len(x))
    proc = ProposedProcessor(ProposedConfig(fs=fs))
    y_blocks = proc.process(x, block_size=240)
    max_diff = float(np.max(np.abs(y_whole - y_blocks)))
    quiet = sine(440.0, fs, 0.5, amp=0.01)
    ceil = PeakCeilingLimiter(fs)
    yq = ceil.process(quiet)
    lim = BroadbandExposureLimiter(fs, target_dba=96.0)
    yl = lim.process(quiet)
    return {
        "passed": bool(max_diff < 1e-8),
        "block_vs_whole_max_abs": max_diff,
        "ceiling_quiet_peak": float(np.max(np.abs(yq))),
        "limiter_quiet_peak": float(np.max(np.abs(yl))),
        "quiet_not_boosted": float(np.max(np.abs(yl))) <= 0.0105,
    }


def run_all_checks(fs: float = 48000.0) -> dict[str, Any]:
    results = {
        "crossover": check_crossover(fs),
        "harmonics": check_harmonics(fs),
        "aweighting": check_aweighting(fs),
        "cweighting": check_cweighting(fs),
        "weighting_ratio": check_weighting_ratio(fs),
        "streaming": check_streaming(fs),
    }
    results["all_passed"] = all(v.get("passed", False) for v in results.values())
    return results
