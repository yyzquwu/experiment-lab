# Experiment Decision Memo

This repo ended up being less about finding one neat experiment win and more about showing the parts of experimentation work that usually get flattened away: guardrails, peeking pressure, variance reduction, ratio metrics, and the uncomfortable fact that the average effect can look fine while a subgroup story looks worse.

## Case summary
| Case | Metric Type | Absolute Lift | Relative Lift | p-value | Harmful Guardrails | Decision |
|---|---|---:|---:|---:|---:|---|
| Case 1: Signup Flow Experiment | binary | 0.020471 | 16.28% | 0.000411 | 1 | Do not ship without guardrail mitigation |
| Case 2: Checkout Value Experiment | continuous | 2.149747 | 4.15% | 0.000000 | 1 | Do not ship without guardrail mitigation |
| Case 3: Sequential Peeking Experiment | binary | 0.013328 | 14.60% | 0.014078 | 0 | Promising but wait for full sample |
| Case 4: Search CTR Ratio-Metric Experiment | ratio | 0.005972 | 6.50% | 0.000002 | 1 | Do not ship without guardrail mitigation |

## What felt convincing
- The repo now covers binary, continuous, and ratio metrics instead of pretending one statistical pattern is enough.
- Sequential peeking is treated as a real decision problem rather than an afterthought.
- Guardrails are integrated into the decision language instead of being left as a footnote.

## What still feels fragile
- These cases are still synthetic, even though they are built to feel more like the tradeoffs I would expect in practice.
- Segment-level differences are useful for follow-up design, but they are not causal personalization claims by themselves.
