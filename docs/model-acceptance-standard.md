# Model acceptance and candidate priority

Status: required Stage 9A gate; design work only until Stage 8 is complete and research is explicitly resumed.

## Purpose

No strategy is selected because it is familiar, recently discussed, popular, or attractive in an exploratory backtest. Stage 9A ranks candidates before their results are known and defines what evidence permits advancement. Passing permits further validation; it never means safe, proven, or approved for trading.

## Candidate scorecard

Record each item as `0` weak, `1` plausible, or `2` strong, with a short justification and cited evidence. Score before implementation.

| Dimension | Required question |
|---|---|
| Rationale | What behavioural, structural, or risk-premium mechanism could persist? |
| Product relevance | How could it improve Passive ETF-12 v1 after costs and risk? |
| Distinct information | What does it add beyond previously tested signals? |
| Data readiness | Is point-in-time, bias-controlled data available at the required resolution? |
| Implementability | Are timing, liquidity, turnover, costs, capacity, and portfolio constraints credible? |
| Falsifiability | What result would reject the idea, and can one finite experiment produce it? |
| Research restraint | Is the search family small enough to control multiplicity and preserve confirmation data? |
| Diversification | Could the return or risk pattern improve the portfolio rather than duplicate its exposure? |

Reject candidates with unavailable point-in-time data, an unfalsifiable rationale, unbounded search, or no credible implementation. Among eligible candidates, prefer the simpler and more independently testable design. The score ranks research effort; it does not estimate alpha.

## Required preregistration

Before computing comparative results, lock the hypothesis and failure mechanism; universe and provenance; primary benchmark and estimand; signal, fill, holding, and portfolio rules; parameter/search budget; costs and stress levels; walk-forward topology; dependence treatment; multiplicity policy; minimum information requirement; acceptance thresholds; and untouched confirmation data. Publish a fingerprint of the immutable specification.

Thresholds are model-specific and must be justified by the objective, expected payoff distribution, sample power, and implementation burden. There is no universal minimum Sharpe ratio, win rate, p-value, or maximum drawdown that validates every strategy.

## Evidence gate

### Research validity

- No look-ahead, survivorship, universe-selection, or execution-timing contamination.
- Sufficient independent observations and regimes for the declared inference.
- All attempted variants recorded; multiplicity and dependence handled as preregistered.
- Reproducible artifacts, data fingerprint, configuration, code version, and deterministic seed.

Any material failure invalidates the experiment; attractive performance cannot rescue it.

### Economic and implementation validity

- Net performance includes locked costs and adverse cost/slippage stress.
- Comparison uses Passive ETF-12 v1; SPY and cash remain diagnostic references.
- Effect size is economically material, not merely statistically detectable.
- Results are not dominated by one asset, period, regime, or trade.
- Nearby admissible parameters and walk-forward folds show acceptable stability.
- Turnover, exposure, cash drag, concentration, liquidity, settlement, and rejected orders are reported.

### Risk and statistical evidence

Report total return, CAGR, volatility, Sharpe, Sortino, maximum drawdown, recovery duration, Calmar, downside/tail loss, win rate with payoff ratio, trade count, exposure, turnover, costs, fold/asset/regime dispersion, confidence intervals, adjusted significance, and sensitivity results. Interpret the metrics jointly:

- win rate without payoff ratio is not a profitability test;
- Sharpe can conceal skew, serial dependence, and tail loss;
- maximum drawdown is one realised path, not a future loss bound;
- a p-value is not the probability that a strategy is true;
- backtest significance is not permission to trade.

## Decisions

- `reject`: the locked claim fails or the experiment is invalid.
- `revise`: evidence exposes a new, independently motivated hypothesis; create a new version and new search budget.
- `continue research`: every preregistered gate passes; run the untouched confirmation test once.
- `eligible for operational validation`: confirmation passes; only then consider bounded paper trading to test data, state, and execution operations.

Paper trading does not prove alpha and zero losses are not an acceptance condition. Define a loss budget, observation horizon, reconciliation rules, and stop conditions before it begins. Live or broker-connected trading requires a separate decision and remains out of scope.

## Candidate-selection record

For each Stage 9 cycle, preserve the complete scored candidate table, conflicts of interest, rejected candidates and reasons, chosen candidate, preregistered protocol fingerprint, experiment ledger, decision, and links to immutable evidence. A later agent must be able to reconstruct what was known before results were observed.
