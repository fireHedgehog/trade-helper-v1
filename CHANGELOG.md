# Changelog

Concise version ledger. Research decisions and exact contracts belong in `docs/`; Git preserves file-level implementation history.

## 0.86.2

Reverted `0.86.1`'s README fix -- it fixed the disclaimer confusion but introduced a worse problem, caught immediately by the user: the root README now had one paragraph speaking to a public reader, then the next addressed to an agent, then back again. Docs-only.

- User-directed: pointed out the root `README.md` is the one file a stranger actually lands on, and mixing an agent-directed process note into it (referencing "a prior agent session," pointing at `identity.md`'s internal reasoning) is jarring and unprofessional there, regardless of whether the content itself was correct.
- Root `README.md`: reverted to its original single-tone, human-only form. The disclaimer-vs-mission clarification stays exactly where it already correctly lived -- `docs/identity.md` only.
- `docs/README.md`: new explicit rule stating the actual, already-existing split -- root README is public/human-only, everything under `docs/` is the internal operating manual; calibration and process notes belong there, never in the root README.
- New persistent memory (`feedback_readme_single_tone_human_only.md`) alongside the existing disclaimer one, since this is a distinct lesson about *where* agent-facing content belongs, not *what* it should say.
- No code changed. 432 passed, 1 known unrelated failure.

## 0.86.1

Clarified that "not an alpha finder" is a public-repo liability disclaimer, not a mission statement. Docs-only.

- User-directed: pointed out that a prior agent session (this project's original setup, ~5 days before this one) converged on the disclaimer language as if it were the project's actual research goal, purely because it was the first line of a README it read cold -- when it was written specifically as a public-GitHub liability disclaimer (protecting a stranger who downloads the code from mistaking exploratory research for validated advice), not a statement that the user's own research intent isn't finding real, tradeable edges for their own private capital.
- `docs/identity.md` (v6 -> v7): "What we run" section gets an explicit note stating this distinction directly, naming it as a cause of this session's own repeated drift toward reflexive over-caution. Root `README.md`: same clarification added right after the disclaimer line itself, where the confusion originated.
- Persistent memory: new `feedback_disclaimer_is_not_a_mission_statement.md`, since this is the kind of root-cause-in-the-docs lesson that needs to survive across sessions the same way the Chapter 4 priority rule did.
- No code changed. 432 passed, 1 known unrelated failure.

## 0.86.0

First genuinely positive Chapter 4 candidate: amihud_illiquidity survives real point-in-time universe correction and real transaction cost.

- User-directed: after sector rotation's null, insisted the project keep searching for a real cross-sectional factor rather than stopping -- "if this one is 0.0, keep find, even it is weak." Rather than starting a new search from scratch, re-evaluated the strongest already-known cross-sectional candidate (`amihud_illiquidity`, factor-zoo-v1 Sec.5d) the way it had never been evaluated: masked to real point-in-time S&P 500 membership (the same reverse-survivorship fix CS-01 applied to individual-stock momentum) and Chapter 4's own instruments (Sharpe/CAGR/drawdown/Calmar, block-bootstrap EV), not the original rank-IC screen.
- `backend/app/run_amihud_illiquidity_chapter4.py` (new): reuses `factor_zoo.evaluate_factor` and `amihud_illiquidity` completely unmodified -- new logic is only the point-in-time eligibility mask. Result: Sharpe `0.29`, CAGR `2.67%`, max drawdown `-41.7%`, Calmar `0.064`, block-bootstrap daily EV interval `[+4.32e-5, +2.22e-4]` (entirely positive), `chapter4_confidence_multiplier` **`0.33`** -- the first genuinely positive confidence multiplier this research program has produced. Survives both the point-in-time correction and this project's own standard 32bps round-trip cost.
- 432 passed, 1 known unrelated failure. No test files changed -- exploratory survey script, same untested-by-design status as every other `run_*.py` in this project.

## 0.85.1

Priority rule restated as a short, explicit ranked list, in the project repo itself, not memory. Terminology fixed: paused, not parked; deprioritized, not deleted. Docs-only.

- User-directed: the hard rule from `0.85.0` was correctly in the repo already (`identity.md`, `README.md`), not only in Claude's cross-session memory file -- but it read as a paragraph, not a ranked list, and used "parked"/"side track" instead of the exact words the user wanted: Chapters 1-3 are **paused**, not deleted, **deprioritized** until the user asks for them, with Chapter 4 explicitly ranked first.
- `docs/identity.md`: Calibration section rewritten as a two-item numbered priority list (Chapter 4 first/default, Chapters 1-3 paused/on-request second) instead of prose. `docs/README.md`'s Non-negotiable state bullet matches the same wording. `docs/research-program.md`'s Chapter 1 status line: "Parked" -> "Paused" for consistency.
- No code changed. 432 passed, 1 known unrelated failure.

## 0.85.0

Hard rule against auto-falling-back to falsification, written into identity.md/README.md after it recurred a third time. Two real Chapter 4 evaluations built to replace it: sector rotation's real backtest, and ATR Vol Premium's first-ever performance survey.

- User-directed, forceful and specific: pointed out the sector-rotation-v1 correlation test used the wrong window shape (a fixed monthly rebalance pooled across 25 years cannot detect an episodic, multi-month regime the way an entry/exit rule can), and that defaulting to a p-value/falsification test for a new candidate at all is the wrong instinct for this project's actual goal -- "quant Sharpe, quant P&L, not p-test again and again." Separately noted ATR Vol Premium has run live in the app since its Tier A translation with zero documented performance survey -- exactly the gap this project's own "don't fabricate, don't omit" culture should have caught.
- `docs/identity.md` (v4 -> v5): Calibration section gets a new hard rule, not a soft default -- a new candidate is evaluated via Chapter 4's instruments (real backtest, Sharpe/CAGR/drawdown, EV confidence interval) by default; Chapters 1-3's falsification protocol runs only when the user explicitly asks for it on that specific candidate. `docs/README.md`'s Non-negotiable state carries the same rule as its first bullet. Persistent memory (`project_rigor-track-parked-favor-actionable-features.md`) updated with the third recurrence and the fix, since the same lesson had already been written down twice before and still didn't stick until stated as an explicit rule.
- `backend/app/run_sector_rotation_chapter4.py` (new): a real entry/exit rule (long top-3/short bottom-3 GICS sectors by 252-session return, rebalance only when the ranked set changes) instead of sector-rotation-v1's fixed monthly rebalance, evaluated on Sharpe/CAGR/drawdown/`block_bootstrap_confidence_interval` -- no p-value. Result: Sharpe -0.17, CAGR -1.87%, max drawdown -51.9%, confidence multiplier 0.0 -- converges with the Chapter 2 correlation null via an independent statistic; 1,879 rebalances over 24.6 years flags real rank-boundary whipsaw as a concrete diagnostic.
- `backend/app/run_atr_vol_premium_survey.py` (new): first-ever performance survey of ATR Vol Premium, per-symbol across the `501`-symbol point-in-time universe via the app's own real backtest engine (real commission/spread/slippage). First pass used each symbol's own full history and produced a nonsensical `-7,160%` median excess-vs-buy-hold (comparing a modest strategy return against `AAPL`'s multi-decade compounding) -- fixed to a common 2015-present window before writeup. Result: median CAGR `3.74%`, max drawdown `-46.6%`, Calmar `0.08`, win rate `62.9%`, profit factor `1.61`, `93%` of symbols Sharpe-positive but only `11%` beat their own buy-and-hold over this bull-heavy window.
- 432 passed, 1 known unrelated failure. No test files changed -- both new scripts are exploratory survey/backtest runners, same untested-by-design status as every other `run_*.py` script in this project.

## 0.84.0

Chapter 2 §4 closed: sector rotation v1 -- tests the user's own named observation ("long chips, short software") at the aggregate GICS-sector level, unlike CS-01's structurally-unable-to-test-it individual-stock design. Clean null.

- User-directed: after CS-01's null, pushed back with a specific, named real-world observation that CS-01 could not have tested (no sector grouping existed anywhere in this codebase before `0.83.0`). Confirmed the free GICS sector data layer and asked to build a real test of the actual claim.
- Reuses `backend/app/research.py:etf12_rotation_bootstrap` completely unmodified -- no new statistical engine needed, only a new sector-aggregation step (`backend/app/run_sector_rotation_v1.py`): equal-weighted daily return across real point-in-time-eligible members per GICS sector, compounded into a synthetic sector-index level, feeding the same engine ETF-12 rotation and CS-01 both used. Formation/holding (252/21 sessions, ~12-month lookback matching the user's own stated horizon) independently chosen, not copied from CS-01's 126/21.
- Result: observed correlation slightly **negative** (`-0.019`), fails both materiality and significance decisively (`p=0.895`) -- a clean null, not CS-01's borderline case. Real Estate sector shows a disclosed coverage gap (368 sparse pre-2016 dates -- it was only carved out of Financials as its own GICS sector in 2016), noted but non-gating. Today's-GICS-classification-not-point-in-time limitation disclosed per protocol.
- Reproducibility verified byte-identical on the first rerun -- no fingerprint bug this time, applying the same-day lesson from CS-01's fingerprint fix.
- `docs/ensemble-construction-engine-v1.md` (separately, `0.83.2`): direct feedback that ADR 0010's alpha-model/risk-model/optimizer section named a shape in prose without specifying it -- replaced with exact formulas, function signatures, a worked 6-asset numeric example, and a test/acceptance checklist, the same relationship `strategy-library.md` has to ADR 0009.
- Real vendor cost research documented (`0.83.1`, docs-only): options data (IV/Greeks/open interest) cheapest at EODHD, $99.99/mo, <3yr depth; Level 2 explicitly excluded by design (this project never reaches live/HFT execution).
- 432 passed, 1 known unrelated failure.

## 0.83.2

Ensemble-construction engine: a real, disciplined design, not just named prose. Docs-only.

- User-directed, a direct and correct critique: ADR 0010's §3 named the alpha model/risk model/optimizer shape in prose but never actually specified them precisely enough to implement without guessing -- "no design how to be disciplined."
- `docs/ensemble-construction-engine-v1.md` (new): exact formulas (composite alpha score with cross-sectional z-scoring and confidence weighting; fixed-intensity Ledoit-Wolf-style shrinkage covariance; a step-by-step rank-and-weight optimizer with an ADR-0004-stop-distance-cap reconciliation -- "optimizer proposes, risk cap disposes"), Python function signatures for a new `backend/app/ensemble.py`, a fully worked 6-asset numeric example, explicit constraint-by-constraint verification against ADR 0010 §1, and a test/acceptance checklist. Same relationship to ADR 0010 that `strategy-library.md` has to ADR 0009 -- the ADR is the decision, this is the exact procedure.
- `docs/adr/0010-long-short-ensemble-construction.md` §3 now points to this document explicitly rather than repeating the same prose.
- No code yet -- design only, against its own written acceptance checklist.

## 0.83.1

Documented real vendor research for options data (IV/Greeks/open interest) and Level 2, per the user's explicit ask for "the cheapest way to get a full real dataset." Docs-only, no purchase made.

- User-directed: after accepting the sector-rotation direction, asked for real cost research on deeper data -- historical IV curves, options open interest (source of "call wall/put wall"), and Level 2 order-book depth.
- `docs/data-layers.md` and `docs/brainstorm/2026-08-19-pending-candidate-checklist.md`: options (IV/Greeks/OI) -- cheapest real option is EODHD's US options API, `$99.99/mo`, but only `Q4 2023`-present depth; deeper history means OptionMetrics/CBOE DataShop, no public pricing, real four-figure/year territory. Not purchased -- no queued hypothesis needs it yet. "Call wall/put wall" clarified as a derived metric from OI-by-strike, not a separate purchase. Level 2 explicitly marked excluded by design, not a pending item -- this project never reaches live/HFT execution (already disclosed in data-layers.md's Intraday/tick row), so microstructure-priced data buys nothing it would use; researched anyway (Databento's metered pricing is the cheapest access model) so the "why not" is a researched answer, not an assumption.
- No code, no tests affected.

## 0.83.0

GICS sector/sub-industry data layer -- free, unblocks CS-07/CS-08 (sector rotation). Also names a sharper, separate survivorship bias that this does not fix.

- User-directed: pushed back on CS-01's null with a real, specific example (sector-level leadership -- "long chips, short software" -- not individual-stock momentum), and pointed out a real, sharp problem: a company can be removed from Nasdaq-100 by reconstitution while remaining listed and traded (their Atlassian example) -- invisible to any universe built from "ever an index member." Confirmed this is a real, different, and deeper bias than the one `universe_pit.py` fixed: point-in-time *entry/exit timing* within an index vs. the index's own *selection* being endogenous to size/performance. No free source is known to exist at CRSP/Sharadar's depth (full US-listed history including non-index delistings) -- named as a likely-real Tier 4 vendor-data case if the sharp version of this claim is ever pursued.
- `backend/app/universe.py`: new `get_sp500_sectors()`, `_fetch_table()` (refactored out of `_tickers_from_wikipedia`) -- GICS Sector/Sub-Industry columns were already sitting unused in the same Wikipedia table the ticker list comes from. `backend/app/universe_sectors.py` (new): ingestion CLI. `backend/app/store.py`: new `equity_sectors` table, `upsert_equity_sectors()`/`load_equity_sectors()`. Live-verified: `503` symbols across all `11` GICS sectors; confirmed real "Semiconductors"/"Semiconductor Materials & Equipment" vs. "Application Software"/"Systems Software" sub-industry granularity -- the exact distinction the user's example needs.
- Disclosed limitation, explicit: today's classification snapshot only, no history of GICS reassignment; inherits the same index-membership selection bias as CS-01 (only compares groups among names that stayed prominent enough to remain index members).
- `docs/brainstorm/2026-08-20-cross-sectional-experiment-ideas.md` updated: CS-07/CS-08's data blocker marked cleared; the sharper index-selection-bias limitation written down as its own named point, not left only in chat.
- 4 new tests. 432 passed, 1 known unrelated failure.

## 0.82.0

Chapter 2 §3 closed: cross-sectional momentum v1 (CS-01), the first confirmatory rank-correlation test at real point-in-time S&P 500 breadth. `not_material_or_not_consistent` -- a genuine, well-earned null, not a bug.

- User-directed: after `0.81.0` cleared the Tier 4 data blocker, ran the full Stage 9A -> preregistration -> execution sequence on CS-01 (plain cross-sectional momentum) the same day, per the user's explicit "both, CS-01 first" choice.
- `docs/research-hypotheses/cross-sectional-momentum-v1.md` (operationalization record) and `docs/research-candidates/2026-08-21-cycle-7.md` (Stage 9A re-score of Cycle 1/6's Candidate C: Data readiness `0 -> 2`, total `14/16`).
- `backend/app/research.py`: new `rotation_pooled_correlation_masked` and `cross_sectional_momentum_bootstrap` -- a genuinely new engine, not a "zero code change" reuse like the earlier feasibility check assumed, because real point-in-time membership means the eligible column set varies by rebalance date, unlike `etf12_rotation_bootstrap`'s fixed panel. Membership is held fixed across every bootstrap resample (a calendar fact, never randomized) -- only the return panel is block-permuted. 6 new tests, including the disjoint-interval (delisted-then-relisted) case.
- `docs/research-protocols/cross-sectional-momentum-v1.md` + `research/experiments/cross-sectional-momentum-v1.json` (locked spec) + `backend/app/run_cross_sectional_momentum_v1.py`: universe is `501` symbols (real point-in-time S&P 500 members with stored bars -- narrower than the feasibility check's `495` on purpose, since Nasdaq-100/XL ETFs have no point-in-time membership data). Result: observed correlation `0.146` clears the `0.10` materiality floor but `p=0.9985` decisively fails significance -- the null is dominated by shared market/regime co-movement, a known limitation of raw non-market-neutral rank correlation, not a design bug. `134` genuine point-in-time S&P 500 additions since 2019 were verified correctly excluded pre-join (e.g. `TSLA`, added `2020-12-21`) -- the reverse-survivorship contamination this run set out to fix, confirmed real and fixed. Residual, narrower survivorship bias disclosed: `705`/`1,206` ever-members have zero stored bars.
- Caught and fixed a real reproducibility bug via this project's own gate: the first execution's data fingerprint hashed raw, unaligned bars rows (which can carry stray dates outside the aligned computation window) rather than the exact aligned data the bootstrap consumed -- non-reproducible despite the actual statistical computation being fully deterministic (verified: identical correlation/p-value across every run, buggy-fingerprint run included). Fixed to fingerprint the aligned closes + eligibility mask directly; re-verified byte-identical across two independent reruns before closing the result.
- 428 passed, 1 known unrelated failure.
- Separately, `docs/adr/0010-long-short-ensemble-construction.md` (**proposed**, not yet accepted): user relayed a quant PM's critique that this project's long-only account model (ADR 0004) is a specific, narrower choice, not a law of portfolio construction -- a CTA gets its risk/return shape from leverage on a long-only book, a cross-sectional quant gets it from being long-short, no leverage needed. ADR 0010 amends ADR 0004's account model (Chapter 4 scope only, Chapters 1-3 untouched) and designs the "ensemble-construction engine" ADR 0007 already named as required-but-unbuilt: an alpha model (combining Chapter-4-eligible signals' per-asset scores), a risk model (v1: shrinkage covariance, no new dependency), and an optimizer (v1: rank-and-weight heuristic, not a new QP dependency) -- plus a disclosed, simplified backtest-only short-sale mechanics section (free borrow, non-reusable proceeds, no leverage beyond 100% gross exposure), per the user's own choice among three scoping questions. No code yet -- this is the design only, pending explicit acceptance.

## 0.81.0

Cleared Chapter 2's real blocker for free: point-in-time S&P 500 membership, no vendor purchase needed. New reusable data layer, no new research claim yet.

- User-directed strategic pivot: after seeing the app's UI/UX land, explicitly redirected research priority toward Cross-Sectional (Chapter 2) over more single-symbol time-series work — the reasoning given was that *selecting* a symbol (a real 10x mover, named example: SNDK/MU-style) can matter more than *timing* one (SPY-style entry/exit), and Chapter 2 is a genuine, documented gap: 2 sections closed vs. Chapter 1's 10, both nulls/feasibility-only. Explicitly authorized paying for data if no free/open path existed ("if open literature, open hypothesis can do, we just do, if not, we can buy data").
- Turned out not to need a purchase: `docs/brainstorm/2026-08-19-pending-candidate-checklist.md`'s Tier 4 blocker ("point-in-time equity membership/delisting data," previously assumed vendor-only, e.g. Norgate/Sharadar/CRSP) has a free, MIT-licensed, hand-maintained alternative ([fja05680/sp500](https://github.com/fja05680/sp500), sourced from Andreas Clenow's "Trading Evolved" base + ongoing Wikipedia cross-referencing). Confirmed via web research before building anything.
- `backend/app/universe_pit.py` (new): ingests real point-in-time S&P 500 membership intervals (`ticker, start_date, end_date`). `backend/app/store.py`: new `universe_membership` table, `upsert_universe_membership()` (atomic per-index replace, same precedent as `upsert_bars`), `members_asof(date, index_name)` for true historical reconstruction. Live-verified against the real source: `1,259` intervals, `1,206` distinct symbols, `503` currently active; `members_asof` correctly reconstructs 492 members on 2001-01-01 vs. 505 on 2019-01-01, and correctly handles a disjoint two-interval case (a symbol delisted then relisted years later under the same ticker).
- Disclosed limitations carried forward, not hidden (this project's standing norm): hand-maintained, updated bimonthly, not automated; maintainer's own README flags 1996-2000 as lower-confidence; S&P 500 only, not Nasdaq-100 or the XL sector ETFs.
- Unlocks 6 of the [cross-sectional idea library](docs/brainstorm/2026-08-20-cross-sectional-experiment-ideas.md)'s 11 queued ideas (CS-01/02/03/04/05/09) at once — the shared blocker research-program.md had flagged. Ingestion existing authorizes nothing: each idea still needs its own hypothesis-engineering note, Stage 9A score, and preregistration before a real run; `docs/research-program.md`, `data-layers.md`, and the pending-candidate-checklist updated to point at this as the next concrete step (CS-01 momentum re-baseline at real S&P 500 breadth, replacing the prior `N=12` ETF-only null).
- 5 new tests (parsing, normalization, as-of reconstruction including the disjoint-interval case, re-ingestion idempotency, missing-column validation). 422 passed, 1 known unrelated failure.

## 0.80.1

Sitewide footer: a persistent pointer to the chaptered research program, on every page. Frontend-only.

- User-directed: browsing the app cold, the research vocabulary (Tier A/B, ADR numbers, chapter references) reads as confusing without a map first -- asked for something that points to the "book, chaptered" framing that's been this project's own vision all along, referencing how a public GitHub research/working-paper page is laid out. Placement was deliberately not the left nav (that's app navigation, and collapses to a top bar on mobile) -- landed on a slim, persistent footer instead, present on every view regardless of viewport.
- `frontend/index.html`: new `#site-footer`, `position: fixed` to the viewport bottom, one line linking straight to `research-program.md` on GitHub (Chapters 1-6). `main` gained matching `padding-bottom` so it never covers the last row of scrolled content -- verified by scrolling Strategy Management's full table to its end and by scrolling the mobile layout, both confirmed clear.
- 417 passed (unchanged), live-verified in a headless browser: footer renders on all six views, stays pinned through scroll at both desktop and a 400px mobile viewport, zero console errors.

## 0.80.0

Macro page: restored a labeled, disclosed "equity read" hypothesis chip per event, fixed the missing Gold card, and decluttered the events table. Backend + frontend + one ADR addendum.

- User-directed, resolving a real tension: the user wanted the pre-`0.33.0` "good/bad for equities" read back, explicitly overriding the ADR 0006 explanation for why it was removed. Direct disclaimer-only compromise ("just add a disclaimer... in the table footer") was rejected as insufficient on its own -- final-revised FRED data used for a bare directional claim is a look-ahead-biased inference (ADR 0006 clause 2), not just an unproven one, so a caption alone doesn't fix it. Landed on the user's own refinement instead: frame it explicitly as an untested **hypothesis** (never a conclusion), with a checklist footer naming exactly which ADR 0006 clauses remain unmet, so it can't be read as a validated claim, isn't blocked by the existing contract, and gets replaced by the real decision (including "rejected") the day a category is actually studied.
- `backend/app/calendar.py`: new `_HEURISTIC_DIRECTION` per category (Fed/Inflation: hotter = bearish; Growth/Consumption/Activity: stronger = bullish; Labor: deliberately unscored -- "bad news is good news" rate-cut regimes make the sign unstable, so asserting one would be exactly the kind of unfounded claim this ADR forbids) and `_heuristic_read()`, wired into `macro_events()`'s `heuristic` field.
- `docs/adr/0006-macro-data-contract.md`: new Consequences bullet documenting this as a scoped, explicit exception to clause 2 -- disclosed common market convention, always labeled "Hypothesis... (untested)", never layered alongside a real result -- so a future session finds the intentional design here instead of rediscovering and re-removing it.
- `frontend/index.html`: events table gained a header row, an "Equity read" column (color-coded hypothesis chip, tooltip with the full disclaimer), and a standing footer explaining the chip and listing the unmet-clause checklist. Decluttered repeated per-row boilerplate (`final revised · release time n/a · consensus history n/a`) since the footer already covers it once; latest-observation values now bold for readability.
- `backend/app/fetch.py`: fixed the Gold (`GC=F`) card being stuck at 2/5 cards -- one real Yahoo data row (2009-11-23, `low > high`) failed the OHLC-envelope check; now dropped and logged, same posture as the existing NaN-row drop, not a validator weakening.
- Tests updated to match the new, intentional design rather than the stale one: `test_macro_calendar.py` (renamed, asserts the heuristic is labeled and Labor stays unscored), `test_frontend_contract.py` (asserts the disclaimer text, still forbids a bare "good/bad for equities" claim), `scripts/browser-smoke.sh` (fixture exercises the heuristic chip and footer). 417 passed, 1 known unrelated failure.

## 0.79.1

Actually grouped the origin distinction in the UI, not just the data. Frontend-only.

- User-directed: `0.79.0` added the `origin` field on the backend but every dropdown/tab/scoreboard still rendered Tier A as one flat list -- `ATR Vol Premium` just looked tacked onto the old 7, not visibly grouped. Also corrected mid-turn: group labels should say "Classic presets" / "Chapter 4 — screened candidates" only, no "(Tier A)" suffix -- that read as a competing tier system next to Strategy Management's real Tier A/B column.
- `frontend/index.html`: `#strategy`, `#today-strategy`, `#lab-watch-strategy` now render real `<optgroup>`s (presets, then screened candidates, then Tier B where that dropdown includes it). Today's "All models & studies" collapsible split into three sub-lists with their own headers instead of one flat 27-button block. Strategy Lab's scoreboard gained a group-header row between presets and screened candidates.
- 415 passed (unchanged, no backend touched), live-verified in a headless browser across all three surfaces: correct optgroup contents, correct tab sub-groups, correct scoreboard grouping, zero console errors.

## 0.79.0

Strategy Management becomes the full library: every Tier A strategy and every onboarded Tier B study, one table, GitHub-traceable. New `origin` grouping within Tier A (classic preset vs. Chapter 4 screened) so the two provenances don't blur together.

- User-directed, two-part: (1) the original 7 strategies are "preset" patterns (the kind a broker app ships by default), qualitatively different in provenance from a strategy sourced from this project's own Chapter 4 screening (`ATR Vol Premium`) even though both are the same Tier A architecturally -- asked for a way to group/label that distinction without inventing a new tier. (2) Strategy Management should show *everything*, not Tier B alone, with a Tier column, so an outside reader can trace any strategy or study to its real verdict and GitHub source in one place.
- `backend/app/research_catalog.py`: new `origin` field (`STRATEGY_ORIGINS`: `preset` | `chapter4_screen`) on all 8 Tier A entries -- a display/grouping label, not a new architectural tier, ADR 0009's Tier A/B test is unchanged. New `library_entries()` normalizes every Tier A strategy and every onboarded Tier B study into one shape (tier, origin, type, category, decision, summary, github_url); a Tier A entry with no closed result yet gets `github_url: null`, never a fabricated link.
- `backend/app/main.py`: new `GET /api/strategy-library` endpoint. `/api/research-record` (Tier B only, feeds the unified Today/Symbol Research/Strategy Lab dropdowns) is unchanged.
- `frontend/index.html`: Strategy Management now renders all 27 entries (8 Tier A + 19 Tier B) with Tier and Origin/Chapter columns; closed-result rows link to GitHub, not-yet-evaluated rows read "no closed result yet" instead of a broken link. Fixed two stale facts caught while rewriting the page's own copy: the deferred-studies note still named the 3 Fed put studies as deferred (they were un-deferred at `0.76.4`), and the page's banner didn't yet reflect that Tier A strategies run live elsewhere.
- 3 new tests (library completeness, per-entry traceability, live-endpoint tier mix). 415 passed, 1 known unrelated failure.

## 0.78.1

Rebalanced the two mandatory first-reads so Chapter 4 (actionable) isn't subordinate to Chapters 1-3 (verification) by default. Docs-only.

- User-directed: a direct, well-reasoned challenge that this project's docs bias every fresh session toward "verification machine" behavior, because Chapters 1-3's falsification framing gets far more textual weight than Chapter 4's actionable track -- and this had visibly recurred this session (the user had to push back multiple times before the agent pivoted to actually building ATR Vol Premium). Named plainly: this project is one person's own unlevered, paper-only capital, not a fund with LPs -- "keep verifying is nonsense" at that stakes level, per ADR 0007's own "no strangers to protect" reasoning.
- `docs/identity.md` (v3 -> v4): new opening "Calibration" section states Chapter 4 is the primary operating mode, not a subordinate second ladder; "What institutions do" rewritten as "Why two shapes, not one" to state the actual reasoning (protects strangers who can't inspect the trial; no strangers here) instead of a vague appeal to institutional practice.
- `docs/README.md`: Checkpoint table compacted (7 fields -> 6; the sprawling per-version "Completed"/"Active research" prose folded into a few sentences, detail pointed at CHANGELOG.md and research-program.md instead of re-narrated inline) -- the same compaction this project already did once before (CHANGELOG `0.75.1`) and had to do again here, now named as a standing constraint rather than a one-time cleanup.
- No code touched -- 412 passed, same 1 known unrelated failure.

## 0.78.0

Second live Chapter 4 candidate (`amihud_illiquidity`), and the factor zoo's first real Tier A execution ("ATR Vol Premium") -- a genuinely tradable (paper) model, not another verification report.

- User-directed, two-part: (1) enrich the factor zoo with genuinely *different* effects rather than more reversal variants -- 5 named academic anomalies (Amihud illiquidity, MAX/lottery-demand, low-volatility, Corwin-Schultz spread, expected idiosyncratic skewness), chosen over a broader open-source search after two fresh web searches during this session confirmed the bigger options found (Qlib Alpha158, a 335-indicator OHLCV repo) were either not yet queued or mostly redundant with families already screened. (2) A direct, fair challenge that verification work had displaced actionable output: build something runnable, not another check.
- `backend/app/factor_zoo.py`: new `ACADEMIC_ANOMALIES` dict (5 formulas, each with its own citation and expected-direction disclosure -- 2 are expected to score negative IC-IR, the literature's own predicted sign, not a misdirection).
- `backend/app/run_factor_zoo_academic_anomalies.py` (new): real run found `low_volatility` and `max_effect` redundant with `atr_normalized` (r=0.81-0.98) -- the same effect, different formula, not new breadth. `amihud_illiquidity` is independent of everything (|r|<0.45 vs. all four) and survives this project's standard transaction cost (Sharpe 0.70->0.29, graceful decay, not the reversal cluster's collapse) -- a second live Chapter 4 candidate. `corwin_schultz_spread` and `expected_skewness_proxy` are clean, honest nulls.
- `backend/app/strategies.py`: new `AtrVolPremium` Tier A strategy (8th registered strategy) -- an own-history, single-asset execution of factor-zoo-v1's cross-sectional `atr_normalized` finding, a new independently-designed protocol, not a retry (a per-symbol rule never existed for the cross-sectional version). Wired through all three parallel implementations this required, found only by running the full test suite: `strategies.py` (backtest engine), `rules.py` (vectorized live-signal computation), `signals.py` (display/"Now:" state) -- confirmed identical across all three via the existing cross-cutting parity tests.
- Live-verified end to end: real backtest on SPY's full history (59 trades, Return 252% vs. Buy & Hold 3083%, Sharpe 0.33 -- a real, honest reject against buy-and-hold, same pattern as the other trend-following strategies over this multi-decade bull run) and in a headless browser (selectable in the dropdown, real entry/exit chart markers, real metrics, zero console errors).
- 8 new tests: 5 hand-checked academic-anomaly formulas (turnover/sign-flip/top-k/two-day-spread arithmetic verified independently, not just re-derived from the same code), 1 new-strategy baseline snapshot, 2 cross-cutting parity fixes already covered by existing parametrized tests.
- Onboarded the academic-anomalies result via `strategy-library.md`'s playbook (19 Tier B studies now); the new Tier A strategy via the same playbook's Step 2a.
- 412 passed (8 new), 1 known unrelated failure (data-fingerprint drift).

## 0.77.1

Factor zoo regime concentration v1 (Chapter 4 §5c): `atr_normalized`'s ADR 0007 clause 5 check closes clean — unlike CTA v2, no single year carries the result.

- User-directed: the next named step after `0.77.0`'s cost-sensitivity result, framed as a natural checkpoint to commit once done.
- `backend/app/factor_zoo.py`: new `regime_concentration_by_year` function -- the exact calculation `cta-v2-pooled-trend-overlay.md` already disclosed (exclude a year, see whether the sample mean flips sign), generalized to sweep every year in a sample instead of a few hand-picked ones, and reusable by any future Chapter 4 candidate. 1 new hand-checked test (5-point synthetic series with one year constructed to flip the sign and one constructed not to).
- `backend/app/run_factor_zoo_regime_concentration.py` (new): real run against current `data/market.db` for `atr_normalized`. Result: full-sample mean `+8.41bps`/day (Sharpe `0.82`); excluding any single year of the 8-year sample, the mean stays positive in a `+7.25` to `+10.31bps` band -- no year flips the sign, unlike CTA v2's 2008 dependency.
- `docs/research-results/factor-zoo-regime-concentration-v1.md` (new immutable result). `factor-zoo-v1.md` and `factor-zoo-cost-sensitivity-v1.md`'s forward pointers updated to close the loop; `research-program.md` Chapter 4 gained `§5c`, and its "next concrete step" narrowed to clauses 1 (mechanism) and 2 (cross-validated point estimate + uncertainty band) -- the two still open before `atr_normalized` can be formally proposed.
- Onboarded via `strategy-library.md`'s playbook a third time (18 studies now on Strategy Management) -- routine at this point, which is the point of having written it down.
- A units error caught before it reached the immutable doc: first draft misread the daily-return decimal as already being in bps (100x off); recomputed and verified against the raw JSON before writing anything down.
- 402 passed (1 new), 1 known unrelated failure (data-fingerprint drift).

## 0.77.0

Factor zoo cost-sensitivity v1 (Chapter 4 §5b): the reversal cluster is not material after this project's own standard transaction cost; `atr_normalized` survives the same check. Built as a reusable engine parameter, not a one-off script.

- User-directed: asked for the promised cost-sensitivity check, and specifically how to build it so it lands in the right chapter, surfaces on the UI, and is reusable by future experiments -- not a bespoke, siloed one-off.
- `backend/app/factor_zoo.py`: `evaluate_factor` gained a `round_trip_cost_bps` parameter (default `0.0`, byte-for-byte unchanged behavior -- unit-tested) that charges cost on quintile turnover (the fraction of the top/bottom quintile whose membership changed since the prior day pays a round-trip rate once). Reusable by any future factor, WQ101 or new -- not specific to this report. 2 new hand-checked tests (a 5-symbol, hand-computed turnover example landing on an exact-zero result by construction).
- The cost rate is this project's own already-decided standard, not invented: derived from `engine.py`'s own `COMMISSION`/`SPREAD`/`SLIPPAGE` ("deliberate, so results aren't fantasy") -- 2 commission fills + 1 quoted spread + 2 slippage fills = 32bps round trip.
- `backend/app/run_factor_zoo_cost_sensitivity.py` (new): re-runs the six-factor reversal cluster (`alpha034/033/009/028/004/026`) plus `atr_normalized` as a control at 0/32/64bps. Real run against current `data/market.db`: every cluster factor flips from a positive Sharpe (0.40-0.78) to deeply negative (-4.4 to -19.3) at the standard rate -- confirms factor-zoo-v1's disclosed bid-ask-bounce suspicion by measurement. `atr_normalized` degrades mildly and monotonically (0.82 -> 0.37 -> -0.09), a second, different confirmation of its independence beyond the earlier correlation check.
- `docs/research-results/factor-zoo-cost-sensitivity-v1.md` (new immutable result): full method, table, and reading. `factor-zoo-v1.md`'s "not yet done" pointer updated to close the loop (original evidence untouched). `docs/research-program.md` Chapter 4 gained `§5b`, appended not rewritten, and its "next concrete step" narrowed to just `atr_normalized`.
- Onboarded via `strategy-library.md`'s own playbook, proving it end-to-end for a genuinely new result, not just the existing backlog: one `CHARACTERIZATION_STUDIES` entry, appeared on Strategy Management and every unified dropdown automatically, no UI code touched. Live-verified.
- Found and fixed along the way: `matplotlib` was declared in `requirements.txt` since `0.74.0` but not actually installed in this machine's venv -- synced it (`pip install -r requirements.txt`), not a new dependency.
- 401 passed (2 new), 1 known unrelated failure (data-fingerprint drift).

## 0.76.6

Closed a real vocabulary gap in docs/README.md, found by testing the question directly rather than assuming: user's own recurring term "trade desk" appeared nowhere in `docs/`. Docs-only.

- User-directed: asked directly whether a future agent, told to "do research" or "make a result available on the trade desk," would actually understand -- rather than answer from confidence, grepped `docs/` for "trade desk": zero hits.
- `docs/README.md`: new Document authority row bridges the user's own term to `strategy-library.md` + `identity.md`, and names the real tension plainly -- the live app looks like a trade desk (dark theme, chart markers, entry/exit state) but `identity.md` is explicit it is not an execution system or alpha finder.
- `docs/strategy-library.md`: opening paragraph now states directly that "available on the trade desk" means this playbook, for Today/Symbol Research/Strategy Lab/Strategy Management collectively.
- "Do research" was checked too and already routes correctly (predates this session) via the checkpoint's "Active research" field and the Resume sequence's link to `identity.md`. The one thing confirmed as *not* a documentation gap: which of several open research threads to pursue on "do research" alone is genuine ambiguity in a terse instruction, not something any doc can resolve -- an agent should ask, not guess.
- 399 passed (unchanged, no code touched), 1 known unrelated failure.

## 0.76.5

Today's "New-entry candidates by model" tab row (26 buttons after `0.76.4`) collapsed into an accordion, reusing the page's own existing pattern instead of inventing a new one. Frontend-only.

- User-directed: the flat 26-button row was "too long" -- asked for something like a Bootstrap accordion, collapsed by default to a simpler view, expandable to see and pick a particular one.
- The 3 aggregate tabs (Intersections, Momentum, New Breakouts) stay always visible -- those are the useful default view. The 23 individual model/study tabs (7 Tier A + 16 Tier B) moved into a `<details class="workflow-collapsible">` -- the exact class this same page already uses for "Manual workflow" and "Daily pipeline," reused rather than styled fresh.
- Collapsed state isn't blank: its summary line reads "Currently viewing: X. 23 models & studies total" whenever the active tab is one of the 23, so which one is selected stays visible without opening it -- and reverts to a plain count when it isn't.
- `modelDiscoveryTabs()` now returns `{fixed, all}` instead of one flat array; a shared `renderModelDiscoveryTabGroup()` renders both containers so there's one button-building code path, not two.
- Live-verified: collapsed by default (3 + 1 summary row), opens to 23 buttons, picking one updates the summary text and persists it through a manual re-collapse, zero console/page errors.
- No backend change -- 399 passed, same 1 known unrelated failure.

## 0.76.4

Unified the dropdowns: Tier B studies now appear in the same lists as Tier A strategies everywhere, not fragmented onto a separate Strategy Management page. Frontend-only.

- User-directed, and a course-correction: after `0.76.2`/`0.76.3` put Tier B studies on their own new page, the user pointed at Today's "New-entry candidates by model" tabs, Symbol Research's `#strategy` dropdown, and Strategy Lab's `#lab-watch-strategy` dropdown and asked why the same items weren't just available there too, in the lists that already existed -- correctly identifying that a second page nobody's told to visit isn't "making it all available."
- `frontend/index.html`: `loadStrategies()` now fetches `/api/research-record` alongside `/api/strategies` and merges both into Symbol Research's and Strategy Lab's dropdowns (as an `<optgroup>`) and into Today's discovery tabs (26 tabs total: 3 fixed + 7 Tier A + 16 Tier B). `#today-strategy` (the action-driving dropdown for "Update watched status"/"Run full-universe candidates"/"Run portfolio comparison") stays Tier A only -- those are genuinely live actions a Tier B study has no function for.
- New `recordCardHtml()`/`discoveryRecordRow()` helpers render a study's name/type/chapter/decision/summary/GitHub link inline, reused across all three surfaces. Selecting a Tier B entry: Symbol Research shows the record in the metrics rail instead of running a backtest (chart/trades/equity cleared, params panel replaced with a note, `Run Backtest` still clickable but computes nothing); Strategy Lab shows it in the Definition card with `Save as strategy watchlist` disabled and the symbol picker cleared instead of calling the strategy-watchlist endpoint (which 400s on a non-Tier-A name); Today's matching tab shows the record instead of a candidate table, exactly like the existing Momentum placeholder tab already does for "no live model yet."
- Fixed one real bug caught by screenshot during verification, not just described: hiding the parameter save-row via the `hidden` attribute silently failed because `.param-save-row`'s own `display:flex` class rule outranks the `[hidden]` UA default -- switched to setting `style.display` directly, verified both directions (hides for Tier B, restores for Tier A) via headless browser.
- `docs/strategy-library.md`: rewrote the "where a result appears" section, which `0.76.3` had gotten wrong (it said Tier B belongs on Strategy Management only) -- corrected in place rather than left stale, since a wrong standing doc is worse than none.
- Live-verified with headless Playwright across all three surfaces plus regression checks (switching Symbol Research and Strategy Lab back from a Tier B selection to a Tier A one still works exactly as before): zero console/page errors. No backend change this round -- 399 passed, same 1 known unrelated failure.

## 0.76.3

Professional `type` taxonomy (Time-Series / Cross-Sectional / Macro) added to every strategy and study; Fed put macro studies un-deferred onto Strategy Management; the onboarding/interface guides extended so this class of question doesn't need re-explaining.

- User-directed: (1) wanted a "pro" `Type` column on Strategy Management, not just chapter numbers. (2) Corrected a misread from `0.76.2` -- "postpone macro" meant postpone it from Today/Symbol Research/Strategy Lab only, never from Strategy Management; those three pages need a real per-day signal to mark on a chart, which the Fed put studies structurally don't have (4-6 discrete QE-launch episodes across ~18 years, not a daily series) -- that's a display-format mismatch, not a reason to withhold the finding. (3) Asked for a durable, phrased-once development guide covering this and related recurring questions (chart P&L, watchlist/candidate-scan separation), instead of re-explaining them each session.
- `backend/app/research_catalog.py`: new `STUDY_TYPES` constant (exactly three values, no fourth bucket); `type` added to all 7 Tier A `STRATEGIES` entries (all `Time-Series` today) and all 17 `CHARACTERIZATION_STUDIES` entries, deferred or not. `chapter4-eligibility-calibration-v1`/`chapter4-orthogonality-v1` typed by what they evaluate (both currently Time-Series candidates), not their own methodology. `factor-zoo-v1` typed `Cross-Sectional` (its rank-IC/quintile-spread methodology is cross-sectional even though several input formulas reference single-asset history).
- The 3 Fed put studies (`fed-put-yield-stress-precursor-v1/v2/v3`) got real `name`/`summary` (drawn from each doc's own decision line, not invented) and were removed from `DEFERRED_FROM_RECORD` -- only `factor-zoo-v1` remains deferred, and only because it's not yet well-explained to the user, not because it's macro or complex.
- `frontend/index.html`: Strategy Management gained a `Type` column (reusing the existing `.chip.trend` badge style, no new CSS); Symbol Research's per-strategy lifecycle line got a signpost comment pointing at the new unrealized-P&L contract below.
- `docs/strategy-library.md`: new "Type taxonomy" and "Where a result actually appears" sections resolve the Tier-B-live-pages-vs-Strategy-Management question permanently, so it's read, not re-asked.
- `docs/workspace-redesign.md`: new contracted-not-yet-implemented requirement -- Symbol Research must show an open position's actual unrealized P&L (computed from entry vs. latest close), not just restate the entry price. Confirmed, not re-designed: the recoverable-watchlist restore flow (line 79) and the accordion's existing "benchmark comparison" requirement (line 92) already cover the watchlist-independence and buy-and-hold-comparison asks -- both already implemented and live-verified at `0.76.2`, not new gaps.
- Tests extended in place (no new `def test_*`, existing assertions widened): every `STRATEGIES`/`CHARACTERIZATION_STUDIES` entry's `type` is asserted to be one of `STUDY_TYPES`; the API test now asserts Fed put v1 is present with `type == "Macro"`. 399 passed (unchanged count -- widened assertions, not new tests), 1 known failure unrelated to this change (data-fingerprint drift, see Environment and data portability).

## 0.76.2

Strategy Management page: the Tier B "Research Record" surface ADR 0009 named as required is now built. 13 of 17 closed studies onboarded live; 4 deliberately deferred.

- User-directed: immediately exercised `strategy-library.md`'s own playbook -- "onboard all the remaining results," excluding factor-zoo-v1 (not yet understood/prioritized) and the 3 Fed put macro-precursor studies (macro work parked for later). Also asked for a GitHub-linked "Strategy Management" table positioned after Data Management, so results stay reachable even from a shared/deployed instance.
- `backend/app/research_catalog.py`: added `name`/`summary` to the 13 onboarded `CHARACTERIZATION_STUDIES` entries (drawn from each study's own "Decision:" line, not invented); new `DEFERRED_FROM_RECORD` set (factor-zoo-v1 + 3 Fed put studies) with its reason recorded inline; new `RESEARCH_REPO_BASE` constant and `research_record_entries()` accessor (filters deferred studies, attaches a ready-to-use `github_url` per entry).
- `backend/app/main.py`: new `GET /api/research-record` endpoint -- the exact route ADR 0009's Consequences named and left unbuilt.
- `frontend/index.html`: new "Strategy Management" nav item (after Data Management) and `#records` view -- a read-only table (name, chapter, decision, summary, GitHub source link) with its own disclaimer banner distinct from Today's ("no live signal, no chart, no hold/exit state" rather than "not an order"). Decision-to-pill-color mapping distinguishes a real negative (`not_material_or_not_consistent`, `not_eligible`, `not_distinguishable_from_chance` -> red) from an inconclusive one (`not_evaluable` -> amber) from a methodology/feasibility check (`engine_feasible`, `methodology_validation`, `methodology_measurement` -> blue) -- these are not all "rejections" and were not flattened into looking like ones.
- `scripts/browser-smoke.sh`, `frontend/README.md`: extended with the same fixture-driven coverage pattern already used for every other view.
- Live-verified with a headless Playwright session (installed ad hoc for this session, not a tracked dependency): all 13 studies render with correct decisions and working GitHub links, nav order matches the request, zero console/page errors.
- 4 new tests (`test_research_catalog.py`, `test_api.py`): every non-deferred study has `name`+`summary` and no deferred study does; `research_record_entries()` excludes exactly `DEFERRED_FROM_RECORD`; `github_url` is well-formed; the live endpoint returns the expected filtered set.
- 399 passed (4 new), 1 known failure unrelated to this change (data-fingerprint drift against a locally refreshed `data/market.db` -- see Environment and data portability).

## 0.76.1

`docs/strategy-library.md` (new): operational playbook, not a new decision — turns ADR 0009 into a mechanical checklist so onboarding a result no longer needs a fresh design discussion each time. Docs-only.

- User-directed: after a live walkthrough of Today/Symbol Research/Strategy Lab confirmed the Tier A red-flagging (visible `rejected`/`not_material_or_not_consistent` labels, real chart markers, linked research docs) already works end-to-end, asked for a standing guide so a future "onboard result X" request doesn't repeat the same back-and-forth -- pre-authorizes showing negative/rejected results (that is the product working, not a fault) and gives exact steps per tier.
- Step 1 classifies Tier A vs. Tier B using ADR 0009's own test. Step 2a lists the three registries a Tier A strategy needs (`backend/app/strategies.py`'s executable `STRATEGIES` + `STRATEGY_PARAMS`; `research_catalog.py`'s metadata `STRATEGIES`, `HYPOTHESES`, `DECISIONS`) and confirms `research_contract` is derived automatically -- no frontend file is ever touched to onboard a strategy. Step 2b is the existing one-entry `CHARACTERIZATION_STUDIES` step for Tier B.
- Deliberately does not duplicate the strategy/study roster into markdown -- names the code registries as the single source of truth, the same staleness risk ADR 0009 itself was written to fix.
- 395 passed, 1 known failure (data-fingerprint drift against locally refreshed `data/market.db`, unrelated to this change -- see docs/README.md's environment/data-portability note).

## 0.76.0

ADR 0009: strategy onboarding contract (Tier A executable / Tier B characterization-only). Fixed a real staleness bug found while investigating.

- User-directed: asked to register CTA v2 as a live strategy and to formalize how future research results get onboarded across Today/Symbol Research/Strategy Lab, "agent-recallable" for next time.
- Investigation found the premise wrong: CTA v2's own locked protocol authorizes no cost, execution, or portfolio simulation (`run_cta_v2.py` docstring) -- it has no per-symbol entry/exit function and cannot get one without a new, independently justified protocol per this project's own standing rule. `GET /api/strategies` iterates strictly `backend/app/strategies.py`'s executable `STRATEGIES` dict; there was no honest path for a no-execution-authorized study to appear anywhere in the live app.
- Separately found: `research_catalog.py`'s `research_contract.decision` field was hardcoded to `"rejected"` (CTA Trend only) or `"not evaluable"` (every other strategy) regardless of each strategy's real evidence -- SMA Cross, RSI Reversion, and Wave Pull each have a genuine closed Chapter 1 verdict (`not_material_or_not_consistent`, each confirmed tied to the live prototype's own default parameters via its protocol's "Parent design" line) that the app has been reporting as `not evaluable`. This is the exact staleness ADR 0008 already named as a required, unbuilt safeguard.
- `docs/adr/0009-strategy-onboarding-contract.md` (new, accepted): defines the two-tier contract precisely, with the CTA v2/`research_catalog.py` findings as the motivating evidence.
- `backend/app/research_catalog.py`: `decision`/`evidence` corrected for SMA Cross, RSI Reversion, Wave Pull; the hardcoded two-value loop replaced with a `DECISIONS` registry (real decision + artifact per strategy, derived not guessed); new `CHARACTERIZATION_STUDIES` dict (Tier B) populated with all 16 closed Tier B studies this project currently has (CTA v2, both calendar candidates, ETF-12 rotation, cross-sectional feasibility, consolidation feasibility, overnight gap, TA breakout, Fed put v1-v3, all 3 Chapter 4 candidate scores, the eligibility calibration and orthogonality studies, and factor zoo v1) plus a `characterization_studies()` accessor.
- Not built yet, named in the ADR's Consequences: the `GET /api/research-record` endpoint and frontend page that would actually render Tier B entries. This closes the contract and data gap, not the UI.
- 9 new/rewritten tests in `test_research_catalog.py`, including the ADR's own core invariant: no Tier B study may ever appear in the executable `STRATEGIES` registry, and every result-doc/artifact path referenced is verified to exist on disk. 396 passed.

## 0.75.1

Chapter 4 compacted to match Chapters 1-3's table shape. Docs-only.

- User-directed: Chapter 4 in `research-program.md` had grown to ~263 lines of inline prose (vs. Chapters 1-3's compact `| § | Result |` tables linking out to individual result files) -- "an all abstracts" table, not the working document itself.
- Extracted six new `docs/research-results/` files: `cta-v2-chapter4-eligibility.md`, `wave-pull-chapter4-eligibility.md`, `calendar-dow-chapter4-eligibility.md`, `chapter4-eligibility-calibration-v1.md`, `chapter4-orthogonality-v1.md`, `factor-zoo-v1.md` -- same structure as every other result doc (decision line, Result, Reading this result). No content lost, only relocated.
- Chapter 4 in `research-program.md` rewritten to the same `| § | Candidate | Result |` shape as Chapters 1-3, one-line-per-row. 578 -> 349 total lines in `research-program.md`.
- 391 passed (no code change).

## 0.75.0

Factor zoo enriched to 27 formulas (classic TA indicators added); new data-layers catalog; Chapter 1-3 explicitly paused in favor of Chapter 4.

- User-directed: web-researched (5 parallel angles, 76 sources) open-source daily-OHLCV-only factor libraries beyond WQ101/191 -- Qlib Alpha158/360, curated awesome-quant lists, academic price-volume-only anomalies (Amihud, MAX effect, low-vol/BAB, Corwin-Schultz spread, overnight/intraday decomposition), maintained backtest frameworks, and a direct check on whether any free point-in-time equity fundamentals source exists (verdict: no ready-to-use free vendor; SEC EDGAR raw XBRL is the one genuinely free option but needs real ETL). Findings documented in `docs/brainstorm/2026-08-21-open-source-factor-source-backlog.md` -- acted on, queued, and excluded items each with reasons.
- `backend/app/factor_zoo.py`: added `CLASSIC_INDICATORS` (RSI14, MACD histogram, Bollinger %B, Stochastic %K, CCI20, Williams %R, ROC12, ATR-normalized range, OBV flow, MFI14) -- hand-implemented, not a new dependency, same evaluation harness as the WQ101 subset. 12 new tests (hand-checkable correctness: RSI=100 with no losses, Bollinger %B at the band, Stochastic/Williams %R at the window extreme, ROC arithmetic).
- Real rerun against the same 495-symbol universe: 27/27 factors evaluated, no errors. Every classic indicator scored negative IC-IR under its conventional "high reading = long" direction -- correctly read as the same short-horizon reversal effect the WQ101 cluster already surfaced, from the opposite side, not a new independent finding, and folded into the existing bid-ask-bounce disclosure rather than presented as six more wins.
- One genuine exception: `atr_normalized` (pure volatility-level factor) posted the best raw Sharpe in the whole zoo (0.84, CAGR 20.0%) and was specifically checked for orthogonality against the reversal cluster (fell outside the default top-8 screen) -- confirmed independent (`|r|<=0.34` against all five cluster members), though with a much larger drawdown (-39.4%), the economically expected shape for a volatility-premium factor.
- `docs/data-layers.md` (new): user asked for "a layered, evolving framework" cataloging data sources (macro/bars/future layers) with rich attributes, explicitly as scaffolding, not a build commitment ("we are not at this stage yet"). One row per layer -- built (macro PIT, macro final-revised, daily bars, universe membership, treasury buybacks, credentials) and planned (earnings dates -- confirmed-free `yfinance.get_earnings_dates()`, PIT fundamentals -- confirmed-free-but-real-ETL via SEC EDGAR) -- each with status/PIT-correctness/cost/coverage/used-by. Intraday/tick explicitly marked excluded by design: this project only ever reaches bounded paper trading, never live/HFT execution.
- User-directed pivot, recorded plainly rather than left implicit: Chapter 1-3's full preregistration ceremony is deliberately paused, not abandoned -- reserved for when something needs rigorous verification, appropriate to unfunded self-research rather than a funded institution. Current focus is Chapter 4 breadth on the free data already in hand; Chapter 1-3 resumes once that's exhausted and/or better data (the planned layers above) arrives. `docs/README.md` checkpoint states this explicitly so a future session doesn't read the pause as neglect.
- 391 passed (12 new).

## 0.74.0

Factor zoo v1: 17-formula screen against the real 495-symbol universe -- real Sharpe ratios, real IC, real charts. Chapter 4 §5.

- User-directed, after explicitly pushing back on Chapter 1-3's falsify-forever loop producing no product: build breadth cheaply (WorldQuant-style formulaic alphas) instead of hand-picking one candidate at a time into Chapter 4, and make Chapter 4's output tangible -- numbers and charts, not descriptions of unbuilt infrastructure.
- `backend/app/factor_zoo.py` (new): cross-sectional/time-series operator vocabulary (rank, delay, correlation, ts_rank, decay_linear, scale, ...) plus 17 of the published WorldQuant "101 Formulaic Alphas" (Kakushadze 2015), verified against the reference implementation the user linked, restricted to OHLCV+volume-only formulas -- alpha191 and vwap-heavy WQ101 formulas need fields this project's free data doesn't have. `evaluate_factor` computes per-date rank-IC and a daily-rebalanced equal-weight top/bottom-quintile spread return; `factor_return_metrics` derives Sharpe/CAGR/max-drawdown/Calmar from that series -- deliberately parallel to `portfolio_metrics.py`'s formulas (same math, different input shape), a disclosed duplicate pending the still-open shared-metrics-engine idea.
- `backend/app/run_factor_zoo_scan.py` (new): reuses the already-locked, disclosed-survivorship-biased 495-symbol universe from `cross-sectional-equity-momentum-feasibility-v1.json`. Real run: 495/495 symbols, 2018-12-07 to 2026-08-14 (1,929 common sessions), all 17 formulas evaluated with no errors, ~3 minutes.
- Added `matplotlib` (new dependency) -- zero charting existed anywhere in this codebase before this. `factor_zoo.render_charts` writes two real PNGs: an IC-IR ranking bar chart and a top-6 quintile-spread equity-curve chart. Both are real, non-placeholder output written to `output/research/factor-zoo-v1/`.
- Results: top by IC-IR `alpha034` (Sharpe 0.76, CAGR 8.8%), `alpha004` (0.71), `alpha028` (0.66); two decisively negative, `alpha001` (-0.45) and `alpha035` (-0.30, -52% max drawdown). Orthogonality screen (same `|r|>=0.5` rule as Chapter 4's existing check) found `alpha034`/`033`/`009`/`028` tightly clustered (r=0.58-0.79) -- disclosed as one shared, unconfirmed hypothesis, not four, and flagged as the classic bid-ask-bounce reversal-artifact risk (Jegadeesh 1990, Lehmann 1990) since this scan models zero transaction cost.
- Explicitly framed as a screening pass, same non-evidential status as the engine-feasibility work it reuses -- confers no Chapter 4 eligibility by itself; next named step is proposing the least-redundant survivors (`alpha028`/`004`/`026`) as individual candidates with a stated mechanism and a cost-sensitivity check.
- `docs/research-program.md` Chapter 4 §5 (new section, appended not rewritten, per the chapter's own living/extensible discipline).
- 16 new tests (`backend/tests/test_factor_zoo.py`): operator correctness on hand-checkable synthetic panels, a planted-signal recovery check, a pure-noise near-zero-IC check. 384 passed.

## 0.73.0

ADR 0008 (bounded paper trading + Track B) accepted. Docs-only; no implementation.

- User-directed: accepted the same way ADR 0007 was -- draft, explicit acceptance, implementation as a separate later step. Zero strategies or candidates hold `eligible for operational validation` via any of the three approval paths (strict ladder, Chapter 4, Track B); none of ADR 0008's required infrastructure (`live_price_snapshots`, `paper_ledger_events`, the Alpaca integration module, the reconciliation action) is built.
- `docs/identity.md` (v2 -> v3): new paragraph naming ADR 0008 as the operational-mechanics definition of `eligible for operational validation`, alongside ADR 0007's existing pointer.
- `docs/adr/0008-bounded-paper-trading.md`, `docs/research-program.md` Chapter 5, `docs/README.md`, `docs/roadmap.md` §9C, `docs/product.md` all updated from `proposed` to `accepted`, `2026-08-21`.
- Real next step (blocked): the user needs to create an Alpaca paper trading account and API keys before any live connectivity code can be tested end-to-end -- this project cannot do that step. Metrics-computation code and schema/module scaffolding can proceed without it.
- Saved a brainstorm memo (`docs/brainstorm/2026-08-21-parallel-multi-agent-research-pipeline.md`, non-evidential): user's idea to parallelize research production across multiple concurrent agents, explicitly parked ~6 months out. Named the real risk (shared-ledger concurrent writes, not production work, is what breaks) and the safe shape if picked up later (parallel production, single sequential integration pass).
- 367 passed (no code change).

## 0.72.0

Docs-only: drafted ADR 0008 (bounded paper trading), status `proposed`. No implementation.

- User-directed: after tonight's Chapter 4 work closed without a positive read, an outside evaluation observed this project has "built the order-placer, but has not yet established a system under which it truly dares to approve orders." Directed to draft the operational bridge design as a new chapter (Chapter 5, positioned after Chapter 4 and before the renumbered Discussion chapter, now Chapter 6) and to check build-vs-buy before designing a paper-trading engine from scratch.
- Investigation found the real gap: `positions` has zero rows, `signals.py:advance_positions` is a full-history replay rather than an incremental ledger, and `research_catalog.py` (the existing but stale status-labeling bridge already wired into `/api/strategies` and the frontend) marks only `CTA Trend` with its real verdict, the other six strategies all read `not evaluable`.
- Build-vs-buy: Alpaca Markets' free paper trading API (US equities/ETFs, no local gateway) checked and adopted over a custom fill simulator -- confirmed a standard backend-to-broker REST integration, explicitly not an MCP server (MCP is for LLM-agent tool use, not this app's own broker connectivity).
- `docs/adr/0008-bounded-paper-trading.md` (new): approval gate (sourced from a corrected `research_catalog.py`, gating only the paper-trading action, never visibility -- preserving workspace-redesign.md's show-everything-label-honestly pattern), point-in-time data contract (new `live_price_snapshots`, decoupled from the retroactively-adjustable `bars`), operational risk (ADR 0004's sizing/drawdown reused unchanged, ADR 0007's confidence multiplier wired in as inert-until-needed), reconciliation (daily, explicit, against Alpaca's own account state), and an explicit amendment to `product.md`'s out-of-scope line distinguishing sandboxed paper connectivity from live.
- `docs/research-program.md`: new Chapter 5 documents the bridge and states plainly that zero strategies/candidates currently hold `eligible for operational validation` under any approval path -- this chapter does not create eligible traffic, only the design for when something does.
- `docs/product.md`, `docs/roadmap.md` (new §9C), `docs/README.md` updated to reference ADR 0008; a stale "ADR 0007 (draft)" reference in README's document-authority table corrected to "accepted" while touching the same table.
- **Track B added to ADR 0008, user-directed**: a third, explicitly lighter approval path alongside the two statistical ladders -- a disclosed discretionary/common-sense-pattern basis (e.g. well-known technical patterns), admitted without requiring statistical proof, but under strict, non-negotiable operational terms: a precisely stated mechanical rule, ADR 0004's sizing formula unchanged, and a kill rule locked *before* the first trade and never adjusted after observing results. The kill rule is framed explicitly as protecting against both the user's own after-the-fact rationalization and an assisting agent's over-confidence in its own pattern-matching. Designed as a reusable template for admitting many pattern types cheaply, not a one-off -- directly responds to a standing concern that this project's own rigor was narrowing research effort onto a handful of deeply-scrutinized mechanism families rather than exploring breadth.
- **Full audit pass, user-directed**, before accepting the batch: found and fixed 11 broken relative links in `research-program.md` (systematic `../../` should have been `../`, file sits one level below repo root not two), `docs/adr/0007-risk-budgeted-ensemble-acceptance.md`'s own status header still claiming the pre-correction "Wave Pull eligible / Day-of-Week 6/12 eligible" framing, Chapter 6's triage still describing already-scored candidates in future tense, `roadmap.md`'s opening line pinned to a 17-versions-stale `0.55.0`, and a missing Chapter 6 exclusion in `research-program.md`'s own intro paragraph. Also trimmed two near-duplicate paragraphs in Chapter 4 (a conclusion stated in full both before and after the evidence supporting it) and two minor README redundancies, while confirming disclosed statistical numbers (calibration rates, CIs, correlation matrices) each appear exactly once and are not bloat.
- Sequenced the same way ADR 0007 was: drafted for explicit review/acceptance before any implementation, matching this project's own established pattern. 367 passed (no code change).

## 0.71.0

Calendar Day-of-Week's `6/12` Chapter 4 breadth result directly tested with a correlation-aware significance test and closed. No trade, no cost, no live sizing.

- User-directed: rather than approximate whether cross-asset correlation explains `6/12` (the open question `0.70.0` left standing), build the rigorous test directly. `backend/app/research.py:dow_breadth_correlation_aware_null` (new) is a joint circular-block-resampling null -- one shared block-shift applied to all 12 assets' real return series at once per replication, the same principle `etf12_rotation_bootstrap`/`overnight_gap_bootstrap` already use, preserving the full real joint correlation structure rather than a hand-adjusted design-effect estimate from a partial correlation matrix.
- `backend/app/score_calendar_dow_full_correlation.py` (new) first measured all 66 pairs across the full 12-asset universe (not just the 6 winners): `31/66` redundant, confirming the broader universe is saturated with ordinary equity-beta correlation.
- Hardened by an independent pre-lock adversarial review before touching real data (2 of 3 lenses completed; the third hit a session usage limit mid-run and was completed directly rather than retried) -- mirroring Overnight Gap Continuation v1's own pre-lock-review precedent. One real, non-obvious bug found and fixed: the original shared `block_bars=20` is an exact multiple of the 5-day trading week, letting resampled blocks quietly reproduce genuine historical Monday-to-return pairings instead of scrambling them, biasing the test conservative. Fixed by decoupling the outer cross-asset block size (now 19, not a multiple of 5) from the inner per-asset CI's block size (left at production's locked 20).
- `backend/app/run_calendar_dow_breadth_significance.py` (new) ran the fixed construction against real data, plus two more coprime-with-5 block sizes (17, 23) as a disclosed robustness check per the review's own recommendation.
- Result: `p≈0.13-0.14`, stable across all three block sizes -- Calendar Day-of-Week's breadth is **not distinguishable from chance** once real correlation is properly preserved. Combined with `0.70.0`'s Wave Pull correction, none of Chapter 4's three scored candidates (CTA v2, Wave Pull, Calendar Day-of-Week) currently has a settled, adversarially-checked positive read.
- See [research-program.md](docs/research-program.md) Chapter 4 §3/§4 for the full, corrected record. 367 passed (6 new tests for the joint-null primitive; one pre-existing, already-documented data-fingerprint drift failure on this machine's `data/market.db`, unrelated to this work).

## 0.70.0

Chapter 4 eligibility rule calibrated and its own first read-outs adversarially corrected. No trade, no cost, no live sizing.

- User-directed: a pasted external critique argued Calendar Day-of-Week's `6/12` was close to chance, and that Wave Pull's `TLT`-only report suffered winner's curse -- rather than argue the arithmetic, `backend/app/calibrate_chapter4_eligibility.py` measures both directly via 300-replication Monte Carlo (same discipline as `event-bootstrap-calibration-v1`).
- Result: two-sample (Day-of-Week-shape) false-eligible rate `16.25%` -- the critique's own `32%` figure does not survive the check. Case-resample (Wave-Pull-shape) single-asset rate `19.08%`; "selected winner of 12" rate `84.67%` -- worse than the critique estimated.
- `backend/app/score_wave_pull_chapter4.py` (new) rescored all 12 Wave Pull assets symmetrically, closing the selection-bias gap in the `TLT`-only report: `2/11` eligible (`GLD`, `TLT`).
- A first-pass reading of these results against the real `6/12` and `2/11` counts was itself run through independent adversarial verification (4 reviewers) before being written into docs -- this project's standing practice of checking critiques empirically, applied for once to its own results. Two corrections resulted: Wave Pull's `2/11` is not distinguishable from the calibrated null (`P(X≥2 of 11)≈65%`, the modal outcome) -- walked back to "clean candidate," not "eligible"; Calendar Day-of-Week's `6/12` remains genuinely open, not settled -- correlation among its own winners (measured, `dow_IEF`/`dow_TLT` `r=0.92`, `dow_EFA`/`dow_XLF` `r=0.81`, `dow_DBC`/`dow_EFA` `r=0.51`) could plausibly explain most or all of the apparent significance, and the correlation data needed to settle it (all 12 assets, not just the 6 winners) has not been measured.
- `backend/app/score_chapter4_orthogonality.py` extended to all 8 nominally-eligible signal-slots (added `wave_pull_GLD`): `3/28` pairs redundant, all three among Day-of-Week's winners.
- ADR 0007 status unchanged (accepted). See [research-program.md](docs/research-program.md) Chapter 4 §2, §2b, §3, §4 for the full, corrected record. 361 passed (no engine change; one pre-existing, already-documented data-fingerprint drift failure on this machine's `data/market.db`, unrelated to this work).

## 0.67.1

Docs-only: brainstorm cleanup pass. Added
[trading-folklore-falsification-list.md](docs/brainstorm/2026-08-20-trading-folklore-falsification-list.md)
(higher-high/lower-low swing structure, Fibonacci, golden/death cross,
volume-confirms-breakout, COT positioning, short interest, gamma
pinning, sell-in-May, PEAD, 52wk-high momentum -- idea-stage, none
scored). Compressed [pending-candidate-checklist.md](docs/brainstorm/2026-08-19-pending-candidate-checklist.md)
(277 -> ~90 lines: closed items became one-line pointers to
research-protocols/README.md instead of re-narrated paragraphs) and
[fed-put-long-end-reversal.md](docs/brainstorm/2026-08-19-fed-put-long-end-reversal.md)
(now a closed-line pointer, not a re-derivation). Fixed a real staleness
bug in [macro-reaction-function-narrative-library.md](docs/brainstorm/2026-08-20-macro-reaction-function-narrative-library.md):
it still claimed the ALFRED ingestion gap was unbuilt, which `0.60.0`/
`0.61.0` already closed.

## 0.67.0

Locked, executed, closed Fed put: yield-stress precursor v3 -- amends v2
with a 20-year lookback (756->5,040 sessions), same score/episodes/
machinery otherwise. No trade, no signal.

- User-directed: v2's 3-year lookback read today's `10Y` as near-average, but "rocket high" means multi-decade, not 3-year. v3 tests that reading directly.
- Result: `not_evaluable`, `p=0.885`. One real, concrete finding: `2025 RMP` -- the actual current episode -- is the only one of six to flip positive (`+0.13`), matching "2Y ok, 10Y too high" against a multi-decade reference. The 4 crisis episodes got *more* negative, not less, exactly as the protocol predicted before execution (their 20yr windows are dominated by the higher 1990s-2000s rate era, a secular-decline asymmetry disclosed in the locked protocol, not a post-hoc excuse).
- Three independent designs (v1 n=4, v2 n=6, v3 20yr lookback) all close `not_evaluable` on the pooled, cross-episode claim. Whether today specifically is a genuine exception is real but not answerable by a 6-episode pooled test either way. See [result](docs/research-results/fed-put-yield-stress-precursor-v3.md).
- Closes the yield-stress-precursor line. Byte-identical on rerun. 332 passed (no engine change).

## 0.66.0

Locked, executed, closed Fed put: yield-stress precursor v2 -- amends v1
with a fuller, action-based episode inventory. No trade, no signal.

- User-directed: real Fed action, not press-release branding, is what matters. v1's episodes were all Fed-branded "QE"; v2 adds two real episodes the Fed itself calls "not QE" -- 2019 bill purchases/repo ops (started 2019-10-15, verified live against NY Fed operating-policy record) and the 2025-12 Reserve Management Purchases (started 2025-12-12, the actual current episode). A mechanical alternative -- detecting action-onset directly from TREAST's own trailing growth rate -- was tried and rejected: it flagged ordinary 2003-2007 organic balance-sheet growth and mistimed 2022's active QT *shrinkage* as "rising" (lagged-window artifact). Official operational dates, sourced from the Desk's own record, proved more reliable.
- Result: `not_evaluable`, `p=0.981`, `6`/`6` episodes negative -- including the current episode itself. Disclosed diagnostic: the 4 crisis episodes show both yields collapsing together (flight-to-safety, per v1); 2019 shows the long end falling more than the short end; 2025 RMP shows the short end easing (rate cuts priced) while the long end sits roughly *neutral* against its own 3-year trailing history, not elevated -- the reverse emphasis from the hypothesis.
- Real limitation surfaced, disclosed rather than patched: 10Y at ~4% reads as extreme against a 20-year memory but near-average against this study's pre-committed 3-year lookback, because that window is itself mostly populated by the already-elevated 2023-2025 period. A longer-lookback design is new, separately-locked work, not a parameter tweak to this closed result. See [result](docs/research-results/fed-put-yield-stress-precursor-v2.md).
- Closes the yield-stress-precursor line as framed across two independent designs (v1, v2). 332 passed (no engine change).

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
