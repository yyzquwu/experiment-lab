"""CUPED adjustment for continuous outcomes."""

from __future__ import annotations

import numpy as np


def apply_cuped(outcome: np.ndarray, covariate: np.ndarray) -> tuple[np.ndarray, float]:
    outcome = np.asarray(outcome, dtype=float)
    covariate = np.asarray(covariate, dtype=float)

    centered = covariate - covariate.mean()
    variance = np.var(centered, ddof=1)
    if variance <= 1e-12:
        return outcome.copy(), 0.0

    theta = np.cov(outcome, covariate, ddof=1)[0, 1] / variance
    adjusted = outcome - theta * centered
    return adjusted, float(theta)
