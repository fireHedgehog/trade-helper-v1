# Documentation and resume checkpoint

This file is the authoritative entry point for a new agent or work session. Do not infer current work from the changelog.

**Audience split, stated once (`2026-08-21`) after it was violated:** the root [`README.md`](../README.md) is the one file a public GitHub visitor actually lands on — human-facing only, single tone, no agent-directed process notes, no "a prior session did X" commentary, ever. Everything under `docs/` (this file included) is the internal operating manual — dense, technical, written for whoever is actively doing the work, human or agent. Calibration/priority/process guidance belongs here or in [identity.md](identity.md), never in the root README.

## Checkpoint

Detail lives in [CHANGELOG.md](../CHANGELOG.md) (per-version) and [research-program.md](research-program.md) (per-chapter) — this table is a compact pointer, not the record. If it and the CHANGELOG disagree, the CHANGELOG wins; fix this table.

| Field | Value |
|---|---|
| Version | `0.87.0` |
| Parent release | `0.37.0` (first Stage 8 acceptance candidate) |
| Current state | [Chaptered research program](research-program.md) — see CHANGELOG for detail per version. **Chapter 4 is the default evaluation for any new candidate now** (hard rule, [identity.md](identity.md)). **Ensemble-construction engine implemented and smoke-tested** (`backend/app/ensemble.py`, [ADR 0010](adr/0010-long-short-ensemble-construction.md) + [design doc](ensemble-construction-engine-v1.md)): real data, all constraints held exactly (100.00% gross, ~0% net) — [smoke-test result](research-results/ensemble-smoke-test-v1.md). `amihud_illiquidity` is the strongest live candidate (Sharpe `0.29`, confidence multiplier `0.33`, entirely positive CI — [result](research-results/amihud-illiquidity-chapter4-v1.md)); `atr_normalized`'s cross-sectional form does **not** survive point-in-time correction (confidence multiplier `0.0` — the own-history "ATR Vol Premium" Tier A strategy is a different, unaffected claim, [surveyed separately](research-results/atr-vol-premium-survey-v1.md)). Sector rotation closed a converging double-null. Chapters 1/3 paused. Chapter 5 ([ADR 0008](adr/0008-bounded-paper-trading.md)) accepted, not built. |
| Verification | `444 passed` at `0.87.0` |
| Next product work | (1) Find a second real cross-sectional candidate — `atr_normalized` no longer qualifies; `amihud_illiquidity` needs a genuinely independent partner for the ensemble to mean anything. (2) `amihud_illiquidity`: clause 1 (mechanism — Amihud 2002's own literature) + clause 2 (EV + uncertainty band, already computed) before a formal Chapter 4 proposal. (3) Sector/cluster caps (ADR 0010 §5) unimplemented in `ensemble.py` — needed before any real deployment. (4) Chapter 2 non-sector ideas (CS-02/03/04/05/09) if picked back up. (5) `factor-zoo-v1` still deferred from Strategy Management. (6) Earnings-dates or SEC EDGAR fundamentals data layer — neither started, [data-layers.md](data-layers.md). (7) ADR 0008 implementation — blocked on an Alpaca account. |
| Parked operations | Stage 10 cron; Stage 11 deployment |
| Pending triage | 2026-08-19 audit — 2 critical, 1 high, 5 medium, 4 low untriaged; see [audits/README.md](audits/README.md) |

Local-optimum guard: Stage 8 is closed, don't add infrastructure/UX polish absent a concrete defect. The single-asset/time-series line is parked — read [stage-closures](stage-closures/2026-08-20-single-asset-time-series-line.md) first. No closed result licenses a reflexive follow-up (wider window, pooled retry, same claim again) — that's always a new, independently justified candidate. Don't tune CTA v1 after its rejection. Don't skip [next-priority-evaluation.md](next-priority-evaluation.md) when more than one candidate is live.

## Non-negotiable state

- **Chapter 4 first, always, for any new candidate** (real backtest, Sharpe/CAGR/drawdown, EV confidence interval). **Chapters 1-3 are paused, not deleted** — they run only when the user explicitly asks for a falsification test on that specific candidate. Full statement: [identity.md](identity.md)'s Calibration section, tightened `2026-08-21` after this was violated three times in one session.
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
| Can a Chapter 4 ensemble be long-short, and how is it constructed (alpha model, risk model, optimizer)? | [ADR 0010 (accepted)](adr/0010-long-short-ensemble-construction.md) — decision and reasoning |
| What is the exact, implementable design of the ensemble-construction engine (formulas, function signatures, worked example)? | [ensemble-construction-engine-v1.md](ensemble-construction-engine-v1.md) |
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
