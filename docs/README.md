# Documentation

[Home](../README.md) · [Roadmap](roadmap.md) · [Product](product.md) · [Research protocol](research-protocol.md) · [Changelog](../CHANGELOG.md)

## Start here

- [Validation roadmap](roadmap.md) — completed work, the local business
  validation gate, remaining safety work, and why cron/AWS are deliberately
  postponed.
- [Product and research design](product.md) — user-facing views, trading ground
  rules, recorded design decisions, and limitations.
- [Research workspace redesign](workspace-redesign.md) — lessons from the older
  app, explicit-run interaction contract, product visual/copy standard, page
  blueprints, usability tests, watchlists, and model discovery.
- [Out-of-sample research protocol](research-protocol.md) — preregistered CTA
  hypothesis, partitions, acceptance gates, and contamination disclosure.
- [CTA Trend walk-forward v1 result](research-results/cta-trend-wf-v1.md) —
  rejected development hypothesis and exact gate outcomes.
- [CTA Trend v1 implementation audit](research-results/cta-trend-wf-v1-audit.md) —
  independent fold/statistics reconciliation and interpretation limits.
- [Parked research backlog](research-backlog.md) — CTA v1 audit checklist,
  possible CTA v2 structural questions, and restart instructions.
- [Changelog](../CHANGELOG.md) — complete version history.

## Architecture decisions

- [ADR 0001: execution timing](adr/0001-execution-timing.md)
- [ADR 0002: market-data contract](adr/0002-market-data-contract.md)
- [ADR 0003: research statistics](adr/0003-research-statistics.md)
- [ADR 0004: portfolio capital and risk](adr/0004-portfolio-risk-contract.md)
- [ADR 0005: product objective and portfolio benchmark](adr/0005-product-objective-and-portfolio-benchmark.md)

## Component guides

- [Backend](../backend/README.md)
- [Frontend](../frontend/README.md)
- [Local data](../data/README.md)
- [CTA walk-forward notebook](../output/jupyter-notebook/cta-trend-walk-forward.ipynb)

## Machine-readable research records

- [CTA Trend v1 experiment](../research/experiments/cta-trend-v1.json)
- [Attempt ledger](../research/attempts.jsonl)
