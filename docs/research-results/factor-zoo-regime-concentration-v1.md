# Factor zoo regime concentration v1 — atr_normalized

Status: screening scan, non-evidential — same standing as
[factor-zoo-v1](factor-zoo-v1.md). Not a Chapter 4 eligibility claim by
itself (ADR 0007 clause 2's cross-validated point estimate + uncertainty
band is a separate, not-yet-done step); this closes clause 5 specifically
— the one check factor-zoo-v1 and factor-zoo-cost-sensitivity-v1 both left
open for `atr_normalized`, the one survivor of both.
Engine: [`factor_zoo.py`](../../backend/app/factor_zoo.py)'s
`regime_concentration_by_year`. Run:
[`run_factor_zoo_regime_concentration.py`](../../backend/app/run_factor_zoo_regime_concentration.py).

## Method

[ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md) clause 5
requires a positive point estimate be disclosed "alongside what fraction
of it traces to any single year or episode (the same calculation CTA v2's
own closed result already discloses)" —
[cta-v2-pooled-trend-overlay.md](cta-v2-pooled-trend-overlay.md)'s own
regime diagnostic: exclude a year, see whether the sample mean changes
sign. That check spot-tested 3 named crisis years (2008/2020/2022)
against a 20-year pooled sample. `atr_normalized`'s sample is ~8 years
(factor-zoo-v1's universe window) — short enough to sweep every year
rather than a chosen few, so this does exactly that: the same
leave-one-year-out calculation, applied exhaustively instead of
selectively.

Same universe and window as factor-zoo-v1 (live rescan against current
`data/market.db`, not a locked/fingerprinted replay — same disclosed
caveat as [factor-zoo-cost-sensitivity-v1](factor-zoo-cost-sensitivity-v1.md)).

Full numbers:
[regime-concentration-report.json](../../output/research/factor-zoo-regime-concentration-v1/regime-concentration-report.json).

## Result

Full-sample mean daily spread return: `+8.41bps` (Sharpe `0.82`, matching
factor-zoo-v1's standout). Leave-one-year-out, every year in the sample:

| Year | Days | That year's own mean | Mean excluding this year | Flips sign? |
|---|---:|---:|---:|---|
| 2018 (partial, 2 days) | 2 | `+141.14bps` | `+8.28bps` | No |
| 2019 | 252 | `+7.01bps` | `+8.63bps` | No |
| 2020 | 253 | `+11.78bps` | `+7.90bps` | No |
| 2021 | 252 | `+7.07bps` | `+8.62bps` | No |
| 2022 | 251 | `-4.17bps` | `+10.31bps` | No |
| 2023 | 250 | `+16.17bps` | `+7.25bps` | No |
| 2024 | 252 | `+3.29bps` | `+9.19bps` | No |
| 2025 | 249 | `+13.67bps` | `+7.63bps` | No |
| 2026 (through Aug) | 155 | `+13.43bps` | `+7.97bps` | No |

**No year's exclusion flips the sign.** Excluding any single year, the
mean stays positive in a narrow `+7.25bps` to `+10.31bps` band — a
`36%`-of-full-mean swing at most (`(10.31-7.25)/8.41`), nowhere near a
sign flip. 2018's own huge `+141bps` figure is a 2-day partial-window artifact
(factor-zoo-v1's universe window starts `2018-12-07`), not a real
year-long effect — noted, not treated as informative on its own. 2022 is
the only year with a *negative* own-year mean (`-4.17bps`, plausibly the
rate-hike/bond-selloff regime), but even removing it outright leaves the
picture essentially unchanged in the other direction.

## Reading this result

**This is the clean case CTA v2 was not.** CTA v2's positive point
estimate flipped negative when 2008 alone was excluded — a single crisis
episode was carrying the whole result. `atr_normalized` shows the
opposite pattern: the effect is spread across 8 different years,
including 3 years usually treated as distinct regimes (2020 COVID crash,
2022 rate-hike selloff, 2018's partial window) without depending on any
one of them. This is exactly what clause 5 asks a candidate to disclose
either way — here, the honest disclosure is a clean pass, not a caveat.

**Consequence for Chapter 4 candidacy**: clause 5 is closed for
`atr_normalized`. Clause 2 (a cross-validated point estimate with an
explicit uncertainty band) and clause 1 (a stated economic mechanism —
ATR/close is a volatility-*level* factor, not yet written up as a
mechanism claim) remain the two open steps before a formal Chapter 4
proposal — this result removes one blocker, not all of them.

[Chapter 4 index](../research-program.md) ·
[Factor zoo v1](factor-zoo-v1.md) ·
[Cost sensitivity v1](factor-zoo-cost-sensitivity-v1.md)
