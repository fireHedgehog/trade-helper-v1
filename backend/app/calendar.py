"""US macro events — event-driven calendar.

A curated catalog of US releases that matter for equities. For each event:
- next: upcoming release date/time + market forecast (Trading Economics)
- last: latest released actual + previous (FRED series stored in the bars DB)
- beat/miss vs consensus: NOT available yet (no free forecast-history source);
  the UI shows it honestly as "consensus n/a" until we source one.

Network: one TE page request per 6h (cached). FRED values come from the DB.
"""
import re
import time
from datetime import datetime

import lxml.html
import requests

from .store import load_recent_bars

TE_URL = "https://tradingeconomics.com/calendar"
TE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
CACHE_TTL = 6 * 3600

# (key, display name, category, TE keywords, FRED series, value mode)
# mode: level | mom | yoy_monthly | none
CATALOG = [
    ("fomc", "FOMC Rate Decision", "Fed", ("fed rate decision",), "DFEDTARU", "level"),
    ("cpi", "CPI Inflation (YoY)", "Inflation", ("inflation rate",), "CPIAUCSL", "yoy_monthly"),
    ("pce", "Core PCE Price Index (YoY)", "Inflation", ("core pce",), "PCEPILFE", "yoy_monthly"),
    ("nfp", "Nonfarm Payrolls", "Labor", ("non farm payrolls",), "PAYEMS", "mom"),
    ("unemp", "Unemployment Rate", "Labor", ("unemployment rate",), "UNRATE", "level"),
    ("claims", "Initial Jobless Claims", "Labor", ("jobless claims",), "ICSA", "level"),
    ("gdp", "GDP Growth (annualized)", "Growth", ("gdp growth",), "A191RL1Q225SBEA", "level"),
    ("retail", "Retail Sales (MoM)", "Consumption", ("retail sales",), "RSXFSN", "mom"),
    ("ism", "ISM Manufacturing PMI", "Activity", ("ism manufacturing",), None, "none"),
]

_cache: dict = {"at": 0.0, "events": []}


def _parse_date(text: str) -> str | None:
    m = re.match(r"^\w+day (\w+) (\d{1,2}) (\d{4})$", text)
    if not m:
        return None
    return datetime.strptime(
        f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y"
    ).strftime("%Y-%m-%d")


def _fetch_te_rows() -> list[dict]:
    response = requests.get(TE_URL, headers=TE_HEADERS, timeout=20)
    response.raise_for_status()
    doc = lxml.html.fromstring(response.text)
    rows: list[dict] = []
    current_date: str | None = None
    for row in doc.xpath('//table[@id="calendar"]//tr'):
        cells = [c.text_content().strip() for c in row.xpath("./td|./th")]
        if not cells:
            continue
        if re.match(r"^\w+day \w+ \d{1,2} \d{4}$", cells[0]):
            current_date = _parse_date(cells[0])
            continue
        if current_date and len(cells) >= 7 and cells[1] == "US":
            rows.append(
                {
                    "date": current_date,
                    "time": cells[0],
                    "name": cells[2],
                    "actual": cells[3],
                    "previous": cells[4],
                    "consensus": cells[5],
                    "forecast": cells[6],
                }
            )
    return rows


def _fred_last(series: str, mode: str) -> dict | None:
    bars = load_recent_bars(series, 320)
    if len(bars) < 2:
        return None
    close = bars["close"].astype(float)
    last, prev = float(close.iloc[-1]), float(close.iloc[-2])
    actual = previous = change = None
    if mode == "level":
        actual, previous, change = last, prev, round(last - prev, 2)
    elif mode == "mom":
        actual = round(last - prev, 2)
        previous = round(prev - float(close.iloc[-3]), 2) if len(bars) > 2 else None
        change = round(actual - previous, 2) if previous is not None else None
    elif mode == "yoy_monthly":
        if len(bars) < 13:
            return None
        actual = round((last / float(close.iloc[-13]) - 1) * 100, 2)
        previous = round((prev / float(close.iloc[-14]) - 1) * 100, 2) if len(bars) > 13 else None
        change = round(actual - previous, 2) if previous is not None else None
    else:
        return None
    return {
        "date": str(bars["date"].iloc[-1]),
        "actual": round(actual, 2) if actual is not None else None,
        "previous": round(previous, 2) if previous is not None else None,
        "change": change,
        "consensus": None,  # forecast history not yet sourced — honest n/a
    }


def macro_events(force: bool = False) -> list[dict]:
    if not force and _cache["events"] and time.time() - _cache["at"] < CACHE_TTL:
        return _cache["events"]
    try:
        te_rows = _fetch_te_rows()
    except Exception:
        te_rows = []
    events = []
    for key, name, category, keywords, fred, mode in CATALOG:
        match = next(
            (r for r in te_rows if any(k in r["name"].lower() for k in keywords)),
            None,
        )
        next_info = None
        if match:
            forecast = match["consensus"] or match["forecast"] or ""
            next_info = {
                "date": match["date"],
                "time": match["time"],
                "forecast": forecast,
            }
        events.append(
            {
                "key": key,
                "name": name,
                "category": category,
                "next": next_info,
                "last": _fred_last(fred, mode) if fred else None,
            }
        )
    _cache["at"] = time.time()
    _cache["events"] = events
    return events

