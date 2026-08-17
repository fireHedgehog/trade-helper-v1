"""The preregistered search family must not drift silently."""

from __future__ import annotations

from pathlib import Path

from app.research import holm_adjust, load_experiment_spec, parameter_candidates


SPEC = Path(__file__).parents[2] / "research" / "experiments" / "cta-trend-v1.json"


def test_locked_experiment_grid_has_declared_family_size() -> None:
    spec = load_experiment_spec(SPEC)
    candidates = parameter_candidates(spec)
    assert len(candidates) == 54
    assert len(spec["universe"]) == 12
    assert spec["multiple_testing"]["block_bars"] == 20
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
