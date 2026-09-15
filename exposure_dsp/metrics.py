"""Digital-domain exposure, loudness, and distortion metrics.

LAeq here is an A-weighted digital proxy. It is not calibrated ear-level SPL.
db_ref=94 maps digital full scale to an arbitrary 94 dB offset for development.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import signal

from .aweighting import AWeightingFilter
from .cweighting import CWeightingFilter
from .kweighting import digital_k_weighting_sos

try:
    import pyloudnorm as pyln
except ImportError:  # pragma: no cover
    pyln = None


def rms(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(x * x) + 1e-20))


def peak(x: np.ndarray) -> float:
    return float(np.max(np.abs(x))) if len(x) else 0.0


def crest_factor_db(x: np.ndarray) -> float:
    r = rms(x)
    return 20.0 * np.log10(peak(x) / r) if r > 0 else 0.0


def laeq_proxy(x: np.ndarray, fs: float, db_ref: float = 94.0) -> float:
    filt = AWeightingFilter(fs)
    xa = filt.process(np.asarray(x, dtype=float))
    return 20.0 * np.log10(rms(xa)) + db_ref


def lceq_proxy(x: np.ndarray, fs: float, db_ref: float = 94.0) -> float:
    """C-weighted digital RMS + the same arbitrary offset as laeq_proxy.

    Not calibrated ear-level SPL. C counts bass that A discards.
    """
    filt = CWeightingFilter(fs)
    xc = filt.process(np.asarray(x, dtype=float))
    return 20.0 * np.log10(rms(xc)) + db_ref


def _k_weighted_ungated(x: np.ndarray, fs: float) -> float:
    """Ungated K-weighted loudness. Used only if pyloudnorm is unavailable."""
    y = signal.sosfilt(digital_k_weighting_sos(fs), np.asarray(x, dtype=float))
    return float(-0.691 + 10.0 * np.log10(np.mean(y * y) + 1e-20))


def lufs(x: np.ndarray, fs: float) -> float:
    x = np.asarray(x, dtype=float)
    if pyln is not None:
        try:
            meter = pyln.Meter(fs)
            val = float(meter.integrated_loudness(x))
            if np.isfinite(val):
                return val
        except Exception:
            pass
    return _k_weighted_ungated(x, fs)


def log_spectral_distance(x: np.ndarray, y: np.ndarray, fs: float, nperseg: int | None = None) -> float:
    nperseg = nperseg or int(fs * 0.02)
    nperseg = min(nperseg, len(x), len(y), max(len(x) // 2, 8))
    _, px = signal.welch(x, fs=fs, nperseg=nperseg)
    _, py = signal.welch(y, fs=fs, nperseg=nperseg)
    px = np.maximum(px, 1e-12)
    py = np.maximum(py, 1e-12)
    d = 10.0 * np.log10(px) - 10.0 * np.log10(py)
    return float(np.sqrt(np.mean(d * d)))


def thd_db(x: np.ndarray, fs: float, f0: float, n_harm: int = 8) -> float:
    """THD of a processed tone relative to the residual fundamental at f0."""
    n = len(x)
    spec = np.abs(np.fft.rfft(x * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / fs)
    mag = []
    for k in range(1, n_harm + 1):
        fk = k * f0
        if fk >= fs / 2:
            break
        idx = int(np.argmin(np.abs(freqs - fk)))
        mag.append(spec[idx])
    if len(mag) < 2 or mag[0] <= 1e-12:
        return float("nan")
    harm = np.sqrt(np.sum(np.square(mag[1:])))
    return 20.0 * np.log10(harm / mag[0] + 1e-12)


def clip_metrics(x: np.ndarray, y: np.ndarray | None, fs: float, db_ref: float = 94.0) -> dict[str, Any]:
    out: dict[str, Any] = {
        "laeq_proxy": laeq_proxy(x, fs, db_ref),
        "lceq_proxy": lceq_proxy(x, fs, db_ref),
        "lufs": lufs(x, fs),
        "crest_db": crest_factor_db(x),
        "peak": peak(x),
        "rms": rms(x),
    }
    if y is not None:
        out["lsd_vs_ref"] = log_spectral_distance(y, x, fs)
        out["dlaeq_vs_ref"] = out["laeq_proxy"] - laeq_proxy(y, fs, db_ref)
        out["dlceq_vs_ref"] = out["lceq_proxy"] - lceq_proxy(y, fs, db_ref)
        out["dlufs_vs_ref"] = out["lufs"] - lufs(y, fs)
    return out
