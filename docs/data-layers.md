# Data layers — evolving catalog

Cross-reference table of every data source this project touches or has
scoped, one row per layer. Distinct from [ADR 0006](adr/0006-macro-data-contract.md)
(governs the macro PIT contract specifically) and
[data/README.md](../data/README.md) (governs `data/` portability
mechanics) — this tracks *what exists and what's scoped*, across all
layers, as a single growing reference. A row here is not a commitment to
build anything not already built; `status: planned` names a real, checked
option, not a promise.

Philosophy, user-set: this project is unfunded self-research, not an
institution — Chapter 1-3's full preregistration ceremony stays reserved
for when something genuinely needs rigorous verification (see
[research-program.md](research-program.md)'s living-chapter framing).
Current focus is Chapter 4 (the factor zoo, breadth over proof) on the
free data already in hand; Chapters 1-3 come back into focus once that's
exhausted and/or better data arrives. This table exists so "better data
arrives" has somewhere to land without a redesign.

| Layer | Module | Status | Point-in-time? | Cost | Coverage | Used by |
|---|---|---|---|---|---|---|
| Macro, vintage-aware | [`macro_pit.py`](../backend/app/macro_pit.py) | built | yes (true ALFRED vintages) | free (FRED key, `key_library`) | any FRED series, revision history | Chapter 3 |
| Macro, final-revised | [`fred.py`](../backend/app/fred.py) | built | no — series confirmed not revision-prone (e.g. DGS2/DGS10) | free | same FRED catalog | Chapter 3 |
| Daily bars, equities/ETFs | [`store.py`](../backend/app/store.py)/[`fetch.py`](../backend/app/fetch.py) | built | no — `auto_adjust=True` retroactively rebases, disclosed | free (Yahoo via yfinance) | 555 symbols, back to 1962 for the oldest | Chapters 1/2/4, factor zoo |
| Equity universe membership, today's snapshot | [`universe.py`](../backend/app/universe.py) | built | no — today's constituents, survivorship-biased, disclosed | free (Wikipedia) | S&P 500 ∪ Nasdaq-100 ∪ XL sector ETFs, 495 in `bars` | Chapters 2/4 |
| Equity universe membership, point-in-time | [`universe_pit.py`](../backend/app/universe_pit.py) | built, live-verified `0.81.0` | yes — `members_asof(date)` reconstructs true S&P 500 membership on any date | free, MIT-licensed ([fja05680/sp500](https://github.com/fja05680/sp500), maintained by hand, not a vendor) | S&P 500 only, 1996–present, `1,259` intervals/`1,206` symbols; maintainer flags 1996–2000 as lower-confidence | Chapter 2 — clears the Tier 4 blocker behind CS-01/02/03/04/05/09 |
| Equity sector classification (GICS) | [`universe_sectors.py`](../backend/app/universe_sectors.py) | built, live-verified `0.83.0` | no — today's classification snapshot; a company's GICS assignment can be reassigned over time with no history tracked here | free (same Wikipedia S&P 500 table `universe.py` already scrapes) | S&P 500 only, `503` symbols, `11` GICS sectors | Chapter 2 — unblocks CS-07/CS-08 (sector/peer-group rotation); inherits the same index-membership selection bias named in [the cross-sectional idea library](brainstorm/2026-08-20-cross-sectional-experiment-ideas.md), not a fix for it |
| Treasury buyback operations | [`treasury_buybacks.py`](../backend/app/treasury_buybacks.py) | built, currently unused | n/a (operational record, not a series) | free (fiscaldata.treasury.gov) | modern buyback program only, ~1 usable episode | none — built for Fed-put v1, dropped when Treasury/Fed were correctly un-conflated |
| Credentials substrate | `key_library` table via [`store.py`](../backend/app/store.py) | built | n/a | n/a | any API key, extensible by name | underpins the two macro rows |
| Corporate events / earnings dates | not built | **planned** | would need as-announced date, not just period-end | free — `yfinance.get_earnings_dates()` confirmed working, 1987-2026 depth | none yet | Chapter 3 (PEAD, currently an open thread) |
| Fundamentals (value/quality) | not built | **planned, real ETL required** | yes, achievable — SEC EDGAR XBRL carries genuine per-filing `filed` timestamps | free (SEC EDGAR `companyfacts`/DERA bulk), but no free *ready-to-use* PIT vendor exists — confirmed via web research 2026-08-21, see [open-source-factor-source-backlog.md](brainstorm/2026-08-21-open-source-factor-source-backlog.md) | dedupe restatements to first-as-filed, join against price/shares-outstanding, coverage effectively starts ~2009 | none yet — currently the reason value/quality factors stay excluded from the factor zoo |
| Intraday / tick | out of scope | **excluded by design** | n/a | n/a | n/a | never — this project only ever reaches bounded paper trading (ADR 0008), never live/HFT execution, so intraday data buys nothing it would use |

## Adding a layer

New row = new source found (matches the ongoing pattern already used for
[the factor-source backlog](brainstorm/2026-08-21-open-source-factor-source-backlog.md)).
`status: planned` stays planned until someone decides the ETL/ingestion
work is worth doing for a specific chapter's named need — this table
tracks options, [research-program.md](research-program.md) tracks what's
actually running.
