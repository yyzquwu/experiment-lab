# Case 4: Search CTR Ratio-Metric Experiment

## Why I looked at it this way
I wanted one ratio-metric case because so many real product metrics are not simple Bernoulli or pure revenue numbers. The harder part is usually deciding whether the ratio gain is worth the mess it creates elsewhere.

## Experiment Question
Does the treatment improve clicks per impression without pushing low-intent users into worse post-click behavior?

## Setup
- Rows: 11000
- Variants: control=5545, treatment=5455
- Primary metric: `clicks` / `impressions` (ratio)
- CUPED: Not applied

## Sanity Checks
- SRM p-value: 0.390828 (chi2=0.736)
- Missing rate on primary metric inputs: 0.0000%

### Covariate Balance
| Column | Mean Control | Mean Treatment | SMD |
|---|---:|---:|---:|
| baseline_sessions | 6.0456 | 5.9872 | -0.0258 |

## Primary Metric
- Control mean: 0.091870
- Treatment mean: 0.097843
- Absolute lift: 0.005972
- Relative lift: 6.50%
- p-value (fixed horizon): 0.000002
- Wald CI: [0.003492, 0.008452]
- Bootstrap CI: [0.002617, 0.007538]
- Standard error: 0.001265
- Current MDE: not shown for this metric type
- Approximate n/variant for observed effect: not shown for this metric type

## Sequential Lens
- Fixed-horizon alpha: 0.0500
- Bonferroni alpha across 5 looks: 0.0100
- Final O'Brien-Fleming alpha: 0.0500

| Look | Rows | Info Fraction | Lift | p-value | Bonf Alpha | OBF Alpha | Sig (Bonf) | Sig (OBF) |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 2200 | 0.20 | 0.006078 | 0.027758 | 0.010000 | 0.000012 | False | False |
| 2 | 4400 | 0.40 | 0.006696 | 0.000664 | 0.010000 | 0.001942 | True | True |
| 3 | 6600 | 0.60 | 0.006779 | 0.000026 | 0.010000 | 0.011396 | True | True |
| 4 | 8800 | 0.80 | 0.006643 | 0.000002 | 0.010000 | 0.028430 | True | True |
| 5 | 11000 | 1.00 | 0.005972 | 0.000002 | 0.010000 | 0.050000 | True | True |

## Guardrails
| Metric | Control Mean | Treatment Mean | Lift | p-value | Direction | Harmful? |
|---|---:|---:|---:|---:|---|---|
| bounce_rate | 0.110911 | 0.125940 | 0.015029 | 0.014703 | lower_is_better | True |

## Heterogeneity
| Segment | Rows | Control Mean | Treatment Mean | Lift | Relative Lift | p-value |
|---|---:|---:|---:|---:|---:|---:|
| power_searchers | 4235 | 0.098487 | 0.109084 | 0.010597 | 10.76% | 0.000000 |
| typical | 5366 | 0.087966 | 0.092193 | 0.004227 | 4.80% | 0.022182 |
| light_searchers | 1399 | 0.082164 | 0.079517 | -0.002647 | -3.22% | 0.436279 |

## Decision
- Do not ship without guardrail mitigation
- Reason: The primary metric improved, but at least one guardrail moved in a harmful direction.

## What Changed My Mind
- A positive average effect matters less once guardrails and segment-level behavior start pulling in different directions.
- The sequential view is useful because it shows whether confidence comes from the final sample or from cherry-picking an early moment.
- The report feels more trustworthy when the uncertainty sections are allowed to stay messy instead of being trimmed away.

## Where This Could Still Fail
- Novelty effects, seasonality, and implementation drift can all survive a statistically clean report.
- Segment-level differences are descriptive here; they are useful for follow-up design, not automatic personalization policy.
