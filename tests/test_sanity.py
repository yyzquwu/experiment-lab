import numpy as np

from exp.sanity import missingness_summary, srm_check


def test_srm_flags_unbalanced_split() -> None:
    result = srm_check(control_n=7000, treatment_n=3000, expected_treatment_ratio=0.5)
    assert result.p_value < 1e-6


def test_missingness_summary() -> None:
    values = np.array([1.0, np.nan, 2.0, np.nan, 3.0])
    summary = missingness_summary(values)
    assert summary["missing_count"] == 2
    assert abs(summary["missing_rate"] - 0.4) < 1e-9
