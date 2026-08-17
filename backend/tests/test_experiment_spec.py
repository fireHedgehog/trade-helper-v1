"""The preregistered search family must not drift silently."""

from __future__ import annotations

from pathlib import Path

from app.research import (
    circular_block_bootstrap_p_value,
    holm_adjust,
    load_experiment_spec,
    multiple_testing_report,
    parameter_candidates,
)


SPEC = Path(__file__).parents[2] / "research" / "experiments" / "cta-trend-v1.json"


def test_locked_experiment_grid_has_declared_family_size() -> None:
    spec = load_experiment_spec(SPEC)
    candidates = parameter_candidates(spec)
    assert len(candidates) == 54
    assert len(spec["universe"]) == 12
    assert spec["multiple_testing"]["block_bars"] == 20
    assert spec["selection"]["minimum_symbols"] == 8
    assert spec["selection"]["no_survivor"].startswith("hold cash")
    assert spec["confirmation"].startswith("prospective")


def test_holm_adjustment_preserves_order_and_is_monotonic_by_rank() -> None:
    raw = [0.04, 0.001, 0.02]
    adjusted = holm_adjust(raw)
    assert adjusted == [0.04, 0.003, 0.04]
    ranked = sorted(zip(raw, adjusted))
    assert [value for _, value in ranked] == sorted(value for _, value in ranked)


def test_holm_rejects_invalid_p_value() -> None:
    try:
        holm_adjust([1.1])
    except ValueError as exc:
        assert "between 0 and 1" in str(exc)
    else:
        raise AssertionError("invalid p-value must be rejected")


def test_circular_block_bootstrap_is_deterministic() -> None:
    returns = [0.01, 0.02, -0.005, 0.015] * 10
    first = circular_block_bootstrap_p_value(
        returns, block_bars=4, resamples=200, seed=7
    )
    second = circular_block_bootstrap_p_value(
        returns, block_bars=4, resamples=200, seed=7
    )
    assert first == second
    assert 0 < first <= 1


def test_positive_constant_excess_survives_small_family_correction() -> None:
    report = multiple_testing_report(
        {"a": [0.01] * 40, "b": [0.02] * 40},
        block_bars=4,
        resamples=200,
        alpha=0.05,
    )
    assert all(row["reject_zero_excess"] for row in report)
    assert all(row["holm_p_value"] > 0 for row in report)


def test_bootstrap_rejects_invalid_block_size() -> None:
    try:
        circular_block_bootstrap_p_value([0.01, 0.02], block_bars=3)
    except ValueError as exc:
        assert "block_bars" in str(exc)
    else:
        raise AssertionError("oversized block must be rejected")
