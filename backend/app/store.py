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

from .execution import validate_bars

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
    set_name    TEXT NOT NULL DEFAULT 'defaults',
    state       TEXT NOT NULL,   -- flat | entry_pending | long | exit_pending
    entry_date  TEXT,
    entry_price REAL,
    stop        REAL,
    tp          REAL,
    exit_date   TEXT,
    exit_price  REAL,
    exit_reason TEXT,   -- 'stop' | 'target'
    exit_pnl_pct REAL,
    exit_pnl_usd REAL,
    updated     TEXT NOT NULL,   -- last bar date processed
    PRIMARY KEY (symbol, strategy, set_name)
);
"""


def connect() -> sqlite3.Connection:
    """Open a connection (as a context manager it commits on success)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)  # multiple statements -> executescript
    # Migration: positions gained set_name (dev ledger, safe to rebuild).
    cols = [row[1] for row in conn.execute("PRAGMA table_info(positions)").fetchall()]
    if cols and "set_name" not in cols:
        conn.execute("DROP TABLE positions")
        conn.executescript(SCHEMA)
        cols = [row[1] for row in conn.execute("PRAGMA table_info(positions)").fetchall()]
    # Migration: positions gained last-exit tracking (rows preserved).
    for column, sql_type in (
        ("exit_date", "TEXT"), ("exit_price", "REAL"), ("exit_reason", "TEXT"),
        ("exit_pnl_pct", "REAL"), ("exit_pnl_usd", "REAL"),
    ):
        if column not in cols:
            conn.execute(f"ALTER TABLE positions ADD COLUMN {column} {sql_type}")
    return conn


def upsert_bars(df: pd.DataFrame) -> None:
    """Insert-or-replace bars keyed by (symbol, date).

    Expects columns: symbol, date (YYYY-MM-DD), open, high, low, close, volume.
    The whole batch is rejected if a row is malformed; callers must clean and
    validate provider data before publishing it.
    """
    required = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"bars missing columns: {', '.join(sorted(missing))}")
    df = df[required].copy()
    if df.empty:
        raise ValueError('no bars to store')
    if df["symbol"].isna().any() or (df["symbol"].astype(str).str.strip() == "").any():
        raise ValueError("bar symbols must be present")
    for _symbol, group in df.groupby("symbol", sort=False):
        validate_bars(group.drop(columns="symbol").reset_index(drop=True))
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


def get_position(symbol: str, strategy: str, set_name: str = "defaults") -> dict | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT state, entry_date, entry_price, stop, tp, "
            "exit_date, exit_price, exit_reason, exit_pnl_pct, exit_pnl_usd, updated "
            "FROM positions WHERE symbol = ? AND strategy = ? AND set_name = ?",
            (symbol, strategy, set_name),
        ).fetchone()
    if row is None:
        return None
    return {
        "state": row[0],
        "entry_date": row[1],
        "entry_price": row[2],
        "stop": row[3],
        "tp": row[4],
        "exit_date": row[5],
        "exit_price": row[6],
        "exit_reason": row[7],
        "exit_pnl_pct": row[8],
        "exit_pnl_usd": row[9],
        "updated": row[10],
    }


def save_position(
    symbol: str, strategy: str, fields: dict, updated: str,
    set_name: str = "defaults",
) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO positions "
            "(symbol, strategy, set_name, state, entry_date, entry_price, stop, tp, "
            "exit_date, exit_price, exit_reason, exit_pnl_pct, exit_pnl_usd, updated) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                symbol,
                strategy,
                set_name,
                fields["state"],
                fields.get("entry_date"),
                fields.get("entry_price"),
                fields.get("stop"),
                fields.get("tp"),
                fields.get("exit_date"),
                fields.get("exit_price"),
                fields.get("exit_reason"),
                fields.get("exit_pnl_pct"),
                fields.get("exit_pnl_usd"),
                updated,
            ),
        )


def delete_position(symbol: str, strategy: str, set_name: str = "defaults") -> None:
    with connect() as conn:
        conn.execute(
            "DELETE FROM positions WHERE symbol = ? AND strategy = ? AND set_name = ?",
            (symbol, strategy, set_name),
        )


def latest_bar_date() -> str:
    """Newest bar date in the DB — cache-invalidation key for derived stats."""
    with connect() as conn:
        row = conn.execute("SELECT MAX(date) FROM bars").fetchone()
    return row[0] or ""
