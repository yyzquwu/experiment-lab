# experiment-lab

`experiment-lab` is a recruiter-friendly experimentation repository for product analytics roles.
It includes reusable A/B testing utilities, sanity checks, sequential-safe decisions, and reproducible case-study reports.

## What This Repo Shows

- Metric definitions and hypothesis tests for binary and continuous outcomes.
- Sample size / MDE calculators.
- CUPED-style variance reduction for continuous metrics.
- Sanity checks: SRM, missingness, covariate balance.
- Sequential-safe options:
  - Frequentist guardrail via Bonferroni-adjusted alpha.
  - Bayesian posterior probability that treatment beats control.
- Markdown report generator for CSV/Parquet experiment files.

## Data Contract

Input file requires at least:

- `user_id`
- `variant` (`control` or `treatment`)
- `timestamp`
- `outcome`

Optional:

- `pre_metric` for CUPED and balance checks.

## Quickstart

```bash
make setup
make test
make demo
```

Generated outputs:

- `reports/case_1_signup.md`
- `reports/case_2_checkout_value.md`
- `reports/case_3_sequential_peeking.md`

## CLI Usage

```bash
PYTHONPATH=src python -m exp.report \
  --input data/synthetic/signup_experiment.csv \
  --output reports/custom_report.md \
  --metric-column outcome \
  --metric-type binary
```

## Project Structure

- `src/exp/`: experimentation package.
- `scripts/generate_synthetic_data.py`: deterministic synthetic datasets.
- `scripts/run_demo.py`: builds end-to-end markdown reports.
- `tests/`: known-answer unit tests.

## Case-Study Narrative Template

Use each generated report to communicate:

1. Business question and success metric.
2. Experiment design and guardrails.
3. Sanity checks and diagnostics.
4. Effect estimate + uncertainty.
5. Decision and next iteration.
