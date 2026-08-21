# Strategy library — standing contract for what gets onboarded, where

Status: operational playbook, `2026-08-21`, extends [ADR 0009](adr/0009-strategy-onboarding-contract.md). Makes no new architectural decision — turns one already accepted into a checklist an agent can execute without reopening the design discussion.

If the request was phrased as "make this result available on the trade desk" — that is this playbook, for Today/Symbol Research/Strategy Lab/Strategy Management collectively. [identity.md](identity.md) is still the anchor on what those pages actually are (a research decision aid, never an execution system); this file is the mechanical *how*, not a reason to relitigate the *what*.

## Read this first: the standing answer to "should we show it?"

Yes. Always. A closed research result with a negative or rejected verdict is a complete, successful output of this product — not a defect to soften, hide, or ask permission about. [ADR 0009](adr/0009-strategy-onboarding-contract.md) already settled this: *"a strategy's research verdict controls its label, never its visibility."* [product.md](product.md) already frames the product's primary output as a sequence of `reject`s. An agent picking up this file does not need to relitigate whether a bad number should ship — it should. The only two open questions for any new result are Step 1 and Step 2 below, never "is this okay to show."

## The disclaimer this app already carries — extend it, don't reinvent it

Today already ships a live disclaimer banner ([frontend/index.html](../frontend/index.html), `.safety-banner`, currently rendered on the Today view only):

> "Research only. 'Entry' and 'exit' describe historical rule state at the latest stored close — not an order, forecast, or permission to trade. Check freshness and failures first."

That sentence is the standing policy, not just UI copy: every strategy and study this project shows — rejected, accepted, exploratory, unvalidated — is shown with its real evidence, correctly labeled, linked to its immutable `docs/research-results/*.md` record. A visible `rejected` is transparency working correctly, not a fault, and nobody reading this app is being told to trade anything. If a page other than Today ends up showing strategy verdicts without this banner nearby, that's a small gap to close (copy the div), never a reason to hold back a result that's otherwise ready to ship.

## Step 1 — Classify: Tier A or Tier B?

Ask exactly the question ADR 0009 already asks: **does the result's own locked protocol authorize a real per-symbol entry/exit rule, with cost and execution simulation?**

- **Yes → Tier A.** It can run live, everywhere.
- **No → Tier B.** Portfolio-level overlays, cross-sectional rankings, macro precursors, factor screens, calibration/orthogonality studies — anything without a per-symbol tradeable rule. Building one *now* just to reach Tier A is new research (its own independently justified protocol), not an onboarding step. Don't fake it to make a page look fuller.

## Type taxonomy — the second classification every entry needs

Tier (A/B) says where a result can run. Type says what *kind* of claim it is — exactly three professional buckets, no fourth, defined in `research_catalog.STUDY_TYPES` and enforced by test:

- **Time-Series** — a single asset's own history (technical patterns, calendar effects, trend/breakout, mean reversion). [research-program.md](research-program.md) Chapter 1.
- **Cross-Sectional** — ranks or compares across the universe at a point in time (rotation, relative strength, factor screens using rank-IC/quintile spreads). Chapter 2.
- **Macro** — driven by policy, rates, or economy-wide series rather than an asset's own price history. Chapter 3.

A methodology/meta-study (calibration, orthogonality) has no signal of its own — classify it by what it evaluates, not its own machinery. `chapter4-eligibility-calibration-v1` and `chapter4-orthogonality-v1` both currently evaluate Chapter 1 (Time-Series) candidates, so both are typed `Time-Series`; that will change the day a Cross-Sectional or Macro candidate reaches Chapter 4 scoring. Every `STRATEGIES` (Tier A) and `CHARACTERIZATION_STUDIES` (Tier B) entry carries a `type`, deferred or not — it is registry metadata, not a display-readiness gate.

## Origin — a display grouping within Tier A, not a fourth tier

