# Documentation and resume checkpoint

This file is the authoritative entry point for a new agent or work session. Do not infer current work from the changelog.

## Checkpoint

| Field | Value |
|---|---|
| Version | `0.76.6` |
| Parent release | `0.37.0` (first Stage 8 acceptance candidate) |
| Current state | Research reorganized into a chaptered, living program — see [research-program.md](research-program.md). Chapters 1-3 hold the existing strict falsification standard unchanged, deliberately paused (unfunded self-research, not an institution — that ceremony is reserved for when something needs rigorous verification, not a default); Chapter 4 (risk-budgeted ensemble construction, [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md), accepted) is the current focus and now has a real breadth generator (§5, a 27-factor zoo: 17 WorldQuant-style formulas + 10 classic technical indicators) instead of one hand-picked candidate at a time; Chapter 5 (operational bridge, [ADR 0008](adr/0008-bounded-paper-trading.md), **accepted** `2026-08-21`) answers a third question — what has to be true operationally before any candidate that clears a ladder can actually be paper-traded. New [data layers catalog](data-layers.md) tracks what data exists/is planned/is excluded across the whole project, extensible as better data arrives later. Acceptance settled the Chapter 5 design; none of its required infrastructure is built yet |
| Verification | `399 passed` at `0.76.6` |
| Completed | Stage 8; Stage 9A Cycles 1–6; CTA v1/v2; TA Breakout, Wave Pull, ETF-12 rotation, both calendar candidates, Overnight Gap, Fed put yield-stress precursor v1+v2+v3 — all closed and indexed in [research-protocols/README.md](research-protocols/README.md); labor-market claims lead-lag operationalized and bounded-explored (not yet scored); Chapter 4's first full pass (CTA v2, Wave Pull, Calendar Day-of-Week) closed with a correlation-aware significance test, not an approximation; ADR 0008 accepted `2026-08-21` (design only, not implemented); factor zoo v1 enriched to 27 formulas (WQ101 subset + classic TA indicators) against the real 495-symbol universe — real Sharpe/IC, real charts, one genuinely independent standout (`atr_normalized`, Sharpe `0.84`) found and orthogonality-checked; [strategy-library.md](strategy-library.md) onboarding playbook written and immediately exercised — the **Strategy Management** page (`#records`, `GET /api/research-record`) shipped `0.76.2`, now showing 16 of 17 Tier B studies (real name/type/chapter/decision/summary/GitHub link each) after `0.76.3` un-deferred the 3 Fed put studies and added a professional `type` taxonomy (Time-Series/Cross-Sectional/Macro, `research_catalog.STUDY_TYPES`) to every Tier A strategy and Tier B study; only `factor-zoo-v1` remains deferred, pending a clearer explanation, not because it's complex or macro. [workspace-redesign.md](workspace-redesign.md) gained one new contracted-not-built item: Symbol Research must show an open position's actual unrealized P&L, not just its entry price. `0.76.4` corrected course on where Tier B appears: it is no longer fragmented onto Strategy Management alone — Today's discovery tabs, Symbol Research's dropdown, and Strategy Lab's dropdown now all include Tier A and Tier B together (`research_record_entries()` feeds every surface); selecting a Tier B entry anywhere shows its record inline instead of attempting a live run |
| Next product work | Four threads. (1) Onboarding follow-up, was ADR 0009's named gap: `factor-zoo-v1` still needs `name`/`summary`/removal from `DEFERRED_FROM_RECORD` to appear on Strategy Management, pending a clearer user-facing explanation of what it measures, per [strategy-library.md](strategy-library.md). Symbol Research's unrealized-P&L display (workspace-redesign.md) is also unbuilt — contracted, safe to pick up whenever Symbol Research work is next touched. (2) Factor zoo follow-up: propose the least-redundant survivors (`alpha028`/`004`/`026`, `atr_normalized`) as individual Chapter 4 candidates with a stated mechanism each, run a transaction-cost-sensitivity check on the whole reversal cluster before trusting its Sharpe numbers, and check `atr_normalized`'s regime concentration (ADR 0007 clause 5) — see [research-program.md](research-program.md) Chapter 4 §5. (3) Data layer follow-up, only when it's actually needed: earnings-date ingestion (confirmed-free `yfinance.get_earnings_dates()`, unblocks PEAD) and/or SEC EDGAR PIT-fundamentals ETL — see [data-layers.md](data-layers.md), neither started. (4) ADR 0008 implementation — `live_price_snapshots`, `paper_ledger_events`, the Alpaca integration module are all still unbuilt, blocked on the user creating an Alpaca paper account and API keys. Chapter 1-3 stays intentionally paused — see Current state — with its open threads unchanged and unabandoned in [research-program.md](research-program.md) |
| Active research | Chapter 4 (ADR 0007, accepted) is the active line, Chapters 1-3 deliberately paused (see Current state). 3 hand-picked candidates from the original pass scored, none with a settled positive read (CTA v2 not eligible; Wave Pull and Calendar Day-of-Week both walked back to chance after calibration — full detail CHANGELOG `0.70.0`/`0.71.0`, [research-program.md](research-program.md) §1-4). §5 (factor zoo, enriched `0.75.0`): 27 factors screened; every classic technical indicator scored negative IC-IR under its conventional direction — read correctly as the same short-horizon reversal effect from the other side, not a new finding; `atr_normalized` (ATR/close, a volatility-level factor) is the one confirmed-independent standout, Sharpe `0.84`, orthogonality-checked against the whole reversal cluster (`|r|≤0.34`). None of this is proposed as a formal Chapter 4 candidate yet — screening only. Stage 9B remains gated. Chapter 5 (ADR 0008, accepted): zero strategies or candidates currently hold `eligible for operational validation` under any of the three approval paths — implementation not yet started |
| Parked operations | Stage 10 cron; Stage 11 deployment |
| Pending triage | 2026-08-19 methodology/implementation audit — H2 (non-atomic bar publication) fixed in `0.54.0`; 2 critical, 1 high (H1, the orphaned mutating `GET /api/today`), 5 medium, 4 low remain untriaged; see [audits/README.md](audits/README.md) |

