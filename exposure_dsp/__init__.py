"""Frequency-adaptive exposure-control DSP used by the research experiments."""

from .aweighting import AWeightingFilter, a_weight_db_iec, digital_a_weighting_sos
from .crossover import LinkwitzRileyCrossover3Way
from .limiter import BroadbandExposureLimiter, PeakCeilingLimiter
from .metrics import clip_metrics, laeq_proxy, log_spectral_distance, lufs
from .proposed import ProposedConfig, ProposedProcessor

__all__ = [
    "AWeightingFilter",
    "BroadbandExposureLimiter",
    "LinkwitzRileyCrossover3Way",
    "PeakCeilingLimiter",
    "ProposedConfig",
    "ProposedProcessor",
    "a_weight_db_iec",
    "clip_metrics",
    "digital_a_weighting_sos",
    "laeq_proxy",
    "log_spectral_distance",
    "lufs",
]
