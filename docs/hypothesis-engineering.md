# Hypothesis engineering

Status: required Stage 9A entry contract; no strategy candidate may be scored until its thesis is operationalized.

## Purpose

A narrative, chart observation, famous investor's opinion, or published factor is an idea source—not an executable hypothesis. This layer converts an idea into a falsifiable claim without silently choosing a profitable-looking trade expression.

The research sequence is:

`idea → operationalization record → bounded exploration → Stage 9A priority → preregistration → Stage 9B experiment`

## Operationalization record

Create one immutable, versioned record with these fields before candidate scoring:

| Field | Required question |
|---|---|
| Claim | What conditional statement about price, return, risk, or market state is asserted? |
| Scope | For which assets, dates, horizons, and market conditions could it apply? |
| Mechanism | Why might the relationship exist and persist after it becomes known? |
| Market-belief proxy | What observable quantity represents what is already priced or expected? |
| Reality proxy | What observable quantity represents the state believed to differ from the market view? |
| Information set | Exactly what was knowable at decision time, including publication and revision timing? |
| Estimand | What population quantity answers the claim? |
| Alternatives | Which rival mechanisms could create the same observation? |
| Falsifier | What admissible result would contradict the claim? |
| Data feasibility | Which point-in-time datasets, licences, coverage, and transformations are required? |
| Expression candidates | Which portfolios could express the claim, including `no trade`? |
| Path and risk | What timing, carry, liquidity, gap, financing, and maximum-loss risks arise from each expression? |

## Separation of claim and trade

A thesis does not imply a position. For example, “market-implied growth exceeds a defensible point-in-time estimate” is a valuation claim. Short stock, a put, a spread, a relative-value portfolio, reduced exposure, or no trade are different expressions with different timing and loss distributions. First test whether the generalized claim is measurable; only then define and compare expressions under a separate portfolio protocol.

Single-person or single-company stories must be generalized into repeatable conditions. “Investor X thinks company Y is mispriced” is not testable as a strategy. A candidate might instead state a point-in-time valuation gap, horizon, reference class, and falsifier that can be observed across eligible events.

## Information classification

Strategies are not divided into “price” versus “orthogonal” types. Record a many-valued information profile:

- own-asset market data: price, volume, spreads, options-implied quantities;
- cross-asset market data: rates, commodities, currencies, credit, or peer returns;
- fundamentals: statements, filings, estimates, and revisions;
- macro and policy releases;
- events and text;
- derived portfolio state: exposure, volatility, liquidity, and constraints.

Orthogonality is an empirical relationship between a candidate's incremental information or returns and the existing portfolio—not a data vendor, subscription status, or permanent label. Free quarterly filings can be incremental; an expensive feed can be redundant.

## Promotion gate

An operationalization record may enter bounded exploration only when the claim, information set, estimand, falsifier, and feasible data path are explicit. It may enter Stage 9A only after exploratory contamination is recorded and the claim remains meaningful without reference to a favourable backtest. If measurement requires unavailable point-in-time data, park the idea rather than substitute today's revised data.
