"""GICS sector/sub-industry classification -- current snapshot, not point-in-time.

Free, same Wikipedia S&P 500 table `app.universe` already scrapes for the
ticker list. Answers "which sector is this stock in today", not "what sector
was it in on some historical date" -- a company's GICS classification can be
reassigned over time and no history of that exists here, the same
disclosed-limitation posture as `app.universe`'s own today's-constituents
scope. Built specifically to test a group-level (sector-vs-sector) relative-
strength/rotation hypothesis (CS-07/CS-08 shape), distinct from CS-01's
flat, ungrouped individual-stock pooling -- see
docs/brainstorm/2026-08-20-cross-sectional-experiment-ideas.md.

Usage (from backend/):
    python -m app.universe_sectors
"""
import datetime as dt
import sys

from .store import upsert_equity_sectors
from .universe import get_sp500_sectors


def main() -> int:
    try:
        df = get_sp500_sectors()
    except Exception as exc:  # network / parse failure
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    as_of = dt.date.today().isoformat()
    upsert_equity_sectors(df, as_of)
    sectors = sorted(df["gics_sector"].unique())
    print(
        f"ingested {len(df)} symbols across {len(sectors)} GICS sectors "
        f"(as of {as_of}): {', '.join(sectors)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
