"""IEC 61672-style A-weighting: analog prototype, digital IIR, and reference curve."""

from __future__ import annotations

import numpy as np
from scipy import signal

from .filters import SOSFilter

# IEC 61672 pole frequencies (Hz) and analog gain used in the paper draft.
F1 = 20.6
F2 = 107.7
F3 = 737.9
F4 = 12194.0
KA = 7.39705e9


def a_weight_db_iec(freq_hz: np.ndarray | float) -> np.ndarray:
    """Analytic A-weighting in dB, 0 dB at 1 kHz (IEC 61672 approximation)."""
    f = np.asarray(freq_hz, dtype=float)
    f2 = f * f
    ra_num = (F4 ** 2) * (f2 ** 2)
    ra_den = (
        (f2 + F1 ** 2)
        * np.sqrt((f2 + F2 ** 2) * (f2 + F3 ** 2))
        * (f2 + F4 ** 2)
    )
    ra = ra_num / np.maximum(ra_den, 1e-30)
    a = 20.0 * np.log10(np.maximum(ra, 1e-30))
    a1000 = 20.0 * np.log10(
        ((F4 ** 2) * (1000.0 ** 4))
        / (
            (1000.0 ** 2 + F1 ** 2)
            * np.sqrt((1000.0 ** 2 + F2 ** 2) * (1000.0 ** 2 + F3 ** 2))
            * (1000.0 ** 2 + F4 ** 2)
        )
    )
    return a - a1000


def digital_a_weighting_ba(fs: float) -> tuple[np.ndarray, np.ndarray]:
    zeros = [0.0, 0.0, 0.0, 0.0]
    poles = [
        -2.0 * np.pi * F1,
        -2.0 * np.pi * F1,
        -2.0 * np.pi * F2,
        -2.0 * np.pi * F3,
        -2.0 * np.pi * F4,
        -2.0 * np.pi * F4,
    ]
    zd, pd, kd = signal.bilinear_zpk(zeros, poles, KA, fs)
    b, a = signal.zpk2tf(zd, pd, kd)
    return b, a


def digital_a_weighting_sos(fs: float) -> np.ndarray:
    b, a = digital_a_weighting_ba(fs)
    return signal.tf2sos(b, a)


class AWeightingFilter:
    def __init__(self, fs: float = 48000.0):
        self.fs = float(fs)
        self._filt = SOSFilter(digital_a_weighting_sos(self.fs))

    def reset(self) -> None:
        self._filt.reset()

    def process(self, x: np.ndarray) -> np.ndarray:
        return self._filt.process(np.asarray(x, dtype=float))
