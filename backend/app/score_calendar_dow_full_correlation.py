"""Full pairwise correlation matrix across all 12 Calendar Day-of-Week
universe assets -- winners and non-winners alike, unlike
score_chapter4_orthogonality.py, which only covers the 6 assets that already
scored eligible.

Usage (from backend/):
    python -m app.score_calendar_dow_full_correlation

Motivated by a gap an adversarial verification pass flagged in the Chapter 4
`6/12` breadth result: the 3 correlated pairs already measured
(`dow_IEF`/`dow_TLT` r=0.92, `dow_EFA`/`dow_XLF` r=0.81, `dow_DBC`/`dow_EFA`
r=0.51) were measured only among the 6 winners (15 of the 66 possible pairs)
-- the other 51 pairs, involving any of the 6 non-winning assets, were never
checked. This fills that gap directly. It is a supplementary, descriptive
measurement only; the significance question itself (is `6/12` distinguishable
from chance given real correlation) is answered separately by
`run_calendar_dow_breadth_significance.py`'s correlation-aware joint null,
not by this correlation matrix alone.

No trade, no cost, no live sizing.
"""

from __future__ import annotations

import json
from pathlib import Path

from .research import CHAPTER4_REDUNDANCY_THRESHOLD, dow_daily_contribution, pairwise_signal_correlation_matrix
from .run_calendar_day_of_week import SPEC_PATH, validate_locked_spec
from .store import load_bars

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "output/research/chapter4-eligibility/calendar-day-of-week/full-correlation-matrix.json"

DOW_ELIGIBLE_SYMBOLS = {"DBC", "EFA", "GLD", "IEF", "TLT", "XLF"}


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    universe = sorted(spec["universe"])
    contributions = {}
    for symbol in universe:
        bars = load_bars(symbol)
        closes = bars["close"].to_numpy(dtype=float)
        dates = bars["date"]
        contributions[symbol] = dow_daily_contribution(closes, dates)

    result = pairwise_signal_correlation_matrix(contributions)

    pair_list = []
    for i, a in enumerate(universe):
        for b in universe[i + 1 :]:
            corr = result["matrix"][a][b]
            pair_list.append({
                "pair": [a, b],
                "correlation": corr,
                "redundant": corr is not None and abs(corr) >= CHAPTER4_REDUNDANCY_THRESHOLD,
                "both_winners": a in DOW_ELIGIBLE_SYMBOLS and b in DOW_ELIGIBLE_SYMBOLS,
            })

    winner_pairs = [p for p in pair_list if p["both_winners"]]
    non_winner_touching_pairs = [p for p in pair_list if not p["both_winners"]]
    redundant_pairs = [p for p in pair_list if p["redundant"]]
    redundant_non_winner_touching = [p for p in redundant_pairs if not p["both_winners"]]

    report = {
        "universe": universe,
        "eligible_symbols": sorted(DOW_ELIGIBLE_SYMBOLS),
        "total_pairs": len(pair_list),
        "winner_vs_winner_pairs": len(winner_pairs),
        "pairs_touching_a_non_winner": len(non_winner_touching_pairs),
        "redundancy_threshold": CHAPTER4_REDUNDANCY_THRESHOLD,
        "pairwise_correlations": pair_list,
        "redundant_pair_count": len(redundant_pairs),
        "redundant_pairs_touching_a_non_winner": redundant_non_winner_touching,
        "reading": (
            f"{len(pair_list)} total pairs across all {len(universe)} Day-of-Week assets "
            f"({len(winner_pairs)} winner-vs-winner, {len(non_winner_touching_pairs)} touching "
            f"at least one non-winning asset). {len(redundant_pairs)} flagged redundant overall"
            f"; {len(redundant_non_winner_touching)} of those touch a non-winning asset -- "
            + (
                "meaning the previously-measured winner-only view (3 redundant pairs among 15) "
                "understated total redundancy in the universe, though this does not by itself "
                "change how many of the 6 winners' hits are independent of each other."
                if redundant_non_winner_touching
                else "meaning the 3 redundant pairs already known among the 6 winners are the "
                "only material redundancy anywhere in the full 12-asset universe -- no additional "
                "hidden correlation was found by checking the other 51 pairs."
            )
        ),
        "disclosed_limitations": [
            "This is a descriptive correlation measurement, not a significance test. Whether "
            "6/12 is distinguishable from chance given this correlation structure is answered "
            "separately by run_calendar_dow_breadth_significance.py's correlation-aware joint "
            "null, which resamples the real return data directly rather than relying on a "
            "design-effect approximation from this matrix.",
            "dow_daily_contribution series are computed on each asset's own full history; "
            "correlation for any pair is over that pair's own overlapping date range only, not "
            "one shared calendar across all 12 (DBC's shorter history means its pairs have less "
            "overlap), matching score_chapter4_orthogonality.py's existing convention.",
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
