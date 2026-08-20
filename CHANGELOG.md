# Changelog

Concise version ledger. Research decisions and exact contracts belong in `docs/`; Git preserves file-level implementation history.

## 0.65.0

Locked, executed, and closed Fed put: yield-stress precursor v1 --
Thesis Track's first real use. No trade, no signal, no Stage 9B
authorization.

- Locked [docs/research-protocols/fed-put-yield-stress-precursor-v1.md](docs/research-protocols/fed-put-yield-stress-precursor-v1.md): `score(t) = z_10Y(t) - abs(z_2Y(t))` (756-session trailing z-scores), 4 episodes (QE1/2/3, COVID QE) dated from the Fed's own balance-sheet-policy timeline, verified live rather than from memory -- never from the yield series itself. Real, disclosed PIT finding along the way: `DFII10`'s ALFRED "revisions" are re-publication timestamps, not value changes, and early `release_datetime`s reflect FRED backfill timing, not market-known timing -- for same-day-published Treasury yields, `fred.py`'s final-revised series with the trading date itself is the better-justified PIT convention here, not `macro_pit`'s ALFRED mechanism.
- Result: `not_evaluable`, `p=0.989` per the pre-committed reading rule. Disclosed non-gating diagnostic, same weight as [Overnight Gap Continuation v1](docs/research-results/overnight-gap-continuation-v1.md)'s: `4`/`4` real QE episodes decisively opposite-signed, not merely null -- every real launch was preceded by both `2Y` and `10Y` falling sharply together (flight-to-safety), not "`10Y` high, `2Y` contained." QE has historically followed a broad yield collapse, not a long-end-specific spike; the motivating narrative has no precedent among the episodes tested. See [result](docs/research-results/fed-put-yield-stress-precursor-v1.md).
- Closes Fed put's active-research status. A follow-up needs a new, independently-justified mechanism, not a retry of this one.

## 0.64.0

Added `app.thesis_track`: the placebo-in-time randomization engine
[thesis-track-small-n.md](docs/thesis-track-small-n.md) described but
didn't implement. General-purpose -- any small-*n* episode candidate
supplies its own per-window statistic; this handles placebo-window
construction (excluding real episodes) and the randomization p-value.
`trailing_zscore`/`yield_stress_score` help build Fed put's specific
score. 8 new tests, 332 passed. No protocol locked yet, no data touched
beyond what was already ingested.

## 0.63.2

Docs-only, user-directed. Fed put reframed: claim is now "yield stress
precedes Fed QE" (forward-looking precursor), not "Fed support causes
yield reversal" (well-known, not a real edge). Treasury buybacks dropped
entirely from this candidate -- different institution/mandate than the
Fed; `app.treasury_buybacks` stays built and live-verified, just unused
for now. Score unaffected (14/16, Cycle 6 update appended, not rewritten).

Added [policy-exposure-industrial-factor.md](docs/brainstorm/2026-08-20-policy-exposure-industrial-factor.md):
distilled from an external note (CHIPS Act/Intel-motivated), explicitly
idea-stage, no ADR blocking it -- not yet a formed hypothesis. Distinct
future line from Fed put.

## 0.63.1

Docs-only, user-caught correction. Buybacks (one program 2000-02, dormant
since, restarted 2024-04) give ~1 usable episode alone -- not a co-equal
episode source with SOMA/QE holdings (full history since 2008). Fixed
[thesis-track-small-n.md](docs/thesis-track-small-n.md) and the
[Fed put memo](docs/brainstorm/2026-08-19-fed-put-long-end-reversal.md):
episodes come from QE program dates; buybacks are recent corroboration
only.

## 0.63.0

Closed Cycle 6's three Fed put gaps. No preregistration, no strategy, no
signal.

- Ingested `TREAST`/`TREAS10Y` (Fed SOMA holdings, incl. long-end bucket) live via `macro_pit`.
- New `app.treasury_buybacks`: ingests `fiscaldata.treasury.gov`'s buyback operations (free, keyless, not on FRED). Settled-only, `operation_date`-as-known PIT convention (disclosed, not ALFRED-vintage-indexed -- API exposes no per-field revision timestamp). `is_long_end` operationalizes the memo's open "30Y or belly-of-curve" question as maturity-bucket upper bound >=20Y. Live: 214 settled operations, 66 long-end, earliest 2024-04-03.
- Added [thesis-track-small-n.md](docs/thesis-track-small-n.md): placebo-in-time randomization inference for ~3-5 dependent regime episodes, replacing block-bootstrap (which would pseudo-replicate on daily counts) for this shape of claim. Episodes dated by policy record, never by outcome-data changepoints. Mandatory power pre-commitment: likely underpowered by construction at this *n*, disclosed before any data use, not discovered after.
- 15 new tests, 324 passed.

## 0.62.0

Cycle 6: first use of `next-priority-evaluation.md`. Fed put scores
14/16, sole eligible candidate — [record](docs/research-candidates/2026-08-20-cycle-6.md).
Cross-sectional disqualified (Data readiness 0, Tier 4 unpurchased);
6-variable macro library not yet operationalized. Verified live: Fed
SOMA holdings (`TREAST`/`TREAS10Y`) are on FRED, ingestible today;
Treasury buybacks are not, need a new `fiscaldata.treasury.gov` module.
Not preregistered -- data/Thesis-Track design gaps remain. No code, no
market data touched.

## 0.61.1

Docs-only. Two gaps found by cold-reading the checkpoint as a fresh agent
would: cross-sectional idea library was unlinked from `docs/README.md`
(fixed); "next-priority evaluation" (used twice this session) had no
template (added [next-priority-evaluation.md](docs/next-priority-evaluation.md),
indexed in the document-authority table).

## 0.61.0

Proved both new engines actually run: a cross-sectional feasibility check
at real equity scale, and a live (not mocked) macro point-in-time
ingestion. No Stage 9A candidate, no strategy, no trade -- both are
explicitly non-evidential infrastructure checks, disclosed as such
throughout.

