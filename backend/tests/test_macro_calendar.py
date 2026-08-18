"""Macro calendar must expose availability limits, never equity direction."""

from __future__ import annotations

import pandas as pd

from app import calendar


def test_macro_events_are_display_only_without_equity_read(monkeypatch) -> None:
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

    assert "read" not in cpi
    assert cpi["signal_eligible"] is False
    assert cpi["next"]["canonical_release_datetime"] is None
    assert cpi["next"]["forecast_history_available"] is False
    assert cpi["last"]["release_datetime"] is None
    assert cpi["last"]["point_in_time"] is False
    assert cpi["last"]["revision_status"] == "final_revised_current_FRED"
