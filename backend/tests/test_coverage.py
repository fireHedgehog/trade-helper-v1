"""Scans must disclose missing and failed symbols instead of silently skipping."""

from __future__ import annotations

import pandas as pd

from app import confidence, signals


def test_scan_reports_processed_missing_and_failed(
    research_bars: pd.DataFrame, monkeypatch
) -> None:
    invalid = research_bars.copy()
    invalid.loc[10, "high"] = 0

    def fake_load(symbol: str) -> pd.DataFrame:
        return {
            "GOOD": research_bars,
            "BAD": invalid,
            "MISSING": pd.DataFrame(),
        }[symbol]

    monkeypatch.setattr(signals, "load_bars", fake_load)
    result = signals.scan("CTA Trend", ["GOOD", "BAD", "MISSING"])

    assert result["coverage"]["requested"] == 3
    assert result["coverage"]["processed"] == 1
    assert result["coverage"]["missing"] == ["MISSING"]
    assert result["coverage"]["failed"][0]["symbol"] == "BAD"
    assert result["coverage"]["failed"][0]["type"] == "ValueError"


def test_confidence_symbol_resolution_discloses_missing(monkeypatch) -> None:
    monkeypatch.setattr(confidence, "list_symbols", lambda: ["SPY", "QQQ"])
    chosen, missing = confidence._resolve_symbols(["SPY", "NOPE", "QQQ"])
    assert chosen == ["SPY", "QQQ"]
    assert missing == ["NOPE"]
