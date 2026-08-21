# ADR 0009: Strategy onboarding contract — from closed research result to live surface

Status: **accepted**, `2026-08-21`. Answers a gap found live, not
speculatively: asked to "just register CTA v2" as a live strategy, the
premise turned out wrong on inspection — there was no documented answer
anywhere to "what does a closed research result need before it can appear
in Today / Symbol Research / Strategy Lab," and `research_catalog.py`'s
`decision` field turned out to be hardcoded to two literal strings
regardless of a strategy's actual closed result — a live instance of the
exact staleness [ADR 0008](0008-bounded-paper-trading.md) already named as
a required, unbuilt safeguard ("a test that fails if
`research_catalog.py`'s recorded status... is inconsistent with its actual
closed result under `docs/research-results/`").

## Why now

Direct inspection of `backend/app/run_cta_v2.py` found its own docstring:
*"No cost, execution, or portfolio simulation is authorised by this run"*
— CTA v2 has no per-symbol entry/exit function and cannot have one without
violating its own locked protocol's scope
([full result](../research-results/cta-v2-pooled-trend-overlay.md): *"a
costed executable version... would be a new, independently justified
protocol, not a retry of this one"*). `GET /api/strategies`
(`backend/app/main.py`) confirmed to iterate strictly `for name in
STRATEGIES` — `backend/app/strategies.py`'s executable registry — which
every one of Today, Symbol Research, and Strategy Lab's scoreboard reads
from. There was no path for a no-execution-authorized study to appear
anywhere honestly; the only paths available would have fabricated an
execution state the study never earned.

Separately, and independently real: `research_catalog.py` line 168 reads
`"decision": "rejected" if _is_locked_cta else "not evaluable"` —
literally two hardcoded strings, ignoring each strategy's own `evidence`
block. `SMA Cross`, `RSI Reversion`, and `Wave Pull` each have a genuine
closed Chapter 1 verdict (`not_material_or_not_consistent`, each
confirmed tied to the live prototype's own default parameters via its
protocol's "Parent design" line) that the live app has been reporting as
`not evaluable` regardless.

## The two-tier contract

Every research result belongs to exactly one tier, fixed by whether its
own locked protocol authorized live execution — this is a property of the
result, not a UI choice made per-surface.

**Tier A — executable.** A `backtesting.py` Strategy subclass exists in
`backend/app/strategies.py` with real per-symbol entry/exit logic. May
appear everywhere: Today (live signal via `/api/signal`, full-universe
scan via `/api/today`), Symbol Research (chart entry/exit markers, the
research dossier accordion), Strategy Lab (a live-computed scoreboard row
via `/api/confidence` + `/api/score-return`). A strategy's research
*verdict* controls its *label*, never its visibility — `CTA Trend` stays
visibly `rejected`, the pattern [workspace-redesign.md](../workspace-redesign.md)
already established. All 7 currently registered strategies are Tier A.

**Tier B — characterization-only.** The study's own locked protocol
authorizes no cost, execution, or live position — CTA v2, Fed put v1-v3,
both calendar candidates, ETF-12 rotation, cross-sectional feasibility,
consolidation feasibility, overnight gap continuation, the factor zoo, and
the event-bootstrap/Chapter-4 calibration and orthogonality studies. No
per-symbol entry/exit function exists or may be built without a new,
independently justified protocol — this project's own standing
no-reflexive-follow-up rule, restated here for this specific case, not a
new one. Tier B **may never** appear in Today, never in Symbol Research's
live chart/signal machinery, and never as a live-computed Strategy Lab
scoreboard row — each would fabricate an execution state the result was
never evidenced to support. Tier B's only surface is a read-only
**Research Record** view: the study's own already-computed, fingerprinted
numbers and charts, rendered as-is from `docs/research-results/*.md` and
`output/research/*/*.json`, never recomputed live, never carrying a
"hold/exit today" state, since no such state exists for a no-trade study.

## Mechanical registry

`research_catalog.py` gets a second dict, `CHARACTERIZATION_STUDIES`,
parallel to `STRATEGIES` but for Tier B — each entry: `study_id`,
`chapter`, `decision`, `result_doc`, `artifact`. This is the durable,
mechanical answer to "how do I onboard result #10,000": add one dict
entry pointing at the already-written result doc and artifact. No new
code and no new judgment call per result, because the tier and its
consequences are fixed by this ADR once, not re-derived each time.

`STRATEGIES`' existing `research_contract.decision` field stops being
hardcoded and is derived per-strategy from its real evidence status —
fixing the `SMA Cross`/`RSI Reversion`/`Wave Pull` staleness above, and
closing the specific gap ADR 0008 already named.

## Consequences

- Fixed now: `research_catalog.py`'s `decision` for `SMA Cross`, `RSI
  Reversion`, `Wave Pull` corrected to their real closed verdicts, each
  linked to its actual result doc; `CHARACTERIZATION_STUDIES` added,
  populated with every closed Tier B study this project currently has.
- Not built yet, named as required: the `GET /api/research-record`
  endpoint and the Research Record frontend page that would actually
  render Tier B entries for a user to browse without reading raw JSON.
  [product.md](../product.md) already names "Research Record" as a
  surface with "no separate UI page"; this ADR is the contract that page
  would be built against, whenever it's picked up — not committed here.
- A consistency test (parallel to the one ADR 0008 already named):
  assert no `CHARACTERIZATION_STUDIES` entry ever appears in
  `backend/app/strategies.py`'s `STRATEGIES` dict, and that every
  `STRATEGIES` entry with a closed result has a `decision` matching that
  result — the next concrete verification step, not yet written.
- This changes nothing about any Chapter 1-4 finding's evidential status.
  It only fixes how honestly the live app reports statuses that were
  already decided, and gives future onboarding (this project's own or an
  agent's) one mechanical registry entry instead of a fresh judgment call.
