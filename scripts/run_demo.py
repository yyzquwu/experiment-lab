from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from exp.report import generate_report


REPORTS_DIR = Path("reports")
FIGURES_DIR = REPORTS_DIR / "figures"


CASE_SPECS = [
    {
        "name": "signup",
        "input_path": "data/synthetic/signup_experiment.csv",
        "output_path": "reports/case_1_signup.md",
        "metric_column": "outcome",
        "metric_type": "binary",
        "covariate_column": "pre_metric",
        "guardrail_columns": ["support_tickets"],
        "guardrail_directions": {"support_tickets": "lower_is_better"},
        "segment_column": "segment",
        "case_title": "Case 1: Signup Flow Experiment",
        "question": "Does the new signup treatment increase completed signup rate without creating enough extra support burden to cancel the gain?",
        "personal_context": "This is the kind of experiment I like because the headline metric is easy to celebrate too early. The useful work starts once the support burden and segment differences are allowed back into the conversation.",
    },
    {
        "name": "checkout_value",
        "input_path": "data/synthetic/checkout_value_experiment.csv",
        "output_path": "reports/case_2_checkout_value.md",
        "metric_column": "outcome",
        "metric_type": "continuous",
        "covariate_column": "pre_metric",
        "guardrail_columns": ["refund_flag"],
        "guardrail_directions": {"refund_flag": "lower_is_better"},
        "segment_column": "segment",
        "case_title": "Case 2: Checkout Value Experiment",
        "question": "Does the treatment increase checkout value enough to matter after variance reduction, and is any gain offset by higher refunds?",
        "personal_context": "I kept this case because it forces a more honest read of continuous-metric experiments. The lift looks strong, but the more useful question is whether the variance reduction and guardrail story still hold once they are written down explicitly.",
    },
    {
        "name": "sequential",
        "input_path": "data/synthetic/sequential_peeking_experiment.csv",
        "output_path": "reports/case_3_sequential_peeking.md",
        "metric_column": "outcome",
        "metric_type": "binary",
        "covariate_column": "pre_metric",
        "guardrail_columns": ["latency_alert"],
        "guardrail_directions": {"latency_alert": "lower_is_better"},
        "segment_column": "segment",
        "sequential_looks": 8,
        "case_title": "Case 3: Sequential Peeking Experiment",
        "question": "If the team keeps checking the result early, does the treatment still look good once the sequential decision rule is made explicit?",
        "personal_context": "This case is here because the most misleading experimentation habit is not a fancy statistical bug. It is ordinary impatience. I wanted one example where the temptation to stop early is visible in the report itself.",
    },
    {
        "name": "search_ratio",
        "input_path": "data/synthetic/search_ctr_experiment.csv",
        "output_path": "reports/case_4_search_ctr.md",
        "metric_column": "clicks",
        "metric_type": "ratio",
        "numerator_column": "clicks",
        "denominator_column": "impressions",
        "guardrail_columns": ["bounce_rate"],
        "guardrail_directions": {"bounce_rate": "lower_is_better"},
        "segment_column": "segment",
        "case_title": "Case 4: Search CTR Ratio-Metric Experiment",
        "question": "Does the treatment improve clicks per impression without pushing low-intent users into worse post-click behavior?",
        "personal_context": "I wanted one ratio-metric case because so many real product metrics are not simple Bernoulli or pure revenue numbers. The harder part is usually deciding whether the ratio gain is worth the mess it creates elsewhere.",
    },
]


