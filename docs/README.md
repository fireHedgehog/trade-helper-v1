# Documentation and resume checkpoint

This file is the authoritative entry point for a new agent or work session. Do not infer current work from the changelog.

## Checkpoint

| Field | Value |
|---|---|
| Version | `0.61.1` |
| Parent release | `0.37.0` (first Stage 8 acceptance candidate) |
| Current state | Nine Stage 9A/CTA-family protocols closed `not_material_or_not_consistent` this session (eight technical-pattern/calendar candidates plus CTA v2), each a different shape; Cycle 5 is closed in full; CTA v2 — a properly-powered pooled retest of CTA v1's own thesis — is also closed: materiality cleared but significance and the paired placebo test did not, with a disclosed dependency on 2008. A Type-I calibration study of the five event-recomputing bootstraps found no anti-conservative bias — several are measurably conservative — answering an external memo's concern, though a companion power calibration remains open. The single-asset/time-series line is now formally parked; `app.macro_pit` (`0.60.0`) closed ADR 0006's point-in-time engineering gap (clauses 2–4) and was then live-verified against the real FRED API (`0.61.0`, real `PAYEMS`/`DFII10` ingestion, three real API quirks found and fixed). A cross-sectional engine feasibility check (`0.61.0`) scaled `etf12_rotation_bootstrap` from `N=12` to `N=495` real equities with no code change, `engine_feasible`. Neither engine check authorizes any candidate — both are explicitly non-evidential |
| Verification | `289 passed` at `0.56.0` (calibration study is a standalone diagnostic script, not part of the pytest suite); `309 passed` at `0.61.0` (`0.58.0`/`0.59.0` were docs-only) |
| Completed | Stage 8; Stage 9A Cycles 1–5 each selected, locked, and executed to a closed result; TA Breakout v1, Wave Pull v1, ETF-12 cross-sectional rotation v1, Calendar Turn-of-Month v1, Calendar Day-of-Week v1, and Overnight Gap Continuation v1 locked, executed, and closed; CTA v2 picked up directly from Cycle 2, locked, executed, and closed; `Wave Pull`'s crash bug fixed and regression-tested; an independent, adversarially verified next-priority evaluation (2026-08-20) scored five options and surfaced Cycle 5, then a second solo-but-adversarially-self-checked evaluation scored CTA v2 above Fed put for the step after Cycle 5; Overnight Gap Continuation v1's and CTA v2's designs each passed adversarial review before any data was touched |
| Next product work | No queued research task. Fed put is the clear #2 priority behind CTA v2 (per the 2026-08-20 evaluation) but remains blocked on ADR 0006 plus two free-but-unbuilt data sources and a not-yet-built small-*n* Thesis Track statistical design. `S/R Bounce` needs a materially different construction to re-score, and a genuinely distinct one (round-number levels) is now known but blocked on an adjusted-vs-nominal-price data gap (ADR 0002). Overnight Gap Continuation v1's disclosed diagnostic suggests a reversal-shaped (not continuation) pattern that protocol could not test — a reversal-framed candidate would be new, independently justified work, and carries a live data-contamination concern (the same locked dataset already produced the diagnostic that suggests it). MACD and full Elliott Wave counting were assessed and not recommended — see [pending checklist](brainstorm/2026-08-19-pending-candidate-checklist.md) |
| Active research | None active. The single-asset/time-series research line is formally **parked** (not rejected) — see [stage-closures/2026-08-20-single-asset-time-series-line.md](stage-closures/2026-08-20-single-asset-time-series-line.md) for the full evidence inventory, lessons, and gate condition. The next line is explicitly undecided: cross-sectional/relative-performance work (Fed put and the wider [macro reaction-function narrative library](brainstorm/2026-08-20-macro-reaction-function-narrative-library.md), or a larger [cross-sectional-momentum extension](brainstorm/2026-08-20-cross-sectional-experiment-ideas.md) still blocked on Tier 4 paid point-in-time equity data) is a live candidate, not a default — it must clear the same scored evaluation CTA v2 did. `app.macro_pit` (`0.60.0`) closes the macro line's engineering blocker (ADR 0006 clauses 2–4) and is now live-verified (`0.61.0`) but authorizes nothing by itself: every macro candidate still needs its own hypothesis-engineering → Stage 9A score → preregistration before any signal use. A cross-sectional engine feasibility check (`0.61.0`, `engine_feasible`) similarly proves the panel-bootstrap engine scales to real equity breadth without authorizing any cross-sectional candidate — the Tier 4 survivorship-free data decision is unchanged and still unmade; Stage 9B remains gated |
| Parked operations | Stage 10 cron; Stage 11 deployment |
| Pending triage | 2026-08-19 methodology/implementation audit — H2 (non-atomic bar publication) fixed in `0.54.0`; 2 critical, 1 high (H1, the orphaned mutating `GET /api/today`), 5 medium, 4 low remain untriaged; see [audits/README.md](audits/README.md) |

