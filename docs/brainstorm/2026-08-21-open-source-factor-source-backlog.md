Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.

# Open-source factor source backlog

Web research (5 parallel angles, 76 sources) to keep the factor zoo
([factor_zoo.py](../../backend/app/factor_zoo.py)) and other chapters fed.
Scope constraint, user-set: daily OHLCV only — no point-in-time
fundamentals, no intraday/tick data, since this project has neither and
only ever reaches paper trading, never live capital.

## Acted on this pass

- **Classic TA indicators** (RSI, MACD, Bollinger %B, Stochastic %K, CCI,
  Williams %R, ROC, ATR-normalized range, OBV flow, MFI) — hand-implemented
  in `factor_zoo.py` (`CLASSIC_INDICATORS`), not a new dependency. See
  [research-program.md](../research-program.md) Chapter 4 §6 for results.

## Queued, real, not yet built

- **Qlib Alpha158** (microsoft/qlib, 47.8k★, active) — 158 hand-engineered
  OHLCV+VWAP features, the standard ML-factor baseline in academic quant
  papers. Bigger, more modern than WQ101; natural next batch.
- **Academic price/volume-only cross-sectional anomalies**, real citations,
  none yet tested here:
  - Amihud illiquidity (2002) — `|return|/dollar volume`.
  - MAX effect / lottery demand (Bali-Cakici-Whitelaw 2011) — robust to
    size/B-M/momentum/liquidity controls; largely subsumes the
    idiosyncratic-volatility puzzle.
  - Low-volatility anomaly (Blitz-van Vliet 2007) / Betting-Against-Beta
    (Frazzini-Pedersen 2014) — contested explanation (leverage constraints
    vs. lottery preference), both well-replicated internationally.
  - Corwin-Schultz high-low spread estimator (2012) — daily H/L/C only,
    now the standard low-frequency liquidity proxy, better than Roll's.
  - Overnight-vs-intraday return decomposition (Lou-Polk-Skouras 2019) —
    close-to-open vs. open-to-close only. Directly adjacent to the closed
    [Overnight Gap Continuation v1](../research-results/overnight-gap-continuation-v1.md)
    result (`12/12` opposite-signed) — a *new*, independently-argued
    mechanism would be needed to reopen that line, not a citation alone.
  - Return seasonality / same-calendar-month effect
    (Keloharju-Linnainmaa-Nyberg 2016) — own-history calendar-lag returns;
    debated as possibly data-mined to its discovery sample.
- **GP/RL alpha-mining frameworks** (AlphaGen — KDD 2023, AlphaForge — AAAI
  2025, both OHLCV-only via Qlib) — search over the WQ101-style operator
  set to discover new expressions, rather than a fixed list. Real
  infrastructure lift (search/training loop); a later step, not a quick win.

## Explicitly excluded, with reason

- **Value/quality fundamentals** (P/E, P/B, ROE) — confirmed no free,
  ready-to-use point-in-time vendor exists (Sharadar/Calcbench/Compustat
  all paid). SEC EDGAR's raw XBRL (`companyfacts`/DERA bulk files) is
  genuinely free and carries real per-filing PIT timestamps, but needs
  real ETL (dedupe restatements to isolate first-as-filed values, join
  against a separately-sourced price/shares-outstanding series, coverage
  effectively starts ~2009) — buildable, not built, a real future option
  if this project ever wants value/quality factors.
- **Volatility risk premium** (Bollerslev-Tauchen-Zhou 2009) — needs
  options-implied vol and intraday realized variance; no daily-OHLCV-only
  substitute exists per the literature itself.
- **Realized skewness/kurtosis** (Amaya et al. 2015) — needs intraday
  returns; use expected idiosyncratic skewness (Boyer-Mitton-Vorkink 2010)
  instead, which is daily-return-based.
- **Turnover-based liquidity** (Datar-Naik-Radcliffe 1998) — needs shares
  outstanding, a security-master field not present in this project's
  `bars` table (price/volume only).

## Tooling note, not adopted

`alphalens-reloaded` (stefan-jansen fork) is a maintained factor-evaluation
tool (IC, quantile returns, turnover) — functionally close to
`factor_zoo.py`'s own `evaluate_factor`. Not adopted: the custom harness is
already built, tested, and carries this project's own disclosure
conventions (non-evidential framing, orthogonality screen); no reason to
add a dependency for equivalent functionality already in hand.
