# Case 2: Checkout Value Experiment

## Why I looked at it this way
I kept this case because it forces a more honest read of continuous-metric experiments. The lift looks strong, but the more useful question is whether the variance reduction and guardrail story still hold once they are written down explicitly.

## Experiment Question
Does the treatment increase checkout value enough to matter after variance reduction, and is any gain offset by higher refunds?

## Setup
- Rows: 9500
- Variants: control=4722, treatment=4778
- Primary metric: `outcome` (continuous)
- CUPED: Applied with theta=0.9638

## Sanity Checks
- SRM p-value: 0.565597 (chi2=0.330)
- Missing rate on primary metric inputs: 0.0000%

### Covariate Balance
| Column | Mean Control | Mean Treatment | SMD |
|---|---:|---:|---:|
| pre_metric | 52.0291 | 51.7172 | -0.0313 |
| prior_value | 47.9442 | 47.8133 | -0.0138 |

## Primary Metric
- Control mean: 51.755817
- Treatment mean: 53.905564
- Absolute lift: 2.149747
- Relative lift: 4.15%
- p-value (fixed horizon): 0.000000
- Wald CI: [1.546802, 2.752693]
- Bootstrap CI: [1.519459, 2.753345]
- Standard error: 0.307631
- Current MDE at n=4722 per variant: 1.028070
- Approximate n/variant for observed effect: 1080

## Sequential Lens
- Fixed-horizon alpha: 0.0500
- Bonferroni alpha across 5 looks: 0.0100
- Final O'Brien-Fleming alpha: 0.0500

| Look | Rows | Info Fraction | Lift | p-value | Bonf Alpha | OBF Alpha | Sig (Bonf) | Sig (OBF) |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 1900 | 0.20 | 3.109294 | 0.000199 | 0.010000 | 0.000012 | True | False |
| 2 | 3800 | 0.40 | 1.726990 | 0.002845 | 0.010000 | 0.001942 | True | False |
| 3 | 5700 | 0.60 | 1.868386 | 0.000077 | 0.010000 | 0.011396 | True | True |
| 4 | 7600 | 0.80 | 1.991681 | 0.000001 | 0.010000 | 0.028430 | True | True |
| 5 | 9500 | 1.00 | 1.849172 | 0.000000 | 0.010000 | 0.050000 | True | True |

## Guardrails
| Metric | Control Mean | Treatment Mean | Lift | p-value | Direction | Harmful? |
|---|---:|---:|---:|---:|---|---|
| refund_flag | 0.033037 | 0.041231 | 0.008194 | 0.034765 | lower_is_better | True |

## Heterogeneity
| Segment | Rows | Control Mean | Treatment Mean | Lift | Relative Lift | p-value |
|---|---:|---:|---:|---:|---:|---:|
| repeat_buyers | 1848 | 51.746132 | 54.702350 | 2.956218 | 5.71% | 0.000321 |
| mixed | 5152 | 51.970438 | 54.107910 | 2.137472 | 4.11% | 0.000020 |
| price_sensitive | 2500 | 51.901044 | 52.375703 | 0.474659 | 0.91% | 0.498644 |

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
