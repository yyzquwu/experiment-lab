# Experiment Report: signup_experiment

## Setup
- Rows: 12000
- Variants: control=5975, treatment=6025
- Metric column: `outcome` (binary)
- CUPED: Not applied

## Sanity Checks
- SRM p-value: 0.648077 (chi2=0.208)
- Missing rate (`outcome`): 0.0000%

## Results
- Control mean: 0.138577
- Treatment mean: 0.157344
- Absolute lift: 0.018767
- Relative lift: 13.54%
- p-value (fixed horizon): 0.003795
- 95% CI for lift: [0.006060, 0.031474]
- Sequential threshold (Bonferroni, 5 looks): 0.010000
- Significant at sequential threshold: True
- Bayesian P(treatment > control): 0.9974
- Current MDE at n=5975 per variant: 0.0177
- Approx required n/variant for observed effect size: 5619

## Decision
- Ship treatment

## Notes
- Use this report with business guardrails (cost, risk, seasonality) before launch.