`0.37.1` fixed two full-universe-scan contract defects (settlement-vs-equity candle confusion; a small invalid subset blocking every scan) — see CHANGELOG if debugging scan coverage.

Local-optimum guard: Stage 8 is closed, do not add infrastructure/UX polish absent a concrete defect. The single-asset/time-series line is parked — read [stage-closures](stage-closures/2026-08-20-single-asset-time-series-line.md) before proposing anything back into it. No closed result licenses a reflexive follow-up (wider window, pooled version, same claim retried) — that is always a new, independently justified candidate.

No research line is currently active — Fed put (Cycle 6) closed across all three designs; see [research-program.md](research-program.md) for the full chaptered state. Do not tune CTA v1 after its rejection. Do not skip [next-priority-evaluation.md](next-priority-evaluation.md) when >1 candidate is live.

## Non-negotiable state

- Product purpose: decide `reject`, `revise`, or `continue research`; never imply validated profit.
- Default project benchmark: Passive ETF-12 v1; every new protocol audits suitability; SPY and cash remain references.
- CTA v1: rejected under its locked protocol; this does not reject trend following generally.
- Execution: signal on completed close `N`, fill at next available open `N+1`.
- Watchlists: user-selected symbols persist per strategy and show lifecycle state.
- Candidate tabs: full-universe new-entry candidates per model, plus intersections; they are not watchlists.
- Data refresh and strategy runs are explicit actions, not navigation side effects.
- Macro series are non-tradable context under [ADR 0006](adr/0006-macro-data-contract.md); they never generate candidates until point-in-time data and a preregistered hypothesis exist.
- Cron, live trading, live broker connectivity, and AWS remain out of scope. Paper trading's design is accepted ([ADR 0008](adr/0008-bounded-paper-trading.md), `accepted` `2026-08-21`) but not implemented or authorized for use — no strategy currently qualifies to use it.

## Environment and data portability

`data/` and `.venv/` are git-ignored ([data/README.md](../data/README.md)); Git carries specifications, code, and immutable evidence, never the local database or interpreter. A checkout without both populated can read, edit, and plan documentation and specifications, and can run any test that does not require `data/market.db` rows; it cannot run the server or any detector/matching/experiment runner against real data.

A locked specification's data fingerprint (for example `consolidation-support-feasibility-v1`'s `development_sha256`) is computed over the exact rows in `data/market.db` at lock time. Re-fetching is not a substitute: Yahoo `auto_adjust=True` rebases full price history on every dividend, so a fresh `python -m app.fetch` run is not guaranteed to reproduce a prior fingerprint, and `run_consolidation_feasibility.py` raises `RuntimeError` on any mismatch rather than proceeding on unverified data. To move locked-data execution to another machine, copy the `data/market.db` file itself; do not re-fetch and expect an identical hash.

Consequence for new locked work (Stage 9A Cycle 2 or later): candidate selection, scorecard, and protocol drafting need no data. Locking a specification's data fingerprint and running its detector must happen on the machine holding the intended `data/market.db`; that machine then becomes the only one able to execute that specification until the database file is copied across.

