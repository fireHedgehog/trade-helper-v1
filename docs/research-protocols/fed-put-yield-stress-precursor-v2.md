# Fed put: yield-stress precursor v2

Status: locked before execution. Amends [v1](fed-put-yield-stress-precursor-v1.md)
(closed `not_evaluable`) — same score, same Thesis Track machinery,
materially different episode construction. Not a retry: v1 only used
crisis-branded "QE" episodes; this version's whole point (user-directed,
2026-08-20) is that **real action, not the Fed's own branding, is what
matters** — the Fed calls both 2019's bill purchases and the 2025-12
"Reserve Management Purchases" *"not QE,"* but both are real, dated
balance-sheet actions. v1's episode set silently excluded exactly the
episodes closest to today's actual situation.

## What changed from v1, and why

- **Episodes now include real "not-QE" actions**, not just branded QE
  (§2) — sourced from the Fed's own operational record (when purchases
  *actually started*), not press-conference framing.
- **No recession-pressure joint condition** (user-directed, 2026-08-20):
  2019 had no recession pressure and the Fed still acted on pure
  market-functioning stress, so requiring it would exclude the closest
  real precedent to today by construction, not by evidence.
- **Score formula, lookback, window, resamples, seed: unchanged from v1**
  — the trigger definition (§3 in v1) wasn't the problem, the episode
  inventory was.

## 1. Hypothesis and falsifier

Unchanged from v1 §1, restated: does long-end yield stress (short end
contained) precede real Fed balance-sheet action — now including
episodes the Fed itself did not brand "QE."

## 2. Episodes (dated by operational record, not by this series or by Fed rhetoric)

| Episode | Start (first real purchase/operation) | End (approx.) | Fed's own framing |
|---|---|---|---|
| QE1 | 2008-11-25 | 2010-03-31 | "QE" |
| QE2 | 2010-11-03 | 2011-06-30 | "QE" |
| QE3 | 2012-09-13 | 2014-10-29 | "QE" |
| COVID QE | 2020-03-23 | 2022-03-16 | "QE" |
| 2019 bill purchases/repo ops | 2019-10-15 | 2020-03-22 (absorbed into COVID QE, no clean natural close) | explicitly **"not QE"** (Powell) |
| 2025 Reserve Management Purchases | 2025-12-12 | ongoing at lock time — treated as extending through the last available session in the aligned data, so no placebo window can be drawn from inside it | explicitly **"not QE"** (Fed communications) |

All 6 verified live (2026-08-20) against NY Fed operating-policy records
and contemporaneous reporting — not from memory, not from `DGS2`/`DGS10`.
The 2025 episode's end is unresolved (still running) — for the exclusion
buffer (§4) it is treated as extending through the data's last available
date, so no placebo window can be drawn from inside it.

A mechanical alternative — detecting "onset" directly from `TREAST`'s own
trailing growth rate — was tried and rejected before this version was
written: it flagged ordinary 2003-2007 organic balance-sheet growth and
mistimed 2022's active QT *shrinkage* as "rising" (lagged-window
artifact). Official operational dates are more reliable and no less
"action-based" — they mark when real purchase operations began, sourced
from the Desk's own record, not from Fed rhetoric about intentions.

## 3. Score, lookback, window, inference

Unchanged from v1 §3, §5, §6: `score(t) = z_10Y(t) - |z_2Y(t)|`,
756-session trailing lookback, 60-session precursor window,
placebo-in-time randomization, `resamples=5000`, `seed=17291`.

## 4. Exclusion buffer

Same rule as v1: placebo windows may not overlap
`[episode_start_index - 60, episode_end_index + 60]` for any of the 6
episodes.

## 5. Power pre-commitment

At $n=6$ (up from v1's $n=4$), still small-sample by construction, but a
meaningfully looser power ceiling than v1's. Same discipline as
[Thesis Track](../thesis-track-small-n.md): a null result here is
`not_evaluable`/`insufficient evidence`, never reframed as rejection.

## 6. Decision

Same vocabulary as v1: `not_evaluable`, `weak_evidence`,
`evidence_present`. Same reading rule: $p\le0.10$ →
`evidence_present`; $0.10<p\le0.30$ → `weak_evidence`; otherwise
`not_evaluable`.

## 7. Scope exclusions

Unchanged from v1 §9 — no trade, no cost, no signal, no Stage 9B
authorization.
