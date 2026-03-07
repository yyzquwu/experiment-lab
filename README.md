# experiment-lab

This repo started as a compact A/B testing toolkit and then turned into something I found more useful: a place to pressure-test the parts of experimentation work that are easy to wave away when a result looks clean.

What I wanted here was not just a reusable stats package. I wanted a workflow that keeps asking harder questions:
- does the result survive sanity checks,
- what changes once sequential peeking is made explicit,
- how much does variance reduction actually help,
- when does a ratio metric behave differently from a simpler mean,
- and what looks fine on average but starts to feel worse once guardrails or segments are broken out.

## What is in here

- Binary, continuous, and ratio-metric experiment summaries.
- Sample-size and MDE calculators for binary and continuous outcomes.
- CUPED adjustment for continuous metrics with pre-period signal.
- Sanity checks for SRM, missingness, assignment balance, and segment splits.
- Sequential decision helpers with Bonferroni and O'Brien-Fleming thresholds.
- Bayesian posterior probability and expected-loss framing for binary outcomes.
- A mix of real public and synthetic case studies with markdown reports, figures, and a summary memo.

## Data setup

This repo now mixes one real public benchmark with synthetic stress cases.

- Real public benchmark: `make demo` downloads and preprocesses the Hillstrom email-marketing experiment into `data/raw/hillstrom_experiment.csv`.
- Synthetic stress cases: sequential-peeking and ratio-metric examples are still generated locally because public datasets rarely expose those failure modes cleanly.

That mix feels more honest to me than forcing everything into one type of dataset. The public benchmark keeps the repo grounded, and the synthetic cases keep it useful for showcasing edge cases that are hard to find in public experimental data.

The full workflow is still one command:

```bash
make demo
```

That writes:
- processed public data to `data/raw/`
- synthetic stress-case CSVs to `data/synthetic/`
- reports and figures to `reports/`

## Input contract

Required columns:
- `user_id`
- `variant`
- `timestamp`

Primary metric inputs:
- binary / continuous case: `outcome`
- ratio case: `numerator` and `denominator` style columns such as `clicks` and `impressions`

Optional columns used by the richer workflow:
- `pre_metric`
- `segment`
- guardrail metrics such as `support_tickets`, `refund_flag`, `latency_alert`, `bounce_rate`

## Quickstart

```bash
make setup
make test
make demo
```

Generated artifacts:
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

## What I cared about while building this

1. A report should get more interesting once the uncertainty and failure modes are added back in, not less.
2. Guardrails should affect the decision language instead of being left as a footnote.
3. Sequential peeking deserves to be treated as a first-class product decision problem.
4. A public benchmark should be present when possible, but synthetic cases still have value when they are modeling specific experimentation traps.
5. The repo should feel personally authored rather than like a generic experimentation template.
