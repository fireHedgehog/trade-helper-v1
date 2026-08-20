"""Bounded exploration: does an ICSA (initial jobless claims) trend
inflection lead a UNRATE (unemployment rate) Sahm Rule trigger?

Usage (from backend/):
    python -m app.explore_claims_unrate_lead_lag

Implements the bounded-exploration stage of
docs/research-hypotheses/labor-market-claims-lead-lag-v1.md. This is NOT a
Stage 9A experiment: no lock, no data fingerprint, no
material_and_consistent/not_material_or_not_consistent/invalid decision
vocabulary. Final-revised FRED data only (ICSA, UNRATE), already stored
locally -- no new fetch, no FRED_API_KEY required. Per the operationalization
record's own information-set field, this cannot authorize a trading
candidate; it only characterizes whether the underlying macro relationship
is worth taking further.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .store import load_bars

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "output/research/labor-market-claims-lead-lag-v1/exploration-report.json"

ICSA_MA_WEEKS = 4
ICSA_YOY_LOOKBACK_WEEKS = 52
ICSA_SUSTAIN_WEEKS = 4
UNRATE_MA_MONTHS = 3
UNRATE_LOOKBACK_MONTHS = 12
SAHM_THRESHOLD_PP = 0.50
FORWARD_MATCH_MONTHS = 24


def _load_series(symbol: str) -> pd.Series:
    bars = load_bars(symbol)
    bars["date"] = pd.to_datetime(bars["date"])
    return pd.Series(bars["close"].to_numpy(dtype=float), index=bars["date"]).sort_index()


def icsa_inflections(icsa: pd.Series) -> list[pd.Timestamp]:
    ma4 = icsa.rolling(ICSA_MA_WEEKS).mean()
    yoy = ma4.pct_change(ICSA_YOY_LOOKBACK_WEEKS) * 100.0
    positive = yoy > 0.0
    inflections = []
    for i in range(len(positive)):
        if not positive.iloc[i]:
            continue
        if i > 0 and positive.iloc[i - 1]:
            continue  # not the first positive week of a run
        window = positive.iloc[i : i + ICSA_SUSTAIN_WEEKS]
        if len(window) == ICSA_SUSTAIN_WEEKS and window.all():
            inflections.append(positive.index[i])
    return inflections


def sahm_triggers(unrate: pd.Series) -> list[pd.Timestamp]:
    ma3 = unrate.rolling(UNRATE_MA_MONTHS).mean()
    trailing_low = ma3.rolling(UNRATE_LOOKBACK_MONTHS).min()
    gap = ma3 - trailing_low
    triggered = gap >= SAHM_THRESHOLD_PP
    triggers = []
    for i in range(len(triggered)):
        if triggered.iloc[i] and not (i > 0 and triggered.iloc[i - 1]):
            triggers.append(triggered.index[i])
    return triggers


def pair_lead_times(icsa_inflect: list[pd.Timestamp], sahm_trig: list[pd.Timestamp]) -> list[dict]:
    results = []
    for inflect_date in icsa_inflect:
        window_end = inflect_date + pd.DateOffset(months=FORWARD_MATCH_MONTHS)
        candidates = [t for t in sahm_trig if inflect_date <= t <= window_end]
        if candidates:
            match = min(candidates)
            lead_weeks = (match - inflect_date).days / 7.0
            results.append({
                "icsa_inflection": str(inflect_date.date()),
                "sahm_trigger": str(match.date()),
                "lead_weeks": round(lead_weeks, 1),
                "miss": False,
            })
        else:
            results.append({
                "icsa_inflection": str(inflect_date.date()),
                "sahm_trigger": None,
                "lead_weeks": None,
                "miss": True,
            })
    return results


def main() -> None:
    icsa = _load_series("ICSA")
    unrate = _load_series("UNRATE")

    icsa_inflect = icsa_inflections(icsa)
    sahm_trig = sahm_triggers(unrate)
    pairs = pair_lead_times(icsa_inflect, sahm_trig)

    leads = [p["lead_weeks"] for p in pairs if not p["miss"]]
    report = {
        "icsa_range": [str(icsa.index.min().date()), str(icsa.index.max().date())],
        "unrate_range": [str(unrate.index.min().date()), str(unrate.index.max().date())],
        "icsa_inflection_count": len(icsa_inflect),
        "sahm_trigger_count": len(sahm_trig),
        "pairs": pairs,
        "lead_weeks_summary": {
            "matched_count": len(leads),
            "miss_count": sum(1 for p in pairs if p["miss"]),
            "median_lead_weeks": sorted(leads)[len(leads) // 2] if leads else None,
            "min_lead_weeks": min(leads) if leads else None,
            "max_lead_weeks": max(leads) if leads else None,
            "negative_or_zero_lead_count": sum(1 for w in leads if w <= 0),
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
