# Experiment Report: sequential_peeking_experiment

## Setup
- Rows: 10000
- Variants: control=4974, treatment=5026
- Metric column: `outcome` (binary)
- CUPED: Not applied

## Sanity Checks
- SRM p-value: 0.603064 (chi2=0.270)
- Missing rate (`outcome`): 0.0000%

## Results
- Control mean: 0.094089
- Treatment mean: 0.105651
- Absolute lift: 0.011561
- Relative lift: 12.29%
- p-value (fixed horizon): 0.053890
- 95% CI for lift: [-0.000193, 0.023316]
- Sequential threshold (Bonferroni, 8 looks): 0.006250
- Significant at sequential threshold: False
- Bayesian P(treatment > control): 0.9720
- Current MDE at n=4974 per variant: 0.0164
- Approx required n/variant for observed effect size: 10558

## Decision
- Ship treatment

## Notes
- Use this report with business guardrails (cost, risk, seasonality) before launch.
