# Product identity

Status: v3 — canonical, distilled identity statement. Read immediately after the authoritative [resume checkpoint](README.md). Full contracts: [product.md](product.md), [hypothesis-engineering.md](hypothesis-engineering.md), [model-acceptance-standard.md](model-acceptance-standard.md), [exploration-protocol.md](exploration-protocol.md), [research-protocol.md](research-protocol.md), [ADRs](adr/). Edits require a version bump; the statement must stay precise and non-redundant.

## What we run (one line)

A systematic, preregistered, falsifiable research process that adjudicates trading-strategy hypotheses and outputs evidence decisions — `reject`, `revise`, `continue research` — against passive ownership after costs. It is a research decision aid; it is not an alpha finder, not a trading recommendation, and not an execution system.

## The four layers

| Layer | Term | What it means here |
|---|---|---|
| Method | Systematic | Rules + code + data, reproducible. No discretionary call is a claim. |
| Discipline | Preregistered / confirmatory | Protocol locked before results; post-hoc tuning is contamination. |
| Statistical core | Multiple-testing control + backtest-overfitting defense | Implemented for CTA v1: Holm + block bootstrap, locked costs, passive comparisons. Stage 9B methods are hypothesis-specific: trial inventory, prospective precision/power, cost stress, exposure decomposition, overfitting diagnostics, and confirmation. The evidence bar rises with search freedom. |
| Product | Research decision aid | Outputs only evidence decisions; never "alpha", never an order. |

Implemented = running in the engine today. Contracted = mandatory reporting for Stage 9B candidates; documented, not yet code.

## Epistemic ladder (what an output means)

| Output | Meaning |
|---|---|
| `reject` | The locked claim fails or the experiment is invalid. |
| `revise` | Evidence motivates a new, independently stated hypothesis (new version, new search budget). |
| `continue research` | All gates pass; run the untouched confirmation test once. |
| `eligible for operational validation` | Confirmation passes; only then bounded paper trading — an operational test (data/state/execution), not an alpha test. |

**A second, parallel ladder exists as of [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md)
(status: accepted `2026-08-20`; the ensemble engine, minimum-breadth floor,
and live attrition rule remain unbuilt) — Chapter 4 of [the research
program](research-program.md).** It does not replace or lower this one: a
signal that clears *this* ladder graduates here, as before. Chapter 4
answers a different question for signals that do not — a disclosed,
modest, *uncertain* expected value, sized down by its own uncertainty via
Loss-based Quantity Determination and combined into a diversified,
risk-controlled ensemble, rather than asked to prove itself alone at high
confidence. Its own terminal state is the same one this ladder already
names: `eligible for operational validation`, never profit claimed
directly.

**[ADR 0008](adr/0008-bounded-paper-trading.md) (status: accepted
`2026-08-21`) defines what `eligible for operational validation` actually
requires operationally** — point-in-time data (decoupled from the
retroactively-adjustable backtesting series), risk-controlled sizing
(reusing [ADR 0004](adr/0004-portfolio-risk-contract.md) unchanged),
daily reconciliation against a broker's own paper-account state, and an
approval gate — before any candidate that reaches this ladder's terminal
state can actually be paper-traded. That gate now has **three** entry
paths: this strict ladder, ADR 0007's parallel one, or ADR 0008's own
Track B — a disclosed discretionary/common-sense-pattern basis, admitted
without statistical proof but under the same unweakened sizing and a
locked-in-advance kill rule. As of acceptance, zero strategies or
candidates hold `eligible for operational validation` via any of the
three paths, and none of ADR 0008's own required infrastructure
(`live_price_snapshots`, `paper_ledger_events`, the broker integration,
the reconciliation action) is built yet — acceptance settled the design,
not the deployment.

## Anti-deceptions (re-read each session)

- Not an alpha finder: the primary output is a sequence of `reject`s; passing grants observation, never profit.
- Falsifiable target is the passive alternative (Passive ETF-12 v1; secondary SPY, cash) after costs — not "retail", not competitions, not the media's star managers.
- Not luck-proof: the process reduces the probability of being fooled; it does not remove luck from realized outcomes.
- Evidence status comes only from a preregistered protocol, never from a profitable curve.

## Immutable anchors

- Execution: signal on close `N`, fill at next available open `N+1` (ADR 0001).
- Default project benchmark: Passive ETF-12 v1, subject to candidate-specific suitability audit (ADR 0005).
- CTA v1: rejected under its locked protocol; trend following in general is not thereby rejected.
- Macro: non-tradable context until ADR 0006 point-in-time data and a preregistered hypothesis exist.
- New hypotheses (any origin, including ML): operationalize thesis → bounded search → 9A scoring and benchmark audit → preregistration → 9B locked experiment.

## What institutions do (why this shape)

The project adopts defensible research-governance principles—separation of search and confirmation, recorded trials, point-in-time data, explicit costs, and independent review—without claiming that every institution uses one identical process. This file keeps those local rules recoverable across session restarts.
