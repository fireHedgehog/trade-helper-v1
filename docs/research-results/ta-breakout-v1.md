# TA Breakout v1 — rejected-resistance breakout vs. raw new-high placebo

Decision: **not material or not consistent**. Completed with abundant event
counts (`1,477` qualifying events across 12 assets, far more than RSI's
`508`), but a real design weakness in this specific implementation is worth
stating plainly rather than filing this alongside the other two results
without qualification.

Specification SHA-256:
`40929c9de93633d15284ded96b6dde84998932044ef502ef75954dbb375bda6a`.
Data SHA-256: `a45bce859cdeee705a06cdea9c03f1bf0f31cff501d5f66c2e544d8f13fb64ab`.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Minimum event count (`≥15`) | `12/12` assets; `49`–`190` events each, `1,477` total | Pass |
| Materiality + significance, after Holm | `0/12` assets | **Fail** |
| Breadth (`≥8/12` required) | `0/12` | **Fail** |
| Placebo comparison | `7/12` assets | Weak signal — see design note below |
| Actual costs or execution accessed | `false` | Pass (no-trade experiment) |

Not one asset reached raw significance before correction — the smallest raw
p-value was `0.099` (`DBC` and `IEF`, tied). Only `2/12` assets (`DBC`,
`XLK`) cleared the raw `+0.5%` materiality threshold in magnitude at all.

## Design weakness, stated plainly

The event definition required at least `2` prior near-miss touches
(`rejections`) of the rolling resistance within the trailing `60` sessions.
In practice this filtered almost nothing: event and placebo counts were
within `5`–`15` occurrences of each other on every asset (e.g. `SPY`: `190`
events vs. `195` placebo occurrences; `DBC`: `87` vs. `94`). Near-miss touches
of a rolling high are common enough in ordinary price action that requiring
`≥2` of them barely distinguishes "confirmed multi-touch resistance" from
"any recent new-high breakout" at this tolerance (`1%`) and window (`60`
sessions). The `7/12` placebo-beating count should be read with this in
mind — it reflects two nearly-identical populations, not a clean
rejection-versus-no-rejection comparison the way SMA Cross v1's placebo
comparison was clean. This is an implementation limitation of this specific
locked construction, not evidence about a better-separated version of the
same idea.

## Reading this result

Two things are true at once and should not be blurred: (1) even setting the
weak event/placebo separation aside, the underlying forward-return effect
was not statistically distinguishable from noise anywhere — `0/12` raw
significant with `1,477` events is not a power problem the way RSI's `508`
events were; there was ample data and still nothing. (2) The specific
"multi-touch rejection adds something beyond a raw breakout" claim was never
well-tested here, because the two groups were not well separated by
construction. A tighter rejection definition (stricter tolerance, longer
lookback, more required touches) might separate the groups better, but that
is a new, independently justified protocol — not a fix to apply to this one
after seeing these counts, per this project's standing rule against
retrospective threshold adjustment.

Per this protocol's own decision vocabulary, only `material_and_consistent`,
`not_material_or_not_consistent`, or `invalid` may be output here.

## Reproducibility and blinding

- Per-asset artifact:
  [`output/research/ta-breakout-v1/40929c9d.../per-asset-results.json`](../../output/research/ta-breakout-v1/40929c9de93633d15284ded96b6dde84998932044ef502ef75954dbb375bda6a/per-asset-results.json).
- Decision artifact:
  [`decision.json`](../../output/research/ta-breakout-v1/40929c9de93633d15284ded96b6dde84998932044ef502ef75954dbb375bda6a/decision.json).
- No cost, execution, position, or portfolio-level field is present in any
  artifact.
- Data fingerprinted fresh at execution time; not guaranteed to reproduce
  bit-for-bit on a different machine's fetch.

[Protocol](../research-protocols/ta-breakout-v1.md) ·
[Selection record (Cycle 2)](../research-candidates/2026-08-19-cycle-2.md) ·
[Machine specification](../../research/experiments/ta-breakout-v1.json)
