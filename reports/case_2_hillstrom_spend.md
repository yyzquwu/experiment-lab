# Case 2: Hillstrom Spend Experiment

## Why I looked at it this way
I kept a continuous case here because binary wins are not the whole job. Spend is noisier and easier to overread, so this is where CUPED and uncertainty intervals feel more necessary than decorative.

## Experiment Question
Does the same email treatment move spend per customer once the outcome is noisier and more skewed than the simple conversion indicator?

## Setup
- Rows: 64000
- Variants: control=21306, treatment=42694
- Primary metric: `outcome_spend` (continuous)
- CUPED: Applied with theta=0.0013

## Sanity Checks
- SRM p-value: 0.818716 (chi2=0.053)
- Missing rate on primary metric inputs: 0.0000%

### Covariate Balance
| Column | Mean Control | Mean Treatment | SMD |
|---|---:|---:|---:|
| pre_metric | 240.8827 | 242.6860 | 0.0071 |

## Primary Metric
- Control mean: 0.654324
- Treatment mean: 1.248820
- Absolute lift: 0.594496
- Relative lift: 90.86%
- p-value (fixed horizon): 0.000000
- Wald CI: [0.373924, 0.815068]
- Bootstrap CI: [0.363060, 0.808801]
- Standard error: 0.112539
- Current MDE at n=21306 per variant: 0.408144
- Approximate n/variant for observed effect: 10043

## Sequential Lens
- Fixed-horizon alpha: 0.0500
- Bonferroni alpha across 1 looks: 0.0500
- Final O'Brien-Fleming alpha: 0.0500

| Look | Rows | Info Fraction | Lift | p-value | Bonf Alpha | OBF Alpha | Sig (Bonf) | Sig (OBF) |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 64000 | 1.00 | 0.596796 | 0.000000 | 0.050000 | 0.050000 | True | True |

## Heterogeneity
| Segment | Rows | Control Mean | Treatment Mean | Lift | Relative Lift | p-value |
|---|---:|---:|---:|---:|---:|---:|
| 7) $1,000 + | 1308 | 2.169808 | 4.060325 | 1.890517 | 87.13% | 0.275647 |
| 5) $500 - $750 | 4911 | 0.538856 | 1.735008 | 1.196152 | 221.98% | 0.001843 |
| 6) $750 - $1,000 | 1859 | 0.349534 | 1.458998 | 1.109464 | 317.41% | 0.010682 |
| 4) $350 - $500 | 6409 | 1.010268 | 1.726562 | 0.716294 | 70.90% | 0.077738 |
| 1) $0 - $100 | 22970 | 0.516893 | 1.098688 | 0.581795 | 112.56% | 0.001159 |
| 2) $100 - $200 | 14254 | 0.422895 | 1.003746 | 0.580851 | 137.35% | 0.001535 |
| 3) $200 - $350 | 12289 | 0.932881 | 1.036212 | 0.103331 | 11.08% | 0.717897 |

## Decision
- Ship treatment
- Reason: The primary metric is positive and clears a defensible significance threshold without obvious guardrail damage.

## What Changed My Mind
- A positive average effect matters less once guardrails and segment-level behavior start pulling in different directions.
- The sequential view is useful because it shows whether confidence comes from the final sample or from cherry-picking an early moment.
- The report feels more trustworthy when the uncertainty sections are allowed to stay messy instead of being trimmed away.

## Where This Could Still Fail
- Novelty effects, seasonality, and implementation drift can all survive a statistically clean report.
- Segment-level differences are descriptive here; they are useful for follow-up design, not automatic personalization policy.