The first real `0.37.0` acceptance run correctly ended `complete_with_errors`, but revealed two contract defects: settlement-based Yahoo futures were treated as equity candles, and a small invalid subset blocked every full-universe daily scan. Version `0.37.1` separates market context from the strategy universe, keeps equity validation strict, gives context bars an honest settlement contract, and permits daily discovery above a visible 90% coverage floor. The repaired real run then completed with zero failed/blocked model jobs: five new and two reused full-universe snapshots; empty watchlist scopes were honestly skipped. Saved snapshots retain exact exclusions and fingerprints. Formal experiments remain governed by their locked coverage rules.

Local-optimum guard: Stage 8 is closed. Do not add more infrastructure or UX polish unless a concrete defect blocks research. Cycle 1 is closed `not_evaluable`; Cycle 2, Cycle 3, TA Breakout v1, Wave Pull v1, ETF-12 cross-sectional rotation v1, Calendar Turn-of-Month v1, Calendar Day-of-Week v1, Overnight Gap Continuation v1, and CTA v2 are all closed `not_material_or_not_consistent`, each for a different reason — read each result's own reading before assuming they generalize to each other. CTA v2 specifically: materiality cleared and all three lookback variants agreed in sign, but significance and the paired placebo test both failed, and the positive point estimate depends materially on 2008 — an informative null, closing the power-limitation gap the 2026-08-19 audit found in CTA v1, not a repair of CTA v1 itself. None licenses a reflexive follow-up — do not widen a window/threshold/tolerance/horizon grid, add a pooled version, or otherwise retry any same claim in reaction to its result; any such attempt is a new, independently justified candidate, not a repair. The single-asset/time-series line these ten results belong to is now formally parked; see [stage-closures/2026-08-20-single-asset-time-series-line.md](stage-closures/2026-08-20-single-asset-time-series-line.md) for the full inventory and lessons before proposing anything back into this line. The next line (Fed put, or a scored cross-sectional-momentum candidate) is a deliberate choice for the user, gated by the same scorecard discipline as every candidate before it, not a default.

Heavy statistical work is intentionally paused. On resumption, first operationalize candidate theses, audit benchmark/universe suitability, and only then apply the model acceptance scorecard. Read the protocol, CTA result, audit, and backlog before experiment design. Do not tune CTA v1 after observing its rejection.

## Non-negotiable state

- Product purpose: decide `reject`, `revise`, or `continue research`; never imply validated profit.
- Default project benchmark: Passive ETF-12 v1; every new protocol audits suitability; SPY and cash remain references.
- CTA v1: rejected under its locked protocol; this does not reject trend following generally.
- Execution: signal on completed close `N`, fill at next available open `N+1`.
- Watchlists: user-selected symbols persist per strategy and show lifecycle state.
- Candidate tabs: full-universe new-entry candidates per model, plus intersections; they are not watchlists.
- Data refresh and strategy runs are explicit actions, not navigation side effects.
- Macro series are non-tradable context under [ADR 0006](adr/0006-macro-data-contract.md); they never generate candidates until point-in-time data and a preregistered hypothesis exist.
- Cron, paper/live trading, brokers, and AWS remain out of scope.

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
| How does a narrative become a measurable hypothesis? | [Hypothesis engineering](hypothesis-engineering.md) |
| How is a candidate selected and allowed to advance? | [Model acceptance standard](model-acceptance-standard.md) |
| How is candidate search governed? | [Exploration protocol](exploration-protocol.md) |
| How to rank across multiple live candidates? | [Next-priority evaluation](next-priority-evaluation.md) |
| Which Stage 9A candidate was prioritised, and why? | [Candidate-selection index](research-candidates/README.md) and [Cycle 1 record](research-candidates/2026-08-19-cycle-1.md) |
| Which new preregistrations exist? | [Research-protocol index](research-protocols/README.md) |
| What did consolidation feasibility v1 establish? | [Result](research-results/consolidation-support-feasibility-v1.md) |
| What did the properly-powered CTA v2 retest show? | [Result](research-results/cta-v2-pooled-trend-overlay.md) |
| Is the event-recomputing bootstrap machinery itself trustworthy? | [Type-I calibration](research-results/event-bootstrap-calibration-v1.md) |
| Where do non-contract brainstorm notes live? | [Brainstorm index](brainstorm/README.md) |
| Where do point-in-time codebase/methodology audits live? | [Audits index](audits/README.md) |
| Where are research-line/paradigm boundaries recorded, and why did a line pause? | [Stage closures index](stage-closures/README.md) |
| How is macro data governed? | [Macro data contract](adr/0006-macro-data-contract.md) |
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
