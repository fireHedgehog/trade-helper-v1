"""Academic anomalies screen -- factor-zoo-v1 follow-up, a deliberately
*different* factor family (illiquidity, lottery-demand, low-vol, spread,
skewness), not more variants of the reversal cluster factor-zoo-v1 and
factor-zoo-cost-sensitivity-v1 already closed.

Usage (from backend/):
    python -m app.run_factor_zoo_academic_anomalies

Same universe/window/harness as factor-zoo-v1 (factor_zoo.evaluate_factor,
same non-evidential screening standing). Two of the five
(max_effect, expected_skewness_proxy) are expected to score a NEGATIVE
IC-IR under this harness's "high reading = long" convention -- that is
each paper's own predicted sign (lottery-demand overpricing), not a
misdirection needing correction. Orthogonality is checked against these 5
plus atr_normalized (factor-zoo-v1's one survivor) to see whether any of
these is genuinely new information or just atr_normalized again from a
different angle.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import factor_zoo
from .run_experiment import _atomic_json
from .run_factor_zoo_scan import load_universe_panels

ROOT = Path(__file__).parents[2]
OUTPUT_DIR = ROOT / "output/research/factor-zoo-academic-anomalies-v1"
MIN_SYMBOLS = 30


def main() -> None:
    panel, present_symbols, missing_symbols = load_universe_panels()

    evaluations: dict[str, factor_zoo.FactorEvaluation] = {}
    errors: dict[str, str] = {}
    for name, formula in factor_zoo.ACADEMIC_ANOMALIES.items():
        try:
            values = formula(panel)
            evaluations[name] = factor_zoo.evaluate_factor(
                name, values, panel.close, min_symbols=MIN_SYMBOLS
            )
        except Exception as exc:  # noqa: BLE001 -- one bad formula must not kill the scan
            errors[name] = str(exc)

    # Control: atr_normalized, factor-zoo-v1's one survivor, for orthogonality context.
    atr_values = factor_zoo.CLASSIC_INDICATORS["atr_normalized"](panel)
    atr_eval = factor_zoo.evaluate_factor(
        "atr_normalized", atr_values, panel.close, min_symbols=MIN_SYMBOLS
    )

    ordered = sorted(evaluations.values(), key=lambda e: e.ic_ir, reverse=True)
    orthogonality = factor_zoo.pairwise_orthogonality(ordered + [atr_eval])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "universe_size": len(present_symbols),
        "missing_symbols": missing_symbols,
        "common_date_start": str(panel.close.index[0]),
        "common_date_end": str(panel.close.index[-1]),
        "n_factors_evaluated": len(evaluations),
        "n_factors_errored": len(errors),
        "errors": errors,
        "evidential_status": "non-evidential -- screening scan only, same standing as factor-zoo-v1",
        "expected_negative_direction": sorted(factor_zoo.NEGATIVE_EXPECTED_DIRECTION),
        "results": [
            {
                "name": e.name,
                "n_days": e.n_days,
                "ic_mean": e.ic_mean,
                "ic_ir": e.ic_ir,
                "sharpe": e.sharpe,
                "cagr": e.cagr,
                "annual_volatility": e.annual_volatility,
                "max_drawdown": e.max_drawdown,
                "calmar": e.calmar,
                "win_rate": e.win_rate,
                "total_return": e.total_return,
            }
            for e in ordered
        ],
        "control_atr_normalized": {
            "ic_ir": atr_eval.ic_ir, "sharpe": atr_eval.sharpe, "cagr": atr_eval.cagr,
        },
        "orthogonality_vs_each_other_and_atr_normalized": orthogonality,
    }
    _atomic_json(OUTPUT_DIR / "academic-anomalies-report.json", report)

    print(json.dumps({
        "output": str(OUTPUT_DIR),
        "n_evaluated": len(evaluations),
        "errors": errors,
        "results": [
            {"name": e.name, "ic_ir": round(e.ic_ir, 4), "sharpe": e.sharpe, "cagr": e.cagr,
             "max_drawdown": e.max_drawdown}
            for e in ordered
        ],
        "orthogonality": orthogonality,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
