# Documentation and resume checkpoint

This file is the authoritative entry point for a new agent or work session. Do not infer current work from the changelog.

## Checkpoint

| Field | Value |
|---|---|
| Version | `0.26.0` |
| Checkpoint commit | `628af02` |
| Verification at checkpoint | `176 passed` |
| Completed | Stage 8A: workspace state and workflow foundation |
| Next product work | Stage 8B: semantic visual system and Today command centre |
| Parked research | Stage 9: new hypothesis and statistical design |
| Parked operations | Stage 10 cron; Stage 11 deployment |

The application is functionally structured but not yet a production-quality research interface. Preserve the v0.26 state model; redesign presentation around the proven workflow of the legacy application without importing its unvalidated algorithms or vague confidence claims.

Heavy statistical work is intentionally paused. On resumption, read the protocol, CTA result, audit, and backlog before proposing CTA v2. Do not tune CTA v1 after observing its rejection.

## Non-negotiable state

- Product purpose: decide `reject`, `revise`, or `continue research`; never imply validated profit.
- Primary benchmark: Passive ETF-12 v1; secondary references: SPY buy-and-hold and cash.
- CTA v1: rejected under its locked protocol; this does not reject trend following generally.
- Execution: signal on completed close `N`, fill at next available open `N+1`.
- Watchlists: user-selected symbols persist per strategy and show lifecycle state.
- Candidate tabs: full-universe new-entry candidates per model, plus intersections; they are not watchlists.
- Data refresh and strategy runs are explicit actions, not navigation side effects.
- Cron, paper/live trading, brokers, and AWS remain out of scope.

## Document authority

| Question | Authoritative document |
|---|---|
| What is the product? | [Product contract](product.md) |
| How should the interface work? | [Workspace redesign](workspace-redesign.md) |
| What happens next? | [Roadmap](roadmap.md) |
| How was CTA v1 tested? | [Research protocol](research-protocol.md) |
| What did CTA v1 show? | [Result](research-results/cta-trend-wf-v1.md) and [audit](research-results/cta-trend-wf-v1-audit.md) |
| What research may follow? | [Research backlog](research-backlog.md) |
| Why are contracts fixed this way? | [ADRs](adr/) |
| What changed by version? | [Changelog](../CHANGELOG.md) |

Component notes: [backend](../backend/README.md), [frontend](../frontend/README.md), [data](../data/README.md), and [generated outputs](../output/research/README.md).

## Resume sequence

1. Confirm `git status`, current version, and tests.
2. Read this checkpoint and the document for the active stage.
3. Preserve locked contracts unless creating a versioned ADR/protocol amendment.
4. Implement one bounded stage slice; update tests, roadmap, checkpoint, and changelog together.
5. Record research evidence as immutable results, not rewritten narrative.
