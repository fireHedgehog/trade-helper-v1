# ADR 0002: Market-data contract

Status: accepted and implemented for local research.

## Valid bar series

For each symbol, bars must be non-empty, unique by session, and strictly increasing. Every OHLC value is finite and volume is finite and non-negative.

Equity/ETF strategy bars must be positive and satisfy:

`high ≥ max(open, close)` and `low ≤ min(open, close)`.

Invalid series fail explicitly; they are not silently repaired.

Yahoo futures and yield proxies (`GC=F`, `CL=F`, `^TNX`) are descriptive market context, not members of the equity/ETF strategy universe. Their settlement close can lie outside the reported intraday high/low, and crude futures traded below zero in April 2020. Context validation therefore permits non-positive prices and out-of-envelope settlement while still requiring finite values, non-negative volume, and `low ≤ high`. This exception never weakens equity/ETF validation.

## Price basis

Yahoo downloads use `auto_adjust=True`. OHLC therefore behaves as a split/dividend-adjusted, total-return-like research series. One run may not mix adjusted and unadjusted prices. Provider revisions can alter historical results and must be captured by data fingerprints.

FRED series and Yahoo market-context symbols are non-tradable context: they are excluded from strategy bars and execution assumptions. FRED is excluded from Yahoo refresh; Yahoo context retains its own descriptive refresh path.

## Refresh policy

Manual refresh may request full history and must expose symbol-level progress, throttling, failures, row counts, first/last session, and final freshness. Navigation never starts a refresh.

Publication is atomic per symbol. If the browser reloads, the in-process worker continues. Refresh job identity, timestamps, counters, and per-symbol outcomes persist in SQLite. If the server restarts, the worker stops and unfinished items become `interrupted`; published rows and the job record remain. The normal resume action recomputes freshness and selects only aging, stale, or invalid symbols; forced core/all actions may deliberately re-download current symbols. Therefore “worker interrupted,” “job record lost,” and “data restarted from zero” are not equivalent.

Before unattended operation, add staged downloads, schema validation, atomic promotion, provenance, holiday/calendar policy, retry/backoff, and provider-revision comparison.

## Consequences

Every experiment identity includes the effective specification and input OHLCV fingerprint. Data coverage and freshness are evidence, not merely UI metadata.

Daily discovery snapshots may proceed with at least 90% current equity/ETF universe coverage, must fingerprint only executed symbols, and must persist every preflight exclusion. This operational tolerance does not apply to formal experiments, which retain their locked protocol-specific universe and coverage requirements.
