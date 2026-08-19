# Calendar Day-of-Week v1 — Monday daily-return differential vs. block-resampled null

Decision: **not material or not consistent**. Seventh straight closure of
this kind this session. Unlike Calendar Turn-of-Month v1's mixed-sign
result, the direction was notably consistent with the literature's claim
(`9`/`12` assets negative), and one asset (`DBC`) crossed the conventional
raw `p < 0.05` threshold — but none survived correction, and none cleared
materiality and significance simultaneously.

Specification SHA-256:
`8283d00b5a10a7778fd5826a6931226013c3435b4f5f14fbe07c40a868d7ff19`.
Data SHA-256: `a45bce859cdeee705a06cdea9c03f1bf0f31cff501d5f66c2e544d8f13fb64ab`.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Minimum event count (`≥200`/asset) | `969`–`1,588` Mondays per asset | Pass, comfortably — no power limitation |
| Materiality (`≤-0.05%`) **and** significance (Holm `p ≤ 0.05`) | `0/12` assets cleared both simultaneously | **Fail** |
| Breadth (`≥8/12`) | `0/12` qualifying | **Fail** |
| Concentration (`≥3/6` clusters) | Moot — no qualifying assets | Not reached |
| Actual costs, execution, or sleeve accessed | `false` | Pass (no-trade study) |

`9` of `12` assets showed a negative differential (`DBC`, `EEM`, `EFA`,
`GLD`, `IEF`, `IWM`, `TLT`, `XLE`, `XLF`), `3` positive (`QQQ`, `SPY`,
`XLK`) — a materially more consistent direction than Turn-of-Month v1's
near-even `7`/`12` split, and the sign matches French (1980)'s original
underperformance claim. `5` assets (`DBC`, `EEM`, `EFA`, `XLE`, `XLF`)
independently cleared the `-0.05%` materiality floor. `DBC` reached raw
`p = 0.048` on a `-0.071%` daily differential (`969` Mondays) — the only
raw-significant result at the conventional `0.05` threshold this session in
either calendar-effect experiment — but its Holm-adjusted `p = 0.578` across
the `12`-asset family is nowhere close to significant. `EFA` (raw
`p = 0.055`) and `IEF` (raw `p = 0.072`) were the next closest.

## Reading this result

Like Turn-of-Month v1, this candidate had no power problem — `969`–`1,588`
Mondays per asset — and the volatility diagnostic (locked in advance,
non-gating) shows no simple confound explains the differential: it is not
uniformly a volatility-timing artifact. It does show a real, disclosed
secondary pattern worth reporting honestly since it wasn't hidden after the
fact: `8` of `12` assets have modestly *higher* realized volatility on
Mondays than other days (e.g. `XLE` `2.05%` vs `1.75%`, `SPY` `1.28%` vs
`1.14%`), consistent with weekend information accumulation being priced in
at the Monday open — while the three bond/gold assets (`TLT`, `IEF`, `GLD`)
show flat or slightly *lower* Monday volatility. This is a genuine
cross-asset pattern, not gating this decision, and not itself tested as a
hypothesis here — it is disclosed as a diagnostic observation, not
interpreted further.

The direction-consistency here (`9`/`12` negative, matching the literature)
is a meaningfully different shape of null than Turn-of-Month v1's
near-even split, and `DBC`'s raw `p = 0.048` is a genuine, if weak, signal
in the historically expected direction. But "9 of 12 point the right way"
is not the same claim as "the effect is material and consistent," and this
protocol's own locked gates require both materiality and Holm-corrected
significance together, which is the honest bar for treating a pattern like
this as more than a directionally-suggestive coincidence across correlated
assets. Zero of twelve cleared both. This reads as a real, weak,
correlated-across-assets tilt that does not rise to a defensible claim at
this sample size and correction standard — not a confound, not a power
failure, and not a design flaw.

This tests one specific, locked design: Monday only (not the other four
weekdays, to avoid a new multiple-comparisons dimension), on daily log
returns, on these `12` ETFs, over each asset's full available history. It
says nothing about a different weekday, a five-way weekday scan, or a
pre-2002 sample. Per this protocol's own decision vocabulary, only
`material_and_consistent`, `not_material_or_not_consistent`, or `invalid`
may be output here.

## Reproducibility and blinding

- Per-asset artifact:
  [`output/research/calendar-day-of-week-v1/8283d00b.../per-asset-results.json`](../../output/research/calendar-day-of-week-v1/8283d00b5a10a7778fd5826a6931226013c3435b4f5f14fbe07c40a868d7ff19/per-asset-results.json).
- Decision artifact:
  [`decision.json`](../../output/research/calendar-day-of-week-v1/8283d00b5a10a7778fd5826a6931226013c3435b4f5f14fbe07c40a868d7ff19/decision.json).
- No cost, execution, position, or portfolio field is present in any
  artifact — this was a no-trade event study throughout.
- Data fingerprinted fresh at execution time; not guaranteed to reproduce
  bit-for-bit on a different machine's fetch (see [environment and data
  portability](../README.md)).

[Protocol](../research-protocols/calendar-day-of-week-v1.md) ·
[Selection record (Cycle 5, Candidate B)](../research-candidates/2026-08-20-cycle-5.md) ·
[Machine specification](../../research/experiments/calendar-day-of-week-v1.json)
