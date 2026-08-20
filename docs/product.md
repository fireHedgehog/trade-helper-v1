# Product contract

## Objective

Trade Research is a local decision workspace for evaluating long-only systematic strategies against explicit passive alternatives after costs. Its output is evidence for `reject`, `revise`, or `continue research`, not an instruction to trade.

## Users and decisions

The primary user is a technically capable individual researcher who needs to answer:

- Is local data complete and recent enough for the intended run?
- What is the latest persisted state of watched symbols under each strategy?
- Which symbols generated a new-entry candidate across the full universe?
- Where do independently specified strategies agree?
- Does a strategy outperform Passive ETF-12, SPY, or cash under a locked protocol?
- Is apparent performance stable, statistically distinguishable, and operationally plausible?

## Product surfaces

| Surface | Business purpose |
|---|---|
| Today | Daily command centre: freshness, explicit actions, holdings/exits, new candidates, and warnings |
| Symbol Research | Human-readable multi-strategy assessment for one symbol, with evidence and risk context |
| Strategy Lab | Configure, run, compare, and inspect versioned historical experiments |
| Data Management | Inspect coverage/freshness and explicitly refresh selected data with throttling and progress |
| Macro | Descriptive, non-tradable economic context under [ADR 0006](adr/0006-macro-data-contract.md): release-based freshness; never a signal or candidate source |
| Research Record | Immutable protocols, artifacts, decisions, and rejection reasons in `docs/` and `output/research/` (documentation surface; no separate UI page) |

Detailed interaction and presentation rules live in [workspace-redesign.md](workspace-redesign.md).

Data Management must evolve into a dataset registry rather than a fixed price-download list. Each dataset records identifier, information class, provider/licence, schema version, cadence, timezone, publication/revision semantics, point-in-time capability, coverage, freshness rule, transformation lineage, quality state, and fingerprint. Adding a research idea may add a dataset type without changing existing market-bar contracts.

Strategy definitions use a versioned schema: strategy/family identifier, information profile, hypothesis record, parameter definitions (name, type, units, bounds/default, research status), required datasets, signal/execution state, benchmark, validation status, and artifact fingerprint. Parameters are rows/objects, not new hard-coded table columns. “Orthogonal” is measured relative to an existing information set or portfolio and is not a strategy type.

## Domain model

### Watchlist lifecycle

A watchlist is user-authored and persistent per strategy. Each symbol occupies one auditable state:

`flat → entry_pending → long → exit_pending → flat`

The table must expose the last entry (`date @ price`) when relevant, the last exit when flat, current signal, holding status, and last evaluated session. Non-applicable values are `—`; entry and exit are events, not permanent states.

### Candidate universe

Candidate tabs are generated from the complete configured universe after an explicit strategy run. Each model—CTA, SMA cross, breakout, momentum horizons, and future validated models—has its own result set. An intersections view shows symbols selected by multiple models. Empty means “no eligible candidates” only when a completed run proves that; otherwise show “not run” or “stale”.

### Data and runs

Navigation reads persisted results and must not trigger network work. Users explicitly:

1. refresh market data;
2. observe progress, throttling, failures, and final freshness;
3. run selected strategies;
4. inspect persisted results.

## Research and execution invariants

- Completed daily bar `N` creates a pending order; execution occurs at next available open `N+1`.
- Portfolio tests use whole shares, explicit costs, cash accounting, settlement, capacity constraints, and drawdown policy.
- Adjusted Yahoo OHLCV cannot be mixed with unadjusted prices in one run.
- Passive ETF-12 v1 is the default project benchmark under [ADR 0005](adr/0005-product-objective-and-portfolio-benchmark.md); every new protocol must audit its suitability and may preregister a better-matched versioned benchmark.
- Statistical claims follow [ADR 0003](adr/0003-research-statistics.md) and the active preregistration.
- Macro series are non-tradable context under [ADR 0006](adr/0006-macro-data-contract.md); release alignment governs their use, never the reference period.
- Failed hypotheses remain failed; new factors or parameters require a new versioned hypothesis.

## Out of scope

- Live brokerage connectivity, real-money execution, automatic orders, leverage, short selling, options, or live risk controls. (Amended by [ADR 0008](adr/0008-bounded-paper-trading.md), status `accepted`: a sandboxed *paper* connection to a broker's own paper-trading endpoint, gated by ADR 0008's approval design and carrying no real capital, is what that ADR authorizes the design of — live connectivity remains out of scope, unchanged.)
- Claims of profitability, suitability, or production readiness.
- Cron refresh before the visible manual workflow is reliable.
- Cloud deployment before research and product gates pass.
- Macro-derived entry signals or candidates before [ADR 0006](adr/0006-macro-data-contract.md) point-in-time data and a preregistered hypothesis exist.

## Release gates

A local staging release requires deterministic tests, explicit loading/error/empty/stale states, durable progress, readable business language, responsive layouts, and no hidden work on page load. Paper trading requires a separate point-in-time data, operational risk, reconciliation, and approval design; it is not an implied next step. That design is accepted in [ADR 0008](adr/0008-bounded-paper-trading.md) (status `accepted`, `2026-08-21`) — acceptance is not itself the implied next step either; it still requires implementation, then a real candidate reaching `eligible for operational validation` before anything paper-trades.
