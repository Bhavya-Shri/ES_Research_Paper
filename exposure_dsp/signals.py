"""Synthetic test signals and a small stand-in program-material corpus."""

from __future__ import annotations

import numpy as np


def time_axis(fs: float, duration_s: float) -> np.ndarray:
    n = int(round(fs * duration_s))
    return np.arange(n) / fs


def sine(freq: float, fs: float, duration_s: float, amp: float = 0.2, phase: float = 0.0) -> np.ndarray:
    t = time_axis(fs, duration_s)
    return amp * np.sin(2.0 * np.pi * freq * t + phase)


def fade(x: np.ndarray, fs: float, fade_s: float = 0.02) -> np.ndarray:
    n = max(1, int(fs * fade_s))
    n = min(n, len(x) // 2)
    w = np.linspace(0.0, 1.0, n)
    y = x.copy()
    y[:n] *= w
    y[-n:] *= w[::-1]
    return y


def six_tone_plus_noise(fs: float = 48000.0, duration_s: float = 2.0, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    freqs = [60.0, 120.0, 440.0, 1000.0, 3000.0, 8000.0]
    amps = [0.25, 0.18, 0.12, 0.10, 0.08, 0.05]
    t = time_axis(fs, duration_s)
    y = np.zeros_like(t)
    for f, a in zip(freqs, amps):
        y += a * np.sin(2.0 * np.pi * f * t)
    y += 0.02 * rng.standard_normal(len(t))
    return fade(0.89 * y / (np.max(np.abs(y)) + 1e-12), fs)


def program_bass_heavy(fs: float = 48000.0, duration_s: float = 8.0, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = time_axis(fs, duration_s)
    y = 0.35 * np.sin(2.0 * np.pi * 40.0 * t)
    y += 0.22 * np.sin(2.0 * np.pi * 50.0 * t)
    y += 0.12 * np.sin(2.0 * np.pi * 80.0 * t)
    y += 0.08 * np.sin(2.0 * np.pi * 220.0 * t)
    y += 0.06 * np.sin(2.0 * np.pi * 440.0 * t)
    y += 0.04 * np.sin(2.0 * np.pi * 1760.0 * t)
    kick = (np.mod(t, 0.5) < 0.05).astype(float) * np.exp(-np.mod(t, 0.5) * 40.0)
    y += 0.4 * kick * np.sin(2.0 * np.pi * 45.0 * t)
    y += 0.03 * rng.standard_normal(len(t))
    return fade(_normalize_peak(y, 0.89), fs)


def program_speech_like(fs: float = 48000.0, duration_s: float = 8.0, seed: int = 2) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = time_axis(fs, duration_s)
    carrier = rng.standard_normal(len(t))
    from scipy import signal

    b, a = signal.butter(4, [300 / (fs / 2), 3400 / (fs / 2)], btype="band")
    y = signal.lfilter(b, a, carrier)
    env = 0.5 + 0.5 * np.sin(2.0 * np.pi * 3.5 * t)
    syllables = (np.sin(2.0 * np.pi * 4.0 * t) > 0).astype(float)
    y *= env * (0.2 + 0.8 * syllables)
    y += 0.04 * np.sin(2.0 * np.pi * 180.0 * t) * syllables
    return fade(_normalize_peak(y, 0.5), fs)


def program_transient(fs: float = 48000.0, duration_s: float = 8.0, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = time_axis(fs, duration_s)
    y = 0.05 * rng.standard_normal(len(t))
    y += 0.08 * np.sin(2.0 * np.pi * 220.0 * t)
    period = 0.25
    clicks = (np.mod(t, period) < 0.004).astype(float)
    hh = clicks * rng.standard_normal(len(t))
    from scipy import signal

    b, a = signal.butter(2, 6000 / (fs / 2), btype="high")
    y += 0.6 * signal.lfilter(b, a, hh)
    return fade(_normalize_peak(y, 0.7), fs)


def program_mixed(fs: float = 48000.0, duration_s: float = 8.0, seed: int = 4) -> np.ndarray:
    y = 0.65 * program_bass_heavy(fs, duration_s, seed)
    y += 0.45 * program_speech_like(fs, duration_s, seed + 10)
    y += 0.35 * program_transient(fs, duration_s, seed + 20)
    return fade(_normalize_peak(y, 0.89), fs)


def _normalize_peak(x: np.ndarray, peak_amp: float) -> np.ndarray:
    p = np.max(np.abs(x)) + 1e-12
    return peak_amp * x / p


def synthetic_corpus(fs: float = 48000.0, duration_s: float = 8.0) -> dict[str, np.ndarray]:
    return {
        "bass_heavy": program_bass_heavy(fs, duration_s, 1),
        "speech_like": program_speech_like(fs, duration_s, 2),
        "transient": program_transient(fs, duration_s, 3),
        "mixed": program_mixed(fs, duration_s, 4),
        "six_tone_debug": six_tone_plus_noise(fs, min(2.0, duration_s), 0),
    }
