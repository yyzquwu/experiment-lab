"""Sequential-safe decision helpers."""

from __future__ import annotations

import numpy as np


def bonferroni_alpha(alpha: float, num_looks: int) -> float:
    return alpha / max(num_looks, 1)


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
