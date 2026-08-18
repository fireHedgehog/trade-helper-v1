from types import SimpleNamespace

import pandas as pd

from app import workspace


def test_snapshot_preserves_watch_order_and_last_exit(monkeypatch) -> None:
    closes = {"QQQ": 20.0, "SPY": 30.0, "IWM": 10.0}

    def fake_bars(symbol):
        return pd.DataFrame(
            {
                "date": ["2024-01-02", "2024-01-03"],
                "open": [closes[symbol] - 1, closes[symbol]],
                "high": [closes[symbol], closes[symbol] + 1],
                "low": [closes[symbol] - 2, closes[symbol] - 1],
                "close": [closes[symbol] - 1, closes[symbol]],
                "volume": [100, 100],
            }
        )

    def fake_signal(bars, _strategy, _params):
        return {
            "note": "flat",
            "rank": float(bars["close"].iloc[-1]),
            "rank_note": "fixture rank",
        }

    def fake_replay(bars, _strategy, _params):
        is_spy = bars["close"].iloc[-1] == closes["SPY"]
        is_iwm = bars["close"].iloc[-1] == closes["IWM"]
        last_exit = (
            {
                "exit_date": "2024-01-03",
                "exit_price": 30.0,
                "exit_reason": "stop",
                "return_pct": -1.5,
            }
            if is_spy
            else None
        )
        return SimpleNamespace(
            position=SimpleNamespace(
                state="entry_pending" if is_iwm else "flat",
                entry_date=None,
                entry_price=None,
                stop=None,
            ),
            last_exit=last_exit,
            last_event="exit" if is_spy else "none",
            trades=(
                [{"entry_date": "2023-12-01", "entry_price": 28.0}]
                if is_spy
                else []
            ),
        )

    monkeypatch.setattr(workspace.store, "load_bars", fake_bars)
    monkeypatch.setattr(workspace, "compute_signal", fake_signal)
    monkeypatch.setattr(workspace, "simulate", fake_replay)

    result = workspace.create_strategy_snapshot(
        "CTA Trend",
        {},
        watch_symbols=["QQQ", "SPY"],
        discovery_symbols=["IWM"],
    )

    assert [row["symbol"] for row in result["watchlist"]] == ["QQQ", "SPY"]
    assert result["watchlist"][1]["status"] == "exited"
    assert result["watchlist"][1]["last_exit"]["reason"] == "stop"
    assert result["watchlist"][1]["last_exit"]["date"] == "2024-01-03"
    assert result["watchlist"][1]["last_entry"] == {
        "date": "2023-12-01",
        "price": 28.0,
    }
    assert [row["symbol"] for row in result["ranked"]] == ["SPY", "QQQ", "IWM"]
    assert [row["symbol"] for row in result["entry_candidates"]] == ["IWM"]
    assert result["coverage"] == {
        "requested": 3,
        "processed": 3,
        "missing": [],
        "failed": [],
    }
