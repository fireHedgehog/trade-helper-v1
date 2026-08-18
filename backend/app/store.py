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

CREATE TABLE IF NOT EXISTS strategy_watchlists (
    strategy   TEXT NOT NULL,
    symbol     TEXT NOT NULL,
    note       TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (strategy, symbol)
);

CREATE TABLE IF NOT EXISTS strategy_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy    TEXT NOT NULL,
    set_name    TEXT NOT NULL DEFAULT 'defaults',
    scope       TEXT NOT NULL,
    status      TEXT NOT NULL,
    data_as_of  TEXT,
    params      TEXT NOT NULL,
    result      TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_strategy_runs_latest
ON strategy_runs(strategy, set_name, id DESC);
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
    watch_cols = [
        row[1]
        for row in conn.execute("PRAGMA table_info(strategy_watchlists)").fetchall()
    ]
    if watch_cols and "sort_order" not in watch_cols:
        conn.execute(
            "ALTER TABLE strategy_watchlists "
            "ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
        )
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


def bar_inventory() -> list[dict]:
    """Return one compact coverage row per stored symbol."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT symbol, COUNT(*), MIN(date), MAX(date) "
            "FROM bars GROUP BY symbol ORDER BY symbol"
        ).fetchall()
    return [
        {
            "symbol": row[0],
            "rows": row[1],
            "first_date": row[2],
            "latest_date": row[3],
        }
        for row in rows
    ]


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


def list_strategy_watchlist(strategy: str) -> list[dict]:
    """Return the user's persistent, explicitly selected symbols in stable order."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT symbol, note, created_at FROM strategy_watchlists "
            "WHERE strategy = ? ORDER BY sort_order, symbol",
            (strategy,),
        ).fetchall()
    return [
        {"symbol": row[0], "note": row[1], "created_at": row[2]}
        for row in rows
    ]


def replace_strategy_watchlist(strategy: str, symbols: list[str]) -> None:
    """Atomically replace one strategy's user-owned observation list."""
    normalized = list(dict.fromkeys(symbol.strip().upper() for symbol in symbols))
    if any(not symbol for symbol in normalized):
        raise ValueError("watchlist symbols must be non-empty")
    with connect() as conn:
        existing = {
            row[0]: row[1]
            for row in conn.execute(
                "SELECT symbol, note FROM strategy_watchlists WHERE strategy = ?",
                (strategy,),
            ).fetchall()
        }
        conn.execute("DELETE FROM strategy_watchlists WHERE strategy = ?", (strategy,))
        conn.executemany(
            "INSERT INTO strategy_watchlists"
            "(strategy, symbol, note, sort_order) VALUES (?, ?, ?, ?)",
            [
                (strategy, symbol, existing.get(symbol, ""), index)
                for index, symbol in enumerate(normalized)
            ],
        )


def save_strategy_run(
    strategy: str,
    set_name: str,
    scope: str,
    status: str,
    data_as_of: str | None,
    params: dict,
    result: dict,
) -> int:
    """Append one immutable explicit-run snapshot and return its identifier."""
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO strategy_runs "
            "(strategy, set_name, scope, status, data_as_of, params, result) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                strategy,
                set_name,
                scope,
                status,
                data_as_of,
                json.dumps(params, sort_keys=True),
                json.dumps(result, sort_keys=True),
            ),
        )
        return int(cursor.lastrowid)


def latest_strategy_run(
    strategy: str,
    set_name: str | None = "defaults",
    scope: str | None = None,
) -> dict | None:
    """Read the latest stored result without recalculating the strategy."""
    clauses = ["strategy = ?"]
    values: list[str] = [strategy]
    if set_name is not None:
        clauses.append("set_name = ?")
        values.append(set_name)
    if scope is not None:
        clauses.append("scope = ?")
        values.append(scope)
    with connect() as conn:
        row = conn.execute(
            "SELECT id, set_name, scope, status, data_as_of, params, result, created_at "
            f"FROM strategy_runs WHERE {' AND '.join(clauses)} "
            "ORDER BY id DESC LIMIT 1",
            values,
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "strategy": strategy,
        "set": row[1],
        "scope": row[2],
        "status": row[3],
        "data_as_of": row[4],
        "params": json.loads(row[5]),
        "result": json.loads(row[6]),
        "created_at": row[7],
    }


def get_strategy_run(run_id: int) -> dict | None:
    """Read one immutable run by identifier."""
    with connect() as conn:
        row = conn.execute(
            "SELECT strategy, set_name, scope, status, data_as_of, params, result, "
            "created_at FROM strategy_runs WHERE id = ?",
            (run_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": run_id,
        "strategy": row[0],
        "set": row[1],
        "scope": row[2],
        "status": row[3],
        "data_as_of": row[4],
        "params": json.loads(row[5]),
        "result": json.loads(row[6]),
        "created_at": row[7],
    }
