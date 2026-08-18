[Home](../../README.md) · [Docs index](../README.md) · [Roadmap](../roadmap.md) · [Product](../product.md) · [Changelog](../../CHANGELOG.md)

# ADR 0005: Product objective and portfolio benchmark

- Status: accepted and implemented for local research
- Date: 2026-08-18

## Context

Working software is not evidence that a trading rule has value. The project also
cannot judge a multi-asset, cash-constrained strategy fairly against whichever
comparison makes its latest result look best. The product purpose and comparison
must therefore be fixed before another strategy hypothesis is proposed.

The locked portfolio contains 12 ETFs across US and international equities,
Treasuries, gold, and commodities. SPY alone is an important reference, but it
does not represent the complete opportunity set available to the strategy.

## Product decision

The first product is a **local research decision assistant**. Its job is to help
the user:

1. state one testable market hypothesis before inspecting its result;
2. replay it under explicit capital, timing, cost, and risk assumptions;
3. compare it with passive alternatives on the same dates and capital basis;
4. understand uncertainty, fragility, and data limitations; and
5. record an honest `reject`, `revise`, or `continue` decision.

The product is successful when it prevents a weak or unsupported strategy from
being mistaken for an edge. Producing frequent signals, finding a strategy that
wins a historical backtest, maximizing user activity, and encouraging trades
are not product objectives.

It remains educational research. It does not recommend securities, size a real
account, connect to a broker, or authorize paper or live trading.

## Primary portfolio benchmark

The primary comparator will be **Passive ETF-12 v1**, an investable, passive
version of the same locked opportunity set:

- universe: the immutable `locked-etf-12-v1` symbols in ADR 0004;
- starting capital: $100,000, matching the strategy account;
- common dates: exactly the dates accepted by the portfolio replay, with no
  forward-filled missing prices;
- target weights: equal weight, `1/12` per ETF;
- entry: buy at the first common open; the strategy does not receive credit for
  avoiding its indicator warm-up while the passive alternative is artificially
  left in cash;
- rebalancing: begins annually at the first common trading open of each calendar
  year; sales occur there and purchases requiring those proceeds occur at the
  following common open after T+1 settlement;
- execution: whole shares and the same commission, quoted spread, adverse
  slippage, adjusted-price data, and next-open convention as the strategy;
- cash: residual and settlement cash receives the same declared yield as the
  strategy account; the current default is zero;
- settlement: sales and subsequent spending follow the same conservative T+1
  research convention as the strategy;
- dividends and splits: represented only through the same adjusted OHLC data
  contract used by the strategy;
- no leverage, borrowing, shorting, tax model, market impact, or parameter
  selection; and
- versioning: membership, weights, rebalance timing, or cost changes create a
  new benchmark version and cannot rewrite prior results.

Equal weighting is intentionally simple and declared before results. It is not
claimed to be optimal. Because the locked universe contains overlapping US
equity and sector exposure, the benchmark is an opportunity-set control rather
than a neutral market portfolio.

## Secondary reference points

Every portfolio result will also report, without using either reference to
replace the primary benchmark after seeing results:

- **SPY buy-and-hold**, with the same start/end dates and cost convention, to
  show the outcome of a simple US-equity choice; and
- **cash**, with the declared account cash yield, to show whether taking market
  risk added value at all.

These references answer different questions. SPY may outperform because it took
more concentrated equity risk; cash may have lower drawdown because it took no
market risk. Neither fact alone proves or disproves a strategy edge.

## How future strategies will be judged

No single metric is allowed to decide success. A future preregistered experiment
must state its intended value—such as higher net return or lower drawdown—before
it runs. The decision record must then show, at minimum:

- net return and CAGR relative to Passive ETF-12 v1, SPY, and cash;
- maximum drawdown, recovery time, and Calmar ratio;
- average and peak exposure, turnover, costs, and capital left idle;
- trade count and uncertainty, including whether the sample is too small;
- stability across time periods, assets, and reasonable cost/fill stresses; and
- all failed attempts and multiple-testing controls.

A candidate cannot pass merely because it has lower drawdown while holding cash
most of the time, or because it beats buy-and-hold in one selected window. Exact
numeric pass/fail thresholds belong to the next preregistered hypothesis and
must be written before that experiment is executed.

## Consequences

- The benchmark is implemented and tested before the portfolio UI makes an
  excess-return comparison. The UI labels it historical evidence and does not
  convert positive relative performance into a validated-edge claim.
- Existing portfolio results remain mechanics demonstrations; adding the
  benchmark does not retroactively validate CTA Trend v1.
- Cron and AWS have no business justification until the local assistant can
  produce a complete, reproducible decision record under this contract.
- A future change from research assistant to advisory or trading product would
  require a separate product, regulatory, security, and operational decision.

## Implementation status

Checkpoint v0.25.0 implements Passive ETF-12 v1, SPY buy-and-hold, and declared
cash yield in `backend/app/portfolio_benchmark.py`. The primary benchmark buys
equal-weight whole shares at the first common open, charges canonical entry and
exit costs, retains residual cash, rebalances annually, and prevents sale
proceeds from funding purchases before the following shared session. The
portfolio API reports return, CAGR, drawdown, Calmar, exposure, turnover, fees,
and explicit strategy differences. The Today view shows the three comparisons
beside the strategy without claiming statistical significance or durable edge.
