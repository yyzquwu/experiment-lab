"""Experiment analysis and markdown report generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .cuped import apply_cuped
from .metrics import (
    MetricResult,
    binary_metric_summary,
    bootstrap_difference_ci,
    continuous_metric_summary,
    ratio_metric_summary,
)
from .power import (
    binary_sample_size_per_variant,
    continuous_sample_size_per_variant,
    mde_binary,
    mde_continuous,
)
from .sanity import covariate_balance_table, missingness_by_variant, missingness_summary, segment_assignment_table, srm_check
from .sequential import (
    alpha_spending_schedule,
    beta_binomial_expected_loss,
    beta_binomial_posterior_prob_lift,
    bonferroni_alpha,
)


BAD_IF_HIGH_KEYWORDS = ("ticket", "refund", "cancel", "bounce", "latency", "delay", "complaint")


def _load_frame(input_path: str) -> pd.DataFrame:
    if input_path.endswith(".parquet"):
        return pd.read_parquet(input_path)
    return pd.read_csv(input_path)


def _metric_missingness(frame: pd.DataFrame, metric_type: str, metric_column: str, numerator_column: str | None, denominator_column: str | None) -> dict[str, float]:
    if metric_type == "ratio":
        missing_num = missingness_summary(frame[numerator_column].to_numpy()) if numerator_column else {"missing_rate": float("nan")}
        missing_den = missingness_summary(frame[denominator_column].to_numpy()) if denominator_column else {"missing_rate": float("nan")}
        return {
            "missing_rate": max(missing_num["missing_rate"], missing_den["missing_rate"]),
            "missing_count": missing_num.get("missing_count", 0.0) + missing_den.get("missing_count", 0.0),
        }
    return missingness_summary(frame[metric_column].to_numpy())


def _infer_guardrail_direction(column: str) -> str:
    lowered = column.lower()
    if any(keyword in lowered for keyword in BAD_IF_HIGH_KEYWORDS):
        return "lower_is_better"
    return "higher_is_better"


def _metric_result_from_frame(
    frame: pd.DataFrame,
    metric_type: str,
    metric_column: str,
    alpha: float,
    numerator_column: str | None = None,
    denominator_column: str | None = None,
    use_cuped: bool = False,
    covariate_column: str | None = None,
) -> tuple[MetricResult, dict[str, object]]:
    control = frame[frame["variant"] == "control"].copy()
    treatment = frame[frame["variant"] == "treatment"].copy()

    note = "Not applied"
    theta = 0.0
    if metric_type == "binary":
        result = binary_metric_summary(control[metric_column].to_numpy(), treatment[metric_column].to_numpy(), alpha=alpha)
        bootstrap_low, bootstrap_high = bootstrap_difference_ci(control[metric_column].to_numpy(), treatment[metric_column].to_numpy())
    elif metric_type == "continuous":
        control_values = control[metric_column].to_numpy()
        treatment_values = treatment[metric_column].to_numpy()
        if use_cuped and covariate_column and covariate_column in frame.columns:
            adjusted_all, theta = apply_cuped(frame[metric_column].to_numpy(), frame[covariate_column].to_numpy())
            working = frame.copy()
            working["_adjusted_metric"] = adjusted_all
            control_values = working.loc[working["variant"] == "control", "_adjusted_metric"].to_numpy()
            treatment_values = working.loc[working["variant"] == "treatment", "_adjusted_metric"].to_numpy()
            note = f"Applied with theta={theta:.4f}"
        result = continuous_metric_summary(control_values, treatment_values, alpha=alpha)
        bootstrap_low, bootstrap_high = bootstrap_difference_ci(control_values, treatment_values)
    elif metric_type == "ratio":
        result = ratio_metric_summary(
            control[numerator_column].to_numpy(),
            control[denominator_column].to_numpy(),
            treatment[numerator_column].to_numpy(),
            treatment[denominator_column].to_numpy(),
            alpha=alpha,
        )
        control_user_ratio = control[numerator_column].to_numpy() / np.maximum(control[denominator_column].to_numpy(), 1e-12)
        treatment_user_ratio = treatment[numerator_column].to_numpy() / np.maximum(treatment[denominator_column].to_numpy(), 1e-12)
        bootstrap_low, bootstrap_high = bootstrap_difference_ci(control_user_ratio, treatment_user_ratio)
    else:
        raise ValueError("metric_type must be 'binary', 'continuous', or 'ratio'")

    return result, {"cuped_note": note, "theta": theta, "bootstrap_ci": (bootstrap_low, bootstrap_high)}


def _guardrail_table(
    frame: pd.DataFrame,
    guardrail_columns: list[str],
    alpha: float,
    variant_column: str = "variant",
    directions: dict[str, str] | None = None,
) -> pd.DataFrame:
    rows = []
    directions = directions or {}
    control = frame[frame[variant_column] == "control"]
    treatment = frame[frame[variant_column] == "treatment"]
    for column in guardrail_columns:
        if column not in frame.columns:
            continue
        series = frame[column].dropna()
        is_binary = set(np.unique(series.astype(float))).issubset({0.0, 1.0}) if not series.empty else False
        result = (
            binary_metric_summary(control[column].to_numpy(), treatment[column].to_numpy(), alpha=alpha)
            if is_binary
            else continuous_metric_summary(control[column].to_numpy(), treatment[column].to_numpy(), alpha=alpha)
        )
        direction = directions.get(column, _infer_guardrail_direction(column))
        harmful = False
        if result.p_value < alpha:
            if direction == "lower_is_better":
                harmful = result.absolute_lift > 0
            else:
                harmful = result.absolute_lift < 0
        rows.append(
            {
                "metric": column,
                "control_mean": result.control_mean,
                "treatment_mean": result.treatment_mean,
                "absolute_lift": result.absolute_lift,
                "p_value": result.p_value,
                "direction": direction,
                "harmful_shift": harmful,
            }
        )
    return pd.DataFrame(rows)


def _segment_table(
    frame: pd.DataFrame,
    segment_column: str,
    metric_type: str,
    metric_column: str,
    alpha: float,
    numerator_column: str | None = None,
    denominator_column: str | None = None,
) -> pd.DataFrame:
    rows = []
    for segment, subset in frame.groupby(segment_column):
        if subset["variant"].nunique() < 2 or len(subset) < 100:
            continue
        result, _ = _metric_result_from_frame(
            subset,
            metric_type=metric_type,
            metric_column=metric_column,
            alpha=alpha,
            numerator_column=numerator_column,
            denominator_column=denominator_column,
        )
        rows.append(
            {
                "segment": segment,
                "rows": len(subset),
                "control_mean": result.control_mean,
                "treatment_mean": result.treatment_mean,
                "absolute_lift": result.absolute_lift,
                "relative_lift": result.relative_lift,
                "p_value": result.p_value,
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("absolute_lift", ascending=False).reset_index(drop=True)


def _interim_table(
    frame: pd.DataFrame,
    metric_type: str,
    metric_column: str,
    alpha: float,
    sequential_looks: int,
    numerator_column: str | None = None,
    denominator_column: str | None = None,
) -> pd.DataFrame:
    ordered = frame.sort_values("timestamp").reset_index(drop=True)
    bonf_alpha = bonferroni_alpha(alpha, sequential_looks)
    obf_alphas = alpha_spending_schedule(alpha, sequential_looks, method="obrien_fleming")
    rows = []

    for look_idx in range(1, sequential_looks + 1):
        cutoff = max(2, int(len(ordered) * look_idx / sequential_looks))
        look_frame = ordered.iloc[:cutoff]
        result, _ = _metric_result_from_frame(
            look_frame,
            metric_type=metric_type,
            metric_column=metric_column,
            alpha=alpha,
            numerator_column=numerator_column,
            denominator_column=denominator_column,
        )
        posterior_prob = float("nan")
        expected_loss = float("nan")
        if metric_type == "binary":
            control = look_frame[look_frame["variant"] == "control"][metric_column].to_numpy()
            treatment = look_frame[look_frame["variant"] == "treatment"][metric_column].to_numpy()
            posterior_prob = beta_binomial_posterior_prob_lift(
                control_successes=int(control.sum()),
                control_failures=len(control) - int(control.sum()),
                treatment_successes=int(treatment.sum()),
                treatment_failures=len(treatment) - int(treatment.sum()),
            )
            expected_loss = beta_binomial_expected_loss(
                control_successes=int(control.sum()),
                control_failures=len(control) - int(control.sum()),
                treatment_successes=int(treatment.sum()),
                treatment_failures=len(treatment) - int(treatment.sum()),
            )

        rows.append(
            {
                "look": look_idx,
                "rows": len(look_frame),
                "information_fraction": look_idx / sequential_looks,
                "absolute_lift": result.absolute_lift,
                "p_value": result.p_value,
                "bonferroni_alpha": bonf_alpha,
                "obrien_fleming_alpha": obf_alphas[look_idx - 1],
                "significant_bonferroni": result.p_value < bonf_alpha,
                "significant_obrien_fleming": result.p_value < obf_alphas[look_idx - 1],
                "posterior_prob_treatment_gt_control": posterior_prob,
                "expected_loss_of_shipping": expected_loss,
            }
        )
    return pd.DataFrame(rows)


def analyze_experiment(
    input_path: str,
    metric_column: str = "outcome",
    metric_type: str = "binary",
    covariate_column: str | None = "pre_metric",
    alpha: float = 0.05,
    expected_treatment_ratio: float = 0.5,
    sequential_looks: int = 5,
    numerator_column: str | None = None,
    denominator_column: str | None = None,
    guardrail_columns: list[str] | None = None,
    segment_column: str | None = "segment",
    guardrail_directions: dict[str, str] | None = None,
) -> dict[str, object]:
    df = _load_frame(input_path)

    required_cols = {"user_id", "variant", "timestamp"}
    if metric_type == "ratio":
        required_cols |= {numerator_column or "", denominator_column or ""}
    else:
        required_cols.add(metric_column)
    missing_cols = {column for column in required_cols if column and column not in df.columns}
    if missing_cols:
        raise ValueError(f"Missing required columns: {sorted(missing_cols)}")

    control_df = df[df["variant"] == "control"].copy()
    treatment_df = df[df["variant"] == "treatment"].copy()
    if control_df.empty or treatment_df.empty:
        raise ValueError("Both control and treatment variants must exist.")

    srm = srm_check(len(control_df), len(treatment_df), expected_treatment_ratio=expected_treatment_ratio)
    miss = _metric_missingness(df, metric_type, metric_column, numerator_column, denominator_column)
    missing_by_variant = missingness_by_variant(df, metric_column if metric_type != "ratio" else numerator_column)

    result, extras = _metric_result_from_frame(
        df,
        metric_type=metric_type,
        metric_column=metric_column,
        alpha=alpha,
        numerator_column=numerator_column,
        denominator_column=denominator_column,
        use_cuped=(metric_type == "continuous"),
        covariate_column=covariate_column,
    )
    bootstrap_low, bootstrap_high = extras["bootstrap_ci"]

    posterior_prob = float("nan")
    expected_loss = float("nan")
    recommended_n = 0
    current_mde = float("nan")
    if metric_type == "binary":
        control_successes = int(control_df[metric_column].sum())
        treatment_successes = int(treatment_df[metric_column].sum())
        posterior_prob = beta_binomial_posterior_prob_lift(
            control_successes=control_successes,
            control_failures=len(control_df) - control_successes,
            treatment_successes=treatment_successes,
            treatment_failures=len(treatment_df) - treatment_successes,
        )
        expected_loss = beta_binomial_expected_loss(
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
        current_mde = mde_binary(
            baseline_rate=max(float(control_df[metric_column].mean()), 1e-4),
            n_per_variant=min(len(control_df), len(treatment_df)),
            alpha=alpha,
            power=0.8,
        )
    elif metric_type == "continuous":
        sigma = float(df[metric_column].std(ddof=1))
        recommended_n = continuous_sample_size_per_variant(
            sigma=max(sigma, 1e-4),
            mde_absolute=max(abs(result.absolute_lift), 0.1),
            alpha=alpha,
            power=0.8,
        )
        current_mde = mde_continuous(
            sigma=max(sigma, 1e-4),
            n_per_variant=min(len(control_df), len(treatment_df)),
            alpha=alpha,
            power=0.8,
        )

    bonf_alpha = bonferroni_alpha(alpha=alpha, num_looks=sequential_looks)
    obf_alphas = alpha_spending_schedule(alpha=alpha, num_looks=sequential_looks, method="obrien_fleming")
    significant_fixed = result.p_value < alpha
    significant_bonferroni = result.p_value < bonf_alpha
    significant_obrien_fleming = result.p_value < obf_alphas[-1]

    guardrail_table = _guardrail_table(df, guardrail_columns or [], alpha, directions=guardrail_directions)
    harmful_guardrails = int(guardrail_table["harmful_shift"].sum()) if not guardrail_table.empty else 0
    segment_table = _segment_table(
        df,
        segment_column=segment_column,
        metric_type=metric_type,
        metric_column=metric_column,
        alpha=alpha,
        numerator_column=numerator_column,
        denominator_column=denominator_column,
    ) if segment_column and segment_column in df.columns else pd.DataFrame()
    assignment_table = segment_assignment_table(df, segment_column) if segment_column and segment_column in df.columns else pd.DataFrame()
    balance_columns = [column for column in [covariate_column, "device_score", "baseline_sessions", "prior_value"] if column and column in df.columns]
    balance_table = covariate_balance_table(df, balance_columns)
    interim_table = _interim_table(
        df,
        metric_type=metric_type,
        metric_column=metric_column,
        alpha=alpha,
        sequential_looks=sequential_looks,
        numerator_column=numerator_column,
        denominator_column=denominator_column,
    )

    decision = "Keep control and iterate"
    rationale = "The primary metric does not clear a convincing decision threshold yet."
    if srm.p_value < 0.01:
        decision = "Stop and investigate randomization"
        rationale = "SRM is too severe to trust the treatment effect estimate."
    elif miss["missing_rate"] > 0.02:
        decision = "Fix data quality before deciding"
        rationale = "Missingness is high enough that the effect estimate could be biased."
    elif harmful_guardrails > 0:
        decision = "Do not ship without guardrail mitigation"
        rationale = "The primary metric improved, but at least one guardrail moved in a harmful direction."
    elif significant_obrien_fleming or significant_fixed:
        decision = "Ship treatment"
        rationale = "The primary metric is positive and clears a defensible significance threshold without obvious guardrail damage."
        if significant_fixed and not significant_bonferroni:
            decision = "Promising but wait for full sample"
            rationale = "The fixed-horizon result is positive, but it is not strong enough to justify peeking-driven launch confidence."

    return {
        "frame": df,
        "result": result,
        "bootstrap_ci": (bootstrap_low, bootstrap_high),
        "srm": srm,
        "missing": miss,
        "missing_by_variant": missing_by_variant,
        "posterior_prob": posterior_prob,
        "expected_loss": expected_loss,
        "recommended_n": recommended_n,
        "current_mde": current_mde,
        "bonferroni_alpha": bonf_alpha,
        "obrien_fleming_alphas": obf_alphas,
        "significant_fixed": significant_fixed,
        "significant_bonferroni": significant_bonferroni,
        "significant_obrien_fleming": significant_obrien_fleming,
        "guardrail_table": guardrail_table,
        "segment_table": segment_table,
        "assignment_table": assignment_table,
        "balance_table": balance_table,
        "interim_table": interim_table,
        "cuped_note": extras["cuped_note"],
        "decision": decision,
        "decision_rationale": rationale,
        "metric_type": metric_type,
        "metric_column": metric_column,
        "numerator_column": numerator_column,
        "denominator_column": denominator_column,
    }


def generate_report(
    input_path: str,
    output_path: str,
    metric_column: str = "outcome",
    metric_type: str = "binary",
    covariate_column: str | None = "pre_metric",
    alpha: float = 0.05,
    expected_treatment_ratio: float = 0.5,
    sequential_looks: int = 5,
    numerator_column: str | None = None,
    denominator_column: str | None = None,
    guardrail_columns: list[str] | None = None,
    segment_column: str | None = "segment",
    case_title: str | None = None,
    question: str | None = None,
    personal_context: str | None = None,
    guardrail_directions: dict[str, str] | None = None,
) -> dict[str, object]:
    analysis = analyze_experiment(
        input_path=input_path,
        metric_column=metric_column,
        metric_type=metric_type,
        covariate_column=covariate_column,
        alpha=alpha,
        expected_treatment_ratio=expected_treatment_ratio,
        sequential_looks=sequential_looks,
        numerator_column=numerator_column,
        denominator_column=denominator_column,
        guardrail_columns=guardrail_columns,
        segment_column=segment_column,
        guardrail_directions=guardrail_directions,
    )

    frame = analysis["frame"]
    result = analysis["result"]
    srm = analysis["srm"]
    miss = analysis["missing"]
    balance_table = analysis["balance_table"]
    guardrail_table = analysis["guardrail_table"]
    segment_table = analysis["segment_table"]
    interim_table = analysis["interim_table"]
    bootstrap_low, bootstrap_high = analysis["bootstrap_ci"]

    title = case_title or Path(input_path).stem.replace("_", " ").title()
    lines = [
        f"# {title}",
        "",
        "## Why I looked at it this way",
        personal_context or "This report is less about proving that treatment wins and more about checking whether the result still looks credible once randomization, guardrails, heterogeneity, and interim peeks are all on the table.",
        "",
        "## Experiment Question",
        question or f"Does treatment move `{metric_column}` enough to matter without creating a worse failure somewhere else?",
        "",
        "## Setup",
        f"- Rows: {len(frame)}",
        f"- Variants: control={(frame['variant'] == 'control').sum()}, treatment={(frame['variant'] == 'treatment').sum()}",
        f"- Primary metric: `{metric_column}` ({metric_type})" if metric_type != "ratio" else f"- Primary metric: `{numerator_column}` / `{denominator_column}` (ratio)",
        f"- CUPED: {analysis['cuped_note']}",
        "",
        "## Sanity Checks",
        f"- SRM p-value: {srm.p_value:.6f} (chi2={srm.chi_square:.3f})",
        f"- Missing rate on primary metric inputs: {miss['missing_rate']:.4%}",
    ]

    if not balance_table.empty:
        lines.extend(["", "### Covariate Balance", "| Column | Mean Control | Mean Treatment | SMD |", "|---|---:|---:|---:|"])
        for row in balance_table.itertuples(index=False):
            lines.append(
                f"| {row.column} | {row.mean_control:.4f} | {row.mean_treatment:.4f} | {row.standardized_diff:.4f} |"
            )

    lines.extend(
        [
            "",
            "## Primary Metric",
            f"- Control mean: {result.control_mean:.6f}",
            f"- Treatment mean: {result.treatment_mean:.6f}",
            f"- Absolute lift: {result.absolute_lift:.6f}",
            f"- Relative lift: {result.relative_lift:.2%}",
            f"- p-value (fixed horizon): {result.p_value:.6f}",
            f"- Wald CI: [{result.ci_low:.6f}, {result.ci_high:.6f}]",
            f"- Bootstrap CI: [{bootstrap_low:.6f}, {bootstrap_high:.6f}]",
            f"- Standard error: {result.standard_error:.6f}",
            f"- Current MDE at n={min((frame['variant'] == 'control').sum(), (frame['variant'] == 'treatment').sum())} per variant: {analysis['current_mde']:.6f}" if np.isfinite(analysis["current_mde"]) else "- Current MDE: not shown for this metric type",
            f"- Approximate n/variant for observed effect: {analysis['recommended_n']}" if analysis["recommended_n"] else "- Approximate n/variant for observed effect: not shown for this metric type",
        ]
    )

    if np.isfinite(analysis["posterior_prob"]):
        lines.extend(
            [
                f"- Bayesian P(treatment > control): {analysis['posterior_prob']:.4f}",
                f"- Bayesian expected loss of shipping treatment: {analysis['expected_loss']:.6f}",
            ]
        )

    lines.extend(
        [
            "",
            "## Sequential Lens",
            f"- Fixed-horizon alpha: {alpha:.4f}",
            f"- Bonferroni alpha across {sequential_looks} looks: {analysis['bonferroni_alpha']:.4f}",
            f"- Final O'Brien-Fleming alpha: {analysis['obrien_fleming_alphas'][-1]:.4f}",
            "",
            "| Look | Rows | Info Fraction | Lift | p-value | Bonf Alpha | OBF Alpha | Sig (Bonf) | Sig (OBF) |",
            "|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in interim_table.itertuples(index=False):
        lines.append(
            f"| {row.look} | {row.rows} | {row.information_fraction:.2f} | {row.absolute_lift:.6f} | {row.p_value:.6f} | "
            f"{row.bonferroni_alpha:.6f} | {row.obrien_fleming_alpha:.6f} | {row.significant_bonferroni} | {row.significant_obrien_fleming} |"
        )

    if not guardrail_table.empty:
        lines.extend(["", "## Guardrails", "| Metric | Control Mean | Treatment Mean | Lift | p-value | Direction | Harmful? |", "|---|---:|---:|---:|---:|---|---|"])
        for row in guardrail_table.itertuples(index=False):
            lines.append(
                f"| {row.metric} | {row.control_mean:.6f} | {row.treatment_mean:.6f} | {row.absolute_lift:.6f} | {row.p_value:.6f} | {row.direction} | {row.harmful_shift} |"
            )

    if not segment_table.empty:
        lines.extend(["", "## Heterogeneity", "| Segment | Rows | Control Mean | Treatment Mean | Lift | Relative Lift | p-value |", "|---|---:|---:|---:|---:|---:|---:|"])
        for row in segment_table.itertuples(index=False):
            lines.append(
                f"| {row.segment} | {row.rows} | {row.control_mean:.6f} | {row.treatment_mean:.6f} | {row.absolute_lift:.6f} | {row.relative_lift:.2%} | {row.p_value:.6f} |"
            )

    lines.extend(
        [
            "",
            "## Decision",
            f"- {analysis['decision']}",
            f"- Reason: {analysis['decision_rationale']}",
            "",
            "## What Changed My Mind",
            "- A positive average effect matters less once guardrails and segment-level behavior start pulling in different directions.",
            "- The sequential view is useful because it shows whether confidence comes from the final sample or from cherry-picking an early moment.",
            "- The report feels more trustworthy when the uncertainty sections are allowed to stay messy instead of being trimmed away.",
            "",
            "## Where This Could Still Fail",
            "- Novelty effects, seasonality, and implementation drift can all survive a statistically clean report.",
            "- Segment-level differences are descriptive here; they are useful for follow-up design, not automatic personalization policy.",
        ]
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return analysis


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate markdown experiment report from CSV/Parquet data.")
    parser.add_argument("--input", required=True, help="Input CSV or Parquet file")
    parser.add_argument("--output", required=True, help="Output markdown report path")
    parser.add_argument("--metric-column", default="outcome")
    parser.add_argument("--metric-type", choices=["binary", "continuous", "ratio"], default="binary")
    parser.add_argument("--covariate-column", default="pre_metric")
    parser.add_argument("--numerator-column")
    parser.add_argument("--denominator-column")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--expected-treatment-ratio", type=float, default=0.5)
    parser.add_argument("--sequential-looks", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    covariate = args.covariate_column if args.covariate_column and args.covariate_column.lower() != "none" else None
    generate_report(
        input_path=args.input,
        output_path=args.output,
        metric_column=args.metric_column,
        metric_type=args.metric_type,
        covariate_column=covariate,
        numerator_column=args.numerator_column,
        denominator_column=args.denominator_column,
        alpha=args.alpha,
        expected_treatment_ratio=args.expected_treatment_ratio,
        sequential_looks=args.sequential_looks,
    )


if __name__ == "__main__":
    main()
