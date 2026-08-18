# CTA trend walk-forward v1: development result

Status: rejected. Experiment fingerprint: `40a79707811b6d13f92fa88a87a9e5251a72d0d5ffa58a2709e027f7bbc0bafd`.

## Locked design

`12` ETFs, `54` candidates, `14` walk-forward folds, and `756/252/252` train/validation/test bars. Validation used a one-sided circular moving-block bootstrap (`20`-bar blocks, `5,000` resamples) with Holm family-wise correction at `α=0.05`. Costs were commission `10 bp/side`, quoted spread `2 bp`, and slippage `5 bp/fill`.

## Observation

No candidate survived multiplicity correction in any fold. Minimum raw validation p-values ranged approximately from `0.251` to `0.985`; the minimum Holm-adjusted p-value was `1.0` in every fold. Therefore all 14 test folds followed the preregistered cash fallback.

| Final gate | Observation | Decision |
|---|---:|---|
| Median OOS excess `> 0` | `0` | Fail |
| Positive excess in `≥60%` folds | `0/14` | Fail |
| Median Calmar `> 0` | Not estimable | Insufficient |
| Pooled drawdown `≥−25%` | `0` | Pass, uninformative |
| Closed OOS trades `≥30` | `0` | Insufficient |

## Decision

Reject CTA v1. Cash test folds are the correct consequence of failed validation, not evidence that cash or trend following is generally superior. The result applies only to the locked universe, candidate family, period, costs, and procedure.

The inspected 2024–2026 tail is contaminated and was not used as final confirmation. Any changed factors, parameters, universe, allocation, or selection method define a new preregistered experiment.
