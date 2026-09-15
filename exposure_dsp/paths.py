"""Paths and figure helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
AUDIO_IN = ROOT / "audio_in"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
WAVS = RESULTS / "wavs"
TABLES = RESULTS / "tables"


def ensure_dirs() -> None:
    for d in (AUDIO_IN, RESULTS, FIGURES, WAVS, TABLES):
        d.mkdir(parents=True, exist_ok=True)


def savefig(name: str) -> Path:
    ensure_dirs()
    path = FIGURES / name
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return path
