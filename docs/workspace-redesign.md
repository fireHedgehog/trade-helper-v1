[Home](../README.md) · [Docs index](README.md) · [Roadmap](roadmap.md) · [Product](product.md) · [Changelog](../CHANGELOG.md)

# Research workspace redesign

## Why this stage was inserted

The previous UI treated navigation as permission to calculate. Opening Today,
Strategy Lab, or Symbol Explorer could start scans, portfolio replays, confidence
calculations, or backtests and leave the user watching a global loading overlay.
That is the wrong daily workflow.

The user normally wants to:

1. refresh market data once after the relevant close;
2. explicitly run selected strategies;
3. revisit the last completed results instantly;
4. keep observing chosen symbols even after their position exits; and
5. inspect ranked discoveries separately without letting an algorithm overwrite
   the personal observation list.

## Reference application studied

The redesign reviewed the user's older
[`trade-research-v1`](https://github.com/fireHedgehog/trade-research-v1)
application. Useful workflow patterns include:

- a command dashboard that prioritizes state, actions, and risks;
- a persistent user-managed watchlist;
- separate ranked monitoring views for long-term momentum, emerging strength,
  and early breakouts;
- per-symbol research organized as a headline conclusion followed by expandable
  evidence questions; and
- explicit data-refresh controls and visible latest-data dates.

The older application's algorithms, rankings, paper positions, confidence
language, and automatic report generation are not imported. They do not inherit
validity merely because the older interface was familiar or useful.

## Product-usability standard

The reference is the old application's **business interaction design**, not its
mathematics. A statistically careful application can still fail as a product if
the user cannot tell what to look at after the close. Conversely, attractive
colors and fluent prose cannot repair weak evidence. Stage 8 must satisfy both
halves independently.

| Reuse from the old product | Do not reuse without evidence |
| --- | --- |
| Task-based menus and a command-center landing page | Its ranking formulas or portfolio rules |
| Spacious cards, readable type, color-coded numbers, and clear sections | Vague high/medium/low confidence or feasibility labels |
| Plain-language state and action sentences | Implied certainty from colored prose |
| A personal observation list distinct from system discoveries | Automatic promotion of a ranked symbol into the watchlist |
| Symbol research that starts with a summary and expands into evidence | Unsupported sector relevance, sizing, or crash-risk claims |
| Separate model views and cross-model intersections | Treating model agreement as independent statistical confirmation |

### Visual language

The finished local product should feel like a calm research workstation, not a
dense debug table.

- Use a comfortable base font and line height. Important prices, states, and
  actions must not be rendered as tiny metadata.
- Use generous card padding, vertical rhythm, and space between unrelated jobs.
  Dense tables are reserved for comparisons, not used as the only page layout.
- Use semantic colors consistently and always pair color with text:
  - green = positive measured value or completed entry;
  - red = loss, failed gate, completed exit, or blocking failure;
  - amber = holding, pending action, stale data, or caution;
  - blue = selected research context or neutral primary action;
  - gray = unavailable, never run, not applicable, or intentionally parked.
- Apply color to the number or keyword that carries meaning, not an entire
  paragraph. Signs and units remain visible: `+$1,240`, `-8.4%`, `$71.20`.
- Tables need comfortable row height, sticky/readable headers where useful, and
  visual priority for Symbol, Status, Action, Entry, Exit, Risk, and Data date.
- Color is not evidence and is not the only carrier of state. Text labels and
  symbols remain mandatory even while broad accessibility work is parked.

### Copy and terminology

The interface must translate engine state into concise research language while
preserving exact timing.

- Prefer `New resistance breakout: close $71.20 above 20-day high $70.90;
  intended entry next available open` over `rank 48 / setup true`.
- Prefer `Holding since 2026-06-09 @ $55.00; stop $51.40; no exit signal` over
  `state=long`.
- Prefer `Exited 2026-06-11 @ $64.36 · stop · -6.9%; observing for a new setup`
  over a blank row or `flat`.
- Prefer `No completed full-universe run` over an empty spinner.
- Use `entry pending` until the next-open fill. “New entry” cannot be called a
  holding one session early.
- Reserve `validated`, `rejected`, `unvalidated`, `exploratory`, and `baseline`
  for documented evidence states. Do not use `high confidence`, `strong buy`,
  `high feasibility`, or similar vague claims.

Every conclusion-oriented block should expose, where applicable: data date,
sample/window, benchmark, costs, interval or insufficient-sample warning,
execution timing, and evidence status.

## Target page blueprints

### Today — daily command center

The first page answers four questions in order:

1. **Is the data ready?** A spacious status strip shows expected session,
   actual data date, stale/failed counts, and last completed model runs.
2. **What do I already follow?** The persistent watched-symbol lifecycle shows
   holding/entry-pending/exit-pending/exited state, last entry, last exit, next
   action, current stop, and a readable reason sentence.
3. **What is newly actionable?** Model tabs show every entry-pending candidate
   from that model's completed full-universe run, plus intersections. Tabs carry
   candidate counts and last-run dates; an unrun tab has a designed empty state.
4. **What needs an explicit action?** Watch update, full-universe model scan, and
   portfolio comparison are distinct buttons with progress, completion, and
   failure feedback.

The page must not lead with portfolio backtest statistics when the daily user
question is “what changed after this close?” Portfolio comparison remains a
separate, lower-priority research panel.

### Symbol Research — modern `投研`

The symbol page should become a research dossier rather than a chart plus a
developer metrics rail.

- A spacious identity/header block: symbol, latest close/change, data date,
  watchlist membership, and current per-model lifecycle state.
- A plain-language summary per algorithm: latest condition, exact threshold,
  intended next action/timing, and evidence label.
- Expandable model sections so the user can compare algorithms without
  duplicating their implementations.
- Inside each section: why the state exists, entry/exit levels, stop/risk,
  current position lifecycle, historical trade metrics, benchmark difference,
  sample size, uncertainty, and known limitations.
- Price, return, drawdown, risk, and failed-gate numbers receive consistent
  semantic color. Prose highlights only the critical phrases.
- Sector/peer context appears only after a tested data contract exists. Until
  then it remains an explicit placeholder, not a fabricated suitability score.
- The chart supports the written explanation; it does not replace it.

The old high/medium/low feasibility presentation is explicitly rejected.
Measured intervals may still be wide or noisy; the product must say so directly.

### Strategy Lab — experiment workspace

- Separate watchlist ownership, parameter selection, historical comparison, and
  experiment execution into visually distinct sections.
- Saved parameter sets are inputs, never labelled “best” or “optimized” without
  a corresponding locked experiment result.
- Completed scoreboard/experiment runs persist with version, universe, period,
  costs, parameters, coverage, and failures.
- Tables use colored signed outcomes and clear benchmark columns, but the final
  evidence decision remains `reject`, `revise`, or `continue` under a written
  protocol.

### Data Management — operator page

- Lead with data readiness and the action required, not hundreds of rows.
- Use large progress, processed/total counts, current symbol, elapsed state,
  failures, and a durable completion summary.
- Preserve the detailed searchable inventory below the operational summary.
- A successful provider refresh does not automatically run strategies. The page
  tells the user which model snapshots are now older than the data.

## Usability acceptance tests

Stage 8 is not complete merely because the APIs work. A non-programmer should be
able to complete these tasks without reading source code or guessing terminology:

1. identify whether data is ready for the intended close;
2. save/remove/reorder watched symbols for one model;
3. distinguish holding, pending entry, pending exit, exited, and never-entered;
4. identify the last entry and exit prices/dates without opening another page;
5. run one model across the full stored universe and see progress;
6. find every new-entry candidate and understand the intended fill timing;
7. compare model tabs and intersections without mistaking agreement for proof;
8. open one symbol and read its state, risk, evidence, and limitations in plain
   language;
9. recover the same state after reload or restart; and
10. recognize stale data, failed calculations, insufficient evidence, and an
    intentionally empty model.

The browser smoke suite should cover the happy path, empty state, stale/failure
state, reload persistence, large-run progress, and a narrow screen. A short
manual usability script should be retained for language and visual judgment that
automation cannot establish.

## Accepted product contract

### Navigation is read-only

Opening a menu may fetch small stored JSON but must not run a scan, backtest,
portfolio replay, or research calculation. The last explicit strategy run is
stored in SQLite and displayed immediately. No stored run is an honest empty
state, not an instruction to calculate automatically.

### Actions are explicit

- Data Management owns provider refresh.
- Today owns separate “Update watched status” and full-universe candidate-scan
  actions.
- The portfolio comparison has its own run button.
- Symbol Research owns “Run Backtest.”
- Strategy Lab owns “Compute / refresh.”

Changing a symbol, strategy, parameter, date range, or menu does not implicitly
press any of those buttons.

### Watched lifecycle and new-entry discovery are different jobs

- **Watched lifecycle:** user-selected, persistent per strategy, stable through
  entry pending, holding, exit pending, exited, and never-entered states. It
  shows the last entry, last completed exit, next canonical action, stop when a
  position is actually held, and data date. A holding row has no current exit.
  There is no implicit core-list fallback: an empty saved list stays empty and
  the update action asks the user to save symbols in Strategy Lab.
- **New-entry discovery:** requires a separately completed `all`-scope run for
  that model. The run evaluates every stored security and retains every
  `entry_pending` candidate, even when it falls outside the top heuristic ranks.
  Tabs never substitute a watchlist/core run for a universe scan.
- **Ordering:** each algorithm preserves its own rule rank. The score is
  descriptive and unvalidated, so it is not a probability or recommendation.

### Research dossiers expose evidence state

Symbol Research uses expandable strategy sections with summary evidence labels,
rules, general risks, and pending sector relevance. CTA v1 stays visibly
rejected; baselines, exploratory strategies, and unvalidated strategies are not
presented as passed models.

### Model discovery uses tabs, not horizon cards

The monitoring workspace keeps separate tabs for intersections, Momentum, New
Breakouts, and every implemented strategy. Each strategy tab reads only that
model's last completed full-universe snapshot, displays every entry-pending
candidate, reports evaluated-universe coverage, and preserves that model's own
ordering. Intersections require the same new-entry candidate in at least two
stored model runs; agreement is not independent statistical evidence.

The Momentum tab is an intentionally empty facility until a cross-sectional
momentum hypothesis is preregistered and validated. Candidate horizons such as
3/6/12 months and the older application's composite factor ranking are not
silently imported. New Breakouts combines entry-pending candidates across
existing full-universe model runs; it is not a separate validated algorithm.
Empty tabs are valid operational/evidence states and explain exactly which full
scan or research definition is missing.

## Persistence contract

`strategy_watchlists` stores the ordered per-strategy observation list.
`strategy_runs` appends immutable completed snapshots containing parameters,
scope, data date, watched lifecycles, full-universe entry candidates, ranking,
failures, and coverage. Reading the latest run performs no calculation. The
latest watchlist status and latest `all`-scope candidate run are queried
independently so a fast watch update cannot erase the discovery board.

This is local research state, not paper trading state. It does not create orders,
positions, brokerage authority, or evidence that a strategy works.

## Remaining redesign slices

### v0.26.0 checkpoint — workflow foundation complete

- Read-only navigation and explicit expensive actions.
- Persistent per-strategy watchlists and immutable strategy snapshots.
- Separate watched lifecycle and full-universe new-entry discovery.
- Per-model and intersection tabs with honest empty states.
- Initial evidence-state accordions and Data Management workflow.

This checkpoint is **not** the finished product design. It intentionally freezes
the business-state contract before the visual and language rebuild.

### Productization still pending

- Build the semantic color/type/spacing system and replace the compact debug-like
  layout with spacious responsive cards and readable tables.
- Redesign Today into the ordered data → watched state → new candidates → action
  command-center hierarchy.
- Redesign Symbol Research to the dossier blueprint above with readable state,
  thresholds, evidence, risk, benchmark, and uncertainty per algorithm.
- Add durable full-universe scan progress and completion/failure history; the
  current synchronous 500+ symbol action can still feel like a long spinner.
- Persist Strategy Lab scoreboard/experiment runs instead of retaining results
  only in the browser session.
- Add watchlist notes and deliberate add/remove/reorder interactions.
- Replace engine jargon and generic rank notes with tested sentence templates
  that include exact levels, timing, units, and data dates.
- Add richer dossier summaries only when backed by explicit data; never
  fabricate sector suitability or confidence levels.
- Split the single frontend file after the interaction and visual contracts
  stabilize, then add automated state/render tests.
- Complete narrow-screen and accessibility work before external use.

## Work after the product stage

- Passive ETF-12, SPY, and cash comparisons are already implemented; they are
  not a missing UI-stage prerequisite and do not prove a strategy edge.
- Stage 9 resumes the research decision gate: one economically justified
  hypothesis, numeric rejection criteria, then a locked experiment.
- Stage 10 cron and Stage 11 AWS remain parked behind product usability,
  research, security, persistence, recovery, and operations gates.

## Preserved next research priority

Before this stage was inserted, the next planned research task was to define one
new economic hypothesis and its numeric pass/fail criteria. CTA v2 and machine
learning were parked. That priority is preserved as Stage 9 and resumes after
the usable local research workspace gate passes.
