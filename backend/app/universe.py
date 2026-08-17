"""Build the trading universe: S&P 500 ∪ Nasdaq-100 ∪ XL sector ETFs.

- Index members come from Wikipedia (free, no API key).
- Cached to `data/universe.csv` (gitignored, regenerable any time).
- Yahoo ticker normalization: "BRK.B" -> "BRK-B".

Usage (from backend/):
    python -m app.universe            # print counts, refresh cache

WARNING (survivorship bias): these are *today's* index members. Historical
backtests on this universe ignore delisted companies and look better than reality.
"""
import io
import sys
from pathlib import Path

import pandas as pd
import requests

from .store import DATA_DIR

CACHE_PATH = DATA_DIR / "universe.csv"

SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
NDX_URL = "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies"

# Wikipedia rejects requests without a browser User-Agent (403).
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# Select Sector SPDR funds — sector rotation tracking.
XL_ETFS = ["XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"]

# Curated prior-probability list: sector/core ETFs + liquid, diverse megacaps.
# Used as the deliberate default sample for confidence and tuning runs — a
# deliberate mix, not a random draw (documented, not hidden).
CURATED_SYMBOLS = (
    ["SPY", "QQQ", "MAGS", "SOXX", "IGV"]
    + XL_ETFS
    + [
        "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "AVGO", "TSLA",
        "JPM", "XOM", "CAT", "UNH", "LLY", "HD", "KO", "V", "MA", "GS",
    ]
)


def _normalize(ticker: str) -> str:
    return ticker.strip().upper().replace(".", "-")


def _tickers_from_wikipedia(url: str, columns: tuple[str, ...]) -> list[str]:
    """Find the first table on the page that has a ticker column and extract it."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    tables = pd.read_html(io.StringIO(response.text))
    for table in tables:
        for column in columns:
            if column in table.columns:
                return [
                    _normalize(value)
                    for value in table[column].astype(str).tolist()
                    if value.strip() and value.strip().lower() != "nan"
                ]
    raise RuntimeError(f"no ticker column {columns} found on {url}")


def get_sp500_tickers() -> list[str]:
    return _tickers_from_wikipedia(SP500_URL, ("Symbol", "Ticker"))


def get_ndx_tickers() -> list[str]:
    return _tickers_from_wikipedia(NDX_URL, ("Ticker", "Symbol"))


def build_universe() -> list[str]:
    sp500 = set(get_sp500_tickers())
    ndx = set(get_ndx_tickers())
    universe = sorted(sp500 | ndx | set(XL_ETFS))
    print(
        f"SP500: {len(sp500)} | NDX: {len(ndx)} | overlap: {len(sp500 & ndx)} "
        f"| XL ETFs: {len(XL_ETFS)} | universe: {len(universe)}"
    )
    return universe


def load_universe(refresh: bool = False) -> list[str]:
    if not refresh and CACHE_PATH.exists():
        return CACHE_PATH.read_text().splitlines()
    universe = build_universe()
    CACHE_PATH.write_text("\n".join(universe) + "\n")
    print(f"universe cached -> {CACHE_PATH}")
    return universe


if __name__ == "__main__":
    try:
        load_universe(refresh=True)
    except Exception as exc:  # network / parse failure
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
