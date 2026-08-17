# ADR 0003: Research statistics and benchmark contract

- Status: accepted for the research prototype
- Date: 2026-08-17

## Context

A backtest is one realized historical path, not a probability forecast. A high
win rate can coexist with poor expectancy, and a strategy return can look good
until it is compared with passive market exposure or realistic trading costs.
Twenty-day forward outcomes also overlap unless sampling explicitly prevents it,
while signals across different symbols can be driven by the same market move.

## Decision

The product separates two different analyses:

- **trade performance** replays the complete strategy with the canonical
  completed-close signal and next-available-open fill model; and
- **historical post-signal statistics** measure the close-to-close return 20
  trading bars after selected entry signals. They exclude execution costs and
  are descriptive statistics, not calibrated probabilities or strategy P&L.

Trade performance reports the exact start/end window, capital, exposure, net
return, CAGR, annualized volatility, downside deviation, Sortino, Calmar,
drawdown magnitude and duration, expectancy, turnover, and closed-trade count.
It includes configurable commission, quoted spread, adverse fill slippage, and
idle-cash yield. Default assumptions are 10 basis points commission per side,
2 basis points quoted spread, 5 basis points adverse slippage per fill, and zero
cash yield. Overnight gaps are naturally included because orders fill at the
following available open.

The comparisons are adjusted-price buy-and-hold and a constant-exposure blend:
the asset's daily adjusted-price return receives the strategy's average exposure
weight and cash receives the remainder. This is a simple exposure control, not a
tradable replication of the strategy's entry/exit timing.

Post-signal observations are at least 20 trading bars apart within each symbol.
Uncertainty is estimated with a deterministic 1,000-resample calendar-month
cluster bootstrap, keeping contemporaneous symbol outcomes together. With fewer
than three month clusters, Wilson hit-rate and normal-mean intervals are shown as
a fallback. Fewer than 30 observations always receives a low-sample warning.

## Consequences and limitations

- Every displayed result states its window, sample or trade count, benchmark,
  execution-cost assumptions, and whether it is a point estimate.
- Cluster bootstrapping reduces the false independence assumption for signals
  occurring in the same month. Dependence across adjacent months can remain,
  especially because the outcome horizon is 20 trading days.
- Neither confidence intervals nor more metrics repair selection bias,
  survivorship bias, parameter overfitting, or multiple testing.
- The adjusted-price buy-and-hold comparison is total-return-like; the strategy
  uses the same adjusted OHLC series but does not currently model taxes, borrow,
  partial fills, market impact, or volume constraints.
- Stage 4 must use a preregistered, out-of-sample walk-forward protocol. Until
  that gate passes, no result in this application is evidence of a durable edge.
