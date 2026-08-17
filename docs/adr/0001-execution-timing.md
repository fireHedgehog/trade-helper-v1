[Home](../../README.md) · [Docs index](../README.md) · [Roadmap](../roadmap.md) · [Research protocol](../research-protocol.md) · [Changelog](../../CHANGELOG.md)

# ADR 0001: Daily signal and execution timing

- Status: accepted and implemented across canonical single-symbol and portfolio
  replay
- Date: 2026-08-17

## Context

Strategies use completed daily bars. A rule that depends on today's closing
price cannot be acted on at that same closing price without an auction-specific
order model and earlier information. Treating it as a same-close fill would
introduce lookahead bias.

## Decision

The canonical convention is:

1. Indicators and signals are calculated after daily bar `N` is complete.
2. An entry or ordinary close-based exit becomes pending after bar `N`.
3. The assumed fill is bar `N+1`'s open.
4. Overnight gaps are accepted at the actual `N+1` open; the model must not fill
   at the prior close or at a stop level that the market skipped through.
5. If there is no next bar, the order remains pending and is not counted as a
   completed trade.
6. Missing calendar sessions do not create synthetic bars; execution occurs at
   the next available recorded session and the data gap is reported separately.

Intraday stop execution is out of scope until the project defines an OHLC-based
ordering assumption for bars that touch multiple levels. Until then, stops are
close-based signals that fill at the following open.

## Consequences

- Backtest, Today, chart, and simulated-ledger code must use the same four states:
  `flat`, `entry_pending`, `long`, and `exit_pending`.
- Same-close ledger exits are known defects until Stage 1 is complete.
- Forced final-bar liquidation must not be presented as an ordinary strategy
  exit in headline performance.
- Tests must include overnight gaps, missing sessions, and a signal on the final
  available bar.