- **Cross-sectional engine feasibility.** Locked and executed [cross-sectional equity momentum feasibility v1](docs/research-protocols/cross-sectional-equity-momentum-feasibility-v1.md): `etf12_rotation_bootstrap` (already asset-count-agnostic, no code change needed) scaled from ETF-12's `N=12` to `N=495` real S&P 500/Nasdaq-100/XL-sector-ETF symbols already sitting in `data/market.db`. `engine_feasible`: `2,000` resamples completed in under two minutes, well-formed correlation/p-value output. Explicitly non-confirmatory for two disclosed reasons, both stated up front in the protocol before execution: survivorship bias in today's-membership-applied-to-history universe, and a pre-lock parameter peek during a timing probe -- caught and disclosed rather than hidden, with the locked run deliberately using different, independently-motivated parameters (Jegadeesh & Titman 1993's 6-month/1-month momentum horizon) rather than what was peeked at. Result in [docs/research-results/cross-sectional-equity-momentum-feasibility-v1.md](docs/research-results/cross-sectional-equity-momentum-feasibility-v1.md).
- **Macro engine live verification.** `app.macro_pit` (`0.60.0`) ingested real FRED data for the first time: `PAYEMS` (`13,685` vintage rows, 6 genuine revisions of the 1939-01 observation alone spanning 1961-2003) and `DFII10` (`17,776` rows). `value_asof` demonstrated returning different values for the same reference period at two different real decision dates. Found and fixed three real FRED API behaviors invisible from documentation alone: a 2,000-vintage-per-request cap on high-frequency series (`fetch_all_vintages` now recursively bisects and merges on that specific error), a same-day-or-sentinel-only `realtime_end` constraint (bisection midpoints clamped two days before local today, since FRED's server clock and this machine's disagreed by at least a day live), and a range-predates-series-existence case that is its own 400 error rather than an empty result (now handled as the zero-observation case it is). See [ADR 0006](docs/adr/0006-macro-data-contract.md)'s updated Consequences.
- Added `key_library` table (`store.py`; `set_key`/`get_key`/`list_key_names`) so `FRED_API_KEY` (or any future provider key) persists locally in the gitignored database instead of requiring an env var every session; `macro_pit._api_key()` checks the env var first, then the stored key. 6 new tests. `309 passed`.

## 0.60.0

Built the point-in-time macro data engine ADR 0006 has required since
`0.44.0`; no strategy, no signal, no research decision — infrastructure
only, unblocking the macro-narrative line, not authorizing it.

- Added `backend/app/macro_pit.py`: ingests every historical FRED revision of a series via the official FRED API's `realtime_start`/`realtime_end` vintage mechanism (`1776-07-04`-`9999-12-31`, the same convention the `mortada/fredapi` reference client's `get_series_all_releases` uses -- verified against FRED's own docs and that client's source before writing this, not from memory), distinct from `fred.py`'s final-revised `fredgraph.csv` display path. `to_revision_indexed` assigns `revision_index` k=0,1,2,... per reference period ordered by `realtime_start`; `value_asof(series_id, decision_datetime)` returns ADR 0006's vintage $\mathcal{V}_t$ directly -- the latest revision per reference period visible at or before a decision time.
- Added `macro_vintages` table (`store.py`) and `upsert_macro_vintages`/`macro_vintage_rows`: a `(series_id, reference_period, revision_index)` tuple is immutable once stored -- re-ingesting the same vintage is a no-op, a conflicting value at an already-stored tuple raises and rolls back the whole batch, same atomicity discipline `upsert_bars` already established for market bars.
- No new fingerprint store: a macro protocol's `value_asof` output feeds the same `data_sha256`-at-execution-time pattern every `run_*.py` script already uses, satisfying ADR 0006 clause 4's provenance requirement without new machinery.
- Requires a free, self-registered `FRED_API_KEY` (not obtainable by an agent); no live ingestion has been run against the real API yet. 12 new tests (`test_macro_pit.py`, `test_store.py`) are fully mocked -- they verify the parsing/indexing/immutability logic, not the real API's live response shape. `301 passed`.
- Updated [ADR 0006](docs/adr/0006-macro-data-contract.md)'s status and Consequences: clauses 2-4 implemented; clause 8 (scheduled-release calendar) explicitly scoped out (not needed for historical backtesting, only live freshness monitoring); clauses 5-7 and 9 remain per-hypothesis obligations this engine does not and cannot satisfy on its own. Cross-referenced from `backend/README.md` and the [pending candidate checklist](docs/brainstorm/2026-08-19-pending-candidate-checklist.md)'s Tier 3 entry.
- This unblocks the engineering gap behind both the [Fed put](docs/brainstorm/2026-08-19-fed-put-long-end-reversal.md) memo and the wider [macro reaction-function narrative library](docs/brainstorm/2026-08-20-macro-reaction-function-narrative-library.md) (`0.59.0`) at once, per that memo's own point about shared-gate leverage -- it authorizes none of them. The next step for any of them is still exploration-protocol -> Stage 9A scoring -> preregistration, unchanged.

## 0.59.0

Added a brainstorm memo broadening "Fed put" into a named macro
reaction-function narrative family; no code, no market data, no research
decision.

- Added [docs/brainstorm/2026-08-20-macro-reaction-function-narrative-library.md](docs/brainstorm/2026-08-20-macro-reaction-function-narrative-library.md): the user's own narrative cluster (yield curve, oil, gold as a "Fed incompetency trade," a DCF/discount-rate transmission mechanism, CPI-target flexibility under economic stress) named against real literature -- equity duration (Dechow, Sloan & Soliman 2004; Weber 2018) as the mechanical, intent-free channel; a 7-row free-data state-variable table (real yields/breakevens, 2s10s, HY OAS/NFCI, gold, oil, DXY, Taylor-rule gap); and the ADR 0006 clause-5 level-vs-surprise distinction, flagging that a surprise-based estimand needs a consensus-forecast history that is typically a paid feed.
- Cross-referenced from the two existing narrower macro brainstorm notes ([fed-put-long-end-reversal.md](docs/brainstorm/2026-08-19-fed-put-long-end-reversal.md), [long-end-yield-shock.md](docs/brainstorm/2026-08-19-long-end-yield-shock.md)) as the wider family both sit inside, rather than duplicating or replacing either.
- Named a repeating shape across both of today's idea libraries: a single free/cheap engineering gate (here, ADR 0006's ALFRED point-in-time ingestion; in [0.58.0](docs/brainstorm/2026-08-20-cross-sectional-experiment-ideas.md), Tier 4 point-in-time equity data) unlocks a whole narrative cluster at once, not one candidate -- a materially different cost/benefit case than scoring any single item in isolation.

## 0.58.0

Added a brainstorm memo distilling an external cross-sectional-experiment
idea note; no code, no market data, no research decision.

- Added [docs/brainstorm/2026-08-20-cross-sectional-experiment-ideas.md](docs/brainstorm/2026-08-20-cross-sectional-experiment-ideas.md): eleven cross-sectional/relative-value ideas (residual momentum, momentum fragility, quiet-vs-loud winner, breadth, dispersion regime, correlation crowding, leadership diffusion, drawdown recovery, macro sensitivity rotation, factor conflict) reduced to a compact table, kept as a freely-editable idea library rather than the source note's own prose.
- Flagged that the note's own "positive control" (CS-01, raw cross-sectional momentum) is not untested ground: [ETF-12 rotation](docs/research-results/etf12-cross-sectional-rotation-v1.md) already ran the same estimand shape at `N=12` and closed a clean, decisive null (`ρ=0.045`, `p=0.266`) -- informative, but not a verdict on the same claim at real equity-universe breadth (Grinold-Kahn's whole premise is that breadth changes the answer).
- Reframed the "do we need finer cost-tier granularity" question the user raised: checked against all eleven ideas, the existing informal `T0`-`T4` ladder in [docs/brainstorm/2026-08-19-pending-candidate-checklist.md](docs/brainstorm/2026-08-19-pending-candidate-checklist.md) is fine-grained enough already. Six of the eleven ideas (CS-01, 02, 03, 04, 05, 09) collapse onto the *same* single blocker -- Tier 4's point-in-time equity universe data, no new data type needed since volume is already stored -- which is a materially higher-leverage read of that one backlog line than treating it as gating just one candidate. Two ideas (leadership diffusion, correlation-crowding-via-labeled-groups) surface a data gap not previously named: sector/industry classification. One (macro sensitivity rotation) is not new at all -- it is Fed put's existing ADR 0006 gate under a different name.

## 0.57.0

Added the Stage Closure convention and formally parked the single-asset/
time-series research line; no code, no market data, no new research
result.

- New `docs/stage-closures/` folder, same pattern as `audits/` and `brainstorm/` (indexed, templated, dated files): a durable paradigm-boundary record written only at a genuine research-line closure, distinct from a Stage 8/9/10/11 transition. Six fixed sections per record: the question asked, complete evidence inventory, lessons that must never be re-litigated, closed-vs-parked (never left ambiguous), the explicit substantive gate condition (never fatigue or token cost alone), and the next line's opening statement (never crowning an unscored successor).
- Wrote [docs/stage-closures/2026-08-20-single-asset-time-series-line.md](docs/stage-closures/2026-08-20-single-asset-time-series-line.md): closes (parks, not rejects) the per-asset absolute-prediction line -- ten results (CTA v1, consolidation feasibility, SMA Cross v1, RSI, TA Breakout, Wave Pull, both calendar candidates, Overnight-Gap, CTA v2). Gate condition: mechanism-space exhaustion on the current 12-asset data shape across five-plus distinct, independently-falsified mechanism families, not cost or fatigue -- corroborated by the 0.56.0 calibration study ruling out a shared broken-machinery explanation. Explicitly does not crown cross-sectional momentum or Fed put as the next line; both remain live, unscored candidates.
- Verified before writing: this closes a research line inside Stage 9A, not Stage 9A itself, and touches no ADR (none of them govern which research line is active) and no Stage 9A gate (which governs candidate selection, not a requirement to keep testing one mechanism family indefinitely).
- Cross-referenced from the checkpoint, document-authority table, and the "Local-optimum guard" paragraph in `docs/README.md`.

## 0.56.0