Tier A now has two provenances, both still Tier A under ADR 0009's same test (a real per-symbol entry/exit rule) — `origin` in `research_catalog.py`'s `STRATEGIES` metadata, one of exactly two values (`STRATEGY_ORIGINS`):

- **`preset`** — the original 7 (CTA Trend, SMA Cross, Donchian Trend, S/R Bounce, Fib Retrace, Wave Pull, RSI Reversion): classic/textbook patterns, the kind a retail broker app ships by default. Most are already closed `not_material_or_not_consistent` or `rejected` — familiar, not validated.
- **`chapter4_screen`** — sourced from a real factor-zoo finding that cleared independence/cost/regime checks first (e.g. `ATR Vol Premium`, from `atr_normalized`). A higher bar of provenance than a preset, still not a validated claim (`evidence.status` says so honestly either way).

This is a label, not an architectural split — don't build a third tier around it. It exists so a dropdown or table can group "familiar baseline" from "actually screened here" without pretending either is proven. The group labels themselves say only "Classic presets" / "Chapter 4 — screened candidates" — deliberately without a "(Tier A)" suffix, so the grouping doesn't read as a competing tier system next to Strategy Management's actual Tier A/B column. Wired into every place Tier A appears as a list: `#strategy`/`#today-strategy`/`#lab-watch-strategy`'s `<optgroup>`s, Today's discovery-tab sub-groups, and Strategy Lab's scoreboard (a group-header row between the two, order preserved: presets first, screened candidates after).

## The full library — Strategy Management shows every tier, not Tier B alone

`research_catalog.library_entries()` (`GET /api/strategy-library`) normalizes **every** Tier A strategy and every onboarded Tier B study into one shape (`tier`, `origin`, `type`, `category` — chapter for Tier B, family for Tier A — `decision`, `summary`, `github_url`) for Strategy Management's table. This is a second, broader accessor than `research_record_entries()` (Tier B only, still what feeds the unified dropdowns on Today/Symbol Research/Strategy Lab) — Strategy Management is the one surface meant to answer "show me literally everything, one row each, traceable" for an outside reader. A Tier A entry with no closed result yet (`artifact` is `None`) gets `github_url: null`, rendered as "no closed result yet" — never a fabricated or broken link.

## Where a result actually appears — one list everywhere, not a separate page

Settled as of `0.76.4`, correcting an earlier version of this section that was wrong: Tier B does **not** live on a separate page from Tier A. Every dropdown/tab list that offers a strategy — Today's "New-entry candidates by model" tabs, Symbol Research's `#strategy` dropdown, Strategy Lab's `#lab-watch-strategy` dropdown — offers Tier A *and* Tier B together, same list, same alphabetical company. There is exactly one thing that differs by tier, not visibility: **what happens when you pick one.**

- **Tier A selected:** the normal live flow — editable params, "Run Backtest," chart markers, scoreboard row, per-symbol watchlist.
- **Tier B selected:** no params, no "Run Backtest" outcome to compute, no chart, no watchlist — instead, its record (`name`, `type`, `chapter`, `decision`, `summary`, `github_url`, via `recordCardHtml()` in `frontend/index.html`) renders inline, right where the live output would have gone. Today's discovery tabs show it as the row content instead of a candidate table; Symbol Research shows it in the metrics rail instead of backtest metrics; Strategy Lab shows it in the Definition card exactly like a Tier A entry's contract, just with "Save as strategy watchlist" disabled.

Why this and not a separate "Research Record" page as originally built at `0.76.2`: fragmenting Tier A and Tier B across two different UI locations meant a real user had to already know Strategy Management existed and remember to go look — the opposite of "make it all available." **Strategy Management still exists** (a dedicated table, one row per study, useful for browsing/comparing the whole roster at once) — it is additive, not the only way in.

The one thing that never changes, restated because it's the actual hard constraint underneath all of this: a Tier B selection never gets a live chart, a live signal, or a "hold/exit today" state, in *any* of these surfaces — that would fabricate execution the study never earned. Appearing in the same list is a visibility question; running live is a Tier A/B question, and only Step 1 answers that one.