def _plot_segment_lift(segment_table: pd.DataFrame, output_path: Path, title: str) -> None:
    if segment_table.empty:
        return
    ordered = segment_table.sort_values("absolute_lift", ascending=True)
    plt.figure(figsize=(8.5, 5.0))
    plt.barh(ordered["segment"], ordered["absolute_lift"], color="#bf6b4a")
    plt.axvline(0.0, linestyle="--", color="#555555", linewidth=1.0)
    plt.xlabel("Absolute lift")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def _plot_interim_path(interim_table: pd.DataFrame, output_path: Path, title: str) -> None:
    plt.figure(figsize=(8.5, 5.0))
    plt.plot(interim_table["look"], interim_table["p_value"], marker="o", label="Observed p-value")
    plt.plot(interim_table["look"], interim_table["bonferroni_alpha"], linestyle="--", label="Bonferroni alpha")
    plt.plot(interim_table["look"], interim_table["obrien_fleming_alpha"], linestyle=":", label="O'Brien-Fleming alpha")
    plt.xlabel("Interim look")
    plt.ylabel("Threshold / p-value")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def _plot_guardrail_summary(guardrail_table: pd.DataFrame, output_path: Path, title: str) -> None:
    if guardrail_table.empty:
        return
    plt.figure(figsize=(8.5, 5.0))
    plt.bar(guardrail_table["metric"], guardrail_table["absolute_lift"], color="#5c7a95")
    plt.axhline(0.0, linestyle="--", color="#555555", linewidth=1.0)
    plt.ylabel("Treatment - control")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def _plot_effect_over_time(frame: pd.DataFrame, metric_column: str, output_path: Path, title: str) -> None:
    ordered = frame.sort_values("timestamp").copy()
    ordered["control_cum"] = (ordered["variant"].eq("control") * ordered[metric_column]).cumsum()
    ordered["control_n"] = ordered["variant"].eq("control").cumsum().clip(lower=1)
    ordered["treatment_cum"] = (ordered["variant"].eq("treatment") * ordered[metric_column]).cumsum()
    ordered["treatment_n"] = ordered["variant"].eq("treatment").cumsum().clip(lower=1)
    ordered["cum_lift"] = ordered["treatment_cum"] / ordered["treatment_n"] - ordered["control_cum"] / ordered["control_n"]

    plt.figure(figsize=(8.5, 5.0))
    plt.plot(np.linspace(0.0, 1.0, num=len(ordered)), ordered["cum_lift"], color="#af4b4b")
    plt.axhline(0.0, linestyle="--", color="#555555", linewidth=1.0)
    plt.xlabel("Share of experiment runtime")
    plt.ylabel("Cumulative lift")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    Path("case_studies").mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, object]] = []
    for spec in CASE_SPECS:
        analysis = generate_report(
            input_path=spec["input_path"],
            output_path=spec["output_path"],
            metric_column=spec.get("metric_column", "outcome"),
            metric_type=spec["metric_type"],
            covariate_column=spec.get("covariate_column", "pre_metric"),
            sequential_looks=spec.get("sequential_looks", 5),
            numerator_column=spec.get("numerator_column"),
            denominator_column=spec.get("denominator_column"),
            guardrail_columns=spec.get("guardrail_columns"),
            segment_column=spec.get("segment_column", "segment"),
            case_title=spec["case_title"],
            question=spec["question"],
            personal_context=spec["personal_context"],
            guardrail_directions=spec.get("guardrail_directions"),
        )

        result = analysis["result"]
        summary_rows.append(
            {
                "case": spec["case_title"],
                "metric_type": spec["metric_type"],
                "absolute_lift": result.absolute_lift,
                "relative_lift": result.relative_lift,
                "p_value": result.p_value,
                "decision": analysis["decision"],
                "harmful_guardrails": int(analysis["guardrail_table"]["harmful_shift"].sum()) if not analysis["guardrail_table"].empty else 0,
            }
        )

        if not analysis["segment_table"].empty:
            _plot_segment_lift(
                analysis["segment_table"],
                FIGURES_DIR / f"{spec['name']}_segment_lift.png",
                f"{spec['case_title']}: segment-level lift",
            )
        if not analysis["guardrail_table"].empty:
            _plot_guardrail_summary(
                analysis["guardrail_table"],
                FIGURES_DIR / f"{spec['name']}_guardrails.png",
                f"{spec['case_title']}: guardrail shifts",
            )
        _plot_interim_path(
            analysis["interim_table"],
            FIGURES_DIR / f"{spec['name']}_interim_path.png",
            f"{spec['case_title']}: interim p-values vs thresholds",
        )
        if spec["metric_type"] != "ratio":
            _plot_effect_over_time(
                analysis["frame"],
                spec["metric_column"],
                FIGURES_DIR / f"{spec['name']}_cumulative_lift.png",
                f"{spec['case_title']}: cumulative lift over runtime",
            )

    summary = pd.DataFrame(summary_rows)

    memo_lines = [
        "# Experiment Decision Memo",
        "",
        "This repo ended up being less about finding one neat experiment win and more about showing the parts of experimentation work that usually get flattened away: guardrails, peeking pressure, variance reduction, ratio metrics, and the uncomfortable fact that the average effect can look fine while a subgroup story looks worse.",
        "",
        "## Case summary",
        "| Case | Metric Type | Absolute Lift | Relative Lift | p-value | Harmful Guardrails | Decision |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in summary.itertuples(index=False):
        memo_lines.append(
            f"| {row.case} | {row.metric_type} | {row.absolute_lift:.6f} | {row.relative_lift:.2%} | {row.p_value:.6f} | {row.harmful_guardrails} | {row.decision} |"
        )
    memo_lines.extend(
        [
            "",
            "## What felt convincing",
            "- The repo now covers binary, continuous, and ratio metrics instead of pretending one statistical pattern is enough.",
            "- Sequential peeking is treated as a real decision problem rather than an afterthought.",
            "- Guardrails are integrated into the decision language instead of being left as a footnote.",
            "",
            "## What still feels fragile",
            "- These cases are still synthetic, even though they are built to feel more like the tradeoffs I would expect in practice.",
            "- Segment-level differences are useful for follow-up design, but they are not causal personalization claims by themselves.",
        ]
    )
    (REPORTS_DIR / "decision_memo.md").write_text("\n".join(memo_lines) + "\n", encoding="utf-8")

    appendix_lines = [
        "# Methods Appendix",
        "",
        "## Primary ideas in this repo",
        "- Fixed-horizon inference for binary, continuous, and ratio metrics.",
        "- Bootstrap confidence intervals as a second lens on mean-difference uncertainty.",
        "- CUPED for continuous outcomes with pre-period signal.",
        "- SRM, missingness, covariate balance, and segment assignment checks.",
        "- Bonferroni and O'Brien-Fleming style sequential thresholds.",
        "- Bayesian posterior probability and expected loss for binary outcomes.",
        "",
        "## Why the case studies differ",
        "- Signup case: primary-metric win with a support-burden guardrail.",
        "- Checkout-value case: CUPED-friendly continuous metric with refund risk.",
        "- Sequential case: novelty effect and peeking pressure.",
        "- Ratio-metric case: clicks per impression with bounce-rate guardrail.",
    ]
    (REPORTS_DIR / "methods_appendix.md").write_text("\n".join(appendix_lines) + "\n", encoding="utf-8")

    case_study_lines = [
        "# Case Studies",
        "",
        "- [Case 1: Signup Flow Experiment](case_1_signup.md)",
        "- [Case 2: Checkout Value Experiment](case_2_checkout_value.md)",
        "- [Case 3: Sequential Peeking Experiment](case_3_sequential_peeking.md)",
        "- [Case 4: Search CTR Ratio-Metric Experiment](case_4_search_ctr.md)",
        "- [Decision Memo](decision_memo.md)",
        "- [Methods Appendix](methods_appendix.md)",
    ]
    Path("case_studies/README.md").write_text("\n".join(case_study_lines) + "\n", encoding="utf-8")

    print("Wrote case reports, decision memo, methods appendix, and figures/")


if __name__ == "__main__":
    main()
