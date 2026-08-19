# Methodology and implementation audit — v0.37.1

> Audit · non-contract leaf · point-in-time review against v0.37.1 · loaded only on
> explicit request · no acceptance weight until findings are separately triaged
> into the roadmap, backlog, or a versioned ADR/protocol amendment. Not evidence,
> not a decision, not a preregistration. See [audits/README.md](README.md).

Audit date: 2026-08-19. Reviewed against `backend/app/version.py` `APP_VERSION =
"0.37.1"`. Revision 2, following external peer review of revision 1 — two claims
in that revision were retracted after verification and are marked below.

## Principal finding

The engineering in this repository is unusually disciplined, and its central
research verdict does not follow from its evidence. CTA v1 was retired on a
protocol with almost no power to detect the effect it was built to find.

The locked CTA v1 protocol requires a true annualized information ratio of
roughly **4.1** to reach 80% power within a single 252-bar validation fold —
approximate, ±7pp of power at the simulation's resolution, and optimistic, since
it assumes i.i.d. returns. At a credible trend-following IR of 1.0, power is
**2.5%**.

The 14-of-14 cash outcome is therefore close to a foregone conclusion of the
*test*, not a measurement of the *strategy* — this design could not have told a
modest true edge from none. It is *not*, however, evidence that a modest edge
exists: a dependence-aware joint bootstrap on the strongest observed candidate
(fold 14, detailed in C1) returns a p-value of **0.63**, indistinguishable from
an unremarkable draw under pure noise. Both things are true at once: the test had
no power, and the one number it produced is not, on its own, evidence of
anything.

`docs/model-acceptance-standard.md:78` already resolves the classification
question directly: CTA v1 keeps its historical `reject` label, because that
consequence was locked before evaluation — but the outcome must be read as
`insufficient evidence`, never `evidence of absence`. That reading does not yet
exist at the experiment-specific level; only a general "this does not reject
trend following" caveat does.

**Scoreboard: 2 critical · 2 high · 5 medium · 4 low.**

## Scope

I read the research statistics, execution engine, rule construction, portfolio
replay, persistence, and API layers against the contracts in `docs/`, then
re-derived the CTA v1 result from the committed artifact and cache. Every
quantitative claim below is reproduced from this repository's own data, not
asserted.

An implementation audit already exists at
`docs/research-results/cta-trend-wf-v1-audit.md` and concluded "no material
implementation defect found; rejection stands." I concur with its narrow claim:
the code computes the protocol correctly. It answers *"did we execute the
specification?"* It does not ask *"could the specification have detected the
effect?"* That is the gap this audit fills.

## Credit — what holds up under inspection

This is materially better than most systematic-research code, and the strengths
are load-bearing for everything that follows.

- **No look-ahead in rule construction.** Every breakout level uses `.shift(1)`
  before the rolling window; ATR is read at the signal index; fills occur at the
  *next* bar's open. I checked each rule in `rules.py` individually and found no
  same-bar leakage.
- **ADR 0001 timing is genuinely shared.** Single-symbol backtests, portfolio
  replay, and research evaluation all route through one `entry_levels` /
  `close_exit_decision` pair. The state machine is not reimplemented per surface.
- **T+1 settlement is real.** Sale proceeds enter `settlements` and cannot
  finance a same-day entry — a detail most retail backtesters skip entirely.
- **The adjusted-price trap is avoided.** Refresh uses `period="max"` and
  republishes full history, correctly recognising that `auto_adjust=True`
  rebases the entire series on every dividend.
- **The result artifact reproduces exactly.** All 14 folds resolve to cash,
  minimum Holm-adjusted p is `1.0` in every fold, zero closed OOS trades —
  precisely as documented. No overstatement anywhere in the results prose.
- **The documentation erratum is exemplary.** Preserving a wrong universe list
  in `research-protocol.md` with an explanatory erratum, rather than silently
  correcting it, is the correct handling of a provenance defect.

## Critical — findings that invalidate a research conclusion

### C1 — The CTA v1 decision gate is underpowered by roughly a factor of six

`research-protocol.md` · `backend/app/research.py` · `run_experiment.py`

Selection requires a candidate to survive Holm correction across 54 candidates at
α = 0.05 within one 252-bar validation fold. The smallest raw p-value must
therefore beat `0.05/54 = 0.000926`, which corresponds to a standardized
statistic of about **3.11** on a single year of data.