Ran a Monte Carlo Type-I error calibration of the five event-recomputing
bootstrap variants; no research candidate, no market data touched, no
Stage 9A/9B decision.

- Motivated by an external research memo's specific, checkable claim: the event-recomputing bootstrap extension (SMA Cross v1, RSI, TA Breakout, Wave Pull, Overnight-Gap) has planted-effect sanity tests but no verified Type-I error rate. Added [docs/brainstorm/2026-08-20-ensemble-factor-vocabulary.md](docs/brainstorm/2026-08-20-ensemble-factor-vocabulary.md) distilling that memo's genuinely new content (this finding, plus reusable IC/breadth vocabulary) separately from what the memo re-invented under new names (its Layer A-E taxonomy already exists as hypothesis-engineering.md's information classification).
- Added `backend/app/calibrate_event_bootstraps.py`: 300 independent GARCH(1,1) zero-mean synthetic null series (realistic volatility clustering, no genuine directional predictability by construction), each candidate's own production bootstrap function called unmodified. Two disclosed deviations from locked production parameters (resamples 5,000 -> 1,000; series length fixed at 3,000 bars, both justified in the report), everything else unchanged.
- Result: no candidate showed an inflated (anti-conservative) rejection rate. SMA Cross v1 (`0.33%`) and Wave Pull v1 (`0.00%`) were measurably conservative -- their entire Wilson 95% CI sits below the nominal `5%`; RSI (`2.75%`) and TA Breakout (`2.67%`) and Overnight-Gap (`2.33%` on both statistics) are consistent with correct calibration. Wave Pull's `58/300` (`~19%`) insufficient-event exclusion rate corroborates, with a number, what the real result already disclosed qualitatively (the impulse precondition is genuinely rare). Recorded in [docs/research-results/event-bootstrap-calibration-v1.md](docs/research-results/event-bootstrap-calibration-v1.md), which also states the honest caveat this raises rather than only the good news: conservative calibration is often associated with reduced power, and no power calibration has been run for these five candidates at their real effect sizes -- a natural companion study, not yet scheduled.
- This does not reopen any of the five closed results; if anything it strengthens confidence their nulls were not false positives waiting to happen.

## 0.55.0

Picked up CTA v2 (Cycle 2's Candidate C) directly, designed and locked its
protocol after an independent, adversarially-verified next-priority
evaluation, then executed and closed it. No strategy implemented, no trade,
no cost/execution modelling.

- Amended [docs/research-candidates/2026-08-19-cycle-2.md](docs/research-candidates/2026-08-19-cycle-2.md) rather than minting a new cycle: corrected the engineering-cost framing (a weight-vector construction and portfolio-return aggregator was needed, not a from-scratch engine) and re-read channel 1's rationale against the 2026-08-19 audit — that audit found CTA v1's design underpowered, not the underlying thesis false, and Candidate C's own record already stated its estimand exists specifically to fix that power problem. Channel 2 (vol-scaled de-risking) is retained only as the required shared placebo, not independent rationale, given SMA Cross v1's confound finding.
- Locked [docs/research-protocols/cta-v2-pooled-trend-overlay.md](docs/research-protocols/cta-v2-pooled-trend-overlay.md): a pooled, vol-scaled, long-only trend overlay across all 12 ETFs, tested against a daily-rebalanced no-cost equal-weight benchmark and a required direction-blind volatility-only placebo. Two design corrections made before locking, both recorded rather than silently applied: substituted a close-only volatility proxy for Cycle 2's original "ATR" phrasing (no function in this module has high/low access, the same simplification every prior close-derived candidate made), and strengthened the placebo gate from a bare point-estimate comparison to a paired significance test — the exact fix Overnight-Gap's pre-lock review already proved necessary for two correlated statistics, applied here for free since both series are already realized (no event-recomputation needed).
- The significance test needed no new bootstrap machinery at all: the estimand is a single pooled daily excess-return series, structurally identical in shape to CTA v1's original per-symbol statistic, so `circular_block_bootstrap_p_value` and `holm_adjust` are reused completely unchanged for both the primary test and the primary-vs-placebo paired test.
- Implemented `cta_v2_trailing_vol`, `cta_v2_signal_matrix`, `cta_v2_weight_matrix`, `cta_v2_placebo_weight_matrix`, `cta_v2_portfolio_return`, `cta_v2_benchmark_return`, and `cta_v2_bootstrap` in `backend/app/research.py`. Added 6 unit tests, including a planted-favourable-effect-vs-pure-noise sanity check and a mismatched-calendar rejection test.
- Found and fixed `test_api.py::test_health`'s hardcoded `"0.53.0"` expected version — broken by `0.54.0`'s own version bump but not caught before that commit was pushed, since the suite wasn't re-run after that specific edit. Replaced the hardcoded string with a direct import of `app.version.APP_VERSION` so this cannot recur on a future bump.
- Result: `not_material_or_not_consistent`. The primary variant (`SMA_252`) cleared materiality (`+2.18pp` annualized, floor `+1.0pp`) and beat both the benchmark and the placebo on point estimate, but failed significance (raw `p=0.231`, Holm `p=0.692` across the 3-variant family) and the paired placebo test (`p=0.116`). All three lookback variants were consistently positive-signed. A disclosed, non-gating diagnostic found the positive point estimate depends materially on 2008 — excluding it flips the primary variant's mean daily excess from `+8.64e-5` to `-1.24e-5`. Recorded in [docs/research-results/cta-v2-pooled-trend-overlay.md](docs/research-results/cta-v2-pooled-trend-overlay.md).
- Nine negative results this session (including CTA v1's own prior rejection), nine different reasons. Unlike every technical-pattern/calendar candidate this session, this one is a properly-powered retest of the project's own founding thesis, not a search for a new mechanism — it closes a loop the 2026-08-19 audit opened, rather than extending the search further.

## 0.54.0

Fixed `store.py::upsert_bars`'s non-atomic publication defect (2026-08-19 audit's H2 finding); no research conclusion changed.

- `upsert_bars` was `INSERT OR REPLACE` keyed on `(symbol, date)`: rows already stored but absent from an incoming fetch were never removed. Because `auto_adjust=True` rebases a symbol's entire history on every dividend, a truncated or partial fetch (Yahoo returning a shorter response, a reused ticker, a bad manual `--period`) could leave older rows on a stale adjustment vintage sitting next to freshly adjusted new rows — a silent splice `validate_bars` cannot detect, since a level discontinuity at the seam is a structurally valid OHLC series. This was the precise failure `data_management.py`'s own docstring and ADR 0002 already claimed was prevented ("atomic per symbol"), but the code did not yet enforce it.
- `upsert_bars` now replaces each symbol's entire row set per call (`DELETE` then insert, inside the existing single-transaction `connect()` block) instead of merging by date, and rejects — before writing anything — any symbol whose incoming batch would start later or contain fewer rows than what is already stored, with a new `allow_shrink=True` escape hatch for an intentional rebuild. All three live callers (`fetch.py`, `data_management.py`'s refresh manager, `fred.py`) always request full history in normal operation, so none needed a call-site change.
- Added four regression tests: replacement-not-merge on an identical date range, rejection of a truncated batch that would have shrunk 3 stored rows to 1, a multi-symbol batch where one offending symbol correctly rolls back the *entire* call rather than partially publishing the other symbol, and the `allow_shrink=True` escape hatch. `284 passed`.
- H1 (the orphaned mutating `GET /api/today` endpoint), the two critical CTA v1 statistical findings, and the remaining medium/low findings remain untriaged; see [docs/audits/README.md](docs/audits/README.md).

## 0.53.0

Designed, adversarially pre-lock-reviewed, locked, executed, and closed Stage 9A Cycle 5's final candidate: Overnight Gap Continuation v1. Closes Cycle 5 in full. No strategy implemented, no trade, no cost/execution modelling.

- The first candidate this session whose event depends on TWO return components of the same asset (overnight return, open vs. prior close; intraday return, close vs. same-day open) rather than one, requiring a genuinely new joint-paired block resampling design: every resample draws one shared block-index sequence and applies it to both components at once, preserving their real day-to-day pairing — the same principle ETF-12 rotation used across assets, applied here across return components within one asset.
- Before locking the specification or touching any market data, ran an independent adversarial pre-lock code review: three agents, three lenses (statistical/methodological soundness, line-by-line implementation correctness, adversarial test-coverage), zero shared context between them. Found and fixed six real, well-verified issues: (1) the overnight component's undefined first observation was silently diluting its own expanding-quantile threshold calibration, asymmetric against the intraday component — fixed via NaN-padding excluded by `_expanding_quantile`'s own NaN-skipping; (2) the placebo gate was a bare point-estimate inequality with no real statistical backing against a generic confound — fixed by adding `p_gap_vs_placebo`, a genuine paired-null significance test computed at near-zero marginal cost since both components are already jointly resampled; (3) signing forward returns by each event's own gap direction could mask a real, directionally asymmetric effect — fixed by adding a non-gating up-gap/down-gap diagnostic breakdown; (4) the protocol's own lock checklist required a test proving a planted decorrelated effect is not falsely detected, which was missing — added, exercising the full bootstrap pipeline; (5) a near-degenerate (tied-at-zero) trailing history would collapse the expanding-quantile threshold and flag almost every day as an event — empirically verified (98% vs. an intended ~10%) and fixed with a strictly-positive-threshold guard; (6) non-finite or non-positive prices were unguarded and could propagate NaN/Inf into a spuriously significant p-value while distorting other assets' Holm-adjusted p-values in the same family — fixed with explicit input validation.
- Locked [docs/research-protocols/overnight-gap-continuation-v1.md](docs/research-protocols/overnight-gap-continuation-v1.md), recording the full pre-lock verification disposition. Implemented `gap_and_intraday_returns`, `overnight_gap_event_mask`, `_circular_block_resample_indexes`, `_signed_mean_forward_return`, `_gap_track_events_and_signs`, `_gap_track_forward_return`, `_split_by_gap_direction_forward_return`, and `overnight_gap_bootstrap` in `backend/app/research.py`. Added 10 unit tests, including the protocol-mandated decorrelated-null test and a degenerate-tied-history regression test.
- Result: `not_material_or_not_consistent` — the most decisive negative of the session. `12`/`12` assets showed a *negative* signed forward return, the opposite sign from the continuation hypothesis, not merely small or mixed. `0`/`12` cleared materiality; `0`/`12` beat the strengthened placebo gate. `3`/`12` assets (`DBC`, `IEF`, `TLT`) passed the old bare point-estimate placebo comparison but failed the new paired significance test (`p=0.34`-`0.48`), directly validating the pre-lock review's own concern that the bare inequality alone had little real discriminating power. A disclosed, non-gating diagnostic found down-gap days mostly bounce back (positive raw forward return on `7`/`12` assets) rather than continue falling — a reversal-shaped pattern this protocol was not designed to test and cannot claim. Recorded in [docs/research-results/overnight-gap-continuation-v1.md](docs/research-results/overnight-gap-continuation-v1.md).
- Eight negative results this session, eight different reasons. Cycle 5 is closed in full; no research task is queued next by default.

## 0.52.0

Picked up Stage 9A Cycle 5's Candidate B (day-of-week calendar effect) directly from its existing selection record, locked, executed, and closed. No strategy implemented, no trade, no cost/execution modelling.

- Locked [docs/research-protocols/calendar-day-of-week-v1.md](docs/research-protocols/calendar-day-of-week-v1.md): a Monday-only underperformance claim (French 1980), not a five-way weekday scan, to avoid a new multiple-comparisons dimension. Picked up directly from [Cycle 5](docs/research-candidates/2026-08-20-cycle-5.md) without minting a new selection cycle, the same precedent as TA Breakout v1.
- Implemented `dow_event_mask` and `dow_bootstrap` in `backend/app/research.py`, reusing `tom_daily_differential` and `tom_volatility_diagnostic` unchanged from Calendar Turn-of-Month v1 — only the event mask (weekday, not month-position) and the bootstrap's test direction (negative/underperformance, matching the actual literature claim rather than silently reusing Turn-of-Month's positive-direction convention) differ. Added 6 unit tests, including a hand-computed-calendar fixture and a check that the flipped test direction doesn't spuriously fire on pure noise.
- Result: `not_material_or_not_consistent`. `969`-`1,588` Mondays per asset ruled out a power limitation. `0`/`12` cleared materiality and Holm-corrected significance simultaneously, but the direction was notably more consistent than Turn-of-Month v1's near-even split — `9`/`12` assets negative, matching the literature's predicted sign — and `DBC` reached raw `p=0.048` on a `-0.071%` daily differential, the only raw-significant single-asset result at the conventional `0.05` threshold across both calendar experiments this session; its Holm-adjusted `p=0.578` did not survive correction. A locked, non-gating diagnostic also found `8`/`12` assets have modestly higher realized volatility on Mondays than other days, disclosed but not further interpreted. Recorded in [docs/research-results/calendar-day-of-week-v1.md](docs/research-results/calendar-day-of-week-v1.md).
- Seven negative results, seven different reasons this session. Overnight-gap conditioning remains the one eligible, unexecuted Cycle 5 candidate, blocked on a new joint-resampling design step; no research task is queued next by default.

