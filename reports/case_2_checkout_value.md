# Experiment Report: checkout_value_experiment

## Setup
- Rows: 9000
- Variants: control=4492, treatment=4508
- Metric column: `outcome` (continuous)
- CUPED: Applied with theta=0.9804; pre-metric SMD=-0.0221

## Sanity Checks
- SRM p-value: 0.866068 (chi2=0.028)
- Missing rate (`outcome`): 0.0000%

## Results
- Control mean: 50.386076
- Treatment mean: 52.571437
- Absolute lift: 2.185361
- Relative lift: 4.34%
- p-value (fixed horizon): 0.000000
- 95% CI for lift: [1.566396, 2.804327]
- Sequential threshold (Bonferroni, 5 looks): 0.010000
- Significant at sequential threshold: True

## Decision
- Ship treatment

## Notes
- Use this report with business guardrails (cost, risk, seasonality) before launch.
