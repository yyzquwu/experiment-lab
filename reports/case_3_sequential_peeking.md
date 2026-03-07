# Case 3: Sequential Peeking Experiment

## Why I looked at it this way
This case is here because the most misleading experimentation habit is not a fancy statistical bug. It is ordinary impatience. I wanted one example where the temptation to stop early is visible in the report itself.

## Experiment Question
If the team keeps checking the result early, does the treatment still look good once the sequential decision rule is made explicit?

## Setup
- Rows: 12000
- Variants: control=5959, treatment=6041
- Primary metric: `outcome` (binary)
- CUPED: Not applied

## Sanity Checks
- SRM p-value: 0.454126 (chi2=0.560)
- Missing rate on primary metric inputs: 0.0000%

### Covariate Balance
| Column | Mean Control | Mean Treatment | SMD |
|---|---:|---:|---:|
| device_score | -0.0035 | -0.0048 | -0.0013 |
| pre_metric | 0.0020 | 0.0132 | 0.0112 |

## Primary Metric
- Control mean: 0.091290
- Treatment mean: 0.104618
- Absolute lift: 0.013328
- Relative lift: 14.60%
- p-value (fixed horizon): 0.014078
- Wald CI: [0.002689, 0.023967]
- Bootstrap CI: [0.003019, 0.023880]
- Standard error: 0.005428
- Current MDE at n=5959 per variant: 0.014783
- Approximate n/variant for observed effect: 7809
- Bayesian P(treatment > control): 0.9924
- Bayesian expected loss of shipping treatment: 0.000017

## Sequential Lens
- Fixed-horizon alpha: 0.0500
- Bonferroni alpha across 8 looks: 0.0063
- Final O'Brien-Fleming alpha: 0.0500

| Look | Rows | Info Fraction | Lift | p-value | Bonf Alpha | OBF Alpha | Sig (Bonf) | Sig (OBF) |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 1500 | 0.12 | -0.014713 | 0.343861 | 0.006250 | 0.000000 | False | False |
| 2 | 3000 | 0.25 | 0.012615 | 0.256584 | 0.006250 | 0.000089 | False | False |
| 3 | 4500 | 0.38 | 0.014095 | 0.116609 | 0.006250 | 0.001371 | False | False |
| 4 | 6000 | 0.50 | 0.012927 | 0.095652 | 0.006250 | 0.005575 | False | False |
| 5 | 7500 | 0.62 | 0.013652 | 0.049058 | 0.006250 | 0.013168 | False | False |
| 6 | 9000 | 0.75 | 0.016937 | 0.007289 | 0.006250 | 0.023625 | False | True |
| 7 | 10500 | 0.88 | 0.013835 | 0.017408 | 0.006250 | 0.036145 | False | True |
| 8 | 12000 | 1.00 | 0.013328 | 0.014078 | 0.006250 | 0.050000 | False | True |

## Guardrails
| Metric | Control Mean | Treatment Mean | Lift | p-value | Direction | Harmful? |
|---|---:|---:|---:|---:|---|---|
| latency_alert | 0.020305 | 0.024334 | 0.004028 | 0.135401 | lower_is_better | False |

## Heterogeneity
| Segment | Rows | Control Mean | Treatment Mean | Lift | Relative Lift | p-value |
|---|---:|---:|---:|---:|---:|---:|
| mixed | 5777 | 0.091131 | 0.108136 | 0.017005 | 18.66% | 0.031017 |
| desktop_heavy | 3314 | 0.088431 | 0.103428 | 0.014996 | 16.96% | 0.142776 |
| mobile_heavy | 2909 | 0.094875 | 0.098976 | 0.004101 | 4.32% | 0.708588 |

## Decision
- Promising but wait for full sample
- Reason: The fixed-horizon result is positive, but it is not strong enough to justify peeking-driven launch confidence.

## What Changed My Mind
- A positive average effect matters less once guardrails and segment-level behavior start pulling in different directions.
- The sequential view is useful because it shows whether confidence comes from the final sample or from cherry-picking an early moment.
- The report feels more trustworthy when the uncertainty sections are allowed to stay messy instead of being trimmed away.

## Where This Could Still Fail
- Novelty effects, seasonality, and implementation drift can all survive a statistically clean report.
- Segment-level differences are descriptive here; they are useful for follow-up design, not automatic personalization policy.
