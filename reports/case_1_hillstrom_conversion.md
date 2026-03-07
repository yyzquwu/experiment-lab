# Case 1: Hillstrom Conversion Experiment

## Why I looked at it this way
I wanted at least one case in this repo to run on a real randomized benchmark instead of a fully constructed sandbox. Hillstrom is not a modern product experiment, but it is public, reproducible, and much better for showing what the workflow looks like on data I did not invent.

## Experiment Question
Does sending email at all increase conversion relative to the holdout group, and where does that effect look stronger or weaker across customer-history segments?

## Setup
- Rows: 64000
- Variants: control=21306, treatment=42694
- Primary metric: `outcome_conversion` (binary)
- CUPED: Not applied

## Sanity Checks
- SRM p-value: 0.818716 (chi2=0.053)
- Missing rate on primary metric inputs: 0.0000%

### Covariate Balance
| Column | Mean Control | Mean Treatment | SMD |
|---|---:|---:|---:|
| pre_metric | 240.8827 | 242.6860 | 0.0071 |

## Primary Metric
- Control mean: 0.005726
- Treatment mean: 0.010681
- Absolute lift: 0.004955
- Relative lift: 86.53%
- p-value (fixed horizon): 0.000000
- Wald CI: [0.003399, 0.006510]
- Bootstrap CI: [0.003593, 0.006337]
- Standard error: 0.000794
- Current MDE at n=21306 per variant: 0.002048
- Approximate n/variant for observed effect: 5203
- Bayesian P(treatment > control): 1.0000
- Bayesian expected loss of shipping treatment: 0.000000

## Sequential Lens
- Fixed-horizon alpha: 0.0500
- Bonferroni alpha across 1 looks: 0.0500
- Final O'Brien-Fleming alpha: 0.0500

| Look | Rows | Info Fraction | Lift | p-value | Bonf Alpha | OBF Alpha | Sig (Bonf) | Sig (OBF) |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 64000 | 1.00 | 0.004955 | 0.000000 | 0.050000 | 0.050000 | True | True |

## Heterogeneity
| Segment | Rows | Control Mean | Treatment Mean | Lift | Relative Lift | p-value |
|---|---:|---:|---:|---:|---:|---:|
| 6) $750 - $1,000 | 1859 | 0.004823 | 0.019402 | 0.014579 | 302.26% | 0.013172 |
| 7) $1,000 + | 1308 | 0.014423 | 0.024664 | 0.010241 | 71.00% | 0.233371 |
| 5) $500 - $750 | 4911 | 0.005448 | 0.014728 | 0.009281 | 170.35% | 0.004119 |
| 1) $0 - $100 | 22970 | 0.004204 | 0.008595 | 0.004391 | 104.45% | 0.000199 |
| 2) $100 - $200 | 14254 | 0.004136 | 0.008388 | 0.004253 | 102.83% | 0.003798 |
| 3) $200 - $350 | 12289 | 0.006924 | 0.010794 | 0.003871 | 55.90% | 0.037879 |
| 4) $350 - $500 | 6409 | 0.011299 | 0.014469 | 0.003170 | 28.05% | 0.299214 |

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
