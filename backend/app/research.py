"""Guard rails for chronological, out-of-sample research.

This module only defines data partitions and manifests. It deliberately does not
choose parameters or evaluate candidate holdout performance. Existing SPY history
has already been inspected, so a tail partition is a workflow rehearsal rather
than a statistically untouched confirmatory sample.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from .execution import validate_bars


@dataclass(frozen=True)
class CandidateHoldout:
    start: str
    end: str
    bars: int


@dataclass(frozen=True)
class WalkForwardFold:
    number: int
    train_start: str
    train_end: str
    validation_start: str
    validation_end: str
    test_start: str
    test_end: str
    train_bars: int
    validation_bars: int
    test_bars: int

    def to_dict(self) -> dict:
        return asdict(self)


def partition_candidate_holdout(
    bars: pd.DataFrame, *, holdout_bars: int
) -> tuple[pd.DataFrame, CandidateHoldout]:
    """Hide a historical tail for workflow rehearsal, not confirmation."""
    validate_bars(bars)
    if holdout_bars <= 0:
        raise ValueError("holdout_bars must be positive")
    if len(bars) <= holdout_bars:
        raise ValueError("holdout must leave at least one development bar")
    boundary = len(bars) - holdout_bars
    development = bars.iloc[:boundary].reset_index(drop=True).copy()
    reserved = bars.iloc[boundary:]
    return development, CandidateHoldout(
        start=str(reserved["date"].iloc[0]),
        end=str(reserved["date"].iloc[-1]),
        bars=len(reserved),
    )


def walk_forward_folds(
    development: pd.DataFrame,
    *,
    train_bars: int,
    validation_bars: int,
    test_bars: int,
    step_bars: int | None = None,
) -> list[WalkForwardFold]:
    """Build expanding-window folds with strictly later validation/test slices."""
    validate_bars(development)
    sizes = {
        "train_bars": train_bars,
        "validation_bars": validation_bars,
        "test_bars": test_bars,
    }
    if any(value <= 0 for value in sizes.values()):
        raise ValueError("train, validation, and test sizes must be positive")
    step = test_bars if step_bars is None else step_bars
    if step <= 0:
        raise ValueError("step_bars must be positive")

    folds: list[WalkForwardFold] = []
    train_end = train_bars
    number = 1
    while train_end + validation_bars + test_bars <= len(development):
        validation_end = train_end + validation_bars
        test_end = validation_end + test_bars
        folds.append(
            WalkForwardFold(
                number=number,
                train_start=str(development["date"].iloc[0]),
                train_end=str(development["date"].iloc[train_end - 1]),
                validation_start=str(development["date"].iloc[train_end]),
                validation_end=str(development["date"].iloc[validation_end - 1]),
                test_start=str(development["date"].iloc[validation_end]),
                test_end=str(development["date"].iloc[test_end - 1]),
                train_bars=train_end,
                validation_bars=validation_bars,
                test_bars=test_bars,
            )
        )
        train_end += step
        number += 1
    if not folds:
        needed = train_bars + validation_bars + test_bars
        raise ValueError(f"development sample has {len(development)} bars; need at least {needed}")
    return folds


def fold_manifest(folds: list[WalkForwardFold]) -> pd.DataFrame:
    """Small reviewable table; contains boundaries, never performance results."""
    return pd.DataFrame([fold.to_dict() for fold in folds])


def load_experiment_spec(path: str | Path) -> dict:
    """Load and validate a preregistration without evaluating any returns."""
    spec = json.loads(Path(path).read_text())
    required = {
        "experiment_id", "status", "strategy", "universe", "parameter_grid",
        "candidate_count", "costs", "partitions", "multiple_testing",
    }
    missing = required - set(spec)
    if missing:
        raise ValueError(f"experiment spec missing: {', '.join(sorted(missing))}")
    if spec["status"] != "preregistered_no_results":
        raise ValueError("new evaluation requires preregistered_no_results status")
    universe = spec["universe"]
    if not universe or len(universe) != len(set(universe)):
        raise ValueError("universe must be non-empty and unique")
    grid = spec["parameter_grid"]
    if not grid or any(not isinstance(values, list) or not values for values in grid.values()):
        raise ValueError("every parameter grid dimension must be a non-empty list")
    combinations = list(itertools.product(*grid.values()))
    if len(combinations) != spec["candidate_count"]:
        raise ValueError("candidate_count does not match parameter grid")
    correction = spec["multiple_testing"]
    if correction.get("family_size") != len(combinations):
        raise ValueError("multiple-testing family must cover every candidate")
    if correction.get("adjustment") != "Holm family-wise error rate":
        raise ValueError("unsupported multiple-testing adjustment")
    return spec


def parameter_candidates(spec: dict) -> list[dict]:
    """Expand the locked grid in deterministic manifest order."""
    grid = spec["parameter_grid"]
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, preserving the caller's order."""
    if any(not 0 <= value <= 1 for value in p_values):
        raise ValueError("p-values must be between 0 and 1")
    count = len(p_values)
    ranked = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * count
    running = 0.0
    for rank, (original, value) in enumerate(ranked):
        running = max(running, min(1.0, (count - rank) * value))
        adjusted[original] = running
    return adjusted
