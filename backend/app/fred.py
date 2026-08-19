"""Fetch Treasury yields from FRED (fredgraph CSV — no API key needed).

Usage (from backend/):
    python -m app.fred DGS2 DGS10

Series are stored in the bars table under the series id (values are yields in
%). FRED publishes the real 2Y yield (DGS2), which Yahoo Finance does not offer.
"""
import argparse
import io

import pandas as pd
import requests

from .assets import FRED_MANAGED_SERIES as MANAGED_SERIES
from .store import upsert_bars

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"


def fetch_series(series_id: str) -> pd.DataFrame:
    response = requests.get(URL.format(series_id), timeout=30)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df.columns = ["date", "value"]
    df = df.dropna()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return pd.DataFrame(
        {
            "symbol": series_id,
            "date": df["date"],
            "open": df["value"],
            "high": df["value"],
            "low": df["value"],
            "close": df["value"],
            "volume": 0,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch FRED series into SQLite")
    parser.add_argument("series", nargs="+", default=["DGS2"])
    args = parser.parse_args()
    for series_id in args.series:
        df = fetch_series(series_id)
        upsert_bars(df)
        print(f"{series_id}: {len(df)} rows upserted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
