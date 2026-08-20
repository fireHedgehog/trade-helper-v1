"""Treasury securities buyback operations -- fiscaldata.treasury.gov, free, keyless.

Not a FRED series (verified 2026-08-20: not on FRED at all). A different
data shape from `macro_pit`'s ALFRED vintages: this is an event log (one
row per completed operation), not a periodically-revised statistic. Each
operation is announced same-day; a small number of very recent rows carry
null `total_par_amt_accepted` (results not yet posted) -- those are
dropped at ingestion, not stored, since this API exposes no per-field
revision timestamp to place them correctly in a vintage model. Point-in-time
convention (disclosed, not proven from the API): a settled operation is
treated as public as of its own `operation_date` -- the data confirms
results routinely post same-day, but this is a design assumption, not a
guarantee from the schema.

Usage (from backend/):
    python -m app.treasury_buybacks
"""
import argparse
import re

import pandas as pd
import requests

from .store import upsert_treasury_buybacks

API_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/buybacks_operations"
LONG_END_MIN_UPPER_YEARS = 20.0


def fetch_operations() -> pd.DataFrame:
    """All buyback operations (217 as of 2026-08-20; a single page[size]
    request covers full history, no pagination needed at this volume)."""
    response = requests.get(API_URL, params={"page[size]": 10000}, timeout=30)
    response.raise_for_status()
    rows = response.json().get("data", [])
    columns = [
        "operation_date", "maturity_bucket", "security_type", "settlement_date",
        "operation_type", "nbr_issues_accepted", "nbr_issues_eligible",
        "total_par_amt_offered", "total_par_amt_accepted",
    ]
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows)[columns]
    df = df.replace("null", None)
    settled = df[df["total_par_amt_accepted"].notna()].copy()
    settled["maturity_bucket"] = settled["maturity_bucket"].fillna("")
    settled["security_type"] = settled["security_type"].fillna("")
    for column in ("nbr_issues_accepted", "nbr_issues_eligible"):
        settled[column] = pd.to_numeric(settled[column], errors="coerce").astype("Int64")
    for column in ("total_par_amt_offered", "total_par_amt_accepted"):
        settled[column] = pd.to_numeric(settled[column], errors="coerce")
    return settled


def _bucket_upper_years(maturity_bucket: str) -> float | None:
    """'10Y to 20Y' -> 20.0, '1Mo to 2Y' -> 2.0, '' or unparseable -> None."""
    match = re.search(r"to\s+([\d.]+)Y", maturity_bucket or "")
    return float(match.group(1)) if match else None


def is_long_end(maturity_bucket: str) -> bool:
    """Operationalizes Fed put's open 'long-end' question: upper bound >= 20Y.

    A disclosed design choice, not derived from the API -- matches the
    memo's own '30Y or belly-of-curve?' framing by picking the long side.
    """
    upper = _bucket_upper_years(maturity_bucket)
    return upper is not None and upper >= LONG_END_MIN_UPPER_YEARS


def ingest() -> int:
    """Fetch and store all settled operations. Returns rows stored (including
    already-present rows re-verified, not just newly-inserted ones)."""
    operations = fetch_operations()
    if operations.empty:
        return 0
    upsert_treasury_buybacks(operations)
    return len(operations)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest Treasury buyback operations")
    parser.parse_args()
    count = ingest()
    print(f"treasury_buybacks: {count} settled operations stored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
