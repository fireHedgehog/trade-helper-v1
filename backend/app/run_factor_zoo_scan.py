"""Run the formulaic alpha factor zoo scan -- Chapter 4 production input.

Usage (from backend/):
    python -m app.run_factor_zoo_scan

A screening pass, not a Stage 9A / Chapter 1-3 hypothesis test, and not
itself a Chapter 4 eligibility claim for any single factor -- see
factor_zoo.py's module docstring and docs/research-program.md Chapter 4 for
how a factor that screens well here gets formally proposed on its own, with
its own stated mechanism (ADR 0007 clause 1), which this scan does not
attempt for all 17 formulas at once.

Non-evidential disclosures, same standing as every other scan/screen in
this project:
  - Universe is the same disclosed-survivorship-biased 495-symbol S&P 500
    union Nasdaq-100 union XL-sector-ETF universe already locked in
    cross-sectional-equity-momentum-feasibility-v1.json (today's index
    members, not point-in-time -- delisted names are absent).
  - Forward return is a raw 1-session close-to-close return; no
    transaction cost, slippage, or borrow cost modeled.
  - IC t-stats/IR are informative, not a hypothesis-test p-value --
    overlapping daily rebalances are not independent draws, and no
    multiple-comparisons correction is applied across the 17 factors.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from . import factor_zoo
from .run_experiment import _atomic_json
from .store import connect

ROOT = Path(__file__).parents[2]
UNIVERSE_SPEC = ROOT / "research/experiments/cross-sectional-equity-momentum-feasibility-v1.json"
OUTPUT_DIR = ROOT / "output/research/factor-zoo-v1"
MIN_SYMBOLS = 30
TOP_N_FOR_ORTHOGONALITY = 8


def load_universe_panels() -> tuple[factor_zoo.Panel, list[str], list[str]]:
    spec = json.loads(UNIVERSE_SPEC.read_text(encoding="utf-8"))
    symbols = list(spec["universe"])
    placeholders = ",".join("?" for _ in symbols)
    with connect() as conn:
        raw = pd.read_sql_query(
            f"SELECT symbol, date, open, high, low, close, volume FROM bars "
            f"WHERE symbol IN ({placeholders}) ORDER BY date",
            conn,
            params=symbols,
        )
    present = sorted(raw["symbol"].unique())
    missing = sorted(set(symbols) - set(present))

    def pivot(column: str) -> pd.DataFrame:
        return raw.pivot(index="date", columns="symbol", values=column)

    frames = {column: pivot(column) for column in ("open", "high", "low", "close", "volume")}
    common_index = frames["close"].index
    for frame in frames.values():
        common_index = common_index.intersection(frame.dropna(axis=0, how="any").index)
    aligned = {name: frame.loc[common_index] for name, frame in frames.items()}
    panel = factor_zoo.Panel.build(
        aligned["open"], aligned["high"], aligned["low"], aligned["close"], aligned["volume"]
    )
    return panel, present, missing


def main() -> None:
    panel, present_symbols, missing_symbols = load_universe_panels()

    all_formulas = {
        **{name: ("wq101", fn) for name, fn in factor_zoo.ALPHAS.items()},
        **{name: ("classic_indicator", fn) for name, fn in factor_zoo.CLASSIC_INDICATORS.items()},
    }
    family_by_name: dict[str, str] = {name: family for name, (family, _) in all_formulas.items()}

    evaluations: list[factor_zoo.FactorEvaluation] = []
    errors: dict[str, str] = {}
    for name, (_, formula) in all_formulas.items():
        try:
            factor_values = formula(panel)
            evaluation = factor_zoo.evaluate_factor(
                name, factor_values, panel.close, min_symbols=MIN_SYMBOLS
            )
            evaluations.append(evaluation)
        except Exception as exc:  # noqa: BLE001 -- one bad formula must not kill the scan
            errors[name] = str(exc)

    evaluations.sort(key=lambda item: item.ic_ir, reverse=True)
    top = evaluations[:TOP_N_FOR_ORTHOGONALITY]
    orthogonality = factor_zoo.pairwise_orthogonality(top)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    scan_report = {
        "universe_size": len(present_symbols),
        "missing_symbols": missing_symbols,
        "common_date_start": str(panel.close.index[0]),
        "common_date_end": str(panel.close.index[-1]),
        "common_date_count": len(panel.close.index),
        "n_factors_evaluated": len(evaluations),
        "n_factors_errored": len(errors),
        "errors": errors,
        "evidential_status": "non-evidential -- screening scan only, see module docstring",
        "results": [
            {
                "name": e.name,
                "family": family_by_name[e.name],
                "n_days": e.n_days,
                "n_symbols_median": e.n_symbols_median,
                "ic_mean": e.ic_mean,
                "ic_std": e.ic_std,
                "ic_ir": e.ic_ir,
                "sharpe": e.sharpe,
                "cagr": e.cagr,
                "annual_volatility": e.annual_volatility,
                "max_drawdown": e.max_drawdown,
                "calmar": e.calmar,
                "win_rate": e.win_rate,
                "total_return": e.total_return,
            }
            for e in evaluations
        ],
        "orthogonality_top_n": TOP_N_FOR_ORTHOGONALITY,
        "orthogonality": orthogonality,
    }
    _atomic_json(OUTPUT_DIR / "scan-report.json", scan_report)

    chart_paths = factor_zoo.render_charts(evaluations, OUTPUT_DIR)

    print(json.dumps({
        "output": str(OUTPUT_DIR),
        "universe_size": len(present_symbols),
        "missing_symbols": missing_symbols,
        "n_factors_evaluated": len(evaluations),
        "n_factors_errored": len(errors),
        "errors": errors,
        "top_5_by_ic_ir": [
            {"name": e.name, "ic_ir": e.ic_ir, "sharpe": e.sharpe} for e in evaluations[:5]
        ],
        "charts": [str(p) for p in chart_paths],
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
