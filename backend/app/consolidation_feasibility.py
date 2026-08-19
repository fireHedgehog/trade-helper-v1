"""Locked consolidation-support feasibility primitives.

This module emits only pre-event structural records.  It deliberately contains no
forward-return, drawdown, P&L, ranking, or trading-rule calculation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product

import numpy as np
import pandas as pd

from .execution import validate_bars
from .rules import atr


@dataclass(frozen=True)
class DetectorVariant:
    window: int
    maximum_zone_width_ratio: float
    maximum_volatility_ratio: float

    @property
    def variant_id(self) -> str:
        return (
            f"w{self.window}-width{self.maximum_zone_width_ratio:.2f}-"
            f"vol{self.maximum_volatility_ratio:.2f}"
        )


@dataclass(frozen=True)
class Zone:
    symbol: str
    variant_id: str
    window: int
    completion_index: int
    completion_date: str
    support: float
    resistance: float
    atr: float
    width_ratio: float
    volatility_ratio: float
    lower_touches: tuple[str, ...]
    upper_touches: tuple[str, ...]


@dataclass(frozen=True)
class StructuralEvent:
    symbol: str
    event_index: int
    event_date: str
    variant_ids: tuple[str, ...]
    zone_completion_dates: tuple[str, ...]
    supports: tuple[float, ...]
    resistances: tuple[float, ...]
    zone_atrs: tuple[float, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def variants_from_spec(spec: dict) -> tuple[DetectorVariant, ...]:
    detector = spec["detector"]
    variants = tuple(
        DetectorVariant(int(window), float(width), float(volatility))
        for window, width, volatility in product(
            detector["windows"],
            detector["maximum_zone_width_ratios"],
            detector["maximum_realized_volatility_ratios"],
        )
    )
    if len(variants) != int(detector["variant_count"]):
        raise ValueError("detector Cartesian product does not match variant_count")
    return variants


def _separated_touch_dates(
    window: pd.DataFrame,
    *,
    boundary: float,
    tolerance: float,
    separation: int,
) -> tuple[str, ...]:
    candidates = [
        index
        for index, row in window.iterrows()
        if float(row["high"]) >= boundary - tolerance
        and float(row["low"]) <= boundary + tolerance
    ]
    selected: list[int] = []
    for index in candidates:
        if not selected or index - selected[-1] >= separation:
            selected.append(index)
    return tuple(str(window.loc[index, "date"]) for index in selected)


def _rolling_inputs(frame: pd.DataFrame, window: int, detector: dict) -> dict[str, pd.Series]:
    close = frame["close"].astype(float)
    log_returns = np.log(close).diff()
    recent_volatility = log_returns.rolling(window).std(ddof=1)
    return {
        "atr": atr(frame, int(detector["atr_period"])),
        "support": close.rolling(window).quantile(detector["lower_close_quantile"]),
        "resistance": close.rolling(window).quantile(detector["upper_close_quantile"]),
        "median": close.rolling(window).median(),
        "recent_volatility": recent_volatility,
        "prior_volatility": recent_volatility.shift(window),
    }


def detect_zones(
    bars: pd.DataFrame,
    *,
    symbol: str,
    variant: DetectorVariant,
    detector: dict,
    rolling: dict[str, pd.Series] | None = None,
) -> tuple[Zone, ...]:
    """Detect locked zones using bars available through each completion close."""
    validate_bars(bars)
    frame = bars.reset_index(drop=True).copy()
    window = variant.window
    inputs = rolling or _rolling_inputs(frame, window, detector)
    next_allowed = 2 * window - 1
    zones: list[Zone] = []

    for index in range(2 * window - 1, len(frame)):
        if index < next_allowed:
            continue
        current_atr = float(inputs["atr"].iloc[index])
        if not np.isfinite(current_atr) or current_atr <= 0:
            continue
        recent = frame.iloc[index - window + 1 : index + 1]
        prior_vol = float(inputs["prior_volatility"].iloc[index])
        recent_vol = float(inputs["recent_volatility"].iloc[index])
        if not np.isfinite(prior_vol) or prior_vol <= 0 or not np.isfinite(recent_vol):
            continue
        support = float(inputs["support"].iloc[index])
        resistance = float(inputs["resistance"].iloc[index])
        median_close = float(inputs["median"].iloc[index])
        if not all(np.isfinite(value) and value > 0 for value in (support, resistance, median_close)):
            continue
        width_ratio = (resistance - support) / median_close
        volatility_ratio = recent_vol / prior_vol
        if width_ratio > variant.maximum_zone_width_ratio:
            continue
        if volatility_ratio > variant.maximum_volatility_ratio:
            continue
        containment_low = support - detector["containment_atr_buffer"] * current_atr
        containment_high = resistance + detector["containment_atr_buffer"] * current_atr
        contained = recent["close"].between(containment_low, containment_high).mean()
        if contained < detector["minimum_close_containment_fraction"]:
            continue
        maximum_buffer = detector["maximum_close_excursion_atr"] * current_atr
        if ((recent["close"] < support - maximum_buffer) | (recent["close"] > resistance + maximum_buffer)).any():
            continue
        tolerance = detector["boundary_touch_atr_tolerance"] * current_atr
        separation = int(detector["minimum_same_side_touch_separation_sessions"])
        lower = _separated_touch_dates(
            recent, boundary=support, tolerance=tolerance, separation=separation
        )
        upper = _separated_touch_dates(
            recent, boundary=resistance, tolerance=tolerance, separation=separation
        )
        minimum = int(detector["minimum_touches_per_boundary"])
        if len(lower) < minimum or len(upper) < minimum:
            continue
        zones.append(
            Zone(
                symbol=symbol,
                variant_id=variant.variant_id,
                window=window,
                completion_index=index,
                completion_date=str(frame.loc[index, "date"]),
                support=support,
                resistance=resistance,
                atr=current_atr,
                width_ratio=width_ratio,
                volatility_ratio=volatility_ratio,
                lower_touches=lower,
                upper_touches=upper,
            )
        )
        next_allowed = index + window
    return tuple(zones)


def detect_variant_events(
    bars: pd.DataFrame,
    *,
    zones: tuple[Zone, ...],
    event_spec: dict,
) -> tuple[tuple[int, Zone], ...]:
    """Return first locked support recovery per zone, with variant cooldown."""
    frame = bars.reset_index(drop=True)
    last_event = -10**9
    found: list[tuple[int, Zone]] = []
    for zone in zones:
        start = zone.completion_index + int(event_spec["search_start_sessions_after_zone"])
        end = min(
            zone.completion_index + int(event_spec["search_end_sessions_after_zone"]),
            len(frame) - 1,
        )
        if start <= last_event + int(event_spec["event_cooldown_sessions"]):
            start = last_event + int(event_spec["event_cooldown_sessions"]) + 1
        prior_failed = False
        for index in range(zone.completion_index + 1, end + 1):
            close = float(frame.loc[index, "close"])
            if close < zone.support + event_spec["prior_failure_close_atr_buffer"] * zone.atr:
                prior_failed = True
            if index < start or prior_failed:
                continue
            if index + int(event_spec["forward_sessions_required"]) >= len(frame):
                continue
            low = float(frame.loc[index, "low"])
            if (
                low <= zone.support + event_spec["low_to_support_atr_buffer"] * zone.atr
                and close >= zone.support
            ):
                found.append((index, zone))
                last_event = index
                break
    return tuple(found)


def structural_events(
    bars: pd.DataFrame,
    *,
    symbol: str,
    spec: dict,
) -> tuple[StructuralEvent, ...]:
    """Detect and deduplicate economic events across all locked variants."""
    frame = bars.reset_index(drop=True)
    by_index: dict[int, list[Zone]] = {}
    rolling_by_window = {
        window: _rolling_inputs(frame, window, spec["detector"])
        for window in spec["detector"]["windows"]
    }
    for variant in variants_from_spec(spec):
        zones = detect_zones(
            frame,
            symbol=symbol,
            variant=variant,
            detector=spec["detector"],
            rolling=rolling_by_window[variant.window],
        )
        for index, zone in detect_variant_events(
            frame, zones=zones, event_spec=spec["event"]
        ):
            by_index.setdefault(index, []).append(zone)
    return tuple(
        StructuralEvent(
            symbol=symbol,
            event_index=index,
            event_date=str(frame.loc[index, "date"]),
            variant_ids=tuple(sorted(zone.variant_id for zone in zones)),
            zone_completion_dates=tuple(zone.completion_date for zone in zones),
            supports=tuple(zone.support for zone in zones),
            resistances=tuple(zone.resistance for zone in zones),
            zone_atrs=tuple(zone.atr for zone in zones),
        )
        for index, zones in sorted(by_index.items())
    )
