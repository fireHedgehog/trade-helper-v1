[Home](../../README.md) · [Docs index](../README.md) · [Roadmap](../roadmap.md) · [Research protocol](../research-protocol.md) · [Changelog](../../CHANGELOG.md)

# ADR 0002: Daily market-data contract

- Status: accepted for the research prototype
- Date: 2026-08-17

## Context

A backtest can return convincing numbers even when its input contains duplicate
dates, impossible candles, partial downloads, or mixed adjustment conventions.
Rejecting malformed input is safer than silently dropping rows and publishing a
partial history.

## Decision

Each stored bar must have:

- a non-empty symbol and a unique, increasing `YYYY-MM-DD` date per symbol;
- finite, strictly positive open, high, low, and close values;
- `high >= max(open, close)`, `low <= min(open, close)`, and `low <= high`;
- finite, non-negative volume (zero is allowed for macro/yield series);
- one consistent daily frequency with missing sessions left absent rather than
  synthetically filled.

Equity and ETF OHLC data fetched from Yahoo uses `auto_adjust=True`, so historical
prices are adjusted for splits and cash distributions. Consequently:

- the buy-and-hold comparison is a total-return-like adjusted-price comparison;
- raw historical execution prices are not available from this stored series;
- adjusted OHLC must not be mixed with unadjusted OHLC in one symbol history;
- provider revisions can change old bars and therefore change later results.

FRED values are stored in the same table for convenience but are economic series,
not tradable OHLC instruments. They must never be passed into strategy or
portfolio performance calculations as if they were executable securities.

Operational ownership is explicit at the application boundary: the known FRED
series are excluded from security selectors and Yahoo refresh jobs. Yahoo manual
refreshes fetch and upsert the full adjusted history rather than mixing a recent
adjusted slice with an older adjustment basis.

## Consequences

- Storage rejects the entire malformed batch before writing any row.
- Fetch adapters are responsible for provider-specific cleaning before storage.
- Stage 9 must add staging, coverage thresholds, revision detection, and atomic
  publication before unattended updates are enabled.
- Data-source, adjustment mode, fetch timestamp, and revision provenance still
  need explicit metadata; this ADR documents the current contract, not completion
  of data lineage.
- v0.23.0 adds a holiday-unaware expected-US-weekday freshness classification,
  provider-separated inventory, and observable manual refresh progress. Exchange
  holidays, persistent run history, staging, and revision diffs remain Stage 9.
