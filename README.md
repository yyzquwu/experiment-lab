# experiment-lab

This repo started as a small A/B testing toolkit and turned into a place for testing the parts of experimentation work that are easy to gloss over when the numbers look good.

- Binary, continuous, and ratio-metric experiment summaries.
- Sample-size and MDE calculators for binary and continuous outcomes.
- CUPED adjustment for continuous metrics with pre-period signal.
- Sanity checks for SRM, missingness, assignment balance, and segment splits.
- Sequential decision helpers with Bonferroni and O'Brien-Fleming thresholds.
- Bayesian posterior probability and expected-loss framing for binary outcomes.
- Real public and synthetic case studies with markdown reports, figures, and a summary memo.

## Data setup

- Real public benchmark: `make demo` downloads and preprocesses the Hillstrom email-marketing experiment into `data/raw/hillstrom_experiment.csv`.
- Synthetic stress cases: sequential-peeking and ratio-metric examples are still generated locally because public datasets rarely expose those failure modes cleanly.

Run the full workflow with:

```bash
make demo
```

It writes processed data to `data/raw/`, synthetic stress-case CSVs to `data/synthetic/`, and reports and figures to `reports/`.

## Quickstart

```bash
make setup
make test
make demo
```

## Input Contract

Required columns:
- `user_id`
- `variant`
- `timestamp`

Primary metric inputs:
- binary / continuous case: `outcome`
- ratio case: `numerator` and `denominator` style columns such as `clicks` and `impressions`

Optional columns:
- `pre_metric`
- `segment`
- guardrails like `support_tickets`, `refund_flag`, `latency_alert`, and `bounce_rate`

Generated artifacts include:
- `reports/case_1_hillstrom_conversion.md`
- `reports/case_2_hillstrom_spend.md`
- `reports/case_3_sequential_peeking.md`
- `reports/case_4_search_ctr.md`
- `reports/decision_memo.md`
- `reports/methods_appendix.md`
- `reports/figures/`
- `notebooks/experiment_walkthrough.ipynb`

## Repo structure

- `src/exp/metrics.py`: fixed-horizon estimators and bootstrap uncertainty helpers.
- `src/exp/power.py`: sample-size and MDE calculations.
- `src/exp/sequential.py`: sequential thresholds and Bayesian decision helpers.
- `src/exp/sanity.py`: SRM, missingness, balance, and segment-assignment checks.
- `src/exp/data.py`: public-data preprocessing helpers.
- `src/exp/report.py`: reusable analysis layer plus markdown report generation.
- `scripts/download_data.py`: public benchmark download + preprocessing.
- `scripts/generate_synthetic_data.py`: deterministic case-study datasets.
- `scripts/run_demo.py`: end-to-end report and figure generation.
