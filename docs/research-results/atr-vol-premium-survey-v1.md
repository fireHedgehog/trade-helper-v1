# ATR Vol Premium — real backtest survey (exploratory)

Status: exploratory, ahead of [ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md)
clauses 1/2 formal sign-off. "ATR Vol Premium" (`backend/app/strategies.py`)
has run live in the app as a real Tier A strategy since its Tier A
translation of `atr_normalized`, but had never been surveyed at real
breadth — Strategy Management's "no closed result yet" for it reflected
that gap, not an absence of any backtest at all. This runs the app's own
real backtest engine (`backend/app/engine.py:backtest_payload` — real
commission, spread, slippage, the same engine every Tier A strategy
already uses) across the `501`-symbol point-in-time universe and reports
Sharpe/CAGR/drawdown directly. No p-value, no null hypothesis.

## Window

Every symbol evaluated over the same fixed window, `2015-01-01` through
the latest stored session — deliberately not each symbol's own full
history (which ranges from a few years to five decades and made the first
pass of this survey produce a nonsensical `-7,160%` median "excess vs.
buy-and-hold," an artifact of comparing modest strategy returns against
multi-decade compounding on old names like `AAPL`, not a real finding).
Fixing the window to something common and recent (spanning both the 2020
crash and the 2022 bear market) is what made this comparison honest.

## Result — 498 of 501 symbols run, 3 skipped (zero trades in window)

| Metric | Value |
|---|---:|
| Median CAGR | `3.74%` |
| Median max drawdown (MDD) | `-46.6%` |
| Worst max drawdown (single symbol) | `-96.6%` |
| Median Calmar Ratio | `0.08` |
| Median trade count | `26` |
| Median win rate | `62.9%` |
| Median profit factor | `1.61` |
| Mean / median Sharpe | `0.29` / `0.29` |
| Symbols with positive Sharpe | `93.2%` |
| Symbols that beat their own buy-and-hold | `10.6%` |
| Median excess return vs. buy-and-hold | `-215%` |

## Reading

Two honest, different facts, not one:

1. **Risk-adjusted, the strategy is broadly positive**: `93%` of symbols
   show a positive Sharpe over an 11-year window that includes two real
   crashes. A modest, positive, wide-in-scope Sharpe is a real signal, not
   nothing.
2. **In absolute terms, it underperforms buy-and-hold on 9 of 10 symbols**
   over this specific window — 2015-2026 was mostly a strong secular bull
   market for US equities, and a strategy that steps out of a position
   during low-ATR-percentile stretches gives up upside during exactly the
   stretches a straight buy-and-hold captured. This is the ordinary,
   expected tradeoff of a volatility-timing strategy in a trending market,
   not a contradiction of point 1 — Sharpe and absolute return are
   different questions.

The median `-46.6%` max drawdown is worth naming plainly: despite "vol
premium" in the name, this is not obviously a low-risk strategy on a
single-symbol basis. A diversified, risk-budgeted deployment across many
symbols (Chapter 4's actual proposal, not a single-symbol bet) is exactly
the mechanism that would need to control this, not a reason to ignore it.

At the trade level the numbers are healthier: a `62.9%` median win rate
and `1.61` median profit factor (gross wins well above gross losses) over
a `26`-trade median count — real, not a coin flip. The Calmar Ratio
(`0.08`) ties both readings together honestly: CAGR divided by max
drawdown is low specifically because the drawdown is large relative to
the return, the same tension point 2 above already names.

## What this does and does not establish

Documents ATR Vol Premium's real, broad-based performance for the first
time — the missing piece Strategy Management's "no closed result yet" was
flagging. Does not: constitute a Chapter 4 clause 1 (mechanism) or clause 2
(cross-validated point estimate with an uncertainty band, via
`block_bootstrap_confidence_interval`) sign-off — this survey is the raw
material for that, not the sign-off itself. Does not: model transaction
costs beyond the app's own default commission/spread/slippage assumptions,
or capacity/liquidity constraints across the whole universe simultaneously.

## Reproducibility

- Artifacts: `output/research/atr-vol-premium-survey-v1/manifest.json`,
  `summary.json`, `per-symbol.json` (per-symbol Sharpe, CAGR, drawdown,
  win rate, trade count for all `498` run symbols).
- `backend/app/run_atr_vol_premium_survey.py` — reuses
  `backend/app/engine.py:backtest_payload` unmodified, the same function
  every Symbol Research/Strategy Lab backtest already calls.

[ATR Vol Premium strategy](../../backend/app/strategies.py) ·
[Factor zoo v1 (origin finding)](factor-zoo-v1.md) ·
[ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md)
