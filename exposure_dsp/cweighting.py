"""IEC 61672-style C-weighting: analog prototype, digital IIR, and reference curve.

C keeps low-frequency energy that A-weighting dumps (A ≈ −35 dB at 40 Hz;
C is only a few dB down there). Same digital-IIR pattern as aweighting.py.
"""

from __future__ import annotations

import numpy as np
from scipy import signal

from .filters import SOSFilter

# Same corner frequencies as the A-weighting prototype in this repo (IEC 61672).
F1 = 20.6
F4 = 12194.0
# Analog gain for H(s) = k s^2 / ((s+ω1)^2 (s+ω4)^2) matching |H| to Rc(f).
KC = (2.0 * np.pi * F4) ** 2


def c_weight_db_iec(freq_hz: np.ndarray | float) -> np.ndarray:
    """Analytic C-weighting in dB, 0 dB at 1 kHz (IEC 61672 approximation)."""
    f = np.asarray(freq_hz, dtype=float)
    f2 = f * f
    rc_num = f2 * (F4 ** 2)
    rc_den = (f2 + F1 ** 2) * (f2 + F4 ** 2)
    rc = rc_num / np.maximum(rc_den, 1e-30)
    c = 20.0 * np.log10(np.maximum(rc, 1e-30))
    f1k = 1000.0
    rc1000 = (f1k ** 2 * F4 ** 2) / ((f1k ** 2 + F1 ** 2) * (f1k ** 2 + F4 ** 2))
    c1000 = 20.0 * np.log10(max(rc1000, 1e-30))
    return c - c1000


def digital_c_weighting_ba(fs: float) -> tuple[np.ndarray, np.ndarray]:
    zeros = [0.0, 0.0]
    poles = [
        -2.0 * np.pi * F1,
        -2.0 * np.pi * F1,
        -2.0 * np.pi * F4,
        -2.0 * np.pi * F4,
    ]
    zd, pd, kd = signal.bilinear_zpk(zeros, poles, KC, fs)
    b, a = signal.zpk2tf(zd, pd, kd)
    return b, a


def digital_c_weighting_sos(fs: float) -> np.ndarray:
    b, a = digital_c_weighting_ba(fs)
    return signal.tf2sos(b, a)


class CWeightingFilter:
    def __init__(self, fs: float = 48000.0):
        self.fs = float(fs)
        self._filt = SOSFilter(digital_c_weighting_sos(self.fs))

    def reset(self) -> None:
        self._filt.reset()

    def process(self, x: np.ndarray) -> np.ndarray:
        return self._filt.process(np.asarray(x, dtype=float))
