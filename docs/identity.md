# Product identity

Status: v1 — canonical, distilled identity statement. Load first on every work session before any other document. Full contracts: [product.md](product.md), [model-acceptance-standard.md](model-acceptance-standard.md), [exploration-protocol.md](exploration-protocol.md), [research-protocol.md](research-protocol.md), [ADRs](adr/). Edits require a version bump; the statement must stay precise and non-redundant.

## What we run (one line)

A systematic, preregistered, falsifiable research process that adjudicates trading-strategy hypotheses and outputs evidence decisions — `reject`, `revise`, `continue research` — against passive ownership after costs. It is a research decision aid; it is not an alpha finder, not a trading recommendation, and not an execution system.

## The four layers

| Layer | Term | What it means here |
|---|---|---|
| Method | Systematic | Rules + code + data, reproducible. No discretionary call is a claim. |
| Discipline | Preregistered / confirmatory | Protocol locked before results; post-hoc tuning is contamination. |
| Statistical core | Multiple-testing control + backtest-overfitting defense | Implemented: multiplicity (Holm) + bootstrap, locked costs, passive benchmark. Contracted for Stage 9B, not yet in the engine: trial-count deflation, CSCV/PBO, power pre-commitment, break-even cost, alpha decomposition. The evidence bar rises with the number of trials. |
| Product | Research decision aid | Outputs only evidence decisions; never "alpha", never an order. |

Implemented = running in the engine today. Contracted = mandatory reporting for Stage 9B candidates; documented, not yet code.

## Epistemic ladder (what an output means)

| Output | Meaning |
|---|---|
| `reject` | The locked claim fails or the experiment is invalid. |
| `revise` | Evidence motivates a new, independently stated hypothesis (new version, new search budget). |
| `continue research` | All gates pass; run the untouched confirmation test once. |
| `eligible for operational validation` | Confirmation passes; only then bounded paper trading — an operational test (data/state/execution), not an alpha test. |

## Anti-deceptions (re-read each session)

- Not an alpha finder: the primary output is a sequence of `reject`s; passing grants observation, never profit.
- Falsifiable target is the passive alternative (Passive ETF-12 v1; secondary SPY, cash) after costs — not "retail", not competitions, not the media's star managers.
- Not luck-proof: the process reduces the probability of being fooled; it does not remove luck from realized outcomes.
- Evidence status comes only from a preregistered protocol, never from a profitable curve.

## Immutable anchors

- Execution: signal on close `N`, fill at next available open `N+1` (ADR 0001).
- Primary benchmark: Passive ETF-12 v1 (ADR 0005).
- CTA v1: rejected under its locked protocol; trend following in general is not thereby rejected.
- Macro: non-tradable context until ADR 0006 point-in-time data and a preregistered hypothesis exist.
- New hypotheses (any origin, including ML): search (exploration-protocol) → 9A scoring → preregistration → 9B locked experiment.

## What institutions do (why this shape)

Serious quant firms do not publish Registered Reports, but they enforce the same substance internally: protocol-before-results, untouched holdouts, multiple-testing discipline, and an independent validation gate before capital. This file is the single-researcher version of that research-governance layer, made explicit so the process survives any number of session restarts.
