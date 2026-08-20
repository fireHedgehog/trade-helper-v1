# ADR 0008: Bounded paper trading — point-in-time data, operational risk, reconciliation, and approval design

Status: **proposed**. Draft for review, not yet accepted. Answers the four
requirements [product.md](../product.md) already names as prerequisites for
paper trading ("a separate point-in-time data, operational risk,
reconciliation, and approval design; it is not an implied next step") and
the same gap [ADR 0004](0004-portfolio-risk-contract.md) names in its own
closing line ("operational reconciliation and broker controls require a
separate design"). This ADR authorizes the *design* of bounded paper
trading. It does not itself authorize deployment, and it does not grant
`eligible for operational validation` status to anything — as of this
draft, zero strategies or candidates hold that status under
[identity.md](../identity.md)'s epistemic ladder, [ADR 0007](0007-risk-budgeted-ensemble-acceptance.md)'s
parallel Chapter 4 ladder, or this ADR's own Track B (a third, lighter
entry path for disclosed discretionary/common-sense patterns, defined
below — lighter on statistical proof, not on risk discipline). See [the
research program](../research-program.md) Chapter 5 for the current,
honest state of who (nobody, yet) is eligible to use what this ADR
designs.

## Why now

Every acceptance path this project has built answers a research question —
is a claim real. None of them answers an operational question — once a
claim clears one of those bars, what actually has to be true before a
position is opened, tracked, and closed without silent drift between what
the system believes and what happened. `positions` in `data/market.db` has
zero rows today; `signals.py:advance_positions` recomputes the entire paper
ledger by replaying full history from `bars` on each call rather than
advancing a persisted, append-only transaction log. There is no daily
loop, no reconciliation, and no data source that isn't retroactively
adjustable. This ADR is that missing design, sequenced the same way ADR
0007 was: drafted and reviewed before anything is built.

## Build-vs-buy: use a broker's paper API, don't build a fill simulator

Checked directly rather than assumed: [Alpaca Markets](https://alpaca.markets/)
offers a free, unlimited, no-minimum-deposit paper trading API for US
equities and ETFs — exactly this project's asset class — with a documented
Python SDK (`alpaca-py`), commission-free simulated fills against real
market prices, and no local gateway or additional infrastructure required
(confirmed current as of 2026). Building a custom order-fill simulator
would duplicate what a broker's own sandbox already does correctly and
would itself need its own validation.

This changes what "point-in-time data" and "reconciliation" below actually
require us to build. Alpaca becomes the ground truth for two things: what
the market price was at the moment an order was placed, and whether an
order actually filled and at what price. What stays ours to build, because
it is specific to this project's own governance and not a broker's
concern: the **approval gate** (which candidates may even reach the
broker), the **operational-risk sizing layer** (ADR 0004's formula applied
before an order is submitted — Alpaca fills orders, it does not decide
their size), and **our own reconciliation check** (comparing what our
strategy logic expected against what Alpaca's account state actually
shows, which is a different question than whether Alpaca itself filled
correctly).

No MCP server is needed or appropriate here. MCP exposes tools to an LLM
agent for conversational, chat-driven use — this project is a human-driven
web app where the user takes explicit actions via buttons, the same
pattern every existing endpoint already uses (`GET /api/today`'s scan,
`POST /api/strategy-runs`, Data Management's refresh actions). Alpaca
integration is a standard backend-to-broker REST client
(`backend/app/paper_broker.py`, calling `alpaca-py`), triggered by the same
explicit-action pattern, not a new architectural layer.

## Approval gate

Paper trading may only be entered by a strategy or candidate whose
*current* research status is `eligible for operational validation` —
identity.md's shared terminal state, reachable via one of **three** paths:
the strict Chapter 1-3 ladder (`continue research` → confirmation passes),
ADR 0007's parallel Chapter 4 ladder (an eligible signal inside a real,
constructed ensemble — itself not yet built), or Track B below (a
disclosed discretionary/common-sense basis, no statistical claim, admitted
under strict, non-negotiable operational terms instead of a statistical
bar). This ADR grants that status to nothing via any of the three. As of
this draft: CTA Trend is the only strategy with a research verdict at all
(`rejected`, per `research_catalog.py`); the other six are recorded only
as `not evaluable` despite several having real, closed Chapter 1-3 results
since (SMA Cross, RSI Reversion, Wave Pull each closed
`not_material_or_not_consistent`); Chapter 4's three scored candidates
(CTA v2, Wave Pull, Calendar Day-of-Week) all closed without a settled
positive read as of `0.71.0`; no strategy has yet been proposed under
Track B.

Concretely, this ADR requires:

1. `research_catalog.py` becomes the single accurate, current source of
   each strategy's research status — corrected for the staleness above as
   the enabling substrate for the gate, not a separate feature. It must
   distinguish, per strategy: no verdict yet, `rejected`/
   `not_material_or_not_consistent`, Chapter-4-eligible-but-not-yet-in-an-
   ensemble, Track-B-admitted, and `eligible for operational validation`.
2. A test that fails if `research_catalog.py`'s recorded status for any
   strategy is inconsistent with its actual closed result under
   `docs/research-results/` or `docs/research-program.md` — so this bridge
   cannot silently go stale the way it already has once.
3. Per [workspace-redesign.md](../workspace-redesign.md)'s established
   pattern, this status continues to be *shown*, not used to hide any
   strategy from the interface — "CTA v1 remains visibly rejected" is the
   existing, deliberate design; this ADR extends that same labeling
   discipline into the one new place it currently has teeth: only a
   strategy/candidate carrying `eligible for operational validation` may
   have the "start/continue paper trading" action exposed at all. Everything
   else stays visible and fully backtestable, exactly as today.

## Track B: discretionary, common-sense-pattern basis

The two ladders above answer "is this statistically proven." Not every
reasonable, risk-managed trading decision needs to clear that bar —
Chapters 1-4's rigor exists because this project holds itself to a
standard that protects a third party from asymmetric information; there is
no third party here, only the user's own capital, and requiring
institutional-grade statistical proof before *any* well-known, commonly-
published pattern (Dow-theory swing structure, a pullback entry — the kind
of thing widely used without controversy) can even be paper-tested is a
real cost, not a neutral default. Track B is a third, explicitly lighter
path into `eligible for operational validation`, and — because this
project has already run into cases of over-narrowing onto a handful of
deeply-scrutinized mechanism families (Chapter 1's ten sections, mostly
close variants of trend/mean-reversion/calendar patterns) — it is designed
as a **reusable template for admitting a genuinely wide variety of pattern
types cheaply**, not a one-off exception carved out for a single pattern.

A strategy is Track-B-admitted if, and only if, its own operationalization
record states all of the following in advance, before any paper trading
begins:

1. **A precisely stated, mechanical entry/exit rule**, sourced from a
   well-established, commonly-published pattern — this project's existing
   "no discretionary call is a claim" systematic-method requirement
   ([identity.md](../identity.md)'s Method layer) still applies to the
   *rule itself*; what Track B relaxes is only the requirement that the
   rule's edge be statistically demonstrated first, not that the rule be
   precise.
2. **Sizing under ADR 0004's formula, unchanged** — `q = floor(min(0.005E
   / d, 0.10E / P))`, same sector/cluster caps, same −15% drawdown halt.
   No Track-B strategy is sized any differently than a statistically
   validated one; the relaxation is entirely in the entry bar, never in
   the risk budget.
3. **A kill rule, locked before the first trade, never adjusted after
   observing results** — e.g. "N consecutive losing trades" or "X%
   drawdown attributable to this strategy specifically" → automatic
   removal. This is the one requirement that does not bend, for two
   distinct reasons, both worth stating rather than leaving implicit: it
   protects the user against their own after-the-fact rationalization
   (identity.md's "evidence status comes only from a preregistered
   protocol, never from a profitable curve," applied to a live track
   record instead of a backtest) — and it protects against an *assisting
   agent's* over-confidence, since an agent proposing or monitoring a
   Track-B strategy does not carry the same instinctive skepticism toward
   its own pattern-matching that a person applies to their own conviction.
   The rule constrains execution discipline regardless of who or what
   identified the pattern.
4. **Permanent, honest labeling**: "discretionary basis — no statistical
   validation claimed," shown wherever the strategy appears, exactly as
   durably as CTA Trend's `rejected` label — never blurred with a Chapter
   1-4-cleared candidate.
5. **The live/paper track record becomes the evidence**, reviewed against
   the locked kill rule on a fixed cadence, using the same reconciliation
   and ledger machinery this ADR already defines below — Track B does not
   get a lighter operational standard, only a lighter *entry* standard.

Track B does not touch Chapters 1-4's own falsification standard, which
stays open, ongoing, and unweakened — a strategy can be pursued on both
tracks at once (paper-traded under Track B's terms today, while a
Chapter 1-3 protocol separately tries to prove or reject the same pattern
on its own timeline), and a Track-B strategy that later clears a
statistical ladder graduates to that ladder's own (larger) sizing
treatment, the same way a Chapter-4-eligible signal graduates to Chapter
1-3 if it ever clears that bar instead.

## Point-in-time data contract

The decision basis for any live/paper trading signal is Alpaca's own
market-data snapshot at the moment of capture, retrieved via an explicit,
manual "capture today" action — never a scheduler (Stage 10 stays parked;
[roadmap.md](../roadmap.md) is explicit that "no scheduling-specific
research logic is permitted" and scheduling itself remains ineligible
until Stage 8D's pipeline is proven trustworthy). That capture is recorded
append-only in a new `live_price_snapshots` table (symbol, date, open,
close, captured_at, source) and is never retroactively rewritten.

This is deliberately decoupled from `bars`, the existing backtesting
table: Yahoo's `auto_adjust=True` fetch can rebase an entire symbol's price
history on a future dividend — a fingerprint-stability issue this
project's own research work already hit directly (`data/README.md`,
`docs/README.md`'s environment/data-portability section). `bars` remains
correct and sufficient for backtesting, where a locked data fingerprint is
the reproducibility guarantee. It is the wrong table for live decisions,
where "what did the system believe on this date, permanently" is the
guarantee needed instead. `live_price_snapshots` is that guarantee;
`bars` is not repurposed to provide it.

## Operational risk

ADR 0004's entry-capacity formula and drawdown policy run unchanged, and
run *before* any order reaches Alpaca:

`q = floor(min(0.005E / d, 0.10E / P))`, sector exposure ≤ 25% of equity,
cluster exposure ≤ 30%, and the existing −15% close-to-close drawdown halt
(cancel pending entries, exit at next open, halt new entries until an
explicit reset) — all reused from `portfolio.py:size_entry`, not
reinvented. Alpaca decides whether an order fills and at what price; it
never decides how large an order is.

Where ADR 0007 applies (a signal reaches paper trading via the Chapter 4
ladder rather than the strict one): `chapter4_confidence_multiplier`
(`research.py`) wires into `size_entry` as an additional scaling factor on
top of the base formula above. This is inert today — nothing currently
qualifies as Chapter-4-eligible-and-in-a-constructed-ensemble — but the
wiring is correctly in place for whenever something does, rather than
needing to be built under time pressure at that moment.

The existing `positions` table (one mutable row per symbol/strategy,
current state only, no history) is replaced as the record of truth by a
new append-only `paper_ledger_events` table — one row per fill or exit,
each carrying the `live_price_snapshots` row it was priced against and the
Alpaca order id it corresponds to. `positions` becomes a view derived from
replaying this log, the same relationship `advance_positions` already
has to `bars` today, just genuinely incremental (forward-only from the
last processed event) instead of a full-history recompute each time.

## Reconciliation

A daily, explicit (not cron) reconcile action, run before any further
entries are permitted for the day, checks:

1. **Fill correctness**: does `paper_ledger_events`' expected next-open
   fill basis ([ADR 0001](0001-execution-timing.md): signal on close `N`,
   fill at next available open `N+1`) match what Alpaca's order/fill API
   actually reports.
2. **Position agreement**: does replaying `paper_ledger_events` produce the
   same holdings Alpaca's own account/positions endpoint reports.
3. **Cash agreement**: is cash non-negative and consistent between our
   ledger and Alpaca's account state.

Any mismatch halts new entries for that day and surfaces the specific
discrepancy rather than proceeding silently — the same discipline
[roadmap.md](../roadmap.md)'s global stop conditions already require
("Stop and document rather than continue when... execution semantics
diverge"). Reconciliation failures are themselves durable records, not
transient log lines — matching how every other pipeline state in this
project (`data_refresh_state`, `daily_pipeline_state`) is already persisted
rather than only printed.

## Scope amendment to product.md

[product.md](../product.md)'s "Out of scope" list currently reads
"Brokerage connectivity, automatic orders, leverage, short selling,
options, or live risk controls" without distinguishing a sandboxed paper
connection from a live one. This ADR amends that line: **live** brokerage
connectivity, real-money execution, leverage, short selling, and options
remain out of scope, unchanged. A sandboxed **paper** connection to a
broker's own paper-trading endpoint, gated by this ADR's approval design
and carrying no real capital, is what this ADR authorizes the design of.
`product.md` should be updated to read the amended line directly rather
than left silently superseded.

## Out of scope, unchanged

This ADR does not authorize *live* or broker-connected-with-real-money
trading. Its terminal state is the same one identity.md's epistemic ladder
already names: bounded paper trading, an operational test (data/state/
execution), never an alpha test, never profit claimed. Cron/scheduling
(Stage 10) and cloud deployment (Stage 11) remain parked, unchanged by
this ADR. Live attrition (ADR 0007's own named, unbuilt requirement) is a
prerequisite for any Chapter-4-sourced signal specifically and is not
addressed further here.

## Consequences

- A strategy or candidate that reaches `eligible for operational
  validation` — via either statistical ladder or Track B — now has a
  defined, concrete path into bounded, reconciled, risk-controlled paper
  trading — but only after reaching that status, which nothing currently
  has under any of the three paths.
- `research_catalog.py` becomes load-bearing rather than decorative: its
  accuracy is now a precondition for the approval gate, not just UI copy,
  and must be kept current or the gate is meaningless.
- Four new pieces of infrastructure are named as required, not yet built:
  `live_price_snapshots`, `paper_ledger_events`, the Alpaca integration
  module, and the reconciliation action. This ADR authorizes their design,
  not their deployment — matching ADR 0007's own closing pattern.
- Chapters 1-4's falsification and risk-budgeting standards are unchanged
  and unweakened by Track B's existence — Track B is a third door, not a
  lowering of the first two. A strategy may be pursued on Track B and a
  statistical ladder simultaneously; it graduates to the stricter
  treatment if it ever clears one.
- No existing contract is weakened: ADR 0001's execution timing, ADR
  0004's sizing/drawdown formulas, and ADR 0007's Chapter 4 eligibility
  bar are all reused unchanged, not loosened to accommodate this design —
  Track B changes only which strategies may attempt paper trading, never
  how they are sized or risk-controlled once there.