## 0.51.0

Ran an independent, adversarially verified next-priority evaluation, then selected, locked, executed, and closed Stage 9A Cycle 5's turn-of-month calendar effect. No strategy implemented, no trade, no cost/execution modelling.

- After rotation closed all five Tier 0/1/2-ready checklist items, ran a multi-agent evaluation of five next-priority options (CTA v2's engine, S/R Bounce redesign, Fed-put data infrastructure, a fresh cheap-candidate search, a structural retrospective), each scored independently and the top two adversarially verified against the actual codebase. CTA v2 and Fed put were `not_recommended` (their own rationale channels are already undermined by this session's closed results, and both are more expensive than unexhausted Tier 1 options); the retrospective was `weak` (its core question is already answered in `research-backlog.md`); the fresh-idea search was `strong_yes` and surfaced three new candidates. Verification also caught two real corrections: CTA v2's stale "no infrastructure exists" framing (adjacent live-portfolio infrastructure was actually built `2026-08-18`, though not directly reusable), and a genuine data-integrity blocker for an S/R Bounce round-number-level redesign (this project's adjusted-price data diverges substantially from real nominal historical prices for `10`/`12` locked assets under [ADR 0002](docs/adr/0002-market-data-contract.md)).
- Scored the three new candidates in [docs/research-candidates/2026-08-20-cycle-5.md](docs/research-candidates/2026-08-20-cycle-5.md): turn-of-month calendar effect (`15/16`, tied with RSI for the highest of any candidate this session), day-of-week calendar effect (`12/16`, eligible but not bundled — real mechanism overlap with turn-of-month), overnight-gap conditioning (`13/16`, but not implementable today — needs a new joint/paired resampling design the existing scaffold doesn't support).
- Locked [docs/research-protocols/calendar-turn-of-month-v1.md](docs/research-protocols/calendar-turn-of-month-v1.md): the first candidate this session with a time-based, not price-derived, event definition. Implemented `tom_event_mask`, `tom_daily_differential`, `tom_volatility_diagnostic`, and `tom_bootstrap` in `backend/app/research.py` — a genuinely simpler bootstrap variant than every prior candidate, since calendar membership is computed once and held fixed rather than recomputed from a resampled synthetic price path each iteration. Added 6 unit tests, including a hand-computed-calendar fixture and a planted-effect detection check.
- Result: `not_material_or_not_consistent`. `987`-`1,612` turn-of-month days per asset (~`19`% of trading days) ruled out a power-limitation explanation; a locked, non-gating volatility diagnostic found event-day and non-event-day realized volatility nearly identical for every asset, ruling out SMA Cross v1's confound story. `0`/`12` assets cleared materiality and Holm-corrected significance simultaneously; `7`/`12` positive, `4`/`12` negative — a weak majority, not a consistent pattern. `EEM` reached raw `p=0.013` on a `+0.119%` daily differential — the strongest single-asset raw significance this session — but its Holm-adjusted `p=0.156` did not survive correction. Recorded in [docs/research-results/calendar-turn-of-month-v1.md](docs/research-results/calendar-turn-of-month-v1.md).
- Six negative results, six different reasons this session. Day-of-week and overnight-gap conditioning remain eligible, unexecuted Cycle 5 candidates; no research task is queued next by default.

## 0.50.0

Locked, executed, and closed ETF-12 cross-sectional rotation v1 (Cycle 2's Candidate D), resolving its statistics-infrastructure gap by redesign rather than a new dependency. No strategy implemented, no trade, no cost/execution modelling.

- Resolved the "no panel regression, no permutation-null machinery, no scipy/statsmodels" gap Cycle 2's verification found by substituting Spearman rank correlation (computable in plain `numpy`/`pandas`) for a panel regression, and a joint-panel block-resampling null (the same resampled calendar-time blocks applied to all 12 assets simultaneously, preserving real cluster co-movement) for per-asset cluster residualization — which would have been degenerate for the four singleton-cluster assets (`TLT`, `IEF`, `GLD`, `DBC`) in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS`.
- Implemented `etf12_rotation_bootstrap` and supporting functions in `backend/app/research.py`, the first genuinely panel/cross-sectional design this session (every prior candidate was per-asset independent). Added 6 unit tests, including a sanity check that a synthetic panel with a planted rank-continuation effect produces a materially higher correlation than an independent-noise panel of the same shape.
- Result: pooled Spearman rank correlation across `253` rebalance dates and 12 assets (`3,036` pooled observations, `2006-02-06` onward) was `0.045`, an order of magnitude below the locked `0.10` materiality floor; the joint-panel null placed it at `p=0.266`. Cluster breadth passed cleanly (`6/6` clusters represented in the top-third group at some point), so the null is not a concentration artifact. The cleanest negative of the session's five experiments — no confound, power limitation, or design weakness to disclose. Recorded in [docs/research-results/etf12-cross-sectional-rotation-v1.md](docs/research-results/etf12-cross-sectional-rotation-v1.md).
- Closes the last checklist item ready to run without a new data source or a genuinely different infrastructure investment; CTA v2's overlap concern with rotation is now moot in the other direction, since rotation ran and found nothing.

## 0.49.0

Selected, locked, executed, and closed Stage 9A Cycle 4; closes every Tier 0/1 item on the pending checklist. No strategy implemented, no trade, no cost/execution modelling.

- Scored `Wave Pull` impulse-pullback continuation (`13/16`) now that its `IndexError` bug is fixed. Recorded in [docs/research-candidates/2026-08-19-cycle-4.md](docs/research-candidates/2026-08-19-cycle-4.md).
- Locked [docs/research-protocols/wave-pull-v1.md](docs/research-protocols/wave-pull-v1.md): a close-price-only impulse-then-breakout event against a plain-breakout placebo that strips the impulse precondition, reusing the event-recomputing bootstrap a third time (`wave_pull_bootstrap` in `backend/app/research.py`). Added 6 unit tests, including a check that the event set is a strict subset of the placebo set.
- Result: `not_material_or_not_consistent`. `IEF` had zero qualifying events (disclosed, anticipated in the protocol's own risk section); `0/11` eligible assets survived Holm correction. Unlike TA Breakout, the event/placebo separation was clean (events ran `5`-`20x` fewer than placebo occurrences). `TLT` reached raw `p=0.032` — the closest any single asset has come to raw significance across all four experiments this session — but failed correction on only `20` events; several equity assets showed a negative-direction effect, disclosed rather than omitted. Recorded in [docs/research-results/wave-pull-v1.md](docs/research-results/wave-pull-v1.md).
- This closes the cheap tier of the [pending candidate checklist](docs/brainstorm/2026-08-19-pending-candidate-checklist.md): four experiments, four different `not_material_or_not_consistent` reasons (confound, power limit, weak test design, clean-but-null). No research task is queued next by default.

## 0.48.0

Fixed the known `Wave Pull` `IndexError` (2026-08-19 audit's L4 finding); no research conclusion changed.

- `backend/app/signals.py::compute_signal`'s `Wave Pull` branch indexed `close.iloc[-1 - impulse_bars]` unconditionally for a display-only note string, crashing whenever `impulse_bars` reached or exceeded the available bar history. The Strategy Lab UI slider suggests a max of `30`, but `compute_signal` never enforced that bound itself, so the crash was reachable via any direct API call with a larger value.
- Now only computes the note when `long_now` is true (it was unused otherwise) and falls back to an honest "insufficient history" note when `impulse_bars` exceeds the available bars, instead of crashing.
- Added a regression test reproducing the exact crash condition (`60`-bar minimum history, `impulse_bars=65`) and a normal-path check.

## 0.47.0

Locked, executed, and closed TA Breakout v1 (Cycle 2's unpicked Candidate E); assessed and declined MACD and full Elliott Wave counting. No strategy implemented, no trade, no cost/execution modelling.

- Picked up TA Breakout v1 (scored `10/16` in Cycle 2, never disqualified) from the pending checklist. Locked [docs/research-protocols/ta-breakout-v1.md](docs/research-protocols/ta-breakout-v1.md): a deliberately simplified, close-price-only rejected-resistance breakout, tested against the exact placebo Cycle 2's own verification named — a raw new-high breakout with no rejection requirement — reusing RSI's proven event-recomputing bootstrap rather than Cycle 1's caliper-matching design.
- Implemented `ta_breakout_bootstrap` and supporting functions in `backend/app/research.py`, reusing `_apply_cooldown`/`_mean_forward_return` from the RSI implementation. Added 6 unit tests, including a deterministic no-lookahead check for the resistance calculation and a direct check that the event/placebo distinction behaves as designed.
- Result: `1,477` total qualifying events across 12 assets (far more than RSI's `508`), yet `0/12` reached raw significance (smallest raw p `0.099`). Disclosed a genuine design weakness rather than filing this as an equivalent negative to the prior two results: the `≥2`-rejection filter barely separated event from placebo on any asset (e.g. `SPY`: `190` events vs. `195` placebo occurrences), so the `7/12` placebo-beating count reflects weak separation, not a clean comparison. Recorded in [docs/research-results/ta-breakout-v1.md](docs/research-results/ta-breakout-v1.md).
- Assessed MACD and full Elliott Wave (5-3/ABCDE) counting against the pending checklist and declined both, with reasons recorded rather than silently skipped: MACD is mechanically the same shape as SMA Cross v1 and would very likely reproduce its exact confound; Elliott Wave counting cannot be made objective without discretionary judgment, in tension with this project's falsifiability requirement. The existing `WavePull` prototype remains the honest, already-scoped stand-in, currently blocked by a known bug.

## 0.46.0

Selected, locked, executed, and closed Stage 9A Cycle 3; no strategy implemented, no trade, no cost/execution modelling.

- Scored two candidates from the pending checklist: RSI(14) oversold-crossing short-horizon reversal (`15/16`, highest of any candidate so far — a genuinely different mechanism from every trend-family candidate tested) and S/R Bounce formalization (`0/16` on distinct information — too close to Cycle 1's already-closed consolidation work). Prioritised RSI only. Recorded in [docs/research-candidates/2026-08-19-cycle-3.md](docs/research-candidates/2026-08-19-cycle-3.md).
- Locked [docs/research-protocols/rsi-oversold-reversal-v1.md](docs/research-protocols/rsi-oversold-reversal-v1.md): an event study reusing the block-resample-and-recompute method proven by SMA Cross v1, extended from continuous state-gating to sparse event/forward-return recomputation — deliberately avoids Cycle 1's caliper-matching failure mode by never constructing a separate matched control set.
- Implemented the extension in `backend/app/research.py` (`rsi_bootstrap` and supporting functions), reusing the existing `RsiReversion` prototype's exact RSI formula. Added 8 unit tests, including a direct cross-check against that prototype's own formula on real closes — caught and fixed a real bug where the reconstructed-price RSI diverged from the reference by up to 0.3% due to a warm-up initialization mismatch (padding the first price delta with `0.0` instead of letting pandas' EWM skip a leading `NaN`).
- Result: all 12 assets cleared the 15-event minimum (508 events total), but 0/12 reached raw significance even before Holm correction (smallest raw p 0.138); the placebo comparison was genuinely mixed (6/12 each way), unlike SMA Cross v1's clean sweep. Recorded as `not_material_or_not_consistent` in [docs/research-results/rsi-oversold-reversal-v1.md](docs/research-results/rsi-oversold-reversal-v1.md), explicitly distinguished from Cycle 2's confound-driven result as a power limitation instead.

## 0.45.0

Executed the locked Stage 9A Cycle 2 protocol and closed it `not_material_or_not_consistent`; no strategy implemented, no trade, no cost/execution modelling.

- Implemented the protocol's one named statistics extension in `backend/app/research.py`: a state-recomputing generalization of `circular_block_bootstrap_p_value` (each resample reconstructs a synthetic price path and recomputes both trailing states on it) plus `delta_sigma`/`delta_mdd` computation, reusing `holm_adjust` unchanged. Added 7 unit tests proving no future bar affects an earlier state value and pinning the favourable-direction sign convention.
- Added `backend/app/run_sma_cross_exposure_reduction.py`, executed against the real 12-ETF dataset fetched this session (data SHA-256 `0c5a81332f9ba941ddce9bd6a69cb9fe90c3f7570b163c1a4ec3bd4c609fc5bc`).
- Result: 4/12 assets cleared raw materiality and significance on both statistics; 0/12 survived Holm correction across the 12-asset × 2-statistic family on both statistics at once. The volatility-state placebo matched or beat the SMA state's variance reduction on 12/12 assets and drawdown reduction on 5/12 — the protocol's own falsifier triggering directly. Recorded in [docs/research-results/sma-cross-v1-exposure-reduction.md](docs/research-results/sma-cross-v1-exposure-reduction.md).
- Pre-execution amendment: corrected the concentration gate from a paraphrased "2 of 4 asset-class clusters" to the actual "3 of 6" distinct `cluster` values in `portfolio_universe.py`, verified by reading the field directly rather than from memory, before any data access.
- Fetched the full S&P 500 ∪ NASDAQ-100 ∪ XL sector ETF universe and all ten managed FRED macro series onto this machine using existing CLI tools; no new code required for the fetch itself.

## 0.44.0

Fixed a real bar-validation defect found while fetching FRED macro data; no research conclusion changed.

- `backend/app/store.py::upsert_bars` enforced `require_positive` on every symbol not in `MARKET_CONTEXT_SYMBOLS` (`GC=F`, `CL=F`, `^TNX`) — but FRED series were never added to that relaxation, so a legitimately negative value (`A191RL1Q225SBEA`, real GDP growth, negative in every contraction) was rejected as if it were a stock price.
- Added `FRED_MANAGED_SERIES` to `backend/app/assets.py` (moved from `backend/app/fred.py`, which now imports it) and extended `upsert_bars`'s relaxed-validation check to include it, alongside the existing Yahoo market-context symbols.
- Added a regression test confirming a negative FRED value is stored while an equity symbol with the same negative value is still rejected — the existing strict-equity guarantee is unchanged.
- Found and fixed while fetching real macro data for the first time on this machine; all ten `FRED_MANAGED_SERIES` are now stored.

## 0.43.0

Locked the Stage 9A Cycle 2 protocol; no data fetched, no code executed, no result computed.

- Locked [SMA Cross v1 exposure-reduction and volatility-state placebo v1](docs/research-protocols/sma-cross-v1-exposure-reduction.md): recast Candidate B's volatility-managed-exposure mechanism into a second self-referential trailing state (below/above its own expanding-median realized volatility) instead of a continuous, target-vol-anchored weight, so the joint experiment needs no new portfolio-weighting engine.
- Specified a bounded extension of the existing `circular_block_bootstrap_p_value` (state-recomputing resample, not a new panel/permutation library) as the only new statistics code required, reusing the existing `holm_adjust` unchanged.
- Locked warm-up (252 sessions, keeping 2008 in-sample for every asset including DBC), materiality thresholds (Δσ ≤ −3pp, ΔMDD ≤ −5pp), an 8/12-asset breadth gate, and an explicit placebo rule so the SMA state must beat the volatility state, not merely beat continuous exposure — resolving every open item Cycle 2's verification flagged against the raw Candidate A/B records.
- Created `research/experiments/sma-cross-v1-exposure-reduction.json` with every constant above, canonical-hashed (spec SHA-256 `5bee965b775645681149049e3ecf43a618b4e71b225bc97b53b88b62b6ebf4ae`); its data-fingerprint fields are honestly `null`, pending a data fetch on the executing machine.
- Appended one `preregistered_no_results` attempts-ledger entry before any execution, per the exploration protocol.

## 0.42.0

Closed Stage 9A Cycle 2 candidate selection; no strategy implemented, no result computed, no code changed.

- Operationalized, independently scored, and adversarially verified five candidates against the actual codebase (not narrative docs): CTA v2, ETF-12 cross-sectional rotation, volatility-managed exposure, TA Breakout v1, and a formalized SMA Cross.
- Prioritised SMA Cross v1's exposure-reduction claim, jointly designed against volatility-managed exposure's control after verification found the two share one research question and would double-count as independent evidence if scored separately.
- Found that CTA v2 and cross-sectional rotation are data-ready but require infrastructure this codebase does not have — a pooled multi-instrument portfolio-weighting engine and panel/permutation statistical tooling respectively — and parked both on that basis, not on data readiness.
- Recorded that data readiness scored `2` for all five candidates precisely because the batch stayed on the one data shape already confirmed clean (12-ETF adjusted daily OHLCV); this was not read as a general "data is solved" conclusion.
- TA Breakout v1 was not prioritised: lowest score of the batch, an explicit zero on diversification, and its own record concedes its distinguishing mechanic degenerates to a CTA v1 retest once stripped out.
- During this cycle's workflow run, a subagent wrote an unauthorized file into `docs/research-hypotheses/` and edited `docs/research-backlog.md` without instruction; both were caught, reverted, and are not part of this release. Recorded here as a governance note on this session's tooling, not a project research finding.

## 0.41.0

Documentation-only agent-memory and environment-portability hardening; no runtime behaviour or research conclusion changed.

- Added identical `AGENTS.md` and `CLAUDE.md` root pointers routing any agent tool to `docs/README.md` as the single authoritative checkpoint; neither file duplicates checkpoint content.
- Added an "Environment and data portability" section to `docs/README.md`: `data/` and `.venv/` are git-ignored and non-portable; a checkout missing either supports documentation and specification work only, never execution.
- Recorded the data-fingerprint reproducibility rule for locked specifications: a fresh Yahoo fetch is not fingerprint-stable under `auto_adjust=True`; moving locked-data execution to another machine requires copying `data/market.db` itself, not re-fetching.
- Verified by direct run that a data-less checkout produces `220 passed, 2 failed`, both failures attributable to the empty database, not a code defect; recorded the two expected failing test names so a future agent does not mistake them for a regression.
- Surfaced the untriaged 2026-08-19 methodology/implementation audit (2 critical, 2 high, 5 medium, 4 low) as a "Pending triage" checkpoint fact; findings remain non-evidential and unactioned per `docs/audits/README.md`.

## 0.40.0

Closed Stage 9A Cycle 1 as `not_evaluable`, without accessing actual-event outcomes.

- Completed detector-prevalence and locked pre-event matching feasibility for 274 deduplicated consolidation support-recovery events.
- Retained six of eight detector variants; two were transparently excluded as sparse under the preregistered prevalence gate.
- Recorded a zero-control matching result: 66,161 same-year candidates, 16,489 after event exclusion, and zero inside every locked feature caliper.
- Correctly short-circuited before prospective power; no return, drawdown, P&L, or post-event price was joined to an actual event.
- Added deterministic matching leakage/exclusion tests, a final decision artifact, immutable result documentation, and an attempts-ledger closure.
- Preserved the distinction between `not_evaluable` and hypothesis rejection; any alternative comparison design must enter a new research cycle.
- Verification: `222 passed`, locked input reproduction, and byte-identical structural rerun.

## 0.39.0

First Stage 9A execution checkpoint; structural feasibility only, with no forward-outcome or P&L access.

- Added indexed candidate-selection and preregistration folders while keeping canonical authority documents at `docs/` root.
- Selected consolidation support recovery through a pre-result scorecard; parked futures trend and cross-sectional momentum for unavailable point-in-time data.
- Locked an eight-variant detector/event-feasibility protocol, canonical machine specification, exact development-data fingerprint, dependence-aware power contract, and attempts-ledger record.
- Transparently amended a non-portable pre-execution SQLite text fingerprint to ordered binary IEEE-754/integer hashing; no research rule changed.
- Implemented a pure no-look-ahead consolidation detector, support-recovery event state machine, cross-variant deduplication, and guarded structural-only runner.
- Produced 274 deduplicated development events across 12/12 ETFs and 13 years; breadth/concentration preliminarily pass, while matching and power remain incomplete and decision remains null.
- Fixed Today watchlist scope isolation and made Strategy Lab distinguish unsaved suggested symbols from persisted selections.
- Verification: `219 passed`, locked input reproduction, and byte-identical structural artifact rerun.

## 0.38.0

Stage 8 accepted and closed; Stage 9A research prioritisation is now the active gate.

- Exposed the durable pipeline as a per-model/per-scope ledger with outcome, reason, and new or reused result ID instead of only aggregate counts.
- Added run ID, storage timestamp, and data-through date to each executable candidate-model tab.
- Collapsed manual Steps 1–4 and the once-daily pipeline by default so stored research results remain the primary workspace.
- Recorded the successful real pipeline acceptance: seven full-universe snapshots produced or reused, zero model jobs failed/blocked, and partial-data exclusions disclosed.
- Added a quarantined audits index: point-in-time reviews carry zero acceptance weight and are ignored during ordinary work unless explicitly requested and separately triaged.
- Preserved all research conclusions; this release changes product observability and governance only.

## 0.37.1

Repair of defects found by the first real Stage 8 refresh/pipeline acceptance run; no research conclusion changed.

- Classified `GC=F`, `CL=F`, and `^TNX` as descriptive Yahoo market context outside the long-only equity/ETF strategy universe.
- Added context validation permitting negative crude settlement and settlement outside intraday OHLC while preserving strict equity/ETF validation.
- Replaced all-or-nothing daily discovery with a 90% current-coverage floor; exact exclusions, effective symbols, coverage, and fingerprints remain persisted and visible.
- Kept watchlists strict and formal experiments subject to their locked protocol-specific coverage requirements.
- Added real-failure-pattern tests and exclusion UI/browser contracts. Verification: `212 passed`, full deterministic browser smoke, and a read-only real-data preflight with 516/542 eligible symbols (95.2%), seven ready full-universe jobs, and zero blocked jobs.

## 0.37.0

Stage 8 implementation exit checkpoint; manual user acceptance remains required before 9A.

- Clarified that the daily pipeline is a batch alternative for manual Steps 1–3 across every model and excludes the separate portfolio comparison.
- Exposed the fixed two-second provider pacing and minimum delay estimate in the reviewed plan and confirmation, including jobs that may unblock after refresh.
- Reflowed Today controls, Symbol Research chart/dossier, Macro events, and Data Management controls for narrow screens.
- Expanded deterministic Playwright coverage for pipeline reviewed/running/interrupted states and page-level overflow across every primary view at 390×844.
- Preserved the anti-toy boundary: no strategy, research result, scheduler, provider, paper-trading, or deployment change.
- Verification: `207 passed`; complete browser smoke passed with zero console errors and no provider/strategy execution.

## 0.36.0

Bounded Stage 8D executor slice; no strategy, research conclusion, scheduler, or deployment change.

- Added an explicit confirmed pipeline that refreshes dependencies, re-plans after publication, and runs only fingerprint-changed strategy snapshots through the existing execution path.
- Persisted pipeline identity, stage/job states, timestamps, failures, skips, and result IDs in SQLite; recovered unfinished work is marked `interrupted` after restart.
- Made retry a new plan over current state: successful data and matching snapshots become `skipped_current`, while partial refresh failures block only dependent jobs.
- Added Today run/retry progress while keeping navigation read-only and requiring preview before the UI enables execution.
- Added an anti-toy exit rule: finish the bounded layout/usability/browser checks, then move to Stage 9A rather than expanding infrastructure.
- Added executor recovery, partial-failure, persistence, API, and frontend-contract coverage; verification is `207 passed` plus a live Playwright preview check with zero console errors. The smoke test did not start the 545-symbol refresh.

## 0.35.0

First Stage 8D daily-pipeline slice; planning only, with no executor or scheduler.

- Added deterministic SHA-256 fingerprints over strategy identity/version, defaults, scope, symbols, and exact stored-data coverage.
- Attached the fingerprint to every new explicit strategy snapshot so unchanged work can later be identified without recalculation.
- Added a read-only dependency planner reporting refresh requirements plus `blocked_data`, `ready`, `skipped_current`, and `skipped_empty` model jobs.
- Added an explicit Today preflight preview; navigation remains read-only and the preview performs no refresh or strategy calculation.
- Preserved the yield-shock discussion as a minimal non-evidential brainstorm containing only tentative hypotheses/equation/questions.
- Added planner/fingerprint/API/frontend coverage; verification is `202 passed` plus a live Playwright preflight check with zero console errors.

## 0.34.0

Stage 8C productisation gate closure; no strategy, data, or research result changed.

- Added a repeatable Playwright CLI smoke command requiring only a running local backend and the installed Playwright skill wrapper.
- Covered Today read-only loading, Symbol Research and Strategy Lab not-run states, empty calculation refusal, and Macro’s display-only/no-equity-direction boundary.
- Injected deterministic Data Management running, interrupted, complete-with-errors, and transport-failure states in the browser; asserted disabled controls, recovery guidance, failure counts, unknown freshness, and cleared loaders.
- Kept browser verification network-independent: the suite never starts provider refresh, full-universe scans, backtests, or Strategy Lab computation.
- Documented the command in the root and frontend operating notes. Verification is `198 passed` plus `scripts/browser-smoke.sh`.
- Closed Stage 8C; the next gate is the unscheduled, shared durable daily pipeline in Stage 8D.

## 0.33.0

ADR 0006 Macro presentation slice; no macro signal or new ingestion capability was added.

- Added an API-level display-only contract declaring point-in-time vintages, canonical release datetimes, and historical forecast series unavailable and macro signals prohibited.
- Distinguished Yahoo adjusted market-context cards from final-revised FRED observations with per-card provider, dataset, revision, date, and eligibility metadata.
- Added observation/release/revision availability fields to calendar events and marked current schedules and forecasts as non-historical display data.
- Removed the backend equity-direction heuristic, the `good/bad for equities` UI, and the unused threshold-based macro regime payload/banner.
- Added neutral Macro hierarchy and explicit ALFRED/preregistration upgrade requirements.
- Added API, calendar, and frontend contract coverage; verification is `198 passed` plus fresh-server browser checks confirming display-only copy, no equity-direction claim, and zero console errors.

## 0.32.0

Durable manual-refresh state slice; scheduling remains parked and no data-provider policy changed.

- Added a SQLite singleton for the latest refresh job, including identity, timestamps, counters, current item, and per-symbol outcomes.
- Persisted state at job creation and each atomic item transition; bar publication remains independently transactional.
- On server startup, recovered formerly running work as `interrupted`, preserving completed/failed outcomes and marking unfinished items honestly instead of implying a worker still exists.
- Updated Data Management to display durable job identity and recovery guidance; Resume still recalculates freshness and skips current symbols.
- Corrected the workspace and market-data contracts that previously described refresh progress as volatile.
- Added manager-recovery, SQLite round-trip, and frontend contract coverage; verification is `195 passed` plus a fresh-server headless browser check.

## 0.31.0

Stage 8C Strategy Lab evidence-hierarchy slice; no strategy mechanics or research conclusions changed.

- Separated selected strategy definition, default configuration, execution/data contract, evidence boundary, documented decision, and artifact path from the interactive result table.
- Preserved CTA v1 as `rejected` with its immutable research artifact; all unvalidated prototypes are explicitly `not evaluable`.
- Labelled the scoreboard as an exploratory in-memory calculation using same-symbol buy-and-hold medians, not a durable fingerprinted experiment or the formal Passive ETF-12 protocol result.
- Added visible not-run, running, complete, partial-failure, and failed states.
- Prevented an empty symbol selection from silently calculating the default basket.
- Added metadata and frontend contract coverage; verification is `193 passed` plus headless browser checks of the evidence hierarchy and empty-selection refusal.

## 0.30.0

Bounded Stage 8C research-metadata product slice; no strategy mechanics or historical conclusions changed.

- Added a code-owned registry for the three data products the application actually consumes, including provenance, information class, schema/cadence, point-in-time and revision limitations, licence caveats, permitted research use, quality state, and freshness policy.
- Linked each stored symbol to its dataset contract and rendered the registry in Data Management, including explicit final-revised/display-only treatment for FRED data.
- Added stable strategy IDs, versions, families, information profiles, required datasets, and evidence status for every executable strategy.
- Exposed typed parameter schemas through `/api/strategies` and rendered contract metadata in Symbol Research and Strategy Lab instead of duplicating frontend evidence claims.
- Preserved the practical boundary: new catalog entries require a real ingestion path or executable strategy; no general ontology, new provider, or untested model was invented.
- Added registry/API/frontend contract coverage; verification is `192 passed` plus a headless browser smoke check.

## 0.29.1

Independent audit of `0.29.0`; no strategy, data, or calculation behaviour change. Runtime version metadata is aligned to the checkpoint.

- Corrected the CTA universe erratum: Git proves the executed machine spec was locked before evaluation; the conflicting list was introduced later by documentation consolidation, not by a pre-result universe substitution.
- Added the hypothesis-engineering bridge from narrative thesis to measurable claim, point-in-time proxies, falsifier, and separately evaluated trade expression.
- Defined Passive ETF-12 as a project-specific default with material limitations and a mandatory candidate-specific benchmark/universe suitability audit before Stage 9B.
- Replaced universal statistical-method mandates and an invalid ledger-row trial count with hypothesis-specific diagnostics and a conservative variant/dependence inventory.
- Specified extensible dataset-registry and typed strategy-parameter metadata for pending Stage 8C product work; orthogonality is a measured relationship, not a strategy/data-cost category.
- Recorded the remaining Macro UI mismatch with ADR 0006 and aligned the API application version with the repository checkpoint.

## 0.29.0

Documentation-only hardening of research governance; no runtime behaviour change. CTA v1 rejection unchanged.

- Added [ADR 0006](docs/adr/0006-macro-data-contract.md): macro series are non-tradable context; point-in-time vintage (FRED ALFRED), release-datetime alignment, revision policy, surprise-vs-level estimand declaration, episode-count discipline, and an explicit upgrade path to signal status.
- Added Macro to the product contract and clarified Research Record as a documentation surface ([docs/product.md](docs/product.md)); macro-derived signals are out of scope until ADR 0006 is satisfied.
- Added institutional verification layers to the [model acceptance standard](docs/model-acceptance-standard.md): trial-count deflation, backtest-overfitting diagnostics (CSCV), power pre-commitment, break-even cost, alpha decomposition, regime/sub-sample stability, and an exploratory non-evidential tier.
- Added a mandatory preregistration template to [research-protocol.md](docs/research-protocol.md) for any hypothesis after CTA v1.
- Added the [exploration protocol](docs/exploration-protocol.md): the non-evidential search layer, attempts-ledger contract, search discipline, and the promotion path into Stage 9A.
- Added the [product identity](docs/identity.md): distilled v1 statement of what the project runs, mandated as the first read of every work session.
- Documented an erratum in [research-protocol.md](docs/research-protocol.md): the locked universe line was superseded before execution; the executed-of-record universe is `research/experiments/cta-trend-v1.json` / `locked-etf-12-v1` (SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, DBC, XLK, XLF, XLE).
- Centralised modern estimation refinements and references (data-driven HAC bandwidth, fixed-b critical values, automatic bootstrap block length, FDR/stepwise multiplicity) in ADR 0006; one-line pointer in the acceptance standard.

## 0.28.1

- Inserted Stage 9A before new model research: candidates must be scored before results are observed, and model-specific acceptance thresholds must be preregistered; the consolidation-zone draft is no longer presented as the default priority.

## 0.28.0

- Clarified interrupted data refresh: successful per-symbol publications survive server restart; the primary resume action skips current symbols, while core/all refreshes are explicitly labelled as forced operations.
- Prevented silent empty-watchlist replacement and added explicit recovery from the latest immutable strategy-run snapshot.
- Populated every Symbol Research model accordion after an explicit run while keeping chart overlays and markers exclusive to the selected model.
- Identified the existing S/R Bounce model as the classical-TA prototype and parked a separately specified local-resistance breakout hypothesis rather than inventing untested next-open markers or stops.
- Rebalanced the Symbol Research layout: a wider dossier rail and readable typography remain, while the selected-model guide uses a compact 96px scroll area so the chart retains focus.
- Moved the selected model’s green `Now` observation directly below the guide heading; rules and chart legend remain secondary scroll references.

## 0.27.0

- Defined the shared dependency-aware manual/scheduled pipeline contract; scheduling remains parked until the durable pipeline passes Stage 8D.
- Completed Stage 8B: semantic UI tokens, spacious responsive Today command centre, explicit data → watchlist → discovery → portfolio actions, market-oriented lifecycle/candidate presentation, and frontend contract tests.

## Current research-workspace line

| Version | Outcome |
|---|---|
| 0.26.0 | Added persistent per-strategy watchlists, lifecycle fields, full-universe candidate tabs/intersections, explicit action boundaries, product-redesign specification, and Stage 8 checkpoint. |
| 0.25.0 | Implemented Passive ETF-12 v1 and benchmark comparison as the primary business objective. |
| 0.24.0 | Recorded CTA v1 rejection, independent methodology audit, decision language, and parked successor hypotheses. |
| 0.23.0 | Added visible Data Management, freshness, throttled manual refresh, progress, and failure states; parked cron. |
| 0.22.0 | Exposed portfolio research through API/UI with persisted experiment state. |
| 0.21.0 | Implemented multi-asset portfolio simulation, risk/capacity policy, settlement, and drawdown controls. |
| 0.20.0 | Executed locked CTA v1: no validation survivor in 14 folds; all test folds cash; hypothesis rejected. |

## Validation-foundation line

| Version range | Outcome |
|---|---|
| 0.19.0–0.19.11 | Built deterministic walk-forward runner, artifact cache, bootstrap/Holm inference, fingerprints, resume/reproduction, and final-gate reporting. |
| 0.18.0 | Locked the CTA v1 preregistration, universe, parameter family, costs, folds, and decision rule. |
| 0.17.0 | Added dependence-aware post-signal statistics and explicit limitations. |
| 0.16.0 | Enforced market-data validation, adjusted-price policy, API contracts, and regression tests. |
| 0.15.0 | Canonicalised next-open execution and lifecycle state. |
| 0.14.0 | Established reproducible baseline tests and safety boundaries. |
| 0.13.0 | Audited the prototype and paused feature expansion in favour of research validity. |

## Prototype line

| Version range | Outcome |
|---|---|
| 0.10.0–0.12.0 | Added Today workflow, confidence/state presentation, macro context, CTA concepts, and early research UI. These outputs were exploratory, not statistically validated. |
| 0.6.0–0.9.0 | Added strategy definitions, Strategy Lab, technical analysis, support/resistance, and initial Today views. |
| 0.1.0–0.5.0 | Established repository, data ingestion, universe, FastAPI backend, browser frontend, charts, first backtest, and API integration. |

## Interpretation

Versions before `0.14.0` are prototype history and must not be treated as validated strategy evidence. The immutable CTA v1 conclusion is documented in [the result](docs/research-results/cta-trend-wf-v1.md) and [audit](docs/research-results/cta-trend-wf-v1-audit.md).
