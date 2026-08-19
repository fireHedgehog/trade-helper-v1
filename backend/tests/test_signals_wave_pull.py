"""Wave Pull's compute_signal must not crash when impulse_bars exceeds the
available bar history — the audit's L4 finding (IndexError at
impulse_bars >= 59), reachable via the API even though the Strategy Lab UI
slider suggests a max of 30.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.signals import compute_signal


def _bars(n: int) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    close = pd.Series(100.0 + np.arange(n) * 0.5, index=dates)
    return pd.DataFrame(
        {
            "date": dates,
            "open": close - 0.1,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": 1_000_000,
        }
    ).reset_index(drop=True)


def test_wave_pull_does_not_crash_when_impulse_bars_exceeds_history() -> None:
    bars = _bars(60)  # exactly the compute_signal minimum
    result = compute_signal(bars, "Wave Pull", {"impulse_bars": 65})
    assert result is not None
    assert "note" in result


def test_wave_pull_reports_normally_within_history() -> None:
    bars = _bars(100)
    result = compute_signal(bars, "Wave Pull", {"impulse_bars": 8})
    assert result is not None
    assert result["state"] in ("long", "flat")
