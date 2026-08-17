"""SQLite storage for daily bars.

Data files live in the repo's `data/` dir (gitignored — data never gets committed).

Schema:
    bars(symbol, date, open, high, low, close, volume)
    PRIMARY KEY (symbol, date)  -> idempotent upserts, safe to run daily.

Prices are split/dividend-adjusted (fetched with yfinance auto_adjust=True).
"""
import json
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

CREATE TABLE IF NOT EXISTS param_sets (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    strategy   TEXT    NOT NULL,
    params     TEXT    NOT NULL,   -- JSON
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS positions (
    symbol      TEXT NOT NULL,
    strategy    TEXT NOT NULL,
    state       TEXT NOT NULL,   -- flat | entry_pending | long
    entry_date  TEXT,
    entry_price REAL,
    stop        REAL,
    tp          REAL,
    updated     TEXT NOT NULL,   -- last bar date processed
    PRIMARY KEY (symbol, strategy)
);
"""


def connect() -> sqlite3.Connection:
    """Open a connection (as a context manager it commits on success)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)  # multiple statements -> executescript
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


def load_recent_bars(symbol: str, n: int) -> pd.DataFrame:
    """Last n bars for one symbol, oldest first (fast — no full-history read)."""
    with connect() as conn:
        df = pd.read_sql_query(
            "SELECT date, open, high, low, close, volume "
            "FROM bars WHERE symbol = ? ORDER BY date DESC LIMIT ?",
            conn,
            params=(symbol, n),
        )
    return df.iloc[::-1].reset_index(drop=True)


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


def save_param_set(name: str, strategy: str, params: dict) -> None:
    """Upsert a named param set (same name overwrites — that's the tune loop)."""
    with connect() as conn:
        conn.execute(
            "INSERT INTO param_sets (name, strategy, params, created_at) "
            "VALUES (?, ?, ?, datetime('now')) "
            "ON CONFLICT(name) DO UPDATE SET "
            "strategy = excluded.strategy, params = excluded.params, "
            "created_at = datetime('now')",
            (name, strategy, json.dumps(params)),
        )


def list_param_sets(strategy: str | None = None) -> list[dict]:
    with connect() as conn:
        if strategy:
            rows = conn.execute(
                "SELECT name, strategy, params, created_at FROM param_sets "
                "WHERE strategy = ? ORDER BY name",
                (strategy,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT name, strategy, params, created_at FROM param_sets ORDER BY name"
            ).fetchall()
    return [
        {
            "name": row[0],
            "strategy": row[1],
            "params": json.loads(row[2]),
            "created_at": row[3],
        }
        for row in rows
    ]


def delete_param_set(name: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM param_sets WHERE name = ?", (name,))


def get_position(symbol: str, strategy: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT state, entry_date, entry_price, stop, tp, updated "
            "FROM positions WHERE symbol = ? AND strategy = ?",
            (symbol, strategy),
        ).fetchone()
    if row is None:
        return None
    return {
        "state": row[0],
        "entry_date": row[1],
        "entry_price": row[2],
        "stop": row[3],
        "tp": row[4],
        "updated": row[5],
    }


def save_position(
    symbol: str, strategy: str, fields: dict, updated: str
) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO positions "
            "(symbol, strategy, state, entry_date, entry_price, stop, tp, updated) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                symbol,
                strategy,
                fields["state"],
                fields.get("entry_date"),
                fields.get("entry_price"),
                fields.get("stop"),
                fields.get("tp"),
                updated,
            ),
        )


def delete_position(symbol: str, strategy: str) -> None:
    with connect() as conn:
        conn.execute(
            "DELETE FROM positions WHERE symbol = ? AND strategy = ?",
            (symbol, strategy),
        )
