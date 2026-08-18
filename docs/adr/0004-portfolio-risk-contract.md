[Home](../../README.md) · [Docs index](../README.md) · [Roadmap](../roadmap.md) · [Research protocol](../research-protocol.md) · [Changelog](../../CHANGELOG.md)

# ADR 0004: Portfolio capital and risk contract

- Status: accepted; Stage 5 implementation complete
- Date: 2026-08-18

## Context

The current UI replays each symbol independently and labels dollar P&L using a
fixed 100-share convention. Independent simulations can collectively spend more
cash than one account owns, while fixed shares create radically different risk
for a $20 ETF and a $700 stock. That is useful for checking signal parity but is
not a portfolio.

CTA Trend v1 failed its development validation. This ADR therefore defines
strategy-independent accounting and safety behavior; it does not authorize CTA,
recommend these limits, or imply that portfolio construction creates an edge.

## Decision

The first portfolio simulator will be deterministic, long-only, daily-bar, and
cash constrained:

- initial capital: $100,000;
- one position per symbol; no leverage, shorting, fractional shares, borrowing,
  or reuse of unsettled hypothetical proceeds;
- signal at completed close, order at the next available open, using the same
  commission, spread, slippage, and gap model as the canonical engine;
- require every symbol in one replay to have the same validated date calendar;
  fail closed rather than silently forward-fill a stale mark or discard a date;
- size from the smaller of 0.5% equity at stop risk and 10% equity at entry
  notional, rounded down to whole shares;
- size provisionally from the signal close, then recheck stop risk, notional,
  cash, sector, and cluster limits at the actual next open; reduce the fill or
  reject it when an overnight gap invalidates the provisional order;
- reject an entry when its stop is missing, non-finite, or not below the expected
  entry. Unknown risk is not treated as zero risk;
- maximum 25% equity in one declared sector and 30% in one declared correlated-
  asset cluster;
- deterministic order priority: higher locked rule score, then symbol ascending;
- the first replay accepts immutable per-symbol priority scores declared before
  the run; omitted scores are equal and therefore resolve by symbol;
- when a valid order does not fully fit a cash, sector, or cluster limit, reduce it
  to the largest permitted whole-share quantity; reject it only when zero shares
  fit;
- every rejected order records date, symbol, requested shares, available cash,
  and one machine-readable reason;
- sale proceeds remain an equity receivable on the trade date and become
  spendable cash on the next recorded shared-calendar session (a conservative
  T+1 research approximation);
- mark all open positions to the same completed close for daily equity, exposure,
  concentration, and drawdown;
- at a 15% portfolio drawdown from the running equity peak, cancel pending entries,
  create next-open liquidation orders for all positions, and prevent new entries
  until an explicit simulation reset. This is a research kill switch, not a
  guarantee against a larger gap loss.

Limits are configuration with the above conservative defaults. Changing them in
research creates a new attempted specification; they are not tuning knobs to fix
a rejected strategy result.

## Consequences and limitations

- The existing 100-share table must be relabeled as a per-symbol signal replay
  until it is replaced by this portfolio ledger.
- Orders can be rejected even when their individual signals are valid.
- A stop-based sizing rule excludes strategies without a defined protective stop
  from the first portfolio implementation.
- Sector and cluster membership must be explicit source data, never inferred
  after seeing which combination improves a backtest.
- Daily bars cannot model intraday order sequence, partial fills, liquidity,
  impact, taxes, settlement rules, or losses inside an overnight gap.
- A kill switch limits modeled continuation risk but cannot cap realized loss at
  exactly 15% because liquidation still occurs at the following available open.
- Account return, risk, concentration, trade, and turnover metrics do not include
  a benchmark-relative claim until portfolio benchmark composition and
  rebalancing are separately specified.

## Implementation status

Checkpoint v0.22.0 completes the Stage 5 implementation. The replay processes
multi-symbol entry and exit signals through one cash ledger, rechecks every limit
at the actual open, charges canonical costs, tracks T+1 sale settlements,
preserves final pending orders, and marks equity/exposure/concentration/drawdown
at each shared close. A 15% completed-close drawdown records an explicit risk
event, halts entries, and creates next-open liquidation orders; a final-bar
liquidation remains pending. `backend/app/portfolio_metrics.py` reports account
return, risk, exposure, concentration, turnover, trade outcomes, rejections,
risk events, and final pending state.

`backend/app/portfolio_universe.py` declares the immutable 12-ETF manifest and
operational risk classifications. `backend/app/portfolio_api.py` fails closed on
missing data or calendar differences and exposes the historical replay through
`/api/portfolio`; a short cache avoids repeating the same expensive local replay.
The Today view now consumes that account instead of displaying fixed-100-share
dollar P&L. Strategies without an explicit protective stop return an
`unsupported` result, so no post-hoc risk rule is invented. The complete suite
has 148 passing deterministic tests, and headless checks cover both a supported
CTA result and the explicit SMA refusal path.

No paper/live store or broker connection exists. The endpoint and UI label this
as historical mechanics only, not prospective evidence or trading authorization.
