# ADR 0010: Long-short ensemble construction — amending the account model, building Chapter 4's engine

Status: **accepted**, `2026-08-21`. Amends
[ADR 0004](0004-portfolio-risk-contract.md)'s account model and fills the
gap [ADR 0007](0007-risk-budgeted-ensemble-acceptance.md) already named and
left unimplemented: *"The ensemble-construction engine, the
confidence-multiplier sizing function, and the minimum-breadth floor are
all named here as required future decisions, not yet implemented. This ADR
authorizes their design, not their deployment."* This ADR is that design.

## Why now

Direct, well-formed critique from a quant PM: this project's long-only
constraint is not a law of portfolio construction, it is a specific,
narrower choice — and one this project inherited without ever separately
deciding it applied to every possible strategy shape. A CTA achieves its
risk/return profile through **leverage on a long-only trend book**. A
cross-sectional equity quant achieves a comparable profile through **being
long-short**, with no leverage required — a different mechanism, not a
watered-down version of the first. ADR 0004's account model (`"Long-only;
no leverage, shorting, borrowing, or fractional shares"`) was written for
single-asset, own-history backtests (Chapter 1's shape) and never
re-examined against Chapter 4's actual job: combining several
independently-modest signals into one diversified, risk-controlled book —
which is precisely the shape a real alpha-model → risk-model → optimizer
pipeline produces, and precisely what ADR 0007 deferred.

## Scope: what this amends, and what it does not

- **Chapters 1-3** (single-asset/cross-sectional/macro falsification) are
  **unchanged**. Their backtests test whether a pattern is real, on its own
  merits, at high confidence — a long-only, no-leverage account model is
  still the right, simplest instrument for that question, and nothing here
  requires revisiting any closed Chapter 1-3 result.
- **Chapter 4 only** gains a new capability: a signal accepted into the
  Chapter 4 ensemble (per ADR 0007's eligibility clauses, unchanged) may now
  be expressed as part of a genuine long-short portfolio, not exclusively as
  independent long-only per-symbol bets.
- This is an **extension of Chapter 4's already-accepted design**, not a
  new chapter and not a new acceptance bar. A signal still has to clear ADR
  0007's five eligibility clauses first; this ADR only changes what happens
  to an eligible signal's score once it has.

## 1. Amended account model (ADR 0004 amendment, Chapter 4 scope only)

Within Chapter 4's ensemble only:

- A position may be **short**, sized and risk-controlled by the same
  stop-distance formula ADR 0004 already defines
  (`q = floor(min(0.005E/d, 0.10E/P))`) — the formula is direction-agnostic
  (`d` is a stop *distance*, not a signed price move), so no new per-position
  formula is needed, matching ADR 0007's own precedent of reusing ADR 0004's
  formula unchanged.
- **No added leverage.** Gross exposure (sum of `|position notional|` across
  every long and short leg) may not exceed `100%` of equity — a long-short
  book trades *composition*, not *size*, for its long-only predecessor's
  leverage-free posture. This is the same "no leverage" principle ADR 0004
  already states, carried forward exactly, not relaxed.
- **Short-sale mechanics: a disclosed, simplified backtest-only assumption**
  (matching how every other ADR's account model discloses its own
  simplification rather than pretending to model a real broker relationship
  that does not exist yet):
  - Borrow is assumed available and free — no borrow rate, no locate
    friction, no recall risk modeled. This is unrealistic for genuinely
    hard-to-borrow names; it is not disclosed as anything more than a
    starting simplification.
  - Short-sale proceeds are held as collateral, not reusable for a new long
    the way a real cash balance would be — the more conservative of the two
    plausible conventions, chosen specifically to avoid a hidden
    double-leverage effect from treating short proceeds as spendable cash.
  - Mark-to-market daily against the existing `E_t = cash_t +
    Σ(q_i × close_i,t)` equity formula, with a short position's `q_i`
    negative.
  - **This entire mechanics section is provisional on paper trading, not
    live trading.** [ADR 0008](0008-bounded-paper-trading.md) is accepted
    but not built; real broker-connected short mechanics (actual borrow
    availability, actual borrow cost, actual locate) are a separate,
    later design decision, required before ADR 0008 is ever implemented for
    a book that includes short legs. Historical simulation under this
    section's assumptions does not imply operational readiness, exactly as
    ADR 0004's own Consequences section already states for the long-only
    case.
- **New portfolio-level constraints**, layered on top of ADR 0004's existing
  sector (`25%`)/cluster (`30%`) exposure caps (which now apply to
  *combined* long+short notional per sector/cluster, the more conservative
  reading):
  - **Net exposure band**: default target is market-neutral, net exposure
    (longs minus shorts, signed) within `±10%` of equity. A specific
    Chapter-4 ensemble may declare a different, wider band in its own
    ensemble-construction record (§3), but must state one explicitly —
    "however the optimizer happens to land" is not a permitted answer.
  - **Minimum names per side**: at least `5` long and `5` short positions
    whenever the ensemble is short at all. This is a diversification floor,
    not a stylistic preference — the entire safety argument for sizing
    individually-unconfirmed Chapter 4 signals small depends on genuine
    breadth existing on both sides of the book, the same reasoning ADR
    0007 already applies to signal count.

## 2. Terminology (for this ADR and everything built from it)

- **Alpha model**: the function that combines every Chapter-4-eligible
  signal's per-asset score into one composite expected-return score per
  asset, per rebalance date. Not "factor synthesizer" (not a term anyone
  else uses) — this is the standard name.
- **Risk model**: the covariance estimate the optimizer uses to price
  diversification and concentration. See §3 for the specific choice.
- **Portfolio optimizer / portfolio construction**: the function that turns
  (alpha scores, risk model, constraints from §1) into target weights per
  asset. See §3.
- **Cross-sectional long-short / market-neutral portfolio**: the general
  shape ("long AAPL, short META" as one output among many, driven by one
  ranking). Not "pair trading" — that term means a specific two-asset
  cointegration/spread thesis, a narrower and different claim than a
  broad ranked book.
- **Synthetic short**: buying puts (or another defined-max-loss expression)
  instead of shorting stock directly, specifically to cap loss at the
  premium paid rather than carry a short's theoretically unbounded loss.
  Named here as a real, legitimate future expression candidate — not
  built by this ADR (options data/pricing is outside current scope,
  [data-layers.md](../data-layers.md) does not carry an options-implied-vol
  layer yet).

## 3. The ensemble-construction engine — required design decisions

This is what ADR 0007 named and deferred. Building it requires three
components, all new to this codebase:

### 3a. Alpha model

Every signal entering the Chapter-4 ensemble must emit a **continuous,
cross-sectional per-asset score** at each rebalance date — not merely an
own-history binary trigger. This is a real translation requirement, not
automatic:

- `amihud_illiquidity` already emits exactly this shape (`factor_zoo.py`'s
  rank-based cross-sectional design) — it slots in directly.
- `atr_normalized`'s existing Tier A translation ("ATR Vol Premium") ranks
  an asset's ATR percentile against its *own* trailing history, not against
  the universe on a given day — a different estimand from "rank this
  asset's ATR percentile against every other eligible asset today." Using
  it in a cross-sectional alpha model requires that second, genuinely new
  computation, named as a new mechanism if pursued (not a retry of the
  existing Tier A strategy, per this project's own reopening discipline).
- Combination rule: each signal's per-asset score, weighted by that
  signal's own ADR-0007 confidence multiplier (already required, already
  named), summed into one composite score. A signal with a wide/weak
  uncertainty band contributes less to the composite, exactly mirroring how
  it would be sized less as a standalone Chapter-4 position.

### 3b. Risk model

**v1 (this ADR)**: a shrinkage-adjusted sample covariance matrix (e.g.
Ledoit-Wolf shrinkage) computed from trailing daily returns across the
eligible universe at each rebalance date — buildable with only
`numpy`/`pandas`, no new dependency, no new paid data. This is a real,
legitimate risk model, not a placeholder; it is simpler than a named-factor
model (Barra/Axioma-style), and that simplicity is disclosed, not hidden.

**Explicitly out of scope for v1**: a full multi-factor risk model with
named style/sector factors. That is a real future upgrade, independently
justified when the simple covariance estimate's limitations (e.g., slow
adaptation to regime change, no explicit sector-factor decomposition)
actually bind on a live candidate — not built speculatively ahead of that
need.

### 3c. Portfolio optimizer

**v1 (this ADR)**: a **rank-and-weight heuristic**, not a formal
mean-variance quadratic program: sort assets by composite alpha score, take
the top group long and bottom group short (subject to §1's minimum-names
and exposure-band constraints), weight within each side inversely to the
risk model's estimated position-level variance (a simple
risk-parity-within-side rule), then scale the whole book to the gross/net
exposure targets. This deliberately does not add a new optimization
dependency (`scipy.optimize`/`cvxpy`) — matching this project's repeated
preference (see [ETF-12 rotation's own scope
decision](research-protocols/etf12-cross-sectional-rotation-v1.md)) for
reusing what plain `numpy`/`pandas` can already do before reaching for new
machinery, and Grinold-Kahn's own observation that a well-constructed
rank-weighted heuristic captures most of a formal optimizer's benefit when
the underlying alpha signals are as noisy as Chapter 4's are by
construction (modest, uncertain, explicitly not statistically proven).

