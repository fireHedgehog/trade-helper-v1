# Labor-market claims lead-lag v1 — operationalization record

Status: operationalization record only. Not preregistered, not scored, not
a Stage 9A candidate. Per [hypothesis-engineering.md](../hypothesis-engineering.md):
`idea → operationalization record (this doc) → bounded exploration → Stage
9A priority → preregistration → Stage 9B`. This document exists at the
first two stages only.

## Why this exists, traced back honestly

Not a new idea invented in isolation. Direct descendant of [Fed
put](../brainstorm/2026-08-19-fed-put-long-end-reversal.md) (closed
`not_evaluable` ×3 — see
[v1](../research-results/fed-put-yield-stress-precursor-v1.md)/[v2](../research-results/fed-put-yield-stress-precursor-v2.md)/[v3](../research-results/fed-put-yield-stress-precursor-v3.md))
and the broader [macro reaction-function
library](../brainstorm/2026-08-20-macro-reaction-function-narrative-library.md)
it opened. Fed put's own logic — test the *precursor* to a well-known
mechanism ("QE causes stocks to rise" is priced-in common knowledge and
untestable for edge; "yield stress precedes the QE decision" is not) — is
sound and is reapplied here, not retried. This candidate uses a different
mechanism family entirely (labor-market flow-vs-stock measures, not
yield/Fed-balance-sheet variables), so it is not adjacent to any of the
seven state variables the macro library already named, and it is not a
retry of Fed put's own closed claim.

**User's own stated skepticism, recorded rather than smoothed over:** "I
still think it maybe the priced-in one." This is a fair, likely-partially-
correct prior. The *direction* of this claim (a flow measure leading a
stock measure it mechanically feeds into) is not surprising on its face.
What is not already established, in this project or obviously "priced in"
as a tradeable fact, is the *magnitude and consistency* of the lead — which
is the actual question this record scopes.

## Operationalization record

