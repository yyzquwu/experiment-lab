# Experiment Decision Memo

This repo ended up being less about finding one neat experiment win and more about showing the parts of experimentation work that usually get flattened away: guardrails, peeking pressure, variance reduction, ratio metrics, and the uncomfortable fact that the average effect can look fine while a subgroup story looks worse.

## Case summary
| Case | Data Source | Metric Type | Absolute Lift | Relative Lift | p-value | Harmful Guardrails | Decision |
|---|---|---|---:|---:|---:|---:|---|
| Case 1: Hillstrom Conversion Experiment | real public benchmark | binary | 0.004955 | 86.53% | 0.000000 | 0 | Ship treatment |
| Case 2: Hillstrom Spend Experiment | real public benchmark | continuous | 0.594496 | 90.86% | 0.000000 | 0 | Ship treatment |
| Case 3: Sequential Peeking Experiment | synthetic stress case | binary | 0.013328 | 14.60% | 0.014078 | 0 | Promising but wait for full sample |
| Case 4: Search CTR Ratio-Metric Experiment | synthetic stress case | ratio | 0.005972 | 6.50% | 0.000002 | 1 | Do not ship without guardrail mitigation |

## What felt convincing
- The repo now mixes a real public benchmark with synthetic stress cases instead of making every claim on invented data.
- It covers binary, continuous, and ratio metrics instead of pretending one statistical pattern is enough.
- Sequential peeking is treated as a real decision problem rather than an afterthought.
- Guardrails are integrated into the decision language instead of being left as a footnote.

## What still feels fragile
- Hillstrom is real but still narrower than a modern product experimentation stack.
- The synthetic cases are useful because they surface failure modes cleanly, but they are still synthetic.
- Segment-level differences are useful for follow-up design, but they are not causal personalization claims by themselves.
