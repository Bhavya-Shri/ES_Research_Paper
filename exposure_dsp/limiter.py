"""Conventional broadband exposure limiter and a fixed-ceiling peak limiter."""

from __future__ import annotations

import numpy as np

from .aweighting import AWeightingFilter
from .filters import EnvelopeFollower


class PeakCeilingLimiter:
    """Causal limiter referenced to a fixed digital ceiling. Never boosts."""

    def __init__(
        self,
        fs: float = 48000.0,
        ceiling_dbfs: float = -1.0,
        attack_s: float = 0.001,
        release_s: float = 0.050,
    ):
        self.ceiling = 10.0 ** (ceiling_dbfs / 20.0)
        self.env = EnvelopeFollower(fs, attack_s, release_s)

    def reset(self) -> None:
        self.env.reset()

    def process(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        env = self.env.process(np.abs(x))
        gain = np.ones(len(x), dtype=float)
        over = env > self.ceiling
        gain[over] = self.ceiling / np.maximum(env[over], 1e-12)
        return x * gain


class BroadbandExposureLimiter:
    """Frequency-flat gain reduction driven by a full-band A-weighted envelope."""

    def __init__(
        self,
        fs: float = 48000.0,
        target_dba: float = 78.0,
        ratio: float = 4.0,
        db_ref: float = 94.0,
        attack_s: float = 0.005,
        release_s: float = 0.050,
        ceiling_dbfs: float = -1.0,
    ):
        self.fs = float(fs)
        self.target_dba = float(target_dba)
        self.ratio = float(ratio)
        self.db_ref = float(db_ref)
        self.aweight = AWeightingFilter(fs)
        self.env = EnvelopeFollower(fs, attack_s, release_s)
        self.ceiling = PeakCeilingLimiter(fs, ceiling_dbfs)

    def reset(self) -> None:
        self.aweight.reset()
        self.env.reset()
        self.ceiling.reset()

    def set_target(self, target_dba: float) -> None:
        self.target_dba = float(target_dba)

    def process_block(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        xa = self.aweight.process(x)
        env = self.env.process(np.abs(xa))
        spl = 20.0 * np.log10(env + 1e-9) + self.db_ref
        excess = np.maximum(spl - self.target_dba, 0.0)
        gr_db = excess * (1.0 - 1.0 / self.ratio)
        gain = 10.0 ** (-gr_db / 20.0)
        return self.ceiling.process(x * gain)

    def process(self, x: np.ndarray, block_size: int = 2048) -> np.ndarray:
        self.reset()
        x = np.asarray(x, dtype=float)
        parts = [self.process_block(x[i : i + block_size]) for i in range(0, len(x), block_size)]
        return np.concatenate(parts) if parts else np.zeros(0, dtype=float)
