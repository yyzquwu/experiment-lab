import numpy as np

from exp.metrics import binary_metric_summary, continuous_metric_summary


def test_binary_metric_summary_detects_positive_lift() -> None:
    control = np.array([0] * 900 + [1] * 100)
    treatment = np.array([0] * 860 + [1] * 140)

    result = binary_metric_summary(control, treatment)
    assert result.absolute_lift > 0
    assert result.p_value < 0.05


def test_continuous_metric_summary_detects_positive_lift() -> None:
    rng = np.random.default_rng(5)
    control = rng.normal(100.0, 10.0, size=2000)
    treatment = rng.normal(102.0, 10.0, size=2000)

    result = continuous_metric_summary(control, treatment)
    assert result.absolute_lift > 0
    assert result.p_value < 0.05