I ran a power simulation through the repository's own
`circular_block_bootstrap_p_value` at the locked parameters (20-bar blocks,
5,000 resamples, n = 252), injecting a known positive edge (120 trials per point,
i.i.d. Gaussian excess returns — the most favourable possible case, since real
serial dependence reduces effective sample size further):

| True annualized IR | Power to survive the Holm gate |
|---:|---:|
| 1.0 | 2.5% |
| 2.0 | 19.2% |
| 3.0 | 55.8% |
| 4.0 | 76.7% |
| 5.0 | 95.0% |
| 6.0 | 99.2% |

The minimum detectable effect at 80% power is an annualized IR near **4.1**. For
context, a diversified managed-futures programme is celebrated at an IR near 1.0.
Now compare against what the experiment actually observed — taken directly from
the existing audit's own reproduced figures for the strongest candidate
(fold 14):

| Quantity | Value | Source |
|---|---:|---|
| Mean daily excess return | 0.0000662 | existing audit |
| Bootstrap-null SD of the mean | 0.00010586 | existing audit |
| Standardized statistic | 0.63 | derived |
| Annualized excess return | +1.67% | derived |
| Annualized tracking error | 2.67% | derived |
| **Implied information ratio** | **0.63** | derived |
| Statistic needed, uncorrected α=0.05 | 1.64 | threshold |
| Statistic needed, Holm across 54 | 3.11 | threshold |

Whether that observed IR of 0.63 reflects anything real is a separate question
from whether the test had power to find it — and it does not survive asking. I
built the test revision 1 of this audit was missing: a joint max-statistic
bootstrap over all 54 fold-14 candidates, using *shared* block-resampling draws
so the null preserves the family's actual 0.84 median correlation instead of
assuming independence (the correct construction for a dependence-aware
family-wise test; see C2).

| Test (fold 14, best-of-54) | p-value |
|---|---:|
| Single candidate, no multiplicity correction | 0.251 |
| Holm across 54 (as run) | 1.0 |
| **Joint dependence-aware bootstrap, best-of-54** | **0.629** |

A joint p of 0.629 is not a marginal miss — it sits almost exactly at the median
of what the null distribution itself produces. The best result out of 54
correlated candidates in this fold is what an unremarkable draw from pure noise
looks like. The observed minimum raw p-values across all 14 folds (0.251 to
0.985) are consistent with the same reading. **The correct conclusion is not "an
edge exists that the test couldn't confirm." It is "this experiment cannot
distinguish a modest true edge from none, and the one number it produced does
not, on its own, argue for either."**

> **Retracted from revision 1:** the original text called this candidate "not
> noise... roughly what a working trend overlay looks like." That claim is
> withdrawn — the joint-bootstrap result above (p ≈ 0.63) directly contradicts
> it. The single-candidate raw p (0.251) was already sitting in revision 1 and
> should have been sufficient to avoid the claim.

