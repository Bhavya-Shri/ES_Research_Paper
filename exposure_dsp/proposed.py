"""Three-band exposure-oriented processor.

Low: attenuate sub-bass and add harmonics that cover the intended fundamental
range. Mid: A-weighted compressor. High: envelope-driven transient-aware gain.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from scipy import signal

from .aweighting import AWeightingFilter
from .crossover import LinkwitzRileyCrossover3Way
from .filters import Biquad, EnvelopeFollower, SOSFilter, rbj_highpass, rbj_lowshelf, rbj_lowpass
from .limiter import PeakCeilingLimiter


@dataclass
class ProposedConfig:
    fs: float = 48000.0
    fc_low: float = 300.0
    fc_high: float = 4000.0
    sub_cutoff: float = 100.0
    sub_atten_db: float = -12.0
    harmonic_mode: str = "wide"  # "wide" (LTI, 80-400 Hz) or "adaptive"
    harmonic_wide: tuple[float, float] = (80.0, 400.0)
    a2: float = 0.8
    a3: float = 0.35
    harmonic_mix: float = 1.0
    hop: int = 256
    mid_target_dba: float = 78.0
    mid_ratio: float = 4.0
    mid_attack_s: float = 0.005
    mid_release_s: float = 0.050
    db_ref: float = 94.0
    high_thresh_db: float = -12.0
    high_gamma: float = 0.5
    high_attack_s: float = 0.002
    high_release_s: float = 0.050
    out_ceiling_dbfs: float = -1.0
    use_low: bool = True
    use_mid: bool = True
    use_high: bool = True
    f0_min: float = 25.0
    f0_max: float = 100.0
    f0_buf_n: int = 8192

    @classmethod
    def aligned(cls) -> "ProposedConfig":
        """S2: no bass shelf, no harmonics, stronger mid cut. Do not retune on the 20-clip mean."""
        return cls(sub_atten_db=0.0, harmonic_mix=0.0, mid_target_dba=72.0)


class ProposedProcessor:
    def __init__(self, cfg: ProposedConfig | None = None):
        self.cfg = cfg or ProposedConfig()
        fs = self.cfg.fs
        self.crossover = LinkwitzRileyCrossover3Way(fs, self.cfg.fc_low, self.cfg.fc_high)
        self.sub_lpf = SOSFilter(signal.butter(4, self.cfg.sub_cutoff, btype="low", fs=fs, output="sos"))
        self.sub_shelf = Biquad(*rbj_lowshelf(self.cfg.sub_cutoff, fs, self.cfg.sub_atten_db))
        wide_lo, wide_hi = self.cfg.harmonic_wide
        self.harm_wide = SOSFilter(
            signal.butter(4, [wide_lo, wide_hi], btype="bandpass", fs=fs, output="sos")
        )
        self.harm_hpf = Biquad(*rbj_highpass(80.0, fs))
        self.harm_lpf = Biquad(*rbj_lowpass(400.0, fs))
        self.mid_aweight = AWeightingFilter(fs)
        self.mid_env = EnvelopeFollower(fs, self.cfg.mid_attack_s, self.cfg.mid_release_s)
        self.high_env = EnvelopeFollower(fs, self.cfg.high_attack_s, self.cfg.high_release_s)
        self.ceiling = PeakCeilingLimiter(fs, self.cfg.out_ceiling_dbfs)
        self.beta = 10.0 ** (self.cfg.sub_atten_db / 20.0)
        self.high_thr = 10.0 ** (self.cfg.high_thresh_db / 20.0)
        self._f0_buf = np.zeros(self.cfg.f0_buf_n, dtype=float)
        self._f0 = 50.0
        self._harm_lo = 80.0
        self._harm_hi = 400.0
        self._carry = np.zeros(0, dtype=float)

    def reset(self) -> None:
        self.crossover.reset()
        self.sub_lpf.reset()
        self.sub_shelf.reset()
        self.harm_wide.reset()
        self.harm_hpf.reset()
        self.harm_lpf.reset()
        self.mid_aweight.reset()
        self.mid_env.reset()
        self.high_env.reset()
        self.ceiling.reset()
        self._f0_buf[:] = 0.0
        self._f0 = 50.0
        self._set_harmonic_edges(80.0, 400.0)
        self._carry = np.zeros(0, dtype=float)

    def _set_harmonic_edges(self, f_lo: float, f_hi: float) -> None:
        fs = self.cfg.fs
        f_lo = float(np.clip(f_lo, 60.0, 250.0))
        f_hi = float(np.clip(max(f_hi, f_lo + 40.0), f_lo + 40.0, 0.45 * fs))
        self._harm_lo, self._harm_hi = f_lo, f_hi
        self.harm_hpf.set_tf(*rbj_highpass(f_lo, fs))
        self.harm_lpf.set_tf(*rbj_lowpass(f_hi, fs))

    def _estimate_f0(self, sub_block: np.ndarray) -> float:
        nbuf = len(self._f0_buf)
        n = len(sub_block)
        if n >= nbuf:
            self._f0_buf[:] = sub_block[-nbuf:]
        else:
            self._f0_buf[:-n] = self._f0_buf[n:]
            self._f0_buf[-n:] = sub_block
        window = self._f0_buf * np.hanning(nbuf)
        nfft = max(8192, nbuf)
        spec = np.abs(np.fft.rfft(window, n=nfft))
        freqs = np.fft.rfftfreq(nfft, 1.0 / self.cfg.fs)
        mask = (freqs >= self.cfg.f0_min) & (freqs <= self.cfg.f0_max)
        if not np.any(mask) or spec[mask].max() < 1e-6:
            return self._f0
        peak = float(freqs[mask][np.argmax(spec[mask])])
        self._f0 = 0.85 * self._f0 + 0.15 * peak
        return self._f0

    def _process_low(self, x_low: np.ndarray) -> np.ndarray:
        x_sub = self.sub_lpf.process(x_low)
        x_nld = self.cfg.a2 * (x_sub ** 2) + self.cfg.a3 * (x_sub ** 3)
        if self.cfg.harmonic_mode == "adaptive":
            f0 = self._estimate_f0(x_sub)
            f_lo = max(1.6 * f0, 70.0)
            f_hi = min(4.0 * f0, 450.0)
            if abs(f_lo - self._harm_lo) > 3.0 or abs(f_hi - self._harm_hi) > 8.0:
                self._set_harmonic_edges(f_lo, f_hi)
            y_harm = self.harm_lpf.process(self.harm_hpf.process(x_nld))
        else:
            y_harm = self.harm_wide.process(x_nld)
        return self.sub_shelf.process(x_low) + self.cfg.harmonic_mix * y_harm

    def _process_mid(self, x_mid: np.ndarray) -> np.ndarray:
        xa = self.mid_aweight.process(x_mid)
        env = self.mid_env.process(np.abs(xa))
        spl = 20.0 * np.log10(env + 1e-9) + self.cfg.db_ref
        excess = np.maximum(spl - self.cfg.mid_target_dba, 0.0)
        gr_db = excess * (1.0 - 1.0 / self.cfg.mid_ratio)
        gain = 10.0 ** (-gr_db / 20.0)
        return x_mid * gain

    def _process_high(self, x_high: np.ndarray) -> np.ndarray:
        env = self.high_env.process(np.abs(x_high))
        gain = 1.0 / (1.0 + self.cfg.high_gamma * np.maximum(env - self.high_thr, 0.0))
        return x_high * gain

    def _process_hop(self, x: np.ndarray) -> np.ndarray:
        low, mid, high = self.crossover.process(x)
        y_low = self._process_low(low) if self.cfg.use_low else low
        y_mid = self._process_mid(mid) if self.cfg.use_mid else mid
        y_high = self._process_high(high) if self.cfg.use_high else high
        return self.ceiling.process(y_low + y_mid + y_high)

    def process_block(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        buf = np.concatenate([self._carry, x]) if len(self._carry) else x
        hop = int(self.cfg.hop)
        outs = []
        i = 0
        while i + hop <= len(buf):
            outs.append(self._process_hop(buf[i : i + hop]))
            i += hop
        self._carry = np.asarray(buf[i:], dtype=float)
        return np.concatenate(outs) if outs else np.zeros(0, dtype=float)

    def flush(self) -> np.ndarray:
        if len(self._carry) == 0:
            return np.zeros(0, dtype=float)
        y = self._process_hop(self._carry)
        self._carry = np.zeros(0, dtype=float)
        return y

    def process(self, x: np.ndarray, block_size: int = 2048) -> np.ndarray:
        self.reset()
        x = np.asarray(x, dtype=float)
        parts = [self.process_block(x[i : i + block_size]) for i in range(0, len(x), block_size)]
        parts.append(self.flush())
        parts = [p for p in parts if len(p)]
        return np.concatenate(parts) if parts else np.zeros(0, dtype=float)


def make_ablation(name: str, base: ProposedConfig | None = None) -> ProposedProcessor:
    flags = {
        "mid_only": (False, True, False),
        "mid_low": (True, True, False),
        "mid_high": (False, True, True),
        "full": (True, True, True),
        "crossover_only": (False, False, False),
    }
    if name not in flags:
        raise ValueError(f"Unknown ablation '{name}'. Choose from {list(flags)}")
    use_low, use_mid, use_high = flags[name]
    cfg = replace(base or ProposedConfig(), use_low=use_low, use_mid=use_mid, use_high=use_high)
    return ProposedProcessor(cfg)
