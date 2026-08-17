"""Resumable runner for the preregistered CTA walk-forward experiment.

Run from ``backend/``:
    python -m app.run_experiment

Candidate caches live under ignored ``data/``. The compact evidence record is
written under ``output/research/`` and is safe to review before committing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .research import (
    CandidateWindowEvaluation,
    evaluate_candidate_window,
    load_experiment_spec,
    parameter_candidates,
    partition_candidate_holdout,
    select_validation_candidate,
    walk_forward_folds,
)
from .store import load_bars


ROOT = Path(__file__).parents[2]
DEFAULT_SPEC = ROOT / "research" / "experiments" / "cta-trend-v1.json"
DEFAULT_OUTPUT = ROOT / "output" / "research" / "cta-trend-wf-v1.json"


def _atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def _fingerprint(spec: dict, bars_by_symbol: dict[str, pd.DataFrame]) -> str:
    digest = hashlib.sha256(
        json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
    )
    columns = ["date", "open", "high", "low", "close", "volume"]
    for symbol in spec["universe"]:
        digest.update(symbol.encode())
        digest.update(
            pd.util.hash_pandas_object(
                bars_by_symbol[symbol][columns], index=False
            ).values.tobytes()
        )
    return digest.hexdigest()


def _candidate_from_dict(payload: dict) -> CandidateWindowEvaluation:
    converted = dict(payload)
    for key in (
        "eligible_symbols",
        "dates",
        "strategy_daily_returns",
        "benchmark_daily_returns",
        "excess_daily_returns",
    ):
        converted[key] = tuple(converted[key])
    converted["excluded_symbols"] = tuple(
        tuple(item) for item in converted["excluded_symbols"]
    )
    return CandidateWindowEvaluation(**converted)


def _experiment_context(spec: dict, bars_by_symbol: dict[str, pd.DataFrame]):
    universe = spec["universe"]
    missing = [symbol for symbol in universe if bars_by_symbol[symbol].empty]
    if missing:
        raise RuntimeError(f"locked symbols missing data: {', '.join(missing)}")
    partitions = spec["partitions"]
    common_start = partitions["common_history_start"]
    observed_start = max(str(bars_by_symbol[s]["date"].iloc[0]) for s in universe)
    if observed_start != common_start:
        raise RuntimeError(
            f"locked common start is {common_start}, observed {observed_start}"
        )
    common_end = min(str(bars_by_symbol[s]["date"].iloc[-1]) for s in universe)
    calendar = bars_by_symbol[partitions["calendar_symbol"]]
    calendar = calendar[
        (calendar["date"] >= common_start) & (calendar["date"] <= common_end)
    ].reset_index(drop=True)
    development, candidate_tail = partition_candidate_holdout(
        calendar, holdout_bars=partitions["candidate_tail_bars"]
    )
    folds = walk_forward_folds(
        development,
        train_bars=partitions["train_bars"],
        validation_bars=partitions["validation_bars"],
        test_bars=partitions["test_bars"],
        step_bars=partitions["step_bars"],
    )
    return common_end, candidate_tail, folds


def run(spec_path: Path, output_path: Path, *, max_folds: int | None = None) -> dict:
    spec = load_experiment_spec(spec_path)
    bars_by_symbol = {symbol: load_bars(symbol) for symbol in spec["universe"]}
    fingerprint = _fingerprint(spec, bars_by_symbol)
    common_end, candidate_tail, folds = _experiment_context(spec, bars_by_symbol)
    if max_folds is not None:
        folds = folds[:max_folds]
    cache = ROOT / "data" / "research-cache" / spec["experiment_id"] / fingerprint
    candidates = parameter_candidates(spec)
    correction = spec["multiple_testing"]
    selection = spec["selection"]
    result = {
        "experiment_id": spec["experiment_id"],
        "status": "incomplete" if max_folds is not None else "development_complete",
        "claim": "exploratory development evidence; not prospective confirmation",
        "spec_sha256_and_data_fingerprint": fingerprint,
        "common_end": common_end,
        "candidate_tail": asdict(candidate_tail),
        "fold_count": len(folds),
        "folds": [],
    }

    for fold in folds:
        print(f"fold {fold.number}/{folds[-1].number}: validation candidates")
        validations: list[CandidateWindowEvaluation] = []
        for index, params in enumerate(candidates):
            cache_path = cache / f"fold-{fold.number:02d}-candidate-{index:03d}.json"
            if cache_path.exists():
                validation = _candidate_from_dict(json.loads(cache_path.read_text()))
            else:
                validation = evaluate_candidate_window(
                    bars_by_symbol,
                    universe=spec["universe"],
                    strategy_name=spec["strategy"],
                    params=params,
                    training_start=fold.train_start,
                    start=fold.validation_start,
                    end=fold.validation_end,
                    minimum_symbols=selection["minimum_symbols"],
                    costs=spec["costs"],
                )
                _atomic_json(cache_path, asdict(validation))
            validations.append(validation)
            if (index + 1) % 9 == 0:
                print(f"  {index + 1}/{len(candidates)}")

        selected, correction_report = select_validation_candidate(
            validations,
            block_bars=correction["block_bars"],
            resamples=correction["resamples"],
            alpha=correction["alpha"],
            expected_family_size=correction["family_size"],
            seed=17_291 + fold.number * 1_000,
        )
        fold_result = {
            "fold": fold.to_dict(),
            "selection": "cash" if selected is None else selected.candidate,
            "validation": None if selected is None else selected.summary(),
            "multiple_testing": correction_report,
            "test": None,
        }
        if selected is not None:
            test = evaluate_candidate_window(
                bars_by_symbol,
                universe=spec["universe"],
                strategy_name=spec["strategy"],
                params=selected.params,
                training_start=fold.train_start,
                start=fold.test_start,
                end=fold.test_end,
                minimum_symbols=selection["minimum_symbols"],
                costs=spec["costs"],
            )
            fold_result["test"] = asdict(test)
        result["folds"].append(fold_result)
        _atomic_json(output_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--max-folds", type=int, default=None,
        help="engineering smoke run only; output is marked incomplete",
    )
    args = parser.parse_args()
    run(args.spec, args.output, max_folds=args.max_folds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
