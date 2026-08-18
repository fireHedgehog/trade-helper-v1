"""Observable, manually triggered market-data refresh coordination.

The refresh worker is deliberately local and in-process. It updates full Yahoo
adjusted histories one symbol at a time with a non-configurable inter-request
delay. Process restart loses job progress, but published SQLite bars remain
transactional and idempotent.
"""

from __future__ import annotations

import copy
import threading
import time
import uuid
from datetime import date, datetime, time as clock_time, timedelta, timezone
from typing import Callable
from zoneinfo import ZoneInfo

import pandas as pd

from . import fetch, store
from .fred import MANAGED_SERIES as FRED_MANAGED_SERIES
from .research_catalog import DATASETS, dataset_for_provider, dataset_registry


REFRESH_PERIOD = "max"
REQUEST_DELAY_SECONDS = fetch.MIN_MULTI_SYMBOL_DELAY_S
NEW_YORK = ZoneInfo("America/New_York")
SESSION_COMPLETE_TIME = clock_time(18, 0)


class RefreshAlreadyRunning(RuntimeError):
    pass


def expected_latest_session(now: datetime | None = None) -> date:
    """Latest likely completed US weekday session (holiday-unaware)."""
    current = now or datetime.now(timezone.utc)
    local = current.astimezone(NEW_YORK)
    candidate = local.date()
    if local.time() < SESSION_COMPLETE_TIME:
        candidate -= timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate


def _weekday_lag(latest: date, expected: date) -> int:
    if latest >= expected:
        return 0
    lag = 0
    cursor = latest + timedelta(days=1)
    while cursor <= expected:
        if cursor.weekday() < 5:
            lag += 1
        cursor += timedelta(days=1)
    return lag


def freshness(
    latest_date: str, *, expected: date | None = None
) -> tuple[str, int, int | None]:
    """Classify recency against the latest expected completed weekday session.

    This intentionally does not pretend to be an exchange calendar. Weekends
    are skipped, but US exchange holidays can make the label conservative.
    """
    reference = expected or expected_latest_session()
    try:
        latest = date.fromisoformat(latest_date)
    except (TypeError, ValueError):
        return "invalid", 0, None
    age = max(0, (reference - latest).days)
    lag = _weekday_lag(latest, reference)
    if lag == 0:
        return "fresh", age, lag
    if lag == 1:
        return "aging", age, lag
    return "stale", age, lag


def inventory_payload(*, today: date | None = None) -> dict:
    expected = today or expected_latest_session()
    rows = []
    counts = {
        "fresh": 0,
        "aging": 0,
        "stale": 0,
        "invalid": 0,
        "fred_managed": 0,
    }
    for stored in store.bar_inventory():
        provider = "fred" if stored["symbol"] in FRED_MANAGED_SERIES else "yahoo"
        dataset_id = dataset_for_provider(provider)
        dataset = DATASETS[dataset_id]
        state, age, session_lag = freshness(stored["latest_date"], expected=expected)
        if provider == "fred":
            state = "provider_managed"
            counts["fred_managed"] += 1
        else:
            counts[state] += 1
        rows.append(
            {
                **stored,
                "provider": provider,
                "dataset_id": dataset_id,
                "information_class": dataset["information_class"],
                "point_in_time": dataset["point_in_time"],
                "research_use": dataset["research_use"],
                "freshness": state,
                "age_days": age,
                "session_lag": session_lag,
            }
        )
    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "source": "Yahoo Finance via yfinance",
        "adjustment": "auto_adjust=True",
        "expected_latest_session": expected.isoformat(),
        "freshness_policy": (
            "latest expected completed US weekday: fresh = current, aging = 1 "
            "session behind, stale = 2+; US exchange holidays are not modeled yet"
        ),
        "refresh_policy": {
            "manual_only": True,
            "period": REFRESH_PERIOD,
            "delay_seconds": REQUEST_DELAY_SECONDS,
            "retry_backoff_seconds": fetch.RATE_LIMIT_BACKOFF_S,
            "note": (
                "the fixed delay and retry backoff reduce request pressure but "
                "cannot guarantee Yahoo will not rate-limit or block requests; "
                "full adjusted history is refreshed to avoid mixing incompatible "
                "adjustment bases, and FRED series are excluded from Yahoo jobs"
            ),
        },
        "summary": {"symbols": len(rows), **counts},
        "datasets": dataset_registry(),
        "symbols": rows,
    }


