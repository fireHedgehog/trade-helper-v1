# RSI(14) oversold-crossing short-horizon reversal v1

Decision: **not material or not consistent**. This is a completed,
event-count-adequate significance test — every asset cleared the `15`-event
minimum — but the epistemic character is different from Cycle 2's SMA Cross
v1 result and worth stating precisely rather than filing under the same label.

Specification SHA-256:
`4e99621b45867b5ed7431d77f8bf642f6988ac48d3972ff9143548099cd5e0f8`.
Data SHA-256: `a45bce859cdeee705a06cdea9c03f1bf0f31cff501d5f66c2e544d8f13fb64ab`.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Minimum event count (`≥15`) | `12/12` assets eligible; `36`–`56` events each, `508` total | Pass |
| Materiality + significance, after Holm | `0/12` assets | **Fail** |
| Breadth (`≥8/12` required) | `0/12` | **Fail** |
| Placebo comparison | `6/12` assets | Mixed — not the deciding factor here |
| Actual costs or execution accessed | `false` | Pass (no-trade experiment) |

**Not one of the 12 assets reached conventional significance even before any
multiplicity correction.** The smallest raw p-value was `XLF`'s `0.138` — Holm
correction pushed every asset's adjusted p-value to `1.0`, but the correction
did not change the substantive outcome: nothing was close to significant on
its own, so this is not a case of an apparent effect being explained away by
testing many assets at once.

Six of twelve assets (`EFA`, `IWM`, `QQQ`, `SPY`, `XLF`, `XLK`) did clear the
raw `+0.5%` materiality threshold in magnitude — `XLF` showed the largest
observed bounce at `+1.98%` mean forward return over `47` events — but none of
these magnitudes were distinguishable from what block-resampled null paths of
the same length produce. With only `36`–`56` qualifying events per asset, the
test's precision at this sample size cannot rule out chance producing an
effect this large.

The placebo comparison, which was the decisive finding for SMA Cross v1, is
genuinely mixed here: the RSI event beat the decline-magnitude placebo on
exactly half the assets (`6/12`) and lost on the other half. This experiment
therefore does **not** support the reading "the effect is just generic
decline-magnitude reversal" the way SMA Cross v1's placebo comparison did —
it simply does not have the statistical power, at this event count, to
distinguish RSI-specific reversal from the placebo, from a real effect, or
from noise.

## Reading this result

This is closer to a genuine *power* limitation than a *confound*
explanation. The correct reading is: with `36`–`56` independent-ish events per
asset over each instrument's full available history, this design cannot
currently tell a real short-horizon reversal effect of plausible economic size
from chance. That is different from SMA Cross v1, where the data was
adequate and the effect looked explained by something else. Neither reading
licenses treating this as a stronger or weaker result than it is — per this
protocol's own decision vocabulary
([docs/research-protocols/rsi-oversold-reversal-v1.md](../research-protocols/rsi-oversold-reversal-v1.md)),
only `material_and_consistent`, `not_material_or_not_consistent`, or `invalid`
may be output here.

A future attempt that wanted to address the power limitation specifically —
more events via a longer horizon, a shorter cooldown, a pooled cross-asset
estimator, or a coarser oversold threshold — would be a new, independently
justified protocol, not an amendment to this one; this result does not itself
recommend any of those changes.

## Reproducibility and blinding

- Per-asset artifact:
  [`output/research/rsi-oversold-reversal-v1/4e99621b.../per-asset-results.json`](../../output/research/rsi-oversold-reversal-v1/4e99621b45867b5ed7431d77f8bf642f6988ac48d3972ff9143548099cd5e0f8/per-asset-results.json).
- Decision artifact:
  [`decision.json`](../../output/research/rsi-oversold-reversal-v1/4e99621b45867b5ed7431d77f8bf642f6988ac48d3972ff9143548099cd5e0f8/decision.json).
- No cost, execution, position, or portfolio-level field is present in any
  artifact — this was a no-trade characterization run throughout.
- Data fingerprinted fresh at execution time from this machine's own stored
  bars; a different machine's fetch of the same symbols is not guaranteed to
  reproduce this exact hash under `auto_adjust=True` rebasing.

[Protocol](../research-protocols/rsi-oversold-reversal-v1.md) ·
[Selection record](../research-candidates/2026-08-19-cycle-3.md) ·
[Machine specification](../../research/experiments/rsi-oversold-reversal-v1.json)
