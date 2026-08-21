"""Macro calendar exposes availability limits; any equity-direction chip must be
a clearly labeled, untested textbook heuristic, never presented as evidence."""

from __future__ import annotations

import pandas as pd

from app import calendar


def test_macro_events_expose_labeled_heuristic_never_bare_equity_claim(monkeypatch) -> None:
    monkeypatch.setattr(
        calendar,
        "_fetch_te_rows",
        lambda: [
            {
                "date": "2026-09-01",
                "time": "08:30 AM",
                "name": "Inflation Rate",
                "actual": "",
                "previous": "2.8%",
                "consensus": "2.7%",
                "forecast": "2.7%",
            }
        ],
    )
    monkeypatch.setattr(
        calendar,
        "load_recent_bars",
        lambda _series, _count: pd.DataFrame(
            {"date": [f"2025-{month:02d}-01" for month in range(1, 13)] + ["2026-01-01", "2026-02-01"],
             "close": list(range(100, 114))}
        ),
    )
    monkeypatch.setattr(calendar.time, "time", lambda: 10_000_000)
    calendar._cache = {"at": 0.0, "events": []}

    events = calendar.macro_events(force=True)
    cpi = next(event for event in events if event["key"] == "cpi")

    # Cooling YoY CPI (change < 0) is conventionally bullish under the Inflation
    # direction (-1), and it must be disclosed as a hypothesis, not a finding.
    assert cpi["heuristic"]["read"] == "bullish"
    assert "not a research finding" in cpi["heuristic"]["basis"]
    assert "not preregistered" in cpi["heuristic"]["adr_0006_status"]
    assert cpi["signal_eligible"] is False
    assert cpi["next"]["canonical_release_datetime"] is None
    assert cpi["next"]["forecast_history_available"] is False
    assert cpi["last"]["release_datetime"] is None
    assert cpi["last"]["point_in_time"] is False
    assert cpi["last"]["revision_status"] == "final_revised_current_FRED"


def test_labor_category_has_no_stable_heuristic_direction() -> None:
    # NFP/unemployment/claims deliberately get no heuristic: "bad news is good
    # news" rate-cut regimes make the sign unstable, so asserting one would be
    # exactly the kind of unfounded claim ADR 0006 forbids.
    assert calendar._heuristic_read("Labor", -5.0) is None
    assert calendar._heuristic_read("Labor", 5.0) is None


def test_zero_change_gets_no_heuristic() -> None:
    assert calendar._heuristic_read("Inflation", 0.0) is None
    assert calendar._heuristic_read("Inflation", None) is None
