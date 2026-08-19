# Calendar Turn-of-Month v1 — daily-return differential vs. block-resampled null

Decision: **not material or not consistent**. Sixth straight closure of this
kind this session, but the first outside the price-derived technical-pattern
family — this tested a calendar-timing mechanism instead, and it also came
back null. One asset (`EEM`) reached the strongest raw single-asset
significance of the whole session, but did not survive family-wise
correction.

Specification SHA-256:
`e961ffd26eb65b77b51ef397a603507aead215a4c9748a3073d4cc2e4bd01e92`.
Data SHA-256: `a45bce859cdeee705a06cdea9c03f1bf0f31cff501d5f66c2e544d8f13fb64ab`.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Minimum event count (`≥200`/asset) | `987`–`1,612` turn-of-month days per asset | Pass, comfortably — no power limitation |
| Materiality (`≥+0.05%`) **and** significance (Holm `p ≤ 0.05`) | `0/12` assets cleared both simultaneously | **Fail** |
| Breadth (`≥8/12`) | `0/12` qualifying | **Fail** |
| Concentration (`≥3/6` clusters) | Moot — no qualifying assets | Not reached |
| Actual costs, execution, or sleeve accessed | `false` | Pass (no-trade study) |

`7` of `12` assets showed a positive differential (`EEM`, `EFA`, `GLD`,
`QQQ`, `SPY`, `XLE`, `XLF`, `XLK`), `4` negative (`DBC`, `IEF`, `IWM`,
`TLT`) — a weak majority, not a consistent pattern. `EEM` reached raw
`p = 0.013` on a `+0.119%` daily differential (`1,123` qualifying days), the
strongest single-asset raw significance of any candidate this session
(stronger than Wave Pull's `TLT` near-miss at raw `p = 0.032`) — but its
Holm-adjusted `p = 0.156` across the `12`-asset family, well above `0.05`.
Even had `EEM` alone cleared correction, the `8`-of-`12` breadth gate would
still fail on a single qualifying asset, so this was not a close call at the
decision level, only at the single-asset level.

## Reading this result

This is the first candidate this session with essentially unlimited
statistical power — turn-of-month days are ~`19`% of trading days, giving
`987`–`1,612` qualifying observations per asset versus RSI's `36`–`56` or
Wave Pull's `15`–`140`. That rules out the power-limitation story that
explained RSI's null and contributed to Wave Pull's near-miss: with this
much data, a real effect of the locked materiality size would very likely
have been detected. The volatility diagnostic (locked in advance,
non-gating) also rules out SMA Cross v1's confound story — event-day and
non-event-day realized volatility are nearly identical for every asset
(e.g. `SPY` `1.14%` vs `1.18%`, `DBC` `1.31%` vs `1.20%`), so turn-of-month
days are not systematically higher- or lower-volatility days in this sample.
What's left is closer to Wave Pull's read than SMA Cross's or RSI's: a
well-powered, cleanly-specified test with one real near-miss (`EEM`, raw
`p = 0.013`) that does not survive correcting for testing `12` assets at
once. This reads as the effect not existing at a material, consistent size
in this sample — not as a design or power failure.

This result is also the expected honest outcome stated in the protocol
before execution: turn-of-month effects were robustly documented in
mid-20th-century US equity data (Lakonishok and Smidt 1988), but this
project's sample sits almost entirely in the modern, highly liquid,
heavily-arbitraged ETF era, where later literature has questioned whether
such calendar patterns persist. A null here does not contradict the
historical literature; it is consistent with the specific claim that
whatever pattern existed has been arbitraged away in this era and this
instrument class — a live empirical question this protocol was designed to
test, not one it assumed the answer to.

This tests one specific, locked design: the Lakonishok and Smidt
(1988) `4`-trading-day window (last day of month plus first `3` of the
next), on daily log returns, on these `12` ETFs, over each asset's full
available history. It says nothing about a different window width, a
different calendar effect (day-of-week remains a distinct, unexecuted
Cycle 5 candidate), or a pre-2002 sample. Per this protocol's own decision
vocabulary, only `material_and_consistent`, `not_material_or_not_consistent`,
or `invalid` may be output here.

## Reproducibility and blinding

- Per-asset artifact:
  [`output/research/calendar-turn-of-month-v1/e961ffd2.../per-asset-results.json`](../../output/research/calendar-turn-of-month-v1/e961ffd26eb65b77b51ef397a603507aead215a4c9748a3073d4cc2e4bd01e92/per-asset-results.json).
- Decision artifact:
  [`decision.json`](../../output/research/calendar-turn-of-month-v1/e961ffd26eb65b77b51ef397a603507aead215a4c9748a3073d4cc2e4bd01e92/decision.json).
- No cost, execution, position, or portfolio field is present in any
  artifact — this was a no-trade event study throughout.
- Data fingerprinted fresh at execution time; not guaranteed to reproduce
  bit-for-bit on a different machine's fetch (see [environment and data
  portability](../README.md)).

[Protocol](../research-protocols/calendar-turn-of-month-v1.md) ·
[Selection record (Cycle 5)](../research-candidates/2026-08-20-cycle-5.md) ·
[Machine specification](../../research/experiments/calendar-turn-of-month-v1.json)
