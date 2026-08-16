"""Daily market-data fetch job: Yahoo Finance -> SQLite.

Usage (from backend/):
    python -m app.fetch                  # default: SPY, full history
    python -m app.fetch SPY GC=F CL=F    # more symbols
    python -m app.fetch SPY --period 5y  # limit history

Idempotent: re-running upserts the same (symbol, date) rows, so it is safe
for a daily cron job or a manual re-fetch.
"""
import argparse
import sys
import time

import pandas as pd
import yfinance as yf

from .store import upsert_bars, row_count
from .universe import load_universe

DEFAULT_SYMBOLS = ["SPY"]
DEFAULT_PERIOD = "max"
RATE_LIMIT_RETRIES = 3
RATE_LIMIT_BACKOFF_S = 30


def fetch_symbol(symbol: str, period: str) -> pd.DataFrame:
    """Pull daily bars for one symbol. auto_adjust=True gives adjusted OHLC."""
    raw = yf.Ticker(symbol).history(period=period, auto_adjust=True)
    if raw is None or raw.empty:
        raise RuntimeError(f"Yahoo returned no data for {symbol}")
    df = raw.reset_index().rename(columns=str.lower)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["symbol"] = symbol
    return df[["symbol", "date", "open", "high", "low", "close", "volume"]]


def fetch_with_retry(symbol: str, period: str) -> pd.DataFrame:
    """Fetch with polite retry/backoff when Yahoo rate-limits us."""
    for attempt in range(1, RATE_LIMIT_RETRIES + 1):
        try:
            return fetch_symbol(symbol, period)
        except Exception as exc:
            message = str(exc)
            rate_limited = "429" in message or "rate limit" in message.lower()
            if attempt == RATE_LIMIT_RETRIES or not rate_limited:
                raise
            wait = RATE_LIMIT_BACKOFF_S * attempt
            print(
                f"  [RETRY {attempt}] {symbol}: rate-limited, waiting {wait}s",
                file=sys.stderr,
            )
            time.sleep(wait)
    raise RuntimeError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch daily bars into SQLite")
    parser.add_argument("symbols", nargs="*", default=DEFAULT_SYMBOLS)
    parser.add_argument("--period", default=DEFAULT_PERIOD)
    parser.add_argument(
        "--universe",
        action="store_true",
        help="fetch the SP500+NDX+XL universe instead of named symbols",
    )
    parser.add_argument(
        "--refresh-universe",
        action="store_true",
        help="rebuild the universe list before fetching",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="seconds between symbols (be polite: 1.0+ for large runs)",
    )
    args = parser.parse_args()

    if args.universe:
        symbols = load_universe(refresh=args.refresh_universe)
        if args.delay == 0.0:
            args.delay = 1.0  # large runs should be polite by default
    else:
        symbols = args.symbols

    failures = 0
    for index, symbol in enumerate(symbols, start=1):
        try:
            df = fetch_with_retry(symbol, args.period)
        except Exception as exc:  # keep going on one bad symbol
            print(
                f"[{index}/{len(symbols)}] [ERROR] {symbol}: {exc}",
                file=sys.stderr,
            )
            failures += 1
            continue
        upsert_bars(df)
        print(
            f"[{index}/{len(symbols)}] {symbol}: {len(df)} rows upserted "
            f"(total: {row_count(symbol)})"
        )
        if args.delay and index < len(symbols):
            time.sleep(args.delay)
    print(f"done: {len(symbols) - failures}/{len(symbols)} symbols OK")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