| Field | Answer |
|---|---|
| **Claim** | The weekly initial-jobless-claims series (`ICSA`), via a sustained year-over-year trend inflection in its 4-week moving average, precedes a corresponding inflection in the monthly unemployment rate (`UNRATE`), measured via the Sahm Rule (3-month `UNRATE` moving average rising `≥0.50pp` above its trailing-12-month low), by a measurable, historically consistent lead time. |
| **Scope** | US labor-market aggregate series only (`ICSA`, `UNRATE`), not any individual equity or asset. Full available history where both series overlap (`UNRATE` from 1948, `ICSA` from 1967 — effective joint window 1967–present). Applies at the level of identified labor-market inflection episodes (historically, a small number — order of magnitude of US recessions/slowdowns since 1967), not a repeatable high-frequency event. |
| **Mechanism** | `ICSA` is a weekly *flow* measure (new layoffs filed that week); `UNRATE` is a monthly, survey-based, smoothed *stock* measure of the labor force. A flow that feeds into a stock should mechanically tend to move first — this is not a novel claim (it is why the Sahm Rule itself and standard real-time macro monitoring already treat claims as an early-read proxy). The open, non-trivial question is lead-time magnitude and cross-episode consistency, not the qualitative direction. |
| **Market-belief proxy** | None directly — this record does not yet test a market/price reaction. It characterizes a relationship between two macro series only. (If this bounded exploration finds something durable, a later, separately-scoped candidate would need to define a market-belief proxy for whatever equity/bond conditioning is proposed next — not assumed here.) |
| **Reality proxy** | The empirically realized lead time (in weeks) between an identified `ICSA` inflection and the subsequent `UNRATE`/Sahm Rule inflection, across historical episodes. |
| **Information set** | **This record uses final-revised `ICSA`/`UNRATE` values, not point-in-time vintages.** Per `hypothesis-engineering.md`'s promotion gate, this explicitly means: this record may not be promoted to Stage 9A or treated as evidence for a tradeable signal on the strength of this data alone. It is scoped as a bounded, pre-signal characterization of the *underlying macro relationship*, not a claim about what a real-time trader could have known or exploited. Both series undergo real revisions (claims data mildly, `UNRATE` less so but not never) — a genuine point-in-time upgrade via `macro_pit` (already built, proven 3× for Fed put) is a named precondition for any future signal-bearing version of this claim, not an optional nicety. |
| **Estimand** | For each identified `ICSA` inflection date (see locked definition below), the number of weeks until the next Sahm Rule trigger date, if any occurs within a 24-month forward window. Reported descriptively (distribution across episodes: median, range, count of misses) — this stage does not compute a p-value or run inference; it is exploratory characterization per `hypothesis-engineering.md`'s staged sequence, not a locked significance test. |
| **Alternatives** | (1) No real lead exists; apparent lead-lag is an artifact of the different smoothing windows used for each series (4-week MA vs. 3-month MA) rather than a genuine economic relationship — must be checked by varying the smoothing choice and confirming the lead is not simply a mechanical consequence of window-length asymmetry. (2) The lead is real but too inconsistent across episodes (large variance, some episodes with no lead or a negative lead) to be practically informative. (3) Any apparent lead is already fully priced into forward-looking asset prices in real time (the user's own stated prior) — this record cannot address this alternative at all, since it tests no market/price reaction; a future market-conditioned version would need to. |
| **Falsifier** | No consistent positive lead is found (median lead ≤ 0, or lead direction is inconsistent — e.g., fewer than half of identified episodes show `ICSA` leading rather than lagging or coinciding), or the lead disappears/reverses under a reasonable alternative smoothing-window specification chosen before inspection. |
| **Data feasibility** | Fully available today, no new fetch: `ICSA` (1967-01-07 to 2026-08-08, `3,110` weekly rows) and `UNRATE` (1948-01-01 to 2026-07-01, `942` monthly rows) both already stored locally in `data/market.db`, confirmed directly. Zero new data, zero new API key dependency for this bounded-exploration stage. A future point-in-time-signal version would need `macro_pit` ALFRED vintage ingestion for both series (blocked today on this machine specifically — `FRED_API_KEY` is stored on a different machine, not a structural blocker, just today's availability). |
| **Expression candidates** | None proposed at this stage. Per the "separation of claim and trade" principle in `hypothesis-engineering.md`, this record tests only whether the underlying macro relationship is measurable and consistent — not whether or how it should condition any equity/bond position. Any expression is a separate, later, separately-scoped decision. |
| **Path and risk** | Not applicable at this stage (no trade, no expression). If a later market-conditioned candidate is built on this, standard timing/gap/liquidity risks would need their own protocol, same as every other candidate this session. |

## Locked inflection definitions (stated before any computation)

Fixed here, before running the bounded exploration below, to avoid
post-hoc pattern-fitting:

- **`ICSA` inflection**: the first week where the year-over-year percent
  change of `ICSA`'s trailing 4-week moving average crosses from negative
  (or zero) to positive, and remains positive for at least `4` consecutive
  weeks (avoiding a single noisy week triggering a false inflection). The
  4-week moving-average convention matches how claims data is
  conventionally reported (not invented for this record).
- **`UNRATE` inflection (Sahm Rule)**: the first month where the 3-month
  moving average of `UNRATE` is `≥0.50` percentage points above its own
  trailing-12-month low — the real, published Sahm Rule threshold (Sahm
  2019), not a parameter invented or tuned for this record.
- **Pairing rule**: each `ICSA` inflection is matched to the *next* Sahm
  Rule trigger occurring within a `24`-month forward window, if any. An
  `ICSA` inflection with no matching Sahm trigger within that window is
  recorded as a miss, not silently dropped from the count.

## What this record does not authorize

No trading candidate, no signal, no UI element, no decision vocabulary
(`material_and_consistent` / `not_material_or_not_consistent` / `invalid`
does not apply to bounded exploration). The next step, if this exploration
finds a real, consistent lead, is Stage 9A scoring against the
model-acceptance-standard — the same gate every other candidate this
session went through, not a shortcut because the exploration looked
promising.