## Step 2a — Onboard Tier A (executable strategy)

Three registries, no per-page work after that — Today, Symbol Research (chart + accordion), and Strategy Lab (definition card + scoreboard) all read the same shared data:

1. `backend/app/strategies.py` — add the real `backtesting.py` Strategy subclass, its `STRATEGY_PARAMS` entry, and register it in that file's `STRATEGIES` dict.
2. `backend/app/research_catalog.py` — add matching entries to that file's own `STRATEGIES` dict (`strategy_id`, `origin` — `preset` or `chapter4_screen`, see below — `type`, `version`, `family`, `information_profile`, `required_datasets`, `evidence.status/label/summary`), to `HYPOTHESES`, and to `DECISIONS` (the real `decision` string — `rejected` is a complete, valid answer — plus the `docs/research-results/*.md` artifact path once one exists, `None` before that).
3. Nothing else. `research_contract` (`hypothesis`, `execution`, `scoreboard_benchmark`, `validation_design`, `decision`, `artifact`) is derived automatically from those three dicts at import time — never set it by hand, and never touch a frontend file to make a new strategy appear.

Also see [workspace-redesign.md](workspace-redesign.md) for what Symbol Research must then show for it (chart markers, accordion, current P&L) — that is an interface contract, not an onboarding step, so it lives there, not here.

## Step 2b — Onboard Tier B (characterization-only study)

One dict entry: `backend/app/research_catalog.py`'s `CHARACTERIZATION_STUDIES[study_id] = {"chapter": ..., "type": ..., "decision": ..., "result_doc": "docs/research-results/....md", "artifact": ...}`.

That is the entire onboarding step — same as ADR 0009 already says. `research_record_entries()` (`GET /api/research-record`) is the one function every surface reads from — Strategy Management's table, and (as of `0.76.4`) Today's discovery tabs, Symbol Research's dropdown, and Strategy Lab's dropdown all pull the same list. A study only needs `name`/`summary`/`type` fields (see the entry shape in `CHARACTERIZATION_STUDIES`) to appear everywhere at once; nothing else to wire, no per-surface work.

A study can be deliberately held back from that page without leaving it un-onboarded in the registry — add its `study_id` to `research_catalog.py`'s `DEFERRED_FROM_RECORD` set with a one-line reason (as of `0.76.2`: only the factor zoo screen, parked pending a clearer explanation to the user, not a rejection). Deferred is not a permanent state — revisit, add `name`/`summary`, and drop it from that set when it's time.

The one hard line here, not up for renegotiation per-result: a `CHARACTERIZATION_STUDIES` entry must never also appear in `backend/app/strategies.py`'s `STRATEGIES`, and never gets a live chart, live signal, or "hold/exit today" state. That would fabricate execution the study never earned — the one thing this contract actually forbids, and the only thing worth pausing to double-check before shipping.

## Where "the library" actually lives

There is exactly one source of truth: `STRATEGIES` + `HYPOTHESES` + `DECISIONS` + `STUDY_TYPES` in `research_catalog.py`, the executable `STRATEGIES` in `strategies.py`, and `CHARACTERIZATION_STUDIES` in `research_catalog.py`. This document is deliberately not a duplicate listing of names, descriptions, and links — a hand-maintained second copy is exactly how `research_catalog.py`'s `decision` field went stale before ADR 0009 caught it. Need the current roster? Read the code, or call `/api/strategies` / `/api/research-record`.

## Out of scope for this playbook

- Promoting a Tier B finding into a real Tier A strategy is new research (its own protocol), not onboarding.
- A finding with no closed verdict yet has nothing to onboard — preregister and run it first.
- This playbook does not reopen ADR 0009's design. If a future case doesn't classify cleanly under Step 1, that's a new ADR-worthy question, not a reason to bend this one.
