# ADR 0002: Market-data contract

Status: accepted and implemented for local research.

## Valid bar series

For each symbol, bars must be non-empty, unique by session, and strictly increasing. Every OHLC value is finite and positive; volume is finite and non-negative. For each bar:

`high ≥ max(open, close)` and `low ≤ min(open, close)`.

Invalid series fail explicitly; they are not silently repaired.

## Price basis

Yahoo downloads use `auto_adjust=True`. OHLC therefore behaves as a split/dividend-adjusted, total-return-like research series. One run may not mix adjusted and unadjusted prices. Provider revisions can alter historical results and must be captured by data fingerprints.

FRED series are non-tradable context: they are excluded from Yahoo refresh, strategy bars, and execution assumptions.

## Refresh policy

Manual refresh may request full history and must expose symbol-level progress, throttling, failures, row counts, first/last session, and final freshness. Navigation never starts a refresh.

Publication is atomic per symbol. If the browser reloads, the in-process worker continues. If the server restarts, volatile job progress is lost but published SQLite rows remain. The normal resume action must recompute freshness and select only aging, stale, or invalid symbols; forced core/all actions may deliberately re-download current symbols. Therefore “job restarted” and “data restarted from zero” are not equivalent.

Before unattended operation, add staged downloads, schema validation, atomic promotion, provenance, holiday/calendar policy, retry/backoff, and provider-revision comparison.

## Consequences

Every experiment identity includes the effective specification and input OHLCV fingerprint. Data coverage and freshness are evidence, not merely UI metadata.
