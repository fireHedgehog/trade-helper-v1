import numpy as np
import pandas as pd

from app.consolidation_feasibility import StructuralEvent
from app.consolidation_matching import FEATURES, match_events, pre_event_feature_frame


def bars(periods: int = 800, *, phase: float = 0.0) -> pd.DataFrame:
    index = np.arange(periods, dtype=float)
    close = 100 + 0.01 * index + 2 * np.sin(index / 20 + phase)
    return pd.DataFrame(
        {
            "date": pd.bdate_range("2006-01-02", periods=periods).strftime("%Y-%m-%d"),
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": 1_000_000,
        }
    )


def event(symbol: str, frame: pd.DataFrame, index: int) -> StructuralEvent:
    return StructuralEvent(
        symbol=symbol,
        event_index=index,
        event_date=str(frame.loc[index, "date"]),
        variant_ids=("v",),
        zone_completion_dates=(str(frame.loc[index - 5, "date"]),),
        supports=(100.0,),
        resistances=(105.0,),
        zone_atrs=(2.0,),
    )


def test_pre_event_features_do_not_change_when_future_prices_change() -> None:
    frame = bars()
    original = pre_event_feature_frame(frame, frame)
    changed = frame.copy()
    changed.loc[501:, ["open", "high", "low", "close"]] *= 4
    rerun = pre_event_feature_frame(changed, changed)
    np.testing.assert_allclose(
        original.loc[500, list(FEATURES)].astype(float),
        rerun.loc[500, list(FEATURES)].astype(float),
    )


def test_matching_excludes_dates_near_any_real_event() -> None:
    spy = bars()
    selected = event("SPY", spy, 500)
    result = match_events(
        {"SPY": spy},
        {"SPY": (selected,)},
        matching_spec={
            "event_exclusion_sessions": 60,
            "per_feature_caliper_pooled_sd": 2.0,
            "controls_per_event_maximum": 5,
        },
    )[0]
    date_to_index = {date: index for index, date in enumerate(spy["date"])}
    assert result.control_dates
    assert all(abs(date_to_index[date] - 500) > 60 for date in result.control_dates)
    assert len(result.control_dates) == len(set(result.control_dates))
