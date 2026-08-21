"""Point-in-time S&P 500 membership -- clears the Chapter 2 Tier 4 blocker.

`app.universe` gives today's constituents only -- survivorship-biased,
disclosed in that module's own docstring. This module ingests a real
point-in-time membership history instead: free, MIT-licensed, maintained by
Farrell Aultman (https://github.com/fja05680/sp500), originally sourced from
Andreas Clenow's "Trading Evolved" (1996-2019 base) plus ongoing manual
updates cross-referenced against Wikipedia. Per the
[cross-sectional idea library](../../docs/brainstorm/2026-08-20-cross-sectional-experiment-ideas.md),
clearing this one item unlocks six queued Chapter 2 ideas (CS-01/02/03/04/05/09)
at once -- it does not by itself authorize any of them as a candidate; each
still needs its own hypothesis-engineering note, Stage 9A score, and
preregistration before a real run.

Disclosed limitations, carried forward honestly, not hidden:
- Maintained by hand, bimonthly, not automated -- a real revision lag exists
  between an actual S&P 500 change and this dataset picking it up.
- The maintainer's own README flags the first ~5 years (1996-2000) as
  lower-confidence (487 vs. an expected ~500 names); prefer 2001 onward for
  any real test.
- Ticker spellings for long-delisted names occasionally differ from a live
  provider's convention; normalized the same way `app.universe` does
  ('.' -> '-') but a residual mismatch against `bars` is possible and is
  exactly why any real use should intersect against what `bars` actually
  holds, the same discipline the momentum-feasibility run already used.

Usage (from backend/):
    python -m app.universe_pit          # fetch, ingest, print coverage
"""
import io
import sys

import pandas as pd
import requests

from .store import upsert_universe_membership

SOURCE_URL = "https://raw.githubusercontent.com/fja05680/sp500/master/sp500_ticker_start_end.csv"
INDEX_NAME = "SP500"


def _normalize(ticker: str) -> str:
    return ticker.strip().upper().replace(".", "-")


def fetch_membership() -> pd.DataFrame:
    response = requests.get(SOURCE_URL, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df["symbol"] = df["ticker"].map(_normalize)
    return df[["symbol", "start_date", "end_date"]]


def ingest_membership() -> pd.DataFrame:
    df = fetch_membership()
    upsert_universe_membership(df, INDEX_NAME)
    return df


def main() -> int:
    try:
        df = ingest_membership()
    except Exception as exc:  # network / parse failure
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    current = df["end_date"].isna().sum()
    print(
        f"ingested {len(df)} membership intervals, {df['symbol'].nunique()} "
        f"distinct symbols, {current} currently active"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
