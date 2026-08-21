# Factor zoo v1 — 27-formula screen

Status: screening scan, non-evidential — same framing as
[cross-sectional-equity-momentum-feasibility-v1](cross-sectional-equity-momentum-feasibility-v1.md).
Not itself a Chapter 4 candidate for any single factor; screening well
confers nothing by itself — a factor still needs its own stated mechanism
(ADR 0007 clause 1) before formal proposal into
[Chapter 4](../research-program.md).
Engine: [`factor_zoo.py`](../../backend/app/factor_zoo.py). Run:
[`run_factor_zoo_scan.py`](../../backend/app/run_factor_zoo_scan.py).

## Method

Two formula families, both OHLCV-only (no vwap/fundamentals/PIT/intraday):

- **17 of WorldQuant's "101 Formulaic Alphas"** (Kakushadze 2015, verified
  against [popbo/alphas](https://github.com/popbo/alphas/blob/main/alphas101.py)) —
  `alpha191` and the vwap-heavy WQ101 formulas excluded, needing fields
  this project's free Yahoo data doesn't have.
- **10 hand-implemented classic technical indicators** (RSI14, MACD
  histogram, Bollinger %B, Stochastic %K, CCI20, Williams %R, ROC12,
  ATR-normalized range, OBV flow, MFI14) — not a new dependency; source
  survey in
  [open-source-factor-source-backlog.md](../brainstorm/2026-08-21-open-source-factor-source-backlog.md).

Universe: `495`/`495` symbols from the same disclosed-survivorship-biased
S&P 500 ∪ Nasdaq-100 ∪ XL-sector-ETF universe already locked in
[cross-sectional-equity-momentum-feasibility-v1](cross-sectional-equity-momentum-feasibility-v1.md).
Window: `2018-12-07`–`2026-08-14` (`1,929` common sessions). Forward
return: raw 1-session close-to-close, no cost/slippage modeled. IC t-stats
are informative only — overlapping draws, no multiple-comparisons
correction across the `27` factors.

Full numbers:
[scan-report.json](../../output/research/factor-zoo-v1/scan-report.json)
(each row tagged `family: wq101` or `classic_indicator`). Charts:
[IC-IR ranking](../../output/research/factor-zoo-v1/ic-ir-ranking.png),
[top-6 equity curves](../../output/research/factor-zoo-v1/top-factor-equity-curves.png).

## Result

Top by IC-IR: `alpha034` (Sharpe `0.76`, CAGR `8.8%`, max drawdown
`-19.0%`), `alpha004` (`0.71`), `alpha028` (`0.66`), `alpha033` (`0.47`),
`alpha026`/`alpha009` (`0.42`/`0.40`). Two WQ101 formulas decisively
negative: `alpha001` (`-0.45`) and `alpha035` (`-0.30`, max drawdown
`-52%`) — both among the more cited WQ101 formulas, so a clean negative
here is itself informative, not noise.

Every classic indicator scored **negative** IC-IR under its conventional
"high reading = long" direction (RSI, Stochastic, Williams %R, CCI, MFI,
MACD histogram, ROC, OBV-flow all lose money long-the-high-reading at this
1-session horizon).

One exception: `atr_normalized` (ATR(14)/close, a pure volatility-level
factor) posted the best raw Sharpe of the entire `27`-factor zoo (`0.84`,
CAGR `20.0%`).

## Reading this result

**Disclosed risk, not yet resolved**: `alpha034`/`alpha033`/`alpha009`/
`alpha028` form one tightly-correlated cluster (`r=0.58`–`0.79`), and
`alpha004`/`alpha026` touch parts of it too (`r=0.52`–`0.55`). Every top
WQ101 performer is some shape of short-horizon (1–10 session) price
reversal — the classic setting for the bid-ask-bounce artifact (Jegadeesh
1990, Lehmann 1990), where raw daily closes alternating near the bid and
ask can manufacture an apparent reversal profit with no real edge once
realistic transaction costs are modeled, and this scan models zero cost.
By the same design-effect logic
[Calendar Day-of-Week's correlated pairs](calendar-dow-chapter4-eligibility.md)
established, this cluster's real breadth is closer to `2`–`3` independent
effects than `6` — until cost-adjusted, read the whole top cluster as one
shared, unconfirmed hypothesis, not six.

The classic indicators' uniform negative sign is the *same* hypothesis
restated from the other direction, not six new findings: a naive
contrarian reading (long the *lowest* RSI/Stochastic/MACD names) would
show the mirrored positive number, and the caution about zero-cost-modeled
1-day reversal applies to it equally. `atr_normalized` was specifically
checked for orthogonality against the whole reversal cluster because it
fell outside the default top-8 screen — confirmed genuinely independent
(`|r|≤0.34` against `alpha034`/`033`/`028`/`004`/`023`), though its
drawdown (`-39.4%`) is much worse than the cluster's (`-19%` to `-31%`),
consistent with a real volatility-premium-style factor rather than a
low-vol/defensive one — the economically expected shape, not a red flag
by itself, but a real regime-concentration question (ADR 0007 clause 5)
still to check before proposing it.

**Not yet done, named as the next concrete step**: propose the
least-redundant survivors — `alpha028`, `alpha004`, `alpha026`, and
`atr_normalized` — as individual Chapter 4 candidates, each with its own
stated mechanism, regime-concentration check, and a cost-sensitivity check
before any eligibility read is trusted. The reversal cluster
(`alpha034`/`033`/`009`/RSI/Stochastic/Williams-%R/CCI/MACD/ROC/OBV, all
one hypothesis) needs a transaction-cost-aware rerun before it is even
scan-worthy of further attention.

[Chapter 4 index](../research-program.md) ·
[Source backlog](../brainstorm/2026-08-21-open-source-factor-source-backlog.md)
