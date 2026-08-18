# Workspace redesign specification

Status: Stages 8A–8B complete; 8C–8D pending. This is the authoritative UX contract.

## Design premise

The legacy `trade-research-v1` application is a reference for product workflow, not scientific truth. Retain its useful qualities—clear menus, spacious composition, coloured numbers and phrases, scan-friendly market language, ranked views, and accordion-based symbol research. Reject its vague feasibility labels, unsupported confidence, and untested algorithms.

The current application contains stronger research machinery but still reads like a developer console. Stage 8 converts it into a daily research product without making its evidence sound stronger than it is.

## Information architecture

| Page | Primary question |
|---|---|
| Today | What changed, what needs action, and what is worth inspecting now? |
| Symbol Research | What do the available models and evidence say about this symbol? |
| Strategy Lab | What exact hypothesis was run, against which benchmark, and why did it pass or fail? |
| Data Management | Is the input current and complete, and what refresh action is required? |
| Research Record | What was specified, observed, decided, and superseded? |

Navigation loads persisted state only. Network refresh and strategy evaluation require explicit labelled actions.

### Shared daily pipeline

Manual buttons and future scheduling must invoke one durable pipeline, never parallel implementations:

`check expected session → refresh required symbols → validate/promote data → run required model versions → persist/publish snapshot`

Each stage starts only after its dependency succeeds. Freshness is evaluated per symbol against the expected completed market session. Strategy currency is evaluated from the input-data fingerprint plus model/version/parameter fingerprint. Consequently:

- current symbols are skipped rather than downloaded again;
- a current strategy snapshot is skipped rather than recomputed;
- an early manual run makes the later scheduled invocation a recorded no-op;
- partial refresh failures block only dependent results and are individually retryable;
- no strategy snapshot may silently combine valid and unvalidated refreshed data.

The permanent controls are `Review/refresh data`, `Update watched status`, `Run full-universe candidates`, `Run portfolio comparison`, and eventually `Run daily pipeline` / `Retry failures`. The scheduler is only a Stage 10 trigger over this pipeline; it adds no business logic.

## Visual and language system

### Layout

- Prefer generous spacing, strong section hierarchy, large primary metrics, and short readable summaries.
- Tables remain dense enough for comparison but not compressed into implementation dashboards.
- Use cards for decisions and summaries; use tables for exact repeated fields; use accordions for secondary per-model evidence.
- Desktop is primary, but narrow layouts must preserve action order and table meaning.

### Semantic colour

Colour communicates domain meaning: favourable, adverse, caution, stale, neutral, price, date, and evidence state. It must never be the sole carrier of status. Unsupported “high/medium/low feasibility” labels are prohibited.

### Copy

Prefer concrete phrases such as “newly closed above $71 resistance”, “entry pending for next open”, “last exited 2026-06-09 @ $55”, “data current through 2026-08-17”, or “model not yet validated”. Avoid raw enum names, generic “success”, or probability language unsupported by the statistical design.

Every result distinguishes:

- signal state from position state;
- model output from validated evidence;
- no result from not run, stale, running, and failed;
- historical observation from an instruction to trade.

## Today command centre

Order sections by daily decision value:

1. Data and run status: latest market session, coverage, last refresh, last strategy run, staleness, and explicit `Refresh data` / `Run strategies` actions.
2. Watched symbols: persistent per-strategy state machine.
3. New-entry candidates: full-universe results by model.
4. Intersections: symbols selected independently by multiple models.
5. Research warnings: invalid/placeholder models, insufficient data, failures, and evidence limitations.

### Watched-symbol table

Required fields: symbol, strategy, position (`Holding` or `Flat`), current signal, last entry, last exit, evaluated through, and concise risk/evidence note. When holding, last exit is `—`; when flat after an exit, active holding fields are `—`. A new entry is an event that normally leads to `Holding`; it is not a third permanent position category.

User additions/removals persist. Rankings and candidate runs never replace this list.

### Candidate tabs

Tabs represent model outputs over the entire configured universe: CTA, SMA cross, breakout, momentum horizons, future versioned models, and intersections. After a completed run, show every eligible new-entry candidate, with deterministic ordering and model-specific reason fields. Before a valid run, show an explicit placeholder or `not run`; never manufacture candidates.

Candidate rows should include symbol, signal phrase, reference price/level, date, model version, rank or locked score where defined, data session, and evidence status. CTA v1 remains visibly rejected; pending models remain visibly unvalidated.

## Symbol Research

The header presents symbol, current price/session, freshness, watched status, and relevant actions. Below it, each available model has an accordion:

- collapsed summary: current state, concise signal phrase, evidence label, and key risk;
- expanded content: rationale, relevant levels/horizons, lifecycle history, benchmark comparison, uncertainty, model version, and data provenance.

Use the application’s own versioned models only. Sector and macro context may be descriptive but cannot masquerade as causal evidence. Accordions with no validated implementation remain honest placeholders.

## Strategy Lab

Separate experiment definition from result inspection. An experiment displays hypothesis, model version, universe, parameters/search space, execution, costs, benchmark, validation design, fingerprint, and status. A run displays durable progress and can be revisited after navigation or reload.

Results lead with the decision (`rejected`, `revise`, `continue research`, or `not evaluable`), then benchmark-relative return/risk, uncertainty and multiplicity, stability, costs/turnover, failure reasons, and artifact links. Never lead with an isolated profitable curve.

## Data Management

Provide a symbol-level table containing provider, rows, first/last session, expected latest session, freshness, last successful refresh, current job state, and failure message. Support selected or all-symbol refresh with a hard-coded provider delay, visible queue/progress, cancellation only when safe, retry of failures, and atomic promotion of valid data.

Freshness is a comparison between the latest valid local session and the expected market session, not wall-clock age alone. A 404 or transport failure is a failure state, not an infinite loader.

## Asynchronous-state contract

Every remote or long-running surface implements: `idle/not run`, `queued`, `running`, `complete`, `complete with no candidates`, `stale`, `failed`, and, where safe, `cancelled`. Persist job identity, requested scope, progress counts, timestamps, errors, and resulting data/experiment fingerprint. Reloading must reconstruct state rather than restart work.

## Delivery slices

- 8A complete: persistence, lifecycle semantics, watchlist/candidate separation, tabs/intersections, explicit actions.
- 8B complete: semantic tokens, copy mapping, responsive spacious shell, ordered Today actions, lifecycle/candidate presentation, and regression/browser verification.
- 8C next: Symbol Research, Strategy Lab, and Data Management productisation.
- 8D: durable jobs; the shared dependency-aware daily pipeline; idempotent `skipped_current`, partial-failure, and retry semantics; responsive/usability pass; smoke/regression coverage.

## Acceptance tests

A user must be able to determine, without source knowledge:

- whether data and results are current;
- whether an action will read, refresh, or compute;
- what is held, pending, or exited and when;
- which full-universe symbols are new candidates for each model;
- whether an empty area means no candidates, no run, stale data, or failure;
- which models are rejected, unvalidated, or eligible for further research;
- what benchmark and version produced a claim.

No workflow may imply that a signal is an order, a ranking is a watchlist, a placeholder is validated, or historical output is investment advice.
