"""Point-in-time macro data ingestion -- ADR 0006 clauses 2-4.

`app.fred` fetches `fredgraph.csv`, the final-revised series -- display-only,
per ADR 0006 clause 2. This module fetches every historical *vintage* of a
FRED series via the official FRED API's realtime_start/realtime_end
mechanism, so a research query can ask "what value was public as of date t",
not "what is the value known today". That is the distinction ADR 0006 exists
to enforce; nothing computed from `app.fred`'s stored series is a legitimate
input to a macro hypothesis test.

Requires a free FRED_API_KEY (self-registered at
https://fred.stlouisfed.org/docs/api/api_key.html -- this module cannot
obtain one on its own). Either export it before running:

    FRED_API_KEY=... python -m app.macro_pit DFII10 T10YIE

or store it once, locally, in the gitignored database (never a tracked
file) so every future run picks it up automatically:

    from app.store import set_key
    set_key("FRED_API_KEY", "...")

Endpoint and parameters verified against the FRED API's own documented
realtime_start/realtime_end vintage-retrieval convention and the
`mortada/fredapi` reference client's `get_series_all_releases`, which the
same convention: series_id + realtime_start=1776-07-04 (FRED's own
"beginning of time" sentinel) + realtime_end=9999-12-31 returns one row per
(reference period, revision), each carrying the realtime_start at which
that specific value first became public -- exactly ADR 0006's tau_i +
Delta_i^(k). No live ingestion has been run against this yet; this module
is built and unit-tested against a mocked response, not verified against
the real API's live shape.
"""
import argparse
import datetime as dt
import os

import pandas as pd
import requests

from .store import get_key, upsert_macro_vintages

API_URL = "https://api.stlouisfed.org/fred/series/observations"
ALFRED_EARLIEST = "1776-07-04"
ALFRED_LATEST = "9999-12-31"
MISSING_VALUE_SENTINEL = "."
FRED_API_KEY_NAME = "FRED_API_KEY"
VINTAGE_CAP_ERROR_MARKER = "exceeds the maximum number of vintage dates"
NOT_YET_EXISTING_ERROR_MARKER = "does not exist in ALFRED"


def _api_key() -> str:
    """FRED_API_KEY env var takes precedence (explicit override); otherwise
    the locally stored key from `key_library` (never a tracked file, see
    `store.set_key`)."""
    key = os.environ.get(FRED_API_KEY_NAME, "").strip() or (get_key(FRED_API_KEY_NAME) or "")
    if not key:
        raise RuntimeError(
            "FRED_API_KEY is not set. Register a free key at "
            "https://fred.stlouisfed.org/docs/api/api_key.html, then either "
            "export FRED_API_KEY or store it once via "
            "app.store.set_key('FRED_API_KEY', '...') -- point-in-time "
            "vintages are not available from the unauthenticated "
            "fredgraph.csv endpoint app.fred uses for display-only series."
        )
    return key


def _midpoint_date(start: str, end: str) -> str:
    """Ordinal midpoint, clamped to <= today.

    Live-verified constraint: FRED rejects any realtime_end beyond today's
    date unless it is exactly the ALFRED_LATEST sentinel. A midpoint is
    always used as an `end` boundary somewhere in the recursion (see
    fetch_all_vintages), so it must never be allowed past today even when
    bisecting toward the far-future ALFRED_LATEST sentinel. Clamped to two
    days before this machine's local today, not today itself -- live-verified
    that FRED's own server clock can disagree with a local clock by at least
    a day (this machine said 2026-08-20, FRED said "today" was 2026-08-19),
    plausibly a timezone offset; two days is a safe margin either direction.
    """
    d0, d1 = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    mid = dt.date.fromordinal(d0.toordinal() + (d1.toordinal() - d0.toordinal()) // 2)
    safe_today = dt.date.today() - dt.timedelta(days=2)
    if mid > safe_today:
        mid = safe_today
    return mid.isoformat()


def _fetch_vintage_page(
    series_id: str, realtime_start: str, realtime_end: str, api_key: str
) -> pd.DataFrame | None:
    """One raw request. Returns None (not an empty frame) if this range
    exceeds FRED's per-request vintage-date cap -- the caller must split
    and retry, an empty frame is a genuine zero-observation result.

    Live-verified: a range entirely before a series' first vintage is not
    an empty `observations: []` response as the FRED docs would suggest --
    it is its own 400 error ("The series does not exist in ALFRED...").
    Treated as a true zero-observation result, not a failure.
    """
    response = requests.get(
        API_URL,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "realtime_start": realtime_start,
            "realtime_end": realtime_end,
        },
        timeout=30,
    )
    if response.status_code == 400 and VINTAGE_CAP_ERROR_MARKER in response.text:
        return None
    if response.status_code == 400 and NOT_YET_EXISTING_ERROR_MARKER in response.text:
        return pd.DataFrame(columns=["reference_period", "value", "realtime_start"])
    response.raise_for_status()
    observations = response.json().get("observations", [])
    columns = ["reference_period", "value", "realtime_start"]
    if not observations:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(observations).rename(columns={"date": "reference_period"})
    df = df[df["value"] != MISSING_VALUE_SENTINEL].copy()
    df["value"] = df["value"].astype(float)
    return df[columns]


