"""Transaction-cost sensitivity of the factor-zoo reversal cluster --
Chapter 4 Sec.5 follow-up, named as the next step in
docs/research-results/factor-zoo-v1.md.

Usage (from backend/):
    python -m app.run_factor_zoo_cost_sensitivity

factor-zoo-v1 modeled zero transaction cost. Its top cluster
(alpha034/033/009/028/004/026, r=0.52-0.79 pairwise) is disclosed there as
one shared, unconfirmed hypothesis -- the classic bid-ask-bounce reversal
artifact (Jegadeesh 1990, Lehmann 1990), where an apparent 1-session
reversal profit can be manufactured by raw closes alternating near the bid
and ask, with no real edge once realistic costs are modeled. This measures
exactly that, instead of leaving it asserted.

`atr_normalized` (confirmed orthogonal to the cluster, |r|<=0.34) is
included as a control: an independent factor should degrade with cost like
any traded strategy, not vanish the way a reversal artifact should.

Cost is charged on quintile turnover via factor_zoo.evaluate_factor's
round_trip_cost_bps parameter (see its docstring for the exact mechanism),
reused unmodified -- not a bespoke cost model for this one report. The
"standard" rate is this project's own already-decided cost assumption
(engine.py's COMMISSION/SPREAD/SLIPPAGE, "deliberate, so results aren't
fantasy" per that module's docstring), not invented fresh for this check:
a round trip = 2 commission fills + 1 quoted spread + 2 slippage fills.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import factor_zoo
from .engine import COMMISSION, SLIPPAGE, SPREAD
from .run_experiment import _atomic_json
from .run_factor_zoo_scan import load_universe_panels

ROOT = Path(__file__).parents[2]
OUTPUT_DIR = ROOT / "output/research/factor-zoo-cost-sensitivity-v1"
MIN_SYMBOLS = 30

# This project's own standard round-trip cost, derived (not invented) from
# engine.py's single-asset assumption: 2 commission fills + 1 quoted spread
# + 2 slippage fills.
STANDARD_ROUND_TRIP_BPS = (2 * COMMISSION + SPREAD + 2 * SLIPPAGE) * 10_000

# The correlated reversal cluster factor-zoo-v1 flagged as one shared
# hypothesis, plus atr_normalized as the confirmed-independent control.
CLUSTER_FACTORS = ["alpha034", "alpha033", "alpha009", "alpha028", "alpha004", "alpha026"]
CONTROL_FACTORS = ["atr_normalized"]
COST_LEVELS_BPS = [0.0, STANDARD_ROUND_TRIP_BPS, 2 * STANDARD_ROUND_TRIP_BPS]


def main() -> None:
    panel, present_symbols, missing_symbols = load_universe_panels()
    all_formulas = {**factor_zoo.ALPHAS, **factor_zoo.CLASSIC_INDICATORS}

    factor_values_cache = {
        name: all_formulas[name](panel) for name in CLUSTER_FACTORS + CONTROL_FACTORS
    }

    results: dict[str, list[dict]] = {}
    for name, values in factor_values_cache.items():
        rows = []
        for cost_bps in COST_LEVELS_BPS:
            evaluation = factor_zoo.evaluate_factor(
                name, values, panel.close, min_symbols=MIN_SYMBOLS,
                round_trip_cost_bps=cost_bps,
            )
            rows.append({
                "cost_bps": cost_bps,
                "sharpe": evaluation.sharpe,
                "cagr": evaluation.cagr,
                "max_drawdown": evaluation.max_drawdown,
                "total_return": evaluation.total_return,
            })
        results[name] = rows

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "universe_size": len(present_symbols),
        "missing_symbols": missing_symbols,
        "common_date_start": str(panel.close.index[0]),
        "common_date_end": str(panel.close.index[-1]),
        "common_date_count": len(panel.close.index),
        "evidential_status": "non-evidential -- screening scan only, same standing as factor-zoo-v1",
        "cost_model": (
            "round-trip cost charged on quintile turnover (factor_zoo.evaluate_factor's "
            "round_trip_cost_bps); standard rate derived from engine.py's own "
            "COMMISSION/SPREAD/SLIPPAGE, not invented for this report"
        ),
        "standard_round_trip_bps": STANDARD_ROUND_TRIP_BPS,
        "cost_levels_bps": COST_LEVELS_BPS,
        "cluster_factors": CLUSTER_FACTORS,
        "control_factors": CONTROL_FACTORS,
        "results": results,
    }
    _atomic_json(OUTPUT_DIR / "cost-sensitivity-report.json", report)

    chart_path = OUTPUT_DIR / "sharpe-vs-cost.png"
    fig, ax = plt.subplots(figsize=(9, 6))
    for name, rows in results.items():
        style = "--" if name in CONTROL_FACTORS else "-"
        ax.plot(
            [row["cost_bps"] for row in rows],
            [row["sharpe"] for row in rows],
            style, marker="o", label=name,
        )
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_title("Factor zoo -- Sharpe vs. round-trip cost (reversal cluster + control)")
    ax.set_xlabel("Round-trip cost charged per unit quintile turnover (bps)")
    ax.set_ylabel("Sharpe (daily-rebalanced quintile spread)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=120)
    plt.close(fig)

    print(json.dumps({
        "output": str(OUTPUT_DIR),
        "standard_round_trip_bps": round(STANDARD_ROUND_TRIP_BPS, 2),
        "results": {
            name: [
                {"cost_bps": round(row["cost_bps"], 2), "sharpe": row["sharpe"]}
                for row in rows
            ]
            for name, rows in results.items()
        },
        "chart": str(chart_path),
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
