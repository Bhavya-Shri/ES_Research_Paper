"""Complementary 3-way Linkwitz–Riley 4th-order crossover.

Independent Butterworth band splits are not magnitude-complementary and can
boost level near the cutoffs. This design uses cascaded LR4 splits at fc_low
and fc_high, and applies the high-frequency LR4 allpass (LP+HP) to the low
band so the three paths sum to an allpass rather than a peaked response.
"""

from __future__ import annotations

import numpy as np

from .filters import SOSFilter, lr4_sos


class LinkwitzRileyCrossover3Way:
    def __init__(self, fs: float = 48000.0, fc_low: float = 300.0, fc_high: float = 4000.0):
        self.fs = float(fs)
        self.fc_low = float(fc_low)
        self.fc_high = float(fc_high)
        self._lp_low = SOSFilter(lr4_sos(self.fc_low, self.fs, "low"))
        self._hp_low = SOSFilter(lr4_sos(self.fc_low, self.fs, "high"))
        self._lp_high_mid = SOSFilter(lr4_sos(self.fc_high, self.fs, "low"))
        self._hp_high_high = SOSFilter(lr4_sos(self.fc_high, self.fs, "high"))
        # Allpass compensation on the low path: LR4 LP + HP at fc_high.
        self._lp_high_low = SOSFilter(lr4_sos(self.fc_high, self.fs, "low"))
        self._hp_high_low = SOSFilter(lr4_sos(self.fc_high, self.fs, "high"))

    def reset(self) -> None:
        for filt in (
            self._lp_low,
            self._hp_low,
            self._lp_high_mid,
            self._hp_high_high,
            self._lp_high_low,
            self._hp_high_low,
        ):
            filt.reset()

    def process(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        x = np.asarray(x, dtype=float)
        low0 = self._lp_low.process(x)
        rest = self._hp_low.process(x)
        mid = self._lp_high_mid.process(rest)
        high = self._hp_high_high.process(rest)
        low = self._lp_high_low.process(low0) + self._hp_high_low.process(low0)
        return low, mid, high

    def reconstruct(self, x: np.ndarray) -> np.ndarray:
        low, mid, high = self.process(x)
        return low + mid + high
