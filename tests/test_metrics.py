import numpy as np

from exp.metrics import (
    binary_metric_summary,
    bootstrap_difference_ci,
    continuous_metric_summary,
    ratio_metric_summary,
)


def test_binary_metric_summary_detects_positive_lift() -> None:
    control = np.array([0] * 900 + [1] * 100)
    treatment = np.array([0] * 860 + [1] * 140)

    result = binary_metric_summary(control, treatment)
    assert result.absolute_lift > 0
    assert result.p_value < 0.05
    assert result.standard_error > 0


def test_continuous_metric_summary_detects_positive_lift() -> None:
    rng = np.random.default_rng(5)
    control = rng.normal(100.0, 10.0, size=2000)
    treatment = rng.normal(102.0, 10.0, size=2000)

    result = continuous_metric_summary(control, treatment)
    assert result.absolute_lift > 0
    assert result.p_value < 0.05


def test_ratio_metric_summary_detects_positive_lift() -> None:
    control_clicks = np.array([8, 6, 10, 5, 9, 7])
    control_impressions = np.array([100, 100, 100, 100, 100, 100])
    treatment_clicks = np.array([10, 9, 12, 8, 11, 10])
    treatment_impressions = np.array([100, 100, 100, 100, 100, 100])

    result = ratio_metric_summary(control_clicks, control_impressions, treatment_clicks, treatment_impressions)
    assert result.absolute_lift > 0
    assert result.standard_error > 0


def test_bootstrap_ci_contains_observed_difference() -> None:
    control = np.array([0.10, 0.12, 0.11, 0.09, 0.10])
    treatment = np.array([0.13, 0.15, 0.14, 0.12, 0.13])
    observed = treatment.mean() - control.mean()
    ci_low, ci_high = bootstrap_difference_ci(control, treatment, n_bootstrap=500, random_seed=3)
    assert ci_low <= observed <= ci_high
