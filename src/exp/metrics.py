"""Core experiment metric summaries."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class MetricResult:
    control_mean: float
    treatment_mean: float
    absolute_lift: float
    relative_lift: float
    p_value: float
    ci_low: float
    ci_high: float
    standard_error: float
    test_statistic: float


def _relative_lift(control: float, treatment: float) -> float:
    if control == 0:
        return float("inf") if treatment > 0 else 0.0
    return (treatment - control) / control


def bootstrap_difference_ci(
    control: np.ndarray,
    treatment: np.ndarray,
    confidence_level: float = 0.95,
    n_bootstrap: int = 2000,
    random_seed: int = 42,
) -> tuple[float, float]:
    control = np.asarray(control, dtype=float)
    treatment = np.asarray(treatment, dtype=float)
    rng = np.random.default_rng(random_seed)

    control_draws = rng.choice(control, size=(n_bootstrap, control.size), replace=True)
    treatment_draws = rng.choice(treatment, size=(n_bootstrap, treatment.size), replace=True)
    diffs = treatment_draws.mean(axis=1) - control_draws.mean(axis=1)

    lower_q = (1.0 - confidence_level) / 2.0
    upper_q = 1.0 - lower_q
    return float(np.quantile(diffs, lower_q)), float(np.quantile(diffs, upper_q))


def binary_metric_summary(control: np.ndarray, treatment: np.ndarray, alpha: float = 0.05) -> MetricResult:
    control = np.asarray(control, dtype=float)
    treatment = np.asarray(treatment, dtype=float)

    p_control = control.mean()
    p_treatment = treatment.mean()
    lift = p_treatment - p_control

    n_control = control.size
    n_treatment = treatment.size
    pooled = (control.sum() + treatment.sum()) / (n_control + n_treatment)
    standard_error = np.sqrt(max(pooled * (1.0 - pooled), 1e-12) * (1.0 / n_control + 1.0 / n_treatment))

    z_stat = lift / max(standard_error, 1e-12)
    p_value = 2.0 * (1.0 - stats.norm.cdf(abs(z_stat)))

    z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)
    ci_low = lift - z_alpha * standard_error
    ci_high = lift + z_alpha * standard_error

    return MetricResult(
        control_mean=float(p_control),
        treatment_mean=float(p_treatment),
        absolute_lift=float(lift),
        relative_lift=float(_relative_lift(p_control, p_treatment)),
        p_value=float(p_value),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        standard_error=float(standard_error),
        test_statistic=float(z_stat),
    )


def continuous_metric_summary(control: np.ndarray, treatment: np.ndarray, alpha: float = 0.05) -> MetricResult:
    control = np.asarray(control, dtype=float)
    treatment = np.asarray(treatment, dtype=float)

    mu_control = control.mean()
    mu_treatment = treatment.mean()
    lift = mu_treatment - mu_control

    t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)

    var_control = np.var(control, ddof=1)
    var_treatment = np.var(treatment, ddof=1)
    standard_error = np.sqrt(var_control / control.size + var_treatment / treatment.size)
    z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)

    ci_low = lift - z_alpha * standard_error
    ci_high = lift + z_alpha * standard_error

    return MetricResult(
        control_mean=float(mu_control),
        treatment_mean=float(mu_treatment),
        absolute_lift=float(lift),
        relative_lift=float(_relative_lift(mu_control, mu_treatment)),
        p_value=float(p_value),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        standard_error=float(standard_error),
        test_statistic=float(t_stat),
    )


def ratio_metric_summary(
    control_numerator: np.ndarray,
    control_denominator: np.ndarray,
    treatment_numerator: np.ndarray,
    treatment_denominator: np.ndarray,
    alpha: float = 0.05,
) -> MetricResult:
    control_numerator = np.asarray(control_numerator, dtype=float)
    control_denominator = np.asarray(control_denominator, dtype=float)
    treatment_numerator = np.asarray(treatment_numerator, dtype=float)
    treatment_denominator = np.asarray(treatment_denominator, dtype=float)

    control_ratio = control_numerator.sum() / max(control_denominator.sum(), 1e-12)
    treatment_ratio = treatment_numerator.sum() / max(treatment_denominator.sum(), 1e-12)
    lift = treatment_ratio - control_ratio

    control_user_ratio = control_numerator / np.maximum(control_denominator, 1e-12)
    treatment_user_ratio = treatment_numerator / np.maximum(treatment_denominator, 1e-12)

    standard_error = np.sqrt(
        np.var(control_user_ratio, ddof=1) / control_user_ratio.size
        + np.var(treatment_user_ratio, ddof=1) / treatment_user_ratio.size
    )
    z_stat = lift / max(standard_error, 1e-12)
    p_value = 2.0 * (1.0 - stats.norm.cdf(abs(z_stat)))

    z_alpha = stats.norm.ppf(1.0 - alpha / 2.0)
    ci_low = lift - z_alpha * standard_error
    ci_high = lift + z_alpha * standard_error

    return MetricResult(
        control_mean=float(control_ratio),
        treatment_mean=float(treatment_ratio),
        absolute_lift=float(lift),
        relative_lift=float(_relative_lift(control_ratio, treatment_ratio)),
        p_value=float(p_value),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        standard_error=float(standard_error),
        test_statistic=float(z_stat),
    )
