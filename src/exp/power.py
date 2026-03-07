"""Power and sample size calculators."""

from __future__ import annotations

import math

from scipy.stats import norm


def binary_sample_size_per_variant(
    baseline_rate: float,
    mde_absolute: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    p1 = baseline_rate
    p2 = baseline_rate + mde_absolute
    p_bar = (p1 + p2) / 2.0

    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    z_beta = norm.ppf(power)
    numerator = 2.0 * (z_alpha + z_beta) ** 2 * p_bar * (1.0 - p_bar)
    denominator = mde_absolute**2

    return int(math.ceil(numerator / max(denominator, 1e-12)))


def continuous_sample_size_per_variant(
    sigma: float,
    mde_absolute: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    z_beta = norm.ppf(power)
    numerator = 2.0 * (z_alpha + z_beta) ** 2 * sigma**2
    denominator = mde_absolute**2
    return int(math.ceil(numerator / max(denominator, 1e-12)))


def mde_binary(
    baseline_rate: float,
    n_per_variant: int,
    alpha: float = 0.05,
    power: float = 0.8,
) -> float:
    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    z_beta = norm.ppf(power)
    scale = math.sqrt(2.0 * baseline_rate * (1.0 - baseline_rate) / max(n_per_variant, 1))
    return (z_alpha + z_beta) * scale


def mde_continuous(
    sigma: float,
    n_per_variant: int,
    alpha: float = 0.05,
    power: float = 0.8,
) -> float:
    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    z_beta = norm.ppf(power)
    scale = math.sqrt(2.0 * sigma**2 / max(n_per_variant, 1))
    return (z_alpha + z_beta) * scale
