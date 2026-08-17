[Home](../../README.md) · [Docs index](../README.md) · [Roadmap](../roadmap.md) · [Research protocol](../research-protocol.md) · [Changelog](../../CHANGELOG.md)

# ADR 0004: Portfolio capital and risk contract

- Status: proposed for Stage 5 implementation
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
- size from the smaller of 0.5% equity at stop risk and 10% equity at entry
  notional, rounded down to whole shares;
- reject an entry when its stop is missing, non-finite, or not below the expected
  entry. Unknown risk is not treated as zero risk;
- maximum 25% equity in one declared sector and 30% in one declared correlated-
  asset cluster;
- deterministic order priority: higher locked rule score, then symbol ascending;
- every rejected order records date, symbol, requested shares, available cash,
  and one machine-readable reason;
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
