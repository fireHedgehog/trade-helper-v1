# Product identity

Status: v7 — canonical, distilled identity statement. Read immediately after the authoritative [resume checkpoint](README.md). Full contracts: [product.md](product.md), [hypothesis-engineering.md](hypothesis-engineering.md), [model-acceptance-standard.md](model-acceptance-standard.md), [exploration-protocol.md](exploration-protocol.md), [research-protocol.md](research-protocol.md), [ADRs](adr/). Edits require a version bump; the statement must stay precise and non-redundant.

## Calibration (read this before the rest — it changes how to read everything below)

Rigor here is a dial, not a maximum. This is one person's own unlevered capital, paper-traded, not a fund with LPs — the "no strangers to protect" reasoning [ADR 0007](adr/0007-risk-budgeted-ensemble-acceptance.md) gives for why Chapter 4 exists at all.

**Standing priority order for a new candidate (`2026-08-21`, tightened after being violated three times in one session):**

1. **Chapter 4** (real backtest — Sharpe, CAGR, drawdown, Calmar, `block_bootstrap_confidence_interval`'s EV estimate) — the default. Every new candidate starts here.
2. **Chapters 1-3** (locked spec, preregistration, Holm correction, a null-hypothesis p-value) — not deleted, not abandoned, **paused**: run *only* when the user explicitly asks for a falsification test on that specific candidate. Never auto-selected for a new idea just because it fits an estimand shape a prior Chapter 1-3 section used.

A long, well-run p-value study that outputs another `not_material_or_not_consistent` is not neutral or free — it costs real time and does not by itself produce a runnable, sizeable, tradeable thing, which is this project's actual goal. If a candidate doesn't clearly need a p-value, it does not get one unasked.

## What we run (one line)

A systematic research process that adjudicates trading-strategy hypotheses and outputs evidence decisions — `reject`, `revise`, `continue research`, or (Chapter 4) risk-budgeted paper-trade observation — against passive ownership after costs. A research and execution-preparation aid; not an alpha finder, not a trading recommendation, not a live-capital execution system.

**What that sentence is actually for, stated once so it stops being misread (`2026-08-21`):** this repository is public on GitHub. "Not an alpha finder / not a trading recommendation" is a liability disclaimer for a stranger who downloads this code and might otherwise mistake an early-stage, exploratory backtest for validated investment advice — it protects *them*, not a statement that the user's own research goal is anything other than finding real, tradeable edges for their own private, unlevered, paper-traded capital. The user's own words: work like this session's factor screening, real backtests, and Chapter 4 candidate-finding *is* seeking alpha, plainly, and that is correct and intended. Reading the disclaimer as "therefore don't actually try to find anything tradeable" is exactly the misread that produced this session's repeated drift toward reflexive falsification (see the Calibration section above) — a fresh session should not re-derive caution from this sentence's first line alone.

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

## Why two shapes, not one

Institutional-grade rigor (Chapters 1-3) exists to protect a third party — investors, regulators — who cannot personally inspect the trial data, and it is what lets a leveraged fund risk other people's capital on a claim. There is no third party here, no leverage, no LP capital — just this project's own money, in paper trading. That is the entire reason Chapter 4's lighter bar (disclosed uncertainty, sized small, diversified, live-monitored) is legitimate instead of sloppy: the safety comes from position sizing and monitoring, not from statistical certainty. Neither shape is "the real one" — they answer different questions for different stakes.
