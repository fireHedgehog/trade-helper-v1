# ADR 0001: Execution timing

Status: accepted and implemented.

## Context

A close-derived signal cannot execute at that same close without look-ahead. Missing sessions and gaps must remain observable rather than synthesized.

## Decision

- Evaluate signals only after completed daily bar `N`.
- Create `entry_pending` or `exit_pending` at `N` close.
- Fill at the next available real bar open, `N+1`, including the observed gap.
- If no later bar exists, retain the pending order; do not invent a fill.
- Do not synthesize missing sessions.
- Evaluate stops from completed closes until an explicit intraday-ordering model exists.

State machine:

`flat → entry_pending → long → exit_pending → flat`

## Consequences

Backtests, portfolio simulation, persisted lifecycle state, tables, and tests must use the same transition semantics. A close-to-close research statistic is not an executable P&L series unless explicitly labelled as such.
