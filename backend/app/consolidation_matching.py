"""Pre-event-only matching for consolidation feasibility.

No function in this module reads a row after the candidate date.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .consolidation_feasibility import StructuralEvent
from .rules import atr


FEATURES = (
    "return_60",
    "atr14_over_close",
    "realized_volatility_60",
    "spy_close_over_sma200",
    "calendar_month_sin",
    "calendar_month_cos",
)


@dataclass(frozen=True)
class EventMatch:
    symbol: str
    event_date: str
    event_features: tuple[float, ...]
    control_dates: tuple[str, ...]
    control_distances: tuple[float, ...]
    same_year_candidates: int
    event_exclusion_candidates: int
    caliper_candidates: int

    @property
    def matched(self) -> bool:
        return len(self.control_dates) >= 3


def pre_event_feature_frame(bars: pd.DataFrame, spy: pd.DataFrame) -> pd.DataFrame:
    frame = bars.reset_index(drop=True).copy()
    close = frame["close"].astype(float)
    log_returns = np.log(close).diff()
    frame["return_60"] = close / close.shift(60) - 1.0
    frame["atr14_over_close"] = atr(frame, 14) / close
    frame["realized_volatility_60"] = log_returns.rolling(60).std(ddof=1)
    spy_frame = spy[["date", "close"]].copy()
    spy_frame["spy_close_over_sma200"] = (
        spy_frame["close"].astype(float)
        / spy_frame["close"].astype(float).rolling(200).mean()
    )
    frame = frame.merge(
        spy_frame[["date", "spy_close_over_sma200"]], on="date", how="left"
    )
    month = pd.to_datetime(frame["date"]).dt.month.astype(float)
    angle = 2.0 * np.pi * (month - 1.0) / 12.0
    frame["calendar_month_sin"] = np.sin(angle)
    frame["calendar_month_cos"] = np.cos(angle)
    return frame


def match_events(
    bars_by_symbol: dict[str, pd.DataFrame],
    events_by_symbol: dict[str, tuple[StructuralEvent, ...]],
    *,
    matching_spec: dict,
) -> tuple[EventMatch, ...]:
    spy = bars_by_symbol["SPY"]
    features = {
        symbol: pre_event_feature_frame(bars, spy)
        for symbol, bars in bars_by_symbol.items()
    }
    pooled = pd.concat(
        [frame[list(FEATURES)] for frame in features.values()], ignore_index=True
    ).dropna()
    means = pooled.mean()
    scales = pooled.std(ddof=1).replace(0.0, np.nan)
    if scales.isna().any():
        raise ValueError("matching feature has zero or undefined development variance")
    standardized_pool = (pooled - means) / scales
    covariance_inverse = np.linalg.pinv(
        standardized_pool.cov().to_numpy(dtype=float)
    )
    exclusion = int(matching_spec["event_exclusion_sessions"])
    forward_required = 60
    caliper = float(matching_spec["per_feature_caliper_pooled_sd"])
    maximum = int(matching_spec["controls_per_event_maximum"])
    matches: list[EventMatch] = []

    for symbol, events in events_by_symbol.items():
        frame = features[symbol]
        event_indices = np.asarray([event.event_index for event in events], dtype=int)
        raw_matrix = frame.loc[:, FEATURES].to_numpy(dtype=float)
        z_matrix = (raw_matrix - means.to_numpy(dtype=float)) / scales.to_numpy(dtype=float)
        dates = frame["date"].astype(str).to_numpy()
        years = np.asarray([date[:4] for date in dates])
        indices = np.arange(len(frame))
        finite = np.isfinite(z_matrix).all(axis=1)
        has_forward = indices + forward_required < len(frame)
        far_from_events = np.ones(len(frame), dtype=bool)
        for event_index in event_indices:
            far_from_events &= np.abs(indices - event_index) > exclusion
        for event in events:
            event_values = raw_matrix[event.event_index]
            if not np.isfinite(event_values).all():
                matches.append(EventMatch(symbol, event.event_date, (), (), (), 0, 0, 0))
                continue
            event_z = z_matrix[event.event_index]
            year = event.event_date[:4]
            same_year_mask = finite & has_forward & (years == year)
            exclusion_mask = same_year_mask & far_from_events
            mask = exclusion_mask
            candidate_indices = indices[mask]
            differences = z_matrix[mask] - event_z
            within = np.all(np.abs(differences) <= caliper, axis=1)
            candidate_indices = candidate_indices[within]
            differences = differences[within]
            squared = np.einsum(
                "ij,jk,ik->i", differences, covariance_inverse, differences
            )
            candidates = [
                (float(np.sqrt(max(0.0, distance))), str(dates[index]))
                for index, distance in zip(candidate_indices, squared)
            ]
            candidates.sort(key=lambda item: (item[0], item[1]))
            chosen = candidates[:maximum]
            matches.append(
                EventMatch(
                    symbol=symbol,
                    event_date=event.event_date,
                    event_features=tuple(float(value) for value in event_values),
                    control_dates=tuple(date for _, date in chosen),
                    control_distances=tuple(distance for distance, _ in chosen),
                    same_year_candidates=int(same_year_mask.sum()),
                    event_exclusion_candidates=int(exclusion_mask.sum()),
                    caliper_candidates=len(candidates),
                )
            )
    return tuple(matches)
