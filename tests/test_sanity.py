import numpy as np
import pandas as pd

from exp.sanity import covariate_balance_table, missingness_by_variant, missingness_summary, srm_check
from exp.sequential import alpha_spending_schedule, beta_binomial_expected_loss, beta_binomial_posterior_prob_lift


def test_srm_flags_unbalanced_split() -> None:
    result = srm_check(control_n=7000, treatment_n=3000, expected_treatment_ratio=0.5)
    assert result.p_value < 1e-6


def test_missingness_summary() -> None:
    values = np.array([1.0, np.nan, 2.0, np.nan, 3.0])
    summary = missingness_summary(values)
    assert summary["missing_count"] == 2
    assert abs(summary["missing_rate"] - 0.4) < 1e-9


def test_missingness_by_variant_and_balance_table() -> None:
    frame = pd.DataFrame(
        {
            "variant": ["control", "control", "treatment", "treatment"],
            "outcome": [1.0, np.nan, 2.0, 3.0],
            "pre_metric": [0.2, 0.4, 0.3, 0.5],
        }
    )
    missing = missingness_by_variant(frame, "outcome")
    balance = covariate_balance_table(frame, ["pre_metric"])
    assert len(missing) == 2
    assert not balance.empty


def test_sequential_helpers_behave_reasonably() -> None:
    schedule = alpha_spending_schedule(alpha=0.05, num_looks=5)
    posterior = beta_binomial_posterior_prob_lift(100, 900, 130, 870, mc_samples=3000, random_seed=7)
    expected_loss = beta_binomial_expected_loss(100, 900, 130, 870, mc_samples=3000, random_seed=7)
    assert schedule[0] < schedule[-1]
    assert posterior > 0.9
    assert expected_loss >= 0.0
