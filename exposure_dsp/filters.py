"""Small stateful filter helpers."""

from __future__ import annotations

import numpy as np
from scipy import signal


def lr4_sos(fc: float, fs: float, btype: str) -> np.ndarray:
    """4th-order Linkwitz–Riley SOS = two cascaded 2nd-order Butterworth sections."""
    sos2 = signal.butter(2, fc, btype=btype, fs=fs, output="sos")
    return np.vstack([sos2, sos2])


class SOSFilter:
    def __init__(self, sos: np.ndarray):
        self.sos = np.atleast_2d(np.asarray(sos, dtype=float))
        self.zi = np.zeros((self.sos.shape[0], 2), dtype=float)

    def reset(self) -> None:
        self.zi[:] = 0.0

    def process(self, x: np.ndarray) -> np.ndarray:
        y, self.zi = signal.sosfilt(self.sos, x, zi=self.zi)
        return y


class Biquad:
    def __init__(self, b: np.ndarray | None = None, a: np.ndarray | None = None):
        self.b = np.array([1.0, 0.0, 0.0] if b is None else b, dtype=float)
        self.a = np.array([1.0, 0.0, 0.0] if a is None else a, dtype=float)
        self.zi = np.zeros(2, dtype=float)

    def set_tf(self, b: np.ndarray, a: np.ndarray) -> None:
        self.b = np.asarray(b, dtype=float)
        self.a = np.asarray(a, dtype=float)

    def reset(self) -> None:
        self.zi[:] = 0.0

    def process(self, x: np.ndarray) -> np.ndarray:
        y, self.zi = signal.lfilter(self.b, self.a, x, zi=self.zi)
        return y


def rbj_lowpass(f0: float, fs: float, q: float = 0.7071067811865476) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2.0 * np.pi * f0 / fs
    cosw = np.cos(w0)
    alpha = np.sin(w0) / (2.0 * q)
    b0 = (1.0 - cosw) / 2.0
    b1 = 1.0 - cosw
    b2 = (1.0 - cosw) / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cosw
    a2 = 1.0 - alpha
    return np.array([b0, b1, b2]) / a0, np.array([1.0, a1 / a0, a2 / a0])


def rbj_lowshelf(f0: float, fs: float, gain_db: float, q: float = 0.7071067811865476) -> tuple[np.ndarray, np.ndarray]:
    a_gain = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * f0 / fs
    cosw = np.cos(w0)
    alpha = np.sin(w0) / (2.0 * q)
    two_sa = 2.0 * np.sqrt(a_gain) * alpha
    b0 = a_gain * ((a_gain + 1.0) - (a_gain - 1.0) * cosw + two_sa)
    b1 = 2.0 * a_gain * ((a_gain - 1.0) - (a_gain + 1.0) * cosw)
    b2 = a_gain * ((a_gain + 1.0) - (a_gain - 1.0) * cosw - two_sa)
    a0 = (a_gain + 1.0) + (a_gain - 1.0) * cosw + two_sa
    a1 = -2.0 * ((a_gain - 1.0) + (a_gain + 1.0) * cosw)
    a2 = (a_gain + 1.0) + (a_gain - 1.0) * cosw - two_sa
    return np.array([b0, b1, b2]) / a0, np.array([1.0, a1 / a0, a2 / a0])


def rbj_highpass(f0: float, fs: float, q: float = 0.7071067811865476) -> tuple[np.ndarray, np.ndarray]:
    w0 = 2.0 * np.pi * f0 / fs
    cosw = np.cos(w0)
    alpha = np.sin(w0) / (2.0 * q)
    b0 = (1.0 + cosw) / 2.0
    b1 = -(1.0 + cosw)
    b2 = (1.0 + cosw) / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cosw
    a2 = 1.0 - alpha
    return np.array([b0, b1, b2]) / a0, np.array([1.0, a1 / a0, a2 / a0])


class EnvelopeFollower:
    """Peak envelope with separate attack and release time constants."""

    def __init__(self, fs: float, attack_s: float, release_s: float):
        self.a_att = float(np.exp(-1.0 / (fs * attack_s)))
        self.a_rel = float(np.exp(-1.0 / (fs * release_s)))
        self.env = 0.0

    def reset(self) -> None:
        self.env = 0.0

    def process(self, x_abs: np.ndarray) -> np.ndarray:
        env = self.env
        a_att, a_rel = self.a_att, self.a_rel
        out = np.empty(len(x_abs), dtype=float)
        for n, r in enumerate(x_abs):
            if r > env:
                env = a_att * env + (1.0 - a_att) * r
            else:
                env = a_rel * env + (1.0 - a_rel) * r
            out[n] = env
        self.env = env
        return out
