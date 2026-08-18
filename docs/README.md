# Documentation and resume checkpoint

This file is the authoritative entry point for a new agent or work session. Do not infer current work from the changelog.

## Checkpoint

| Field | Value |
|---|---|
| Version | `0.30.0` |
| Parent release | `0.29.1` (independent governance audit) |
| Current state | Stage 8C in progress: bounded dataset and strategy metadata productised |
| Verification | `192 passed` plus headless Playwright workflow checks |
| Completed | Stage 8A state foundation; Stage 8B visual system and Today command centre |
| Next product work | Continue Stage 8C with explicit Strategy Lab experiment hierarchy and durable Data Management job presentation |
| Parked research | Stage 9A: acceptance standard and candidate priority; then 9B locked experiment |
| Parked operations | Stage 10 cron; Stage 11 deployment |

The application has the Stage 8B Today command centre plus Stage 8C improvements to Symbol Research, refresh/watchlist recovery, and research metadata. Version 0.30.0 implements a deliberately bounded registry for the three existing data products and exposes version, family, evidence status, information profile, required datasets, and typed parameters for every executable strategy in the API and UI. It is not a universal ontology and does not authorize new providers, factors, or strategies. Preserve the v0.26 state model and shared manual/scheduled pipeline contract; continue productising the remaining surfaces without importing legacy algorithms or vague confidence claims.

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
| Where do non-contract brainstorm notes live? | [Brainstorm index](brainstorm/README.md) |
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
