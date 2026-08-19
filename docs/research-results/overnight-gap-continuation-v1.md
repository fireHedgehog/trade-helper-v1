# Overnight Gap Continuation v1 — gap-conditioned signed forward return vs. joint-paired-resampled null

Decision: **not material or not consistent**. The most decisive negative of
the session: `12`/`12` assets show a *negative* signed forward return — the
opposite sign from the continuation hypothesis — not merely a small or
mixed one. The strengthened placebo gate (added during pre-lock review)
correctly rejected several assets that would have trivially passed the
old, bare point-estimate comparison used by every prior candidate.

Specification SHA-256:
`8cf8881c155fc7006b76055c443a3e830e214ca9d2f65d2d05cc350a68df17e5`.
Data SHA-256: `a45bce859cdeee705a06cdea9c03f1bf0f31cff501d5f66c2e544d8f13fb64ab`.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Minimum event count (`≥30`) | `189`–`371` `Gap` occurrences per asset | Pass, comfortably |
| Materiality (`≥+0.5%`) **and** significance (Holm `p ≤ 0.05`) | `0/12` — every asset's signed mean was *negative* | **Fail** |
| Placebo (`Gap` beats `Placebo` point estimate **and** `p_gap_vs_placebo ≤ 0.05`) | `0/12` | **Fail** |
| Breadth (`≥8/12`) | `0/12` qualifying | **Fail** |
| Concentration (`≥3/6` clusters) | Moot — no qualifying assets | Not reached |
| Actual costs, execution, or sleeve accessed | `false` | Pass (no-trade study) |

`12`/`12` assets show a negative `observed_gap_mean_signed_forward_return`
(range `-0.93%` to `+0.002%`, with only `TLT` and `XLE` landing at an
essentially-zero `+0.002%`) — not one asset points in the hypothesized
(continuation) direction with any real magnitude. Raw `p_event` ranges
`0.20`–`0.96`, nowhere near the `0.05` favourable-direction threshold; most
assets sit on the *unfavourable* side of their own null distribution
(observed statistic worse than the median resample), consistent with a
genuinely negative, not merely null, signed effect. The point-estimate
placebo comparison (`Gap` mean `>` `Placebo` mean) was true for `3` of `12`
assets (`DBC`, `IEF`, `TLT`) — but the paired-null significance test added
during this protocol's pre-lock review, `p_gap_vs_placebo`, was `0.34`–`0.98`
for all three, correctly rejecting what the old bare-inequality convention
used by every prior candidate this session would have accepted as
"beats placebo" on those three assets.

## Reading this result

This candidate's own event/placebo direction was wrong, not just weak — a
materially different shape of null than anything else this session. Six
of seven prior closures found a small, mixed, or near-miss signal in the
*hypothesized* direction that failed to clear significance or correction.
This one found a consistent signal in the *opposite* direction across the
whole universe. That is itself informative, though not evidence this
protocol is authorised to claim: this locked design tested **continuation**
specifically (materiality requires `SFR ≥ +0.5%`, one-sided favourable-
positive), so a uniformly negative result is reported honestly as
`not_material_or_not_consistent` against that claim — not as a confirmed
reversal effect, which would need its own separately preregistered
protocol with its own gates, materiality direction, and multiplicity
accounting.

The disclosed, non-gating up/down diagnostic (added during pre-lock review)
shows where this negative tilt is coming from: on most assets, **down-gap**
days show a *positive* raw mean forward return (`SPY +0.49%`, `EFA +1.08%`,
`DBC +0.78%`, `IWM +0.53%`, `QQQ +0.49%`, `XLF +0.45%`, `XLK +0.40%`) — a
bounce-back after a large overnight decline, not continued weakness — while
**up-gap** days are more mixed, several also negative (`EFA -0.73%`,
`XLF -0.34%`, `DBC -0.09%`, `EEM -0.13%`, `XLK -0.06%`). Pooling both
directions with the signed-continuation statistic this protocol locked
correctly reports this as "not continuation" rather than manufacturing a
false positive from one direction alone — but the pattern itself (large
gaps, especially down-gaps, tending to partially reverse rather than
extend) is a real, disclosed observation, not this protocol's finding, and
not something this locked design can claim as evidence of a reversal edge.

The pre-lock review's own contribution is validated directly by this
result: under the bare point-estimate placebo convention every prior
candidate used (Wave Pull, TA Breakout), `DBC`, `IEF`, and `TLT` would have
trivially "beaten placebo," inflating the breadth count on a comparison
with no real statistical backing. The strengthened `p_gap_vs_placebo` test
correctly identified that none of these three point-estimate wins were
distinguishable from chance (`p = 0.34`–`0.48`) — precisely the failure
mode ("could satisfy the gate by sampling noise between two correlated
statistics") the review predicted before any data was touched, now
observed in the actual result it was designed to guard against.

This tests one specific, locked design: continuation signed by the
overnight gap's own direction, `10`-session horizon, `90`th-percentile
self-calibrating threshold, on these `12` ETFs. It says nothing about a
reversal-framed claim, a different horizon, or a different threshold — any
of those would be a new, independently justified protocol. Per this
protocol's own decision vocabulary, only `material_and_consistent`,
`not_material_or_not_consistent`, or `invalid` may be output here.

## Reproducibility and blinding

- Per-asset artifact:
  [`output/research/overnight-gap-continuation-v1/8cf8881c.../per-asset-results.json`](../../output/research/overnight-gap-continuation-v1/8cf8881c155fc7006b76055c443a3e830e214ca9d2f65d2d05cc350a68df17e5/per-asset-results.json).
- Decision artifact:
  [`decision.json`](../../output/research/overnight-gap-continuation-v1/8cf8881c155fc7006b76055c443a3e830e214ca9d2f65d2d05cc350a68df17e5/decision.json).
- No cost, execution, position, or portfolio field is present in any
  artifact — this was a no-trade event study throughout.
- Data fingerprinted fresh at execution time; not guaranteed to reproduce
  bit-for-bit on a different machine's fetch (see [environment and data
  portability](../README.md)).
- This protocol underwent independent adversarial pre-lock code review
  (three lenses, three agents, six findings, all fixed) before the
  specification hash above was computed and before any data was touched —
  see the [protocol](../research-protocols/overnight-gap-continuation-v1.md)'s
  Pre-lock verification record.

[Protocol](../research-protocols/overnight-gap-continuation-v1.md) ·
[Selection record (Cycle 5, Candidate C)](../research-candidates/2026-08-20-cycle-5.md) ·
[Machine specification](../../research/experiments/overnight-gap-continuation-v1.json)
