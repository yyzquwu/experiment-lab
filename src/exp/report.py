"""Markdown report generation for A/B experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .cuped import apply_cuped
from .metrics import binary_metric_summary, continuous_metric_summary
from .power import binary_sample_size_per_variant, mde_binary
from .sanity import covariate_balance, missingness_summary, srm_check
from .sequential import beta_binomial_posterior_prob_lift, bonferroni_alpha


def generate_report(
    input_path: str,
    output_path: str,
    metric_column: str = "outcome",
    metric_type: str = "binary",
    covariate_column: str | None = "pre_metric",
    alpha: float = 0.05,
    expected_treatment_ratio: float = 0.5,
    sequential_looks: int = 5,
) -> None:
    df = pd.read_parquet(input_path) if input_path.endswith(".parquet") else pd.read_csv(input_path)

    required_cols = {"user_id", "variant", "timestamp", metric_column}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {sorted(missing_cols)}")

    control_df = df[df["variant"] == "control"].copy()
    treatment_df = df[df["variant"] == "treatment"].copy()
    if control_df.empty or treatment_df.empty:
        raise ValueError("Both control and treatment variants must exist.")

    srm = srm_check(len(control_df), len(treatment_df), expected_treatment_ratio=expected_treatment_ratio)
    miss = missingness_summary(df[metric_column].to_numpy())

    cuped_note = "Not applied"
    analysis_control = control_df[metric_column].to_numpy()
    analysis_treatment = treatment_df[metric_column].to_numpy()

    if covariate_column and covariate_column in df.columns and metric_type == "continuous":
        adjusted_all, theta = apply_cuped(df[metric_column].to_numpy(), df[covariate_column].to_numpy())
        control_mask = df["variant"] == "control"
        treatment_mask = df["variant"] == "treatment"
        analysis_control = adjusted_all[control_mask]
        analysis_treatment = adjusted_all[treatment_mask]
        balance = covariate_balance(control_df[covariate_column].to_numpy(), treatment_df[covariate_column].to_numpy())
        cuped_note = f"Applied with theta={theta:.4f}; pre-metric SMD={balance.standardized_diff:.4f}"

    if metric_type == "binary":
        result = binary_metric_summary(analysis_control, analysis_treatment, alpha=alpha)
        control_successes = int(control_df[metric_column].sum())
        treatment_successes = int(treatment_df[metric_column].sum())
        posterior_prob = beta_binomial_posterior_prob_lift(
            control_successes=control_successes,
            control_failures=len(control_df) - control_successes,
            treatment_successes=treatment_successes,
            treatment_failures=len(treatment_df) - treatment_successes,
        )

        recommended_n = binary_sample_size_per_variant(
            baseline_rate=max(float(control_df[metric_column].mean()), 1e-4),
            mde_absolute=max(abs(result.absolute_lift), 0.001),
            alpha=alpha,
            power=0.8,
        )

    elif metric_type == "continuous":
        result = continuous_metric_summary(analysis_control, analysis_treatment, alpha=alpha)
        posterior_prob = float("nan")
        recommended_n = 0
    else:
        raise ValueError("metric_type must be 'binary' or 'continuous'")

    alpha_seq = bonferroni_alpha(alpha=alpha, num_looks=sequential_looks)
    significant_fixed = result.p_value < alpha
    significant_sequential = result.p_value < alpha_seq

    mde_now = mde_binary(
        baseline_rate=max(float(control_df[metric_column].mean()), 1e-4),
        n_per_variant=min(len(control_df), len(treatment_df)),
        alpha=alpha,
        power=0.8,
    ) if metric_type == "binary" else float("nan")

    decision = "Ship treatment"
    if not significant_fixed and (pd.isna(posterior_prob) or posterior_prob < 0.95):
        decision = "Keep control and iterate"
    elif significant_fixed and not significant_sequential:
        decision = "Promising but wait for full sample"

    lines = [
        f"# Experiment Report: {Path(input_path).stem}",
        "",
        "## Setup",
        f"- Rows: {len(df)}",
        f"- Variants: control={len(control_df)}, treatment={len(treatment_df)}",
        f"- Metric column: `{metric_column}` ({metric_type})",
        f"- CUPED: {cuped_note}",
        "",
        "## Sanity Checks",
        f"- SRM p-value: {srm.p_value:.6f} (chi2={srm.chi_square:.3f})",
        f"- Missing rate (`{metric_column}`): {miss['missing_rate']:.4%}",
        "",
        "## Results",
        f"- Control mean: {result.control_mean:.6f}",
        f"- Treatment mean: {result.treatment_mean:.6f}",
        f"- Absolute lift: {result.absolute_lift:.6f}",
        f"- Relative lift: {result.relative_lift:.2%}",
        f"- p-value (fixed horizon): {result.p_value:.6f}",
        f"- {100*(1-alpha):.0f}% CI for lift: [{result.ci_low:.6f}, {result.ci_high:.6f}]",
        f"- Sequential threshold (Bonferroni, {sequential_looks} looks): {alpha_seq:.6f}",
        f"- Significant at sequential threshold: {significant_sequential}",
    ]

    if metric_type == "binary":
        lines.extend(
            [
                f"- Bayesian P(treatment > control): {posterior_prob:.4f}",
                f"- Current MDE at n={min(len(control_df), len(treatment_df))} per variant: {mde_now:.4f}",
                f"- Approx required n/variant for observed effect size: {recommended_n}",
            ]
        )

    lines.extend(
        [
            "",
            "## Decision",
            f"- {decision}",
            "",
            "## Notes",
            "- Use this report with business guardrails (cost, risk, seasonality) before launch.",
        ]
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate markdown experiment report from CSV/Parquet data.")
    parser.add_argument("--input", required=True, help="Input CSV or Parquet file")
    parser.add_argument("--output", required=True, help="Output markdown report path")
    parser.add_argument("--metric-column", default="outcome")
    parser.add_argument("--metric-type", choices=["binary", "continuous"], default="binary")
    parser.add_argument("--covariate-column", default="pre_metric")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--expected-treatment-ratio", type=float, default=0.5)
    parser.add_argument("--sequential-looks", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    covariate = args.covariate_column if args.covariate_column.lower() != "none" else None
    generate_report(
        input_path=args.input,
        output_path=args.output,
        metric_column=args.metric_column,
        metric_type=args.metric_type,
        covariate_column=covariate,
        alpha=args.alpha,
        expected_treatment_ratio=args.expected_treatment_ratio,
        sequential_looks=args.sequential_looks,
    )


if __name__ == "__main__":
    main()
