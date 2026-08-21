# amihud_illiquidity — Chapter 4 evaluation, point-in-time universe (exploratory)

Status: exploratory, ahead of [ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md)
clauses 1/2 formal sign-off. [Factor zoo v1 §5d](factor-zoo-v1.md) already
screened `amihud_illiquidity` (Sharpe `0.70 → 0.29` after cost), but using
this project's standard today's-membership universe — the same
reverse-survivorship contamination [CS-01](cross-sectional-momentum-v1.md)
fixed for individual-stock momentum. This reruns the same, unmodified
engine (`factor_zoo.evaluate_factor`) with the factor masked to real
point-in-time S&P 500 membership first, and reports Sharpe/CAGR/drawdown/
Calmar plus a block-bootstrap EV confidence interval — no p-value.

## Result

| Metric | Value |
|---|---:|
| Sharpe | `0.29` |
| CAGR | `2.67%` |
| Annualized volatility | `11.5%` |
| Max drawdown | `-41.7%` |
| Calmar Ratio | `0.064` |
| Total return | `95.6%` (`~25` years) |
| Win rate (daily spread sign) | `49.4%` |
| Round-trip cost charged | `32` bps (this project's standard rate) |
| IC mean / IC-IR | `0.0047` / `0.035` |
| Median daily cross-section size | `297` symbols |

Block-bootstrap daily EV (68% coverage): observed mean `+1.31e-4`/day,
interval `[+4.32e-5, +2.22e-4]` — **entirely positive**, unlike sector
rotation's interval spanning zero. `chapter4_confidence_multiplier` =
**`0.33`** — the first genuinely positive confidence multiplier of this
research program. A weak per-day information coefficient (`IC≈0.005`)
compounding over `6,424` days and a median `297`-name cross-section into a
real Sharpe is the Grinold-Kahn breadth argument this project has cited
all session, observed directly rather than asserted.

## Reading

The edge survives two things that could each have killed it: real
point-in-time S&P 500 membership (masked exactly like CS-01, not today's
survivorship-biased list) and this project's own standard transaction cost
(`32` bps round-trip, not a zero-cost fantasy). Neither the direction nor
the confidence interval's lower bound flipped negative. This is not proof —
still ahead of clauses 1/2 — but it is the first candidate this session
where the numbers themselves argue for continuing, not stopping.

## What this does and does not establish

Confirms the factor-zoo screen's finding survives point-in-time correction
and real cost, evaluated the way Chapter 4 actually evaluates a candidate
(Sharpe/EV/CI), not the rank-IC screen's own framing. Does not: constitute
a Chapter 4 clause 1 (mechanism) or clause 2 sign-off — this is the raw
material for clause 2, not the decision itself. Does not: model capacity,
borrow cost for the short leg, or sector/cluster concentration within the
long-short book (ADR 0010 §1's caps, not yet applied here).

## Reproducibility

- Artifacts: `output/research/amihud-illiquidity-chapter4-v1/manifest.json`,
  `result.json`.
- `backend/app/run_amihud_illiquidity_chapter4.py` — reuses
  `factor_zoo.evaluate_factor` and `amihud_illiquidity` completely
  unmodified; new logic is the point-in-time eligibility mask (same
  `members_asof`-based construction as CS-01/sector-rotation-v1).

[Factor zoo v1 §5d (original screen)](factor-zoo-v1.md) ·
[Factor zoo cost sensitivity v1](factor-zoo-cost-sensitivity-v1.md) ·
[CS-01 (same point-in-time fix, individual-stock momentum)](cross-sectional-momentum-v1.md) ·
[ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md)
