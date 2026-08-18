# ADR 0005: Product objective and portfolio benchmark

Status: accepted; Passive ETF-12 v1 implemented in `0.25.0`.

## Objective

The product is a local research decision assistant. Its business question is whether a strategy improves a feasible long-only portfolio relative to passive ownership after costs and risk, sufficiently to justify further research.

## Primary benchmark: Passive ETF-12 v1

- Locked 12-ETF universe defined by the active protocol.
- Initial equity `$100,000`; strict common sessions.
- Equal target weight `1/12` per asset.
- Establish at the first common open; rebalance annually at the first common-session open.
- Whole shares, adjusted prices, the same trading costs, residual cash, `T+1` sale proceeds, and zero cash yield as the strategy portfolio.
- No leverage, shorts, borrowing, or discretionary substitutions.

Changing universe, weighting, rebalance timing, costs, calendar, or cash treatment creates a new benchmark version.

## Secondary references

SPY buy-and-hold and cash are diagnostic references, not substitutes for the primary portfolio benchmark.

## Evaluation dimensions

- Return: total return and CAGR.
- Risk: maximum drawdown, recovery, and Calmar ratio.
- Implementation: exposure, turnover, costs, rejected orders, and cash drag.
- Evidence: trade count, uncertainty, stability across folds/assets/regimes, stress sensitivity, and multiplicity control.

## Consequences

A strategy is not useful merely because it is profitable or has lower drawdown. It must improve the locked objective with evidence strong enough for the declared research stage.
