# Sector rotation — Chapter 4 evaluation (exploratory)

Status: exploratory, ahead of [ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md)
clauses 1/2 formal sign-off — same status `atr_normalized`'s own Tier A
translation carried before its mechanism was written down. Evaluated on
realized Sharpe, CAGR, drawdown, and a block-bootstrap EV confidence
interval — not a null-hypothesis p-value, per direct user feedback
(`2026-08-21`) that Chapter 2's falsification bar is the wrong instrument
for a modest, potentially episodic, personally-observed edge.

## Rule

A real entry/exit rule, not [sector-rotation-v1](sector-rotation-v1.md)'s
fixed monthly rebalance: at each session, rank the 11 GICS sectors by
trailing 252-session return. Long the top-3, short the bottom-3,
equal-weighted within each side, 50%/50% gross (market-neutral). Positions
change only when the top-3/bottom-3 *set* changes from the prior session —
holds through a stable ranking rather than rebalancing on a calendar.

## Result

| Metric | Value |
|---|---:|
| CAGR | `-1.87%` |
| Annualized return | `-1.50%` |
| Annualized volatility | `8.77%` |
| Sharpe (0% risk-free) | `-0.17` |
| Max drawdown | `-51.9%` |
| Calmar | `-0.036` |
| Total return | `-37.1%` |
| Rebalance count | `1,879` over `6,193` sessions (~`24.6` years) |
| Benchmark (equal-weight, always-long, all 11 sectors) CAGR | `+13.58%` |

Block-bootstrap daily EV (68% coverage): observed mean `-5.96e-5`/day,
interval `[-1.24e-4, +3.29e-6]` — the interval's upper bound barely
touches zero; the point estimate is negative. `chapter4_confidence_multiplier`
= **`0.0`**: per ADR 0007, a non-positive point estimate sizes to zero and
fails Chapter 4 eligibility outright, the same as a Chapter 1-3 `reject`
would in that track.

## Reading

This converges with [sector-rotation-v1](sector-rotation-v1.md)'s
correlation-based null, via a completely different statistic and a real
entry/exit rule instead of a fixed rebalance — two independent methods
agreeing is a stronger negative than either alone, not a contradiction of
"the p-value was the wrong tool." The tool was wrong for what it could
show either way; running the right tool did not reverse the answer.

One concrete, actionable diagnostic: `1,879` rebalances over `24.6` years
is roughly one every `3.3` sessions — far higher turnover than a genuine
"multi-month regime" rule should produce. This indicates the top-3/bottom-3
boundary is noisy day-to-day (names near the 3rd/4th rank flip in and out
frequently even when the broader trend is stable), which by itself
degrades returns through whipsaw — before any transaction cost is even
modeled. A smoother rule (a persistence requirement before triggering a
change, a wider band, or a slower formation window) is a plausible fix,
but it is a new, independently-justified design decision, not a silent
retry of this one.

## What this does and does not establish

Confirms the same conclusion [sector-rotation-v1](sector-rotation-v1.md)
reached, this time in P&L terms an investor would actually recognize:
this specific top-3/bottom-3, 252-session-formation design has no edge and
loses money net of its own whipsaw, before costs. Does not test: a
smoother entry/exit design, a narrower or wider top/bottom band, a
different formation window, or GICS Sub-Industry-level rotation
("Semiconductors" specifically). Each is a new, independently justified
candidate.

## Reproducibility

- Artifacts: `output/research/sector-rotation-chapter4-v1/manifest.json`,
  `result.json`. No cost, no live capital, no fingerprint lock — exploratory
  status only, per this project's own distinction between a locked
  Stage 9A/9B protocol and an exploratory screen.
- Same sector-index construction as
  [sector-rotation-v1](sector-rotation-v1.md) (`backend/app/run_sector_rotation_v1.py:build_sector_panel`,
  reused unmodified); new logic is the entry/exit rule and metrics
  (`backend/app/run_sector_rotation_chapter4.py`).

[Sector rotation, Chapter 2 result](sector-rotation-v1.md) ·
[ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md)
