Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.

# Shared metrics/charting engine: backtest ranking + paper-trading metrics, one engine

Raised 2026-08-21, closing out the ADR 0008 acceptance session. User's
framing: the metrics engine planned for Chapter 5 (Sharpe, drawdown, hit
rate — the numbers an institution would actually read once real paper
trades accumulate) shouldn't be built as a paper-trading-only tool. It
could double as a **backtest ranking and charting engine** for Chapters
1-3's own closed/composite factors (their example: Dow-theory-style
composed factors) — something that produces a readable chart for the
research program itself and a frontend showcase surface, not just a table
of numbers in a markdown file.

## Why this might be worth doing together, not separately

- The actual metric math (Sharpe, max drawdown, hit rate, turnover) is
  identical whether the return series comes from a historical backtest
  (`backtesting.py`-based, per `backend/app/strategies.py`) or a real
  `paper_ledger_events` log (ADR 0008). Building it once, validated against
  known backtest data (where the right answer is checkable), gives Chapter
  5 a metrics engine already proven correct before any real trade history
  exists to test it against — the same "validate on synthetic/known data
  before trusting it on real data" discipline this project already applies
  everywhere else (the Type-I calibration, the Chapter 4 eligibility
  calibration).
- A ranking/charting surface for Chapters 1-3's own composite factors is
  independently useful and does not require ADR 0008's implementation at
  all — it could be built and shown in the product sooner, on data that
  already exists (every closed Chapter 1-3 result already has a decision
  record and forward-return numbers).
- Ties into [workspace-redesign.md](../workspace-redesign.md)'s existing
  "evidence strength" semantic tokens and Strategy Lab surface
  (`docs/product.md`'s product-surfaces table already names Strategy Lab as
  "configure, run, compare, and inspect versioned historical experiments")
  — a real chart here would be extending an existing, already-approved
  surface, not inventing a new one.

## Not scoped or started

This is an idea, not a design. Real open questions before it could become
an ADR/protocol addition: what counts as a "composed factor" precisely
(a literal multi-signal ensemble like Chapter 4's, or just any single
closed candidate charted individually); whether ranking implies a
cross-candidate comparison that itself needs a preregistered, disclosed
methodology (to avoid quietly becoming a new form of multiple-comparisons
exposure, the exact failure mode this project has spent most of a session
guarding against); and where in the frontend this would actually render
(Strategy Lab, a new Research Record UI page — `product.md` currently
notes Research Record has "no separate UI page" — or somewhere else).