def select_refresh_symbols(
    scope: str, inventory: list[dict], core_symbols: list[str]
) -> list[str]:
    known = {
        row["symbol"]: row
        for row in inventory
        if row.get("provider", "yahoo") == "yahoo"
    }
    if scope == "all":
        return sorted(known)
    if scope == "core":
        return [symbol for symbol in core_symbols if symbol in known]
    if scope == "stale":
        return sorted(
            symbol
            for symbol, row in known.items()
            if row["freshness"] in {"aging", "stale", "invalid"}
        )
    raise ValueError(f"unknown refresh scope: {scope}")


class DataRefreshManager:
    """Run at most one observable full-history refresh in a daemon thread."""

    def __init__(
        self,
        *,
        fetcher: Callable[[str, str], pd.DataFrame] = fetch.fetch_with_retry,
        sleeper: Callable[[float], None] = time.sleep,
        on_publish: Callable[[], None] | None = None,
    ) -> None:
        self._fetcher = fetcher
        self._sleeper = sleeper
        self._on_publish = on_publish or (lambda: None)
        self._lock = threading.Lock()
        self._job: dict | None = None

    def snapshot(self) -> dict:
        with self._lock:
            if self._job is None:
                return {
                    "state": "idle",
                    "job_id": None,
                    "completed": 0,
                    "failed": 0,
                    "total": 0,
                    "current_symbol": None,
                    "items": [],
                }
            return copy.deepcopy(self._job)

    def start(self, symbols: list[str]) -> dict:
        ordered = list(dict.fromkeys(symbols))
        if not ordered:
            raise ValueError("refresh requires at least one stored symbol")
        with self._lock:
            if self._job and self._job["state"] == "running":
                raise RefreshAlreadyRunning("a data refresh is already running")
            now = datetime.now(timezone.utc).isoformat()
            self._job = {
                "state": "running",
                "job_id": uuid.uuid4().hex,
                "started_at": now,
                "finished_at": None,
                "completed": 0,
                "failed": 0,
                "total": len(ordered),
                "current_symbol": None,
                "items": [
                    {
                        "symbol": symbol,
                        "state": "pending",
                        "message": "waiting",
                        "rows_received": None,
                        "total_rows": None,
                        "latest_date": None,
                    }
                    for symbol in ordered
                ],
            }
            snapshot = copy.deepcopy(self._job)
        threading.Thread(
            target=self._run,
            args=(ordered,),
            name=f"market-data-refresh-{snapshot['job_id'][:8]}",
            daemon=True,
        ).start()
        return snapshot

    def _update_item(self, index: int, **changes) -> None:
        with self._lock:
            assert self._job is not None
            self._job["items"][index].update(changes)

    def _run(self, symbols: list[str]) -> None:
        for index, symbol in enumerate(symbols):
            with self._lock:
                assert self._job is not None
                self._job["current_symbol"] = symbol
            self._update_item(
                index,
                state="fetching",
                message="requesting full adjusted history",
            )
            try:
                frame = self._fetcher(symbol, REFRESH_PERIOD)
                store.upsert_bars(frame)
                self._on_publish()
                self._update_item(
                    index,
                    state="complete",
                    message="published",
                    rows_received=len(frame),
                    total_rows=store.row_count(symbol),
                    latest_date=str(frame["date"].iloc[-1]),
                )
                with self._lock:
                    assert self._job is not None
                    self._job["completed"] += 1
            except Exception as exc:
                self._update_item(
                    index,
                    state="failed",
                    message=f"{type(exc).__name__}: {exc}"[:300],
                )
                with self._lock:
                    assert self._job is not None
                    self._job["failed"] += 1
            if index < len(symbols) - 1:
                self._sleeper(REQUEST_DELAY_SECONDS)

        with self._lock:
            assert self._job is not None
            self._job["state"] = (
                "complete" if self._job["failed"] == 0 else "complete_with_errors"
            )
            self._job["current_symbol"] = None
            self._job["finished_at"] = datetime.now(timezone.utc).isoformat()
