"""SQLite storage for daily bars.

Data files live in the repo's `data/` dir (gitignored — data never gets committed).

Schema:
    bars(symbol, date, open, high, low, close, volume)
    PRIMARY KEY (symbol, date)  -> idempotent upserts, safe to run daily.

Prices are split/dividend-adjusted (fetched with yfinance auto_adjust=True).
"""
import sqlite3
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "market.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS bars (
    symbol TEXT    NOT NULL,
    date   TEXT    NOT NULL,   -- YYYY-MM-DD
    open   REAL    NOT NULL,
    high   REAL    NOT NULL,
    low    REAL    NOT NULL,
    close  REAL    NOT NULL,
    volume INTEGER NOT NULL,
    PRIMARY KEY (symbol, date)
);
"""


def connect() -> sqlite3.Connection:
    """Open a connection (as a context manager it commits on success)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def upsert_bars(df: pd.DataFrame) -> None:
    """Insert-or-replace bars keyed by (symbol, date).

    Expects columns: symbol, date (YYYY-MM-DD), open, high, low, close, volume.
    Rows with missing OHLC values are dropped (Yahoo can return NaN rows).
    """
    df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']].copy()
    df = df.dropna(subset=['open', 'high', 'low', 'close'])
    if df.empty:
        raise RuntimeError('no valid bars to store (all rows had missing values)')
    # Convert to plain Python types so sqlite3 binds them without errors.
    df["date"] = df["date"].astype(str)
    df = df.astype(
        {"open": float, "high": float, "low": float, "close": float, "volume": int}
    )
    with connect() as conn:
        conn.executemany(
            """INSERT OR REPLACE INTO bars (symbol, date, open, high, low, close, volume)
               VALUES (:symbol, :date, :open, :high, :low, :close, :volume)""",
            df.to_dict("records"),
        )


def load_bars(symbol: str) -> pd.DataFrame:
    """All bars for one symbol, oldest first."""
    with connect() as conn:
        return pd.read_sql_query(
            "SELECT date, open, high, low, close, volume "
            "FROM bars WHERE symbol = ? ORDER BY date",
            conn,
            params=(symbol,),
        )


def list_symbols() -> list[str]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT symbol FROM bars ORDER BY symbol"
        ).fetchall()
    return [row[0] for row in rows]


def row_count(symbol: str) -> int:
    with connect() as conn:
        (count,) = conn.execute(
            "SELECT COUNT(*) FROM bars WHERE symbol = ?", (symbol,)
        ).fetchone()
    return count