def fetch_all_vintages(
    series_id: str,
    *,
    api_key: str | None = None,
    _realtime_start: str = ALFRED_EARLIEST,
    _realtime_end: str = ALFRED_LATEST,
) -> pd.DataFrame:
    """Every historical revision of series_id, one row per (reference_period, vintage).

    Returns columns: reference_period, value, realtime_start. Rows where the
    reference period had no published value at that vintage (FRED's "."
    sentinel) are dropped. High-frequency (e.g. daily) series can exceed
    FRED's 2,000-vintage-dates-per-request cap over full history (found
    live: DFII10 has 5,073) -- this recursively bisects the realtime_start/
    realtime_end range on that specific error and merges the pages, so the
    public interface never needs to know the cap exists.
    """
    key = api_key or _api_key()
    page = _fetch_vintage_page(series_id, _realtime_start, _realtime_end, key)
    if page is not None:
        return page

    mid = _midpoint_date(_realtime_start, _realtime_end)
    if mid == _realtime_start or mid == _realtime_end:
        raise RuntimeError(
            f"{series_id}: vintage range {_realtime_start}..{_realtime_end} "
            "cannot be split further but still exceeds FRED's per-request "
            "vintage-date cap -- unexpected, investigate before retrying."
        )
    left = fetch_all_vintages(
        series_id, api_key=key, _realtime_start=_realtime_start, _realtime_end=mid
    )
    right = fetch_all_vintages(
        series_id, api_key=key, _realtime_start=mid, _realtime_end=_realtime_end
    )
    combined = pd.concat([left, right], ignore_index=True)
    return combined.drop_duplicates(subset=["reference_period", "realtime_start", "value"])


def to_revision_indexed(series_id: str, vintages: pd.DataFrame) -> pd.DataFrame:
    """Assign revision_index k=0,1,2,... per reference_period, ordered by realtime_start.

    release_datetime is each revision's own realtime_start -- the first
    instant that specific value became public.
    """
    columns = ["series_id", "reference_period", "revision_index", "release_datetime", "value"]
    if vintages.empty:
        return pd.DataFrame(columns=columns)
    ordered = vintages.sort_values(["reference_period", "realtime_start"]).copy()
    ordered["revision_index"] = ordered.groupby("reference_period").cumcount()
    ordered["series_id"] = series_id
    ordered["release_datetime"] = ordered["realtime_start"]
    return ordered[columns].reset_index(drop=True)


def value_asof(series_id: str, decision_datetime: str) -> pd.DataFrame:
    """The vintage visible at decision_datetime: ADR 0006's V_t.

    For each reference period, the latest stored revision whose
    release_datetime is at or before decision_datetime. Empty if nothing has
    been ingested, or nothing was public yet at decision_datetime.
    """
    from .store import macro_vintage_rows

    columns = ["reference_period", "value", "revision_index", "release_datetime"]
    rows = macro_vintage_rows(series_id)
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows)
    visible = df[df["release_datetime"] <= decision_datetime]
    if visible.empty:
        return pd.DataFrame(columns=columns)
    latest = (
        visible.sort_values("revision_index")
        .groupby("reference_period", as_index=False)
        .last()
    )
    return latest.sort_values("reference_period").reset_index(drop=True)[columns]


def ingest(series_id: str, *, api_key: str | None = None) -> int:
    """Fetch, index, and store every revision of series_id. Returns rows stored."""
    vintages = fetch_all_vintages(series_id, api_key=api_key)
    indexed = to_revision_indexed(series_id, vintages)
    if indexed.empty:
        return 0
    upsert_macro_vintages(indexed)
    return len(indexed)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest FRED point-in-time vintage history")
    parser.add_argument("series", nargs="+")
    args = parser.parse_args()
    for series_id in args.series:
        count = ingest(series_id)
        print(f"{series_id}: {count} vintage rows stored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
