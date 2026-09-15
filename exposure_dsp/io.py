"""WAV load/save with soundfile, falling back to scipy."""

from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    import soundfile as sf
except ImportError:  # pragma: no cover
    sf = None


def load_mono(path: str | Path, target_fs: float | None = 48000.0) -> tuple[np.ndarray, float]:
    path = Path(path)
    if sf is not None:
        x, fs = sf.read(str(path), always_2d=True)
        x = np.mean(x, axis=1)
    else:
        from scipy.io import wavfile

        fs, x = wavfile.read(str(path))
        x = np.asarray(x)
        if x.ndim > 1:
            x = np.mean(x, axis=1)
        if np.issubdtype(x.dtype, np.integer):
            x = x.astype(float) / np.iinfo(x.dtype).max
        else:
            x = x.astype(float)
    fs = float(fs)
    if target_fs is not None and abs(fs - target_fs) > 1e-6:
        from scipy.signal import resample_poly

        g = np.gcd(int(round(fs)), int(round(target_fs)))
        x = resample_poly(x, int(round(target_fs)) // g, int(round(fs)) // g)
        fs = float(target_fs)
    return np.asarray(x, dtype=float), fs


def save_wav(path: str | Path, x: np.ndarray, fs: float) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    y = np.asarray(x, dtype=float)
    peak = np.max(np.abs(y))
    if peak > 1.0:
        y = y / peak
    if sf is not None:
        sf.write(str(path), y, int(fs), subtype="PCM_16")
        return
    from scipy.io import wavfile

    wavfile.write(str(path), int(fs), np.int16(np.clip(y, -1, 1) * 32767))
