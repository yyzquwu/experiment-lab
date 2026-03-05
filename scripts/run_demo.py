from __future__ import annotations

from pathlib import Path

from exp.report import generate_report


def main() -> None:
    Path("reports").mkdir(parents=True, exist_ok=True)

    generate_report(
        input_path="data/synthetic/signup_experiment.csv",
        output_path="reports/case_1_signup.md",
        metric_column="outcome",
        metric_type="binary",
        covariate_column="pre_metric",
        alpha=0.05,
        sequential_looks=5,
    )

    generate_report(
        input_path="data/synthetic/checkout_value_experiment.csv",
        output_path="reports/case_2_checkout_value.md",
        metric_column="outcome",
        metric_type="continuous",
        covariate_column="pre_metric",
        alpha=0.05,
        sequential_looks=5,
    )

    generate_report(
        input_path="data/synthetic/sequential_peeking_experiment.csv",
        output_path="reports/case_3_sequential_peeking.md",
        metric_column="outcome",
        metric_type="binary",
        covariate_column="pre_metric",
        alpha=0.05,
        sequential_looks=8,
    )


if __name__ == "__main__":
    main()
