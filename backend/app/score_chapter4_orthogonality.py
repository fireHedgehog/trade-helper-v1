"""Measure pairwise orthogonality across all currently Chapter 4-eligible
signals, per docs/adr/0007-risk-budgeted-ensemble-acceptance.md clause 3:
"Measured, not assumed, orthogonality ... Redundant signals do not expand
effective breadth and must be disclosed as redundant, not silently
included as if independent."

Usage (from backend/):
    python -m app.score_chapter4_orthogonality

Covers all 8 eligible signal-slots scored so far: Wave Pull's TLT and GLD
(score_wave_pull_chapter4.py, 2026-08-20, superseding the TLT-only script's
partial coverage), and the 6 Calendar Day-of-Week assets (DBC, EFA, GLD,
IEF, TLT, XLF). No trade, no cost, no live sizing -- contribution series
are illustrative exposure proxies for correlation measurement only, not
real, costed, executable positions.
"""

from __future__ import annotations

import json
from pathlib import Path

from .research import (
    CHAPTER4_REDUNDANCY_THRESHOLD,
    dow_daily_contribution,
    pairwise_signal_correlation_matrix,
    wave_pull_daily_contribution,
)
from .store import load_bars

ROOT = Path(__file__).parents[2]
OUTPUT = ROOT / "output/research/chapter4-eligibility/orthogonality/score.json"

# The 8 signal-slots eligible as of score_wave_pull_chapter4.py (all 12
# assets scored) and score_calendar_dow_chapter4.py.
WAVE_PULL_ELIGIBLE_SYMBOLS = ["GLD", "TLT"]
DOW_ELIGIBLE_SYMBOLS = ["DBC", "EFA", "GLD", "IEF", "TLT", "XLF"]


def main() -> None:
    contributions = {}

    for symbol in WAVE_PULL_ELIGIBLE_SYMBOLS:
        bars = load_bars(symbol)
        closes = bars["close"].to_numpy(dtype=float)
        dates = bars["date"]
        contributions[f"wave_pull_{symbol}"] = wave_pull_daily_contribution(closes, dates)

    for symbol in DOW_ELIGIBLE_SYMBOLS:
        bars = load_bars(symbol)
        closes = bars["close"].to_numpy(dtype=float)
        dates = bars["date"]
        contributions[f"dow_{symbol}"] = dow_daily_contribution(closes, dates)

    result = pairwise_signal_correlation_matrix(contributions)

    # Flatten the matrix into a readable, ordered pair list alongside the
    # raw dict, for a human scanning the JSON without reconstructing pairs.
    names = list(contributions)
    pair_list = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            pair_list.append({
                "pair": [a, b],
                "correlation": result["matrix"][a][b],
                "redundant": (
                    result["matrix"][a][b] is not None
                    and abs(result["matrix"][a][b]) >= CHAPTER4_REDUNDANCY_THRESHOLD
                ),
            })

    independent_count = len(names) - len({p for r in result["redundant_pairs"] for p in r["pair"]})

    report = {
        "signals_scored": names,
        "signal_count": len(names),
        "redundancy_threshold": CHAPTER4_REDUNDANCY_THRESHOLD,
        "pairwise_correlations": pair_list,
        "redundant_pairs": result["redundant_pairs"],
        "redundant_pair_count": len(result["redundant_pairs"]),
        "reading": (
            f"{len(names)} signal-slots scored eligible by Chapter 4 so far. "
            f"{len(result['redundant_pairs'])} pair(s) flagged as materially "
            f"redundant (|correlation| >= {CHAPTER4_REDUNDANCY_THRESHOLD}) -- "
            "these do not each count as independent breadth toward a future "
            "minimum-breadth floor, per ADR 0007 clause 3. This score does "
            "not itself authorize an ensemble; it is the measurement that "
            "clause 3 requires before one could be built honestly."
        ),
        "disclosed_limitations": [
            "Contribution series are illustrative exposure proxies (asset "
            "return during Wave Pull's holding window; negative asset return "
            "on Monday for Day-of-Week) for correlation measurement only -- "
            "not real, costed, executable positions.",
            "Correlation is computed pairwise over each pair's own "
            "overlapping date range, not a single shared calendar across all "
            "signals -- DBC's shorter history means its pairs have less "
            "overlap than, e.g., TLT-vs-TLT-based pairs.",
            "0.5 is a disclosed, locked rule-of-thumb threshold, not derived "
            "from this project's own data -- treat the raw correlation "
            "values as the primary evidence, the redundant/not-redundant "
            "label as one reasonable cut of it.",
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
