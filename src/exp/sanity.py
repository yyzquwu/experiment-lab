"""Experiment data quality and sanity checks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import chi2


@dataclass(frozen=True)
class SRMResult:
    chi_square: float
    p_value: float
    observed: tuple[int, int]
    expected: tuple[float, float]


@dataclass(frozen=True)
class BalanceResult:
    mean_control: float
    mean_treatment: float
    standardized_diff: float


def srm_check(control_n: int, treatment_n: int, expected_treatment_ratio: float = 0.5) -> SRMResult:
    total = control_n + treatment_n
    expected_treatment = total * expected_treatment_ratio
    expected_control = total - expected_treatment

    chi_sq = ((control_n - expected_control) ** 2) / max(expected_control, 1e-12)
    chi_sq += ((treatment_n - expected_treatment) ** 2) / max(expected_treatment, 1e-12)

    p_value = 1.0 - chi2.cdf(chi_sq, df=1)
    return SRMResult(
        chi_square=float(chi_sq),
        p_value=float(p_value),
        observed=(control_n, treatment_n),
        expected=(float(expected_control), float(expected_treatment)),
    )


def missingness_summary(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values)
    missing = np.isnan(values).sum()
    total = values.size
    return {
        "missing_count": float(missing),
        "total_count": float(total),
        "missing_rate": float(missing / max(total, 1)),
    }


def missingness_by_variant(frame: pd.DataFrame, value_column: str, variant_column: str = "variant") -> pd.DataFrame:
    rows = []
    for variant, subset in frame.groupby(variant_column):
        summary = missingness_summary(subset[value_column].to_numpy())
        rows.append(
            {
                "variant": variant,
                "missing_count": summary["missing_count"],
                "total_count": summary["total_count"],
                "missing_rate": summary["missing_rate"],
            }
        )
    return pd.DataFrame(rows).sort_values("variant").reset_index(drop=True)


def covariate_balance(control_values: np.ndarray, treatment_values: np.ndarray) -> BalanceResult:
    control_values = np.asarray(control_values, dtype=float)
    treatment_values = np.asarray(treatment_values, dtype=float)

    mean_control = control_values.mean()
    mean_treatment = treatment_values.mean()

    pooled_sd = np.sqrt((np.var(control_values, ddof=1) + np.var(treatment_values, ddof=1)) / 2.0)
    standardized_diff = (mean_treatment - mean_control) / max(pooled_sd, 1e-12)

    return BalanceResult(
        mean_control=float(mean_control),
        mean_treatment=float(mean_treatment),
        standardized_diff=float(standardized_diff),
    )


def covariate_balance_table(frame: pd.DataFrame, columns: list[str], variant_column: str = "variant") -> pd.DataFrame:
    rows = []
    control = frame[frame[variant_column] == "control"]
    treatment = frame[frame[variant_column] == "treatment"]
    for column in columns:
        if column not in frame.columns or not pd.api.types.is_numeric_dtype(frame[column]):
            continue
        balance = covariate_balance(control[column].to_numpy(), treatment[column].to_numpy())
        rows.append(
            {
                "column": column,
                "mean_control": balance.mean_control,
                "mean_treatment": balance.mean_treatment,
                "standardized_diff": balance.standardized_diff,
            }
        )
    return pd.DataFrame(rows).sort_values("column").reset_index(drop=True)


def segment_assignment_table(frame: pd.DataFrame, segment_column: str, variant_column: str = "variant") -> pd.DataFrame:
    counts = pd.crosstab(frame[segment_column], frame[variant_column])
    counts = counts.reset_index().rename(columns={segment_column: "segment"})
    return counts