On a checkout with no `data/market.db` rows, `pytest -q` fails exactly two tests, not zero: `test_consolidation_feasibility.py::test_real_locked_spec_and_development_data_reproduce` (fingerprint mismatch against an empty database) and `test_api.py::test_signal_rejects_unknown_parameter` (`/api/signal/SPY` returns `404` before parameter validation because `SPY` is not stored). Both are the expected empty-database state, confirmed by direct run at `0.41.0`, not a regression to fix.

## Document authority

| Question | Authoritative document |
|---|---|
| What is the product? | [Product contract](product.md) |
| What are we actually running? (distilled, load first) | [Product identity](identity.md) |
| How should the interface work? | [Workspace redesign](workspace-redesign.md) |
| What happens next? | [Roadmap](roadmap.md) |
| How was CTA v1 tested? | [Research protocol](research-protocol.md) |
| What did CTA v1 show? | [Result](research-results/cta-trend-wf-v1.md) and [audit](research-results/cta-trend-wf-v1-audit.md) |
| What research may follow? | [Research backlog](research-backlog.md) |
| What's the whole research program's shape, and how does a closed line get reopened honestly? | [Research program index](research-program.md) |
| Can a signal that hasn't cleared the strict falsification bar ever be sized and traded? | [ADR 0007 (accepted)](adr/0007-risk-budgeted-ensemble-acceptance.md) |
| What has to be true operationally before any candidate can be paper-traded? | [ADR 0008 (accepted)](adr/0008-bounded-paper-trading.md) |
| How does a narrative become a measurable hypothesis? | [Hypothesis engineering](hypothesis-engineering.md) |
| How is a candidate selected and allowed to advance? | [Model acceptance standard](model-acceptance-standard.md) |
| How is candidate search governed? | [Exploration protocol](exploration-protocol.md) |
| How to rank across multiple live candidates? | [Next-priority evaluation](next-priority-evaluation.md) |
| How to test a claim with only a handful of regime episodes? | [Thesis Track](thesis-track-small-n.md) |
| Which Stage 9A candidate was prioritised, and why? | [Candidate-selection index](research-candidates/README.md) and [Cycle 1 record](research-candidates/2026-08-19-cycle-1.md) |
| Which new preregistrations exist? | [Research-protocol index](research-protocols/README.md) |
| What did consolidation feasibility v1 establish? | [Result](research-results/consolidation-support-feasibility-v1.md) |
| What did the properly-powered CTA v2 retest show? | [Result](research-results/cta-v2-pooled-trend-overlay.md) |
| Is the event-recomputing bootstrap machinery itself trustworthy? | [Type-I calibration](research-results/event-bootstrap-calibration-v1.md) |
| Where do non-contract brainstorm notes live? | [Brainstorm index](brainstorm/README.md) |
| Where do point-in-time codebase/methodology audits live? | [Audits index](audits/README.md) |
| Where are research-line/paradigm boundaries recorded, and why did a line pause? | [Stage closures index](stage-closures/README.md) |
| How is macro data governed? | [Macro data contract](adr/0006-macro-data-contract.md) |
| What data sources exist, are built, or are scoped-but-planned? | [Data layers catalog](data-layers.md) |
| How does a closed research result get onboarded into the live app, and what may never be shown as a live signal? | [ADR 0009 (accepted)](adr/0009-strategy-onboarding-contract.md) |
| What are the mechanical steps to onboard one new result, without reopening ADR 0009's design each time? | [Strategy library](strategy-library.md) |
| User's own term for the live app (Today/Symbol Research/Strategy Lab/Strategy Management) is "the trade desk" — looks the part (dark theme, chart markers, entry/exit state), but [identity.md](identity.md) is explicit it is not an execution system or alpha finder. "Make a result available on the trade desk" means: run [strategy-library.md](strategy-library.md)'s onboarding steps | [Strategy library](strategy-library.md) and [Product identity](identity.md) |
| What is the drafted consolidation study? | [Daily Consolidation Zone v1](research-hypotheses/daily-consolidation-zone-v1.md) |
| Why are contracts fixed this way? | [ADRs](adr/) |
| What changed by version? | [Changelog](../CHANGELOG.md) |

Component notes: [backend](../backend/README.md), [frontend](../frontend/README.md), [data](../data/README.md), and [generated outputs](../output/research/README.md).

## Resume sequence

1. Confirm `git status`, current version, and tests.
2. Read this checkpoint, then [product identity](identity.md), then the document for the active stage.
3. Preserve locked contracts unless creating a versioned ADR/protocol amendment.
4. Implement one bounded stage slice; update tests, roadmap, checkpoint, and changelog together.
5. Record research evidence as immutable results, not rewritten narrative.
