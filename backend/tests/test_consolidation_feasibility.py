import json
from pathlib import Path

import numpy as np
import pandas as pd

from app import consolidation_feasibility as feasibility
from app.consolidation_feasibility import (
    DetectorVariant,
    Zone,
    detect_variant_events,
    detect_zones,
    structural_events,
    variants_from_spec,
)
from app.run_consolidation_feasibility import (
    SPEC_SHA256,
    canonical_spec_sha256,
    development_bars,
    development_data_sha256,
    finalize_existing,
    validate_locked_inputs,
)
from app import run_consolidation_feasibility as runner


ROOT = Path(__file__).parents[2]
SPEC = json.loads(
    (ROOT / "research/experiments/consolidation-support-feasibility-v1.json").read_text()
)


def bars_from_close(close: list[float]) -> pd.DataFrame:
    dates = pd.date_range("2006-02-06", periods=len(close), freq="B").strftime("%Y-%m-%d")
    values = np.asarray(close, dtype=float)
    return pd.DataFrame(
        {
            "date": dates,
            "open": values,
            "high": values + 1.0,
            "low": values - 1.0,
            "close": values,
            "volume": np.full(len(values), 1_000_000),
        }
    )


def zone_at(index: int = 20, *, variant_id: str = "v") -> Zone:
    return Zone(
        symbol="SPY",
        variant_id=variant_id,
        window=40,
        completion_index=index,
        completion_date="2006-03-06",
        support=100.0,
        resistance=110.0,
        atr=2.0,
        width_ratio=0.1,
        volatility_ratio=0.7,
        lower_touches=("a", "b"),
        upper_touches=("c", "d"),
    )


def test_machine_spec_expands_to_exactly_eight_variants() -> None:
    variants = variants_from_spec(SPEC)
    assert len(variants) == 8
    assert len({variant.variant_id for variant in variants}) == 8


def test_real_locked_spec_and_development_data_reproduce() -> None:
    bars = development_bars(SPEC)
    checks = validate_locked_inputs(SPEC, bars)
    assert canonical_spec_sha256(SPEC) == SPEC_SHA256
    assert development_data_sha256(SPEC, bars) == SPEC["data"]["development_sha256"]
    assert checks["rows"] == 38_976


def test_zone_detection_is_invariant_to_later_bar_values() -> None:
    prior = [100 + (index % 2) * 8 for index in range(80)]
    quiet = [100, 101, 102, 103, 104, 105, 104, 103, 102, 101] * 6
    future = [103.0] * 80
    bars = bars_from_close(prior + quiet + future)
    variant = DetectorVariant(40, 0.12, 1.0)
    original = detect_zones(
        bars, symbol="SPY", variant=variant, detector=SPEC["detector"]
    )
    assert original
    cutoff = original[0].completion_index
    changed = bars.copy()
    changed.loc[cutoff + 1 :, ["open", "high", "low", "close"]] *= 3
    rerun = detect_zones(
        changed.iloc[: cutoff + 1],
        symbol="SPY",
        variant=variant,
        detector=SPEC["detector"],
    )
    assert rerun[0] == original[0]


def test_event_uses_recovery_close_and_requires_forward_availability() -> None:
    bars = bars_from_close([105.0] * 100)
    bars.loc[25, ["low", "close"]] = [100.2, 100.5]
    found = detect_variant_events(
        bars, zones=(zone_at(),), event_spec=SPEC["event"]
    )
    assert [(index, zone.variant_id) for index, zone in found] == [(25, "v")]

    too_short = bars.iloc[:70]
    assert detect_variant_events(
        too_short, zones=(zone_at(),), event_spec=SPEC["event"]
    ) == ()


def test_close_below_failure_buffer_invalidates_later_recovery() -> None:
    bars = bars_from_close([105.0] * 100)
    bars.loc[23, ["low", "close"]] = [98.0, 98.5]
    bars.loc[25, ["low", "close"]] = [100.0, 101.0]
    assert detect_variant_events(
        bars, zones=(zone_at(),), event_spec=SPEC["event"]
    ) == ()


def test_events_are_deduplicated_across_variants(monkeypatch) -> None:
    bars = bars_from_close([105.0] * 100)

    def fake_zones(_bars, *, symbol, variant, detector, rolling=None):
        return (zone_at(variant_id=variant.variant_id),)

    def fake_events(_bars, *, zones, event_spec):
        return ((25, zones[0]),)

    monkeypatch.setattr(feasibility, "detect_zones", fake_zones)
    monkeypatch.setattr(feasibility, "detect_variant_events", fake_events)
    events = structural_events(bars, symbol="SPY", spec=SPEC)
    assert len(events) == 1
    assert events[0].event_date == bars.loc[25, "date"]
    assert len(events[0].variant_ids) == 8
    forbidden = {"forward_return", "drawdown", "pnl", "rank", "signal"}
    assert forbidden.isdisjoint(events[0].to_dict())


def test_finalize_short_circuits_to_not_evaluable_when_matching_fails(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    output = tmp_path / "output/research/consolidation-support-feasibility-v1" / SPEC_SHA256
    output.mkdir(parents=True)
    prevalence = {
        variant.variant_id: 0.01 for variant in variants_from_spec(SPEC)
    }
    (output / "feasibility.json").write_text(
        json.dumps(
            {
                "deduplicated_events": 100,
                "events_by_symbol": {symbol: 9 for symbol in SPEC["universe"]},
                "events_by_year": {str(year): 10 for year in range(2007, 2017)},
                "detector_prevalence_by_variant": prevalence,
                "matching_coverage": 0.0,
                "prospective_power": None,
            }
        )
    )
    checks = {
        "spec_matches": True,
        "data_matches": True,
        "rows_match": True,
        "data_sha256": SPEC["data"]["development_sha256"],
    }
    _, decision = finalize_existing(SPEC, checks)
    assert decision["decision"] == "not_evaluable"
    assert decision["gates"]["prospective_power"] is None
    assert decision["actual_event_forward_outcomes_accessed"] is False