`docs/model-acceptance-standard.md:78` already settles how this should be
recorded, and settles it more precisely than "reclassify": CTA v1 **retains**
its historical `reject` label — that consequence was locked before evaluation
and executed correctly — layered with an explicit evidential note that an
underpowered result is `insufficient evidence`, never `evidence of absence`.
That second layer does not yet exist at the CTA v1 experiment level; only a
general, domain-wide caveat does (`docs/README.md`: "this does not reject trend
following generally").

> **Retracted from revision 1:** the original recommendation was to "reclassify
> CTA v1 from `rejected` to `not evaluable`." That directly contradicted
> existing governance at `model-acceptance-standard.md:78`, which had already
> settled this — retained label plus a separate evidential note — before this
> audit was written. Withdrawn in favor of the recommendation below.

**Recommended.** Add a dated interpretation note to
`docs/research-results/cta-trend-wf-v1.md`, in the same erratum convention
already used for the universe-list defect: protocol decision stays `rejected`;
evidential status is `insufficient evidence, not evidence of absence`, citing the
MDE and the joint-bootstrap result above. Separately, evaluate re-running the
*same* locked hypothesis pooled across all 14 folds (3,528 bars) rather than 14
independent one-year tests — but log any such re-run as exploratory /
CTA-v2-track, not confirmatory: fold 14 and its winning candidate are now known,
so the inspection this project's own rules guard against has already occurred.
Any surviving claim still needs genuinely untouched future data.

### C2 — Holm correction is far too conservative for a candidate family this correlated

`backend/app/research.py:412` · `multiple_testing_report`

The 54 candidates are a Cartesian grid of neighbouring lookbacks over one
universe, so their excess-return series are near-duplicates. Measured on this
repository's own fold-04 cache:

| Statistic (fold 04) | Value |
|---|---:|
| Median pairwise correlation | 0.843 |
| Mean pairwise correlation | 0.828 |
| Variance explained by first principal component | 83.3% |
| **Effective number of independent tests** | **≈ 1.4** |
| Number Holm corrects for | 54 |

Holm is *valid* under arbitrary dependence — it will not inflate type-I error,
and "mis-specified" overstates the defect (revision 1's heading used that word;
corrected here). What it is: calibrated for 54 independent tests when there are
effectively about 1.4, wasting most of the family's power. The 1.4 figure is a
single-fold eigenvalue estimate and shouldn't be read as precise or as a literal
substitute family size — but it doesn't need to be, because the same
conservatism was confirmed directly rather than through that estimate. The joint
dependence-aware bootstrap built for C1 (shared block draws, no effective-N step
at all) gives fold 14's best-of-54 candidate a p of **0.629** against Holm's
reported **1.0** — a genuinely more informative number, still nowhere near
significant. That is the concrete demonstration of "conservative," measured on
its own terms.

**In fairness, this did not cause the CTA v1 rejection.** The smallest raw
p-value observed in any fold was 0.251, and the joint-corrected figure above is
0.629 — nothing would have survived under any reasonable correction. C2 is a
forward-looking defect: it will suppress real effects in every future experiment
run through this machinery, at a family this correlated.

**Recommended.** For families this correlated, prefer a Westfall–Young step-down
max-statistic bootstrap over Holm — prototyped above for fold 14 with 5,000
shared-index resamples, confirming it is both valid and materially more
informative than Holm on this data. This is a method choice for a specific
dependence structure, not a blanket policy change; other candidate families in
future experiments may not share this correlation profile and should be assessed
on their own terms, per `model-acceptance-standard.md`'s "justify use or non-use
before results." Hansen's SPA is the alternative. The bootstrap machinery in
`research.py` already does the hard part — this is a contained change, not a
rewrite.

## High — contract violations and silent-corruption paths

### H1 — An orphaned endpoint mutates the ledger on GET and can replay 554 symbols

`backend/app/main.py:612–640`

`GET /api/today` calls `advance_positions(...)`, which writes to the `positions`
table for every core symbol, then runs `scan()`, which replays a full-history
`simulate()` per symbol. With `scope != "core"` it fans out across
`store.list_symbols()` — currently **554 symbols**, full history each — behind a
60-second cache.

This contradicts three stated contracts:

- "Data refresh and strategy runs are explicit actions, not navigation side
  effects" — `docs/README.md`, non-negotiable state
- "no hidden work on page load" — `product.md`, release gates
- HTTP GET idempotency: a prefetch, crawler, or double-click mutates persisted
  state

**The shipped UI is compliant.** The Today view loads through
`loadTodayStored()` → `/api/strategy-runs/latest`, a pure persisted read. I
verified `/api/today` has **zero references in the frontend and zero in the test
suite**. So this is an exposed governance bypass on the API surface with no
coverage, rather than a live defect in the user path — but it is reachable, and
it is the one route that can write the ledger without an explicit run record.

**Recommended.** Delete the endpoint. If the capability is still wanted, make it
`POST /api/strategy-runs`-governed like every other explicit run, and cover it
with a test. Also correct the stale `signals.py` module docstring, which still
tells the reader "State persists in `positions` and refreshes with
`/api/today`."

### H2 — Bar publication is a row-level upsert, so the "atomic per symbol" guarantee does not hold

`backend/app/store.py:130` · `upsert_bars`

`upsert_bars` issues `INSERT OR REPLACE` keyed on `(symbol, date)`. Rows already
in the database but *absent* from the incoming fetch are never removed. Because
`auto_adjust=True` rebases the entire history on every dividend, any fetch
returning a shorter history than what is stored — Yahoo truncation, a partial
response, a reused ticker — leaves older rows on a **stale adjustment basis
spliced onto newly-adjusted rows**.

`validate_bars` cannot catch this: a level discontinuity at a splice point is a
structurally valid OHLC series. Every downstream metric would be computed on a
series that silently mixes two adjustment vintages — the precise failure
`data_management.py` claims to prevent when it states that "full adjusted
history is refreshed to avoid mixing incompatible adjustment bases," and that
ADR 0002 calls "atomic per symbol."

**Recommended.** Make publication a true per-symbol replacement:
`DELETE FROM bars WHERE symbol = ?` followed by insert, inside one transaction.
Before publishing, assert that the fetched history's first date is no later than
the stored first date and that row count does not regress; fail loudly instead
of publishing a splice.

## Medium — accuracy, disclosure, and capability gaps

### M1 — Confidence statistics overstate the window they were measured on

`backend/app/confidence.py:127` · `compute_confidence`

The module loads `max_days + HORIZON` = 272 bars and reports `sample.days = 252`
with `sample.start` set to the first loaded bar. But the entry rules need
indicator warm-up. Verified against SPY with default parameters:

| Strategy | Bars loaded | First entry possible | First entry fired | Window lost |
|---|---:|---:|---:|---:|
| CTA Trend | 272 | ~100 | 109 | ~40% |
| SMA Cross | 272 | ~50 | 49 | ~18% |

For the default strategy, no signal could fire in the first ~100 sessions of a
window the interface presents as 252 days beginning `2025-07-21`. The hit-rate
arithmetic over the observations that exist is correct; the *stated evidentiary
base* is not. In a product whose stated premise is honest sample disclosure,
this is the kind of overstatement the rest of the codebase works hard to avoid.

**Recommended.** Report the signal-eligible window — first non-NaN rule bar
through last — or extend the load by each strategy's warm-up requirement so the
reported window is the window that was actually sampled.

### M2 — Structural survivorship bias blocks the point-in-time universe standard

`backend/app/research.py:281` · `portfolio_execution.py:129`

`evaluate_candidate_window` excludes any symbol whose stored history ends before
the evaluation window's end — so a name delisted in 2015 is excluded from the
2008 folds too, using information unavailable at that time. `_prepared_inputs`
goes further and requires *identical* calendars across all symbols, meaning only
names alive for the entire replay can enter a portfolio at all.

Immaterial for twelve surviving large ETFs. But the preregistration template
mandates "Point-in-time universe; survivorship policy," and the engine currently
cannot express one. Any future study on an equity universe will be silently
biased upward, and the protocol field will be unfillable rather than merely
unfilled.

**Recommended.** Record a listing/delisting window per symbol and make
eligibility a function of the fold's own dates. Relax the portfolio calendar
constraint to a union calendar with explicit per-symbol availability.

### M3 — The significance test and the decision statistic measure different things

`backend/app/research.py:304–356` · `research-protocol.md`

The bootstrap gate is applied to `equal_weight_excess` — the cross-sectional
*mean* of daily excess returns. The primary fold statistic and the ranking key
are the *median across symbols of cumulative* excess. These are different
estimands: a candidate can be significant on the equal-weighted mean while the
median symbol is negative, or the reverse. One of them should govern, and the
protocol should say which.

### M4 — The constant-exposure control is calibrated on ex-post realized exposure

`backend/app/research.py:218–222` · `evaluate_window`

`exposure` is the mean of the strategy's own `exposed` flag over the whole
evaluation window, then applied as a constant weight to every day in that
window — including days before the exposure was knowable. The docstring and ADR
0003 are explicit that this is a control rather than a tradable replica, so it
is a labelling question, not leakage into the strategy.

The consequence worth stating in ADR 0003: because each candidate is
benchmarked against a control calibrated to *its own* exposure, excess returns
are not strictly comparable *across* candidates with different exposure
profiles — and the ranking rule compares exactly that.

### M5 — "Last 3 years" is anchored to the last signal, not to today

`backend/app/confidence.py:184–190`

The `recent_3y` cutoff is computed as three years back from the most recent
*signal date*, not from the current date. If a strategy last fired two years
ago, the panel labelled "last 3 years" actually covers years five through two
ago. Rename it or re-anchor it to `data_date`.

## Low — hygiene

- **L1 — Divergent duplicate rule logic.** `signals.compute_signal`
  reimplements every entry rule independently of `rules.build_rules`, and they
  already disagree: the CTA exit is a *crossing* in `signals.py` and a *level*
  in `rules.py`. `compute_stateful_signal` overrides state and event from the
  canonical replay so output is not currently corrupted, but a flat symbol still
  displays the divergent note. This is a latent inconsistency in the one place
  the codebase otherwise refuses to duplicate.
- **L2 — Spec deviation, non-binding.** `multiple_testing_report` tests
  `adjusted <= alpha`; the protocol says adjusted `p < 0.05`. The discrete
  bootstrap p-value times integer Holm multipliers cannot land exactly on 0.05,
  so the outcome is unaffected — but the code and the locked protocol should
  read the same.
- **L3 — Dead code.** `execution.simulate` computes `exposure_bars` and never
  uses it; `confidence.CACHE_TTL` is defined but unused, the cache being
  date-keyed instead.
- **L4 — Unbounded cache.** `confidence._cache` grows with every distinct
  symbol-list key and is never evicted. Also `signals.compute_signal` indexes
  `close.iloc[-1 - impulse_bars]` for Wave Pull, which raises `IndexError` for
  `impulse_bars >= 59`.

## Sequence — what I would do, in order

Two of these are cheap and one is a research decision that should not be
rushed.

1. **First, H2.** It is a small, contained change that closes a silent
   data-corruption path. Everything else in the repository depends on the bars
   being one consistent vintage.
2. **Then H1 and M1.** Both are quick, and both close gaps between what the
   product claims and what it does — which is the standard this project has set
   for itself.
3. **Then record the CTA v1 interpretation note.** Protocol decision stays
   `rejected` — that consequence was locked pre-evaluation and the selection
   rule executed correctly. Add the evidential layer
   `model-acceptance-standard.md:78` already prescribes: `insufficient
   evidence`, never `evidence of absence`, citing the MDE (IR≈4.1) and the
   joint-bootstrap result (p≈0.63 on the strongest candidate) as the reasons.
   This is a documentation addition, not a reopening of the decision.
4. **Then C2, scoped to this family.** Adopt the dependence-aware step-down
   bootstrap for candidate families with this correlation profile; don't
   install it as a blanket default. Any pooled-fold re-run of the same
   hypothesis is now exploratory, not confirmatory — fold 14 has been
   inspected — and needs its own governed track plus genuinely untouched
   confirmation data before any claim.
5. **Then align the estimand (M3) before Stage 9A's acceptance standard is
   designed.** The significance test and the ranking statistic should measure
   the same thing before the next experiment is built on this machinery.
6. **M2 before any equity-universe study.** The point-in-time capability gap is
   invisible while the universe is twelve surviving ETFs and decisive the
   moment it is not.

### A closing note on the standard being applied

The instinct behind "failed hypotheses remain failed" is right, and it is the
reason this project is trustworthy where most are not. But that rule polices a
specific failure mode — reviving a dead hypothesis by tuning it after seeing the
result. It was never meant to protect a *test design* from scrutiny.
Distinguishing "the strategy did not work" from "the experiment could not tell"
is not a loophole in research discipline. It is research discipline — and it is
not license to read a single underpowered point estimate as a working edge
either. Both errors are the same mistake: mistaking what one number can carry
for what the question needs.

---

**Provenance.** Revision 2 (2026-08-19), following external review of revision
1. Two claims were retracted after verification, not assumption — flagged inline
above rather than silently corrected, in keeping with this project's own
erratum convention. All quantitative claims reproduced from this repository at
version 0.37.1, using its own `circular_block_bootstrap_p_value`, the committed
`output/research/cta-trend-wf-v1.json`, and the fold-04 and fold-14 candidate
caches. Power simulation: 120 trials per effect size, i.i.d. Gaussian excess
returns, locked parameters (20-bar blocks, 5,000 resamples, n = 252). Joint
bootstrap: 5,000 shared-index resamples across all 54 fold-14 candidates.

A visually designed rendering of revision 2 remains published as a Claude
Artifact (link kept by the author outside this repository); this file is the
archived source of record and takes precedence over that page if the two ever
diverge.
