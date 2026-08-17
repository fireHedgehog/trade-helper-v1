[Home](../../README.md) · [Docs index](../README.md) · [Protocol](../research-protocol.md) · [Roadmap](../roadmap.md) · [Evidence](../../output/research/cta-trend-wf-v1.json)

# CTA Trend walk-forward v1: rejected

- Decision date: 2026-08-18
- Status: development hypothesis rejected for insufficient validated evidence
- Claim level: exploratory historical research only
- Evidence fingerprint: `40a79707811b6d13f92fa88a87a9e5251a72d0d5ffa58a2709e027f7bbc0bafd`

## Locked experiment

- 12 preregistered long-lived ETFs
- 54 CTA parameter candidates
- 14 expanding folds: 756 training, 252 validation, 252 test bars
- 10 bps commission per side, 2 bps quoted spread, 5 bps adverse slippage
- one-sided 20-bar circular block bootstrap with 5,000 resamples
- Holm family-wise correction across all 54 candidates at alpha 0.05
- rule: if no validation candidate survives, hold cash in the test fold

## Result

No candidate survived the validation significance gate in any of the 14 folds.
The minimum raw p-value by fold ranged from approximately 0.251 to 0.985; after
Holm correction, the minimum adjusted p-value was 1.0 in every fold.

The locked fallback therefore selected cash for all 14 test periods:

| Gate | Required | Observed | Decision |
| --- | ---: | ---: | --- |
| Median test excess return | positive | 0% (cash) | fail |
| Positive-excess test folds | at least 60% | 0/14 | fail |
| Median test Calmar | positive | not estimable | insufficient |
| Pooled drawdown | no worse than −25% | 0% (cash) | pass but uninformative |
| Closed test trades | at least 30 | 0 | insufficient |

This is not evidence that cash is a good strategy. It means the selection
protocol found no CTA configuration with enough validation evidence to authorize
out-of-sample exposure. The version fails its preregistered gates and is rejected.

## Interpretation

- The earlier attractive in-sample CTA statistics did not survive the validation
  requirement after costs and correction for 54 simultaneous candidates.
- No “best of the failures” was promoted, and thresholds were not changed.
- Parameter-stability and market-regime performance are not estimable because no
  configuration was selected for a test fold.
- The contaminated 2024–2026 candidate tail was not evaluated by this run.
- Any revised hypothesis must receive a new experiment ID and count as another
  attempt. Reusing this result to choose a friendlier grid would be exploratory,
  not confirmation.
