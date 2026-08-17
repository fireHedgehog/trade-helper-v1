"""Runner manifests and caches must be reproducible and self-identifying."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd

from app.research import CandidateWindowEvaluation, load_experiment_spec
from app.run_experiment import _candidate_from_dict, _experiment_context, _fingerprint


SPEC = Path(__file__).parents[2] / "research" / "experiments" / "cta-trend-v1.json"


def test_candidate_cache_round_trip() -> None:
    original = CandidateWindowEvaluation(
        candidate="candidate",
        params={"n": 1},
        eligible_symbols=("ONE",),
        excluded_symbols=(("TWO", "missing"),),
        median_strategy_return=0.1,
        median_benchmark_return=0.05,
        median_excess_return=0.05,
        median_calmar=1.0,
        median_max_drawdown=-0.1,
        median_exposure=0.5,
        total_closed_trades=2,
        dates=("2024-01-01", "2024-01-02"),
        strategy_daily_returns=(0.1, 0.0),
        benchmark_daily_returns=(0.05, 0.0),
        excess_daily_returns=(0.05, 0.0),
    )
    assert _candidate_from_dict(asdict(original)) == original


def test_data_fingerprint_changes_with_price(research_bars: pd.DataFrame) -> None:
    spec = {"universe": ["ONE"], "experiment_id": "test"}
    first = _fingerprint(spec, {"ONE": research_bars})
    changed = research_bars.copy()
    changed.loc[0, "close"] += 0.01
    second = _fingerprint(spec, {"ONE": changed})
    assert first != second


def test_real_spec_context_has_expected_fold_contract() -> None:
    spec = load_experiment_spec(SPEC)
    # This test exercises structure without depending on the user's local DB.
    dates = pd.bdate_range("2006-02-06", periods=5_200).strftime("%Y-%m-%d")
    frame = pd.DataFrame(
        {
            "date": dates,
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1_000.0,
        }
    )
    bars = {symbol: frame.copy() for symbol in spec["universe"]}
    _, tail, folds = _experiment_context(spec, bars)
    assert tail.bars == 504
    assert len(folds) >= 14
    assert folds[0].validation_start > folds[0].train_end
