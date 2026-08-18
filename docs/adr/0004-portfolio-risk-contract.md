# ADR 0004: Portfolio and risk contract

Status: accepted and implemented for historical simulation only.

## Account model

- Initial equity: `$100,000`.
- Long-only; no leverage, shorting, borrowing, or fractional shares.
- Strict common trading calendar across included symbols.
- Orders follow [ADR 0001](0001-execution-timing.md) and use explicit costs.
- Cash from a sale becomes reusable at `T+1`; cash yield is zero.

At close `t`, equity is `E_t = cash_t + Σ(q_i × close_i,t)`. Drawdown is `D_t = E_t / max_{u≤t}(E_u) − 1`.

## Entry capacity

For equity `E`, expected fill `P`, and per-share stop distance `d > 0`, target shares are bounded by:

`q = floor(min(0.005E / d, 0.10E / P))`.

Recheck size at the actual next open including costs and available settled cash. Sector exposure may not exceed `25%` of equity; cluster exposure may not exceed `30%`. If capacity is constrained, allocate by higher locked score then symbol. Partial size is permitted; zero size is rejected and recorded.

The stop must be below expected entry. Every rejection records its binding reason.

## Drawdown policy

When close-to-close portfolio drawdown reaches `−15%`:

1. cancel pending entries;
2. submit all exits for the next available open;
3. halt new entries until an explicit reset.

## Consequences

Per-symbol backtests cannot establish portfolio feasibility. Historical simulation does not imply paper/live readiness; operational reconciliation and broker controls require a separate design.