**Explicitly out of scope for v1**: a real quadratic-program optimizer with
full covariance-aware weight solving. Named here as the natural v2, gated
on v1's heuristic actually being deployed and its limitations (e.g., a
risk-parity-within-side rule ignoring cross-asset covariance when weighting)
actually mattering in practice — the same "don't build ahead of a
demonstrated need" discipline as §3b.

## 4. Governance — this ADR's own acceptance is not deployment authorization

Consistent with ADR 0007's own pattern: accepting this ADR means the
*design* is settled enough to build against, not that any long-short book
may be sized with real (even paper) capital yet. Before any Chapter-4
long-short ensemble reaches paper-traded observation (ADR 0008, still not
built), it separately needs:

- at least the minimum-breadth floor ADR 0007 already requires, now
  evaluated per side (§1);
- a live-attrition rule per ADR 0007, unchanged;
- the risk model (§3b) and optimizer (§3c) implemented, tested, and
  live-verified against real data the same way every other piece of
  research infrastructure in this project has been (e.g.
  `universe_pit.py`'s live-verification pattern), not merely unit-tested
  against synthetic panels.

## Consequences

- Chapter 4 signals may now, in principle, be expressed as a genuine
  long-short portfolio rather than exclusively independent long-only bets —
  but only after the alpha model, risk model, and optimizer named in §3 are
  actually built (not authorized by this document alone).
- ADR 0004's long-only account model remains the default and only model for
  Chapters 1-3; this amendment is additive and Chapter-4-scoped, not a
  wholesale replacement.
- Short-sale mechanics (§1) are a disclosed backtest-only simplification;
  real broker-connected short mechanics are a required, separate decision
  before ADR 0008 covers a book with short legs.
- `atr_normalized`'s cross-sectional re-expression (§3a) is new research
  work if pursued, with its own mechanism statement, not a silent reuse of
  the existing Tier A strategy's evidence.
