"""Sequential-safe decision helpers."""

from __future__ import annotations

import numpy as np
from scipy.stats import norm


def bonferroni_alpha(alpha: float, num_looks: int) -> float:
    return alpha / max(num_looks, 1)


def obrien_fleming_alpha(alpha: float, information_fraction: float) -> float:
    information_fraction = min(max(information_fraction, 1e-6), 1.0)
    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    return float(2.0 * (1.0 - norm.cdf(z_alpha / np.sqrt(information_fraction))))


def alpha_spending_schedule(alpha: float, num_looks: int, method: str = "obrien_fleming") -> list[float]:
    if num_looks <= 0:
        return []
    if method == "bonferroni":
        return [bonferroni_alpha(alpha, num_looks)] * num_looks
    if method != "obrien_fleming":
        raise ValueError("method must be 'obrien_fleming' or 'bonferroni'")
    return [obrien_fleming_alpha(alpha, idx / num_looks) for idx in range(1, num_looks + 1)]


def beta_binomial_posterior_prob_lift(
    control_successes: int,
    control_failures: int,
    treatment_successes: int,
    treatment_failures: int,
    mc_samples: int = 20000,
    random_seed: int = 42,
) -> float:
    rng = np.random.default_rng(random_seed)

    control_draws = rng.beta(1 + control_successes, 1 + control_failures, size=mc_samples)
    treatment_draws = rng.beta(1 + treatment_successes, 1 + treatment_failures, size=mc_samples)

    return float(np.mean(treatment_draws > control_draws))


def beta_binomial_expected_loss(
    control_successes: int,
    control_failures: int,
    treatment_successes: int,
    treatment_failures: int,
    mc_samples: int = 20000,
    random_seed: int = 42,
) -> float:
    rng = np.random.default_rng(random_seed)

    control_draws = rng.beta(1 + control_successes, 1 + control_failures, size=mc_samples)
    treatment_draws = rng.beta(1 + treatment_successes, 1 + treatment_failures, size=mc_samples)

    return float(np.mean(np.maximum(control_draws - treatment_draws, 0.0)))
