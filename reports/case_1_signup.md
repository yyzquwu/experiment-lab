# Case 1: Signup Flow Experiment

## Why I looked at it this way
This is the kind of experiment I like because the headline metric is easy to celebrate too early. The useful work starts once the support burden and segment differences are allowed back into the conversation.

## Experiment Question
Does the new signup treatment increase completed signup rate without creating enough extra support burden to cancel the gain?

## Setup
- Rows: 14000
- Variants: control=6968, treatment=7032
- Primary metric: `outcome` (binary)
- CUPED: Not applied

## Sanity Checks
- SRM p-value: 0.588577 (chi2=0.293)
- Missing rate on primary metric inputs: 0.0000%

### Covariate Balance
| Column | Mean Control | Mean Treatment | SMD |
|---|---:|---:|---:|
| baseline_sessions | 3.5774 | 3.6241 | 0.0248 |
| pre_metric | -0.0079 | 0.0072 | 0.0153 |

## Primary Metric
- Control mean: 0.125718
- Treatment mean: 0.146189
- Absolute lift: 0.020471
- Relative lift: 16.28%
- p-value (fixed horizon): 0.000411
- Wald CI: [0.009115, 0.031828]
- Bootstrap CI: [0.008415, 0.031874]
- Standard error: 0.005794
- Current MDE at n=6968 per variant: 0.015736
- Approximate n/variant for observed effect: 4401
- Bayesian P(treatment > control): 0.9994
- Bayesian expected loss of shipping treatment: 0.000001

## Sequential Lens
- Fixed-horizon alpha: 0.0500
- Bonferroni alpha across 5 looks: 0.0100
- Final O'Brien-Fleming alpha: 0.0500

| Look | Rows | Info Fraction | Lift | p-value | Bonf Alpha | OBF Alpha | Sig (Bonf) | Sig (OBF) |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 2800 | 0.20 | 0.016855 | 0.199216 | 0.010000 | 0.000012 | False | False |
| 2 | 5600 | 0.40 | 0.022457 | 0.016359 | 0.010000 | 0.001942 | False | False |
| 3 | 8400 | 0.60 | 0.024861 | 0.000951 | 0.010000 | 0.011396 | True | True |
| 4 | 11200 | 0.80 | 0.023742 | 0.000263 | 0.010000 | 0.028430 | True | True |
| 5 | 14000 | 1.00 | 0.020471 | 0.000411 | 0.010000 | 0.050000 | True | True |

## Guardrails
| Metric | Control Mean | Treatment Mean | Lift | p-value | Direction | Harmful? |
|---|---:|---:|---:|---:|---|---|
| support_tickets | 0.019518 | 0.025882 | 0.006364 | 0.011507 | lower_is_better | True |

## Heterogeneity
| Segment | Rows | Control Mean | Treatment Mean | Lift | Relative Lift | p-value |
|---|---:|---:|---:|---:|---:|---:|
| high_intent | 2988 | 0.113043 | 0.172137 | 0.059093 | 52.27% | 0.000004 |
| casual | 4323 | 0.112292 | 0.130153 | 0.017861 | 15.91% | 0.072008 |
| exploring | 6689 | 0.140224 | 0.144970 | 0.004747 | 3.39% | 0.578849 |

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
