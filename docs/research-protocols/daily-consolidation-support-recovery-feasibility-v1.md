# Consolidation support-recovery feasibility v1

Status: locked preregistration; implementation not started. Detector structure,
event counts, blinded matching coverage, and prospective pseudo-event power are
authorised only after implementation verification. Actual-event forward outcomes,
trading rules, and P&L remain prohibited.

Selection authority: [Stage 9A Cycle 1](../research-candidates/2026-08-19-cycle-1.md).
Parent design: [Daily Consolidation Zone v1](../research-hypotheses/daily-consolidation-zone-v1.md).

## Decision this protocol may make

This is a **feasibility gate**, not a return test. It may output only:

- `feasible`: one or more locked detectors produce structurally valid,
  sufficiently distributed events and prospective power for the declared minimum
  effect is attainable;
- `not evaluable`: event count, independence, breadth, or attainable power is
  insufficient;
- `invalid`: implementation, data, leakage, fingerprint, or blinding checks fail.

It may not output `reject`, `revise`, `continue research`, alpha, an entry signal,
a stop, a rank, or a profitable/unprofitable conclusion. A `feasible` result permits
one separately fingerprinted Stage 9B event-study protocol.

## Claim and primary estimand reserved for the later event study

After an objectively completed consolidation, a later lower-boundary test followed
by a same-session recovery close may reduce 60-session adverse excursion relative
to matched same-symbol non-events.

For an event at completed close $t$, execution-independent path measurement begins
at the next available open $O_{t+1}$. Define 60-session adverse excursion

$$
A_{i,t}^{60} = -\min\left(0,\min_{1\le h\le60}
\left(\frac{L_{i,t+h}}{O_{i,t+1}}-1\right)\right).
$$

The reserved primary estimand is the median matched difference

$$
\theta_A = \operatorname{median}_{(i,t)}
\left(A_{i,t}^{60}-\frac{1}{K_{i,t}}\sum_{j=1}^{K_{i,t}}A_{i,c_j}^{60}\right).
$$

Lower is favourable. This protocol may estimate nuisance dispersion from
pseudo-events, but it must never join actual detected event dates to $A^{60}$ or
any other forward outcome.

## Universe, data, and time partitions

- Assets: `SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, DBC, XLK, XLF, XLE`.
- Input: adjusted daily OHLCV governed by [ADR 0002](../adr/0002-market-data-contract.md).
- Calendar: per-symbol sessions; no synthetic filling; detector input ends at close
  $t$.
- Development/feasibility interval: common window `2006-02-06` through
  `2018-12-31`.
- Reserved historical event-study interval: `2019-01-01` through `2023-12-29`.
  Feasibility code must not calculate its actual event outcomes.
- Contaminated/non-confirmatory interval: `2024-01-01` through the specification
  fingerprint date; it has been exposed through prior charts and research.
- Untouched confirmation: observations strictly after the fingerprint date. They
  remain unavailable to development and may be accessed once only after a later
  event-study gate passes.

The current 500-ish stock list is prohibited. Daily volume is total session volume,
not volume-at-price; `HVN` and order-book claims are prohibited.

## Detector family

All quantities use observations ending at candidate completion close $t$.
For window $W$, let

$$
S_t=Q_{0.10}(C_{t-W+1:t}),\qquad
R_t=Q_{0.90}(C_{t-W+1:t}),
$$

and $M_t=\operatorname{median}(C_{t-W+1:t})$. ATR is Wilder ATR(14),
calculated using data through $t$. Realised volatility is the sample standard
deviation of close-to-close log returns.

The finite detector family is the Cartesian product:

| Parameter | Locked values |
|---|---|
| Window $W$ | `40`, `60` sessions |
| Maximum quantile-zone width $(R_t-S_t)/M_t$ | `0.08`, `0.12` |
| Maximum volatility ratio $\sigma_{t-W+1:t}/\sigma_{t-2W+1:t-W}$ | `0.75`, `1.00` |

Total variants: `8`. Every variant also requires:

1. at least two lower-boundary touches and two upper-boundary touches, where a
   touch has session range intersecting boundary $\pm0.5\,ATR_t$;
2. same-side touches separated by at least five sessions;
3. at least 80% of closes inside $[S_t-0.5ATR_t,R_t+0.5ATR_t]$;
4. no single close more than $1.0ATR_t$ outside that interval;
5. finite positive ATR, prices, and prior-window volatility.

For each asset/variant, accept the earliest qualifying completion and suppress any
new completion until $W$ sessions later. This rule prevents rolling-window clones
from being counted as independent zones. All eight variants remain in the trial
inventory; feasibility filtering does not erase a variant.

## Support-recovery event

For an accepted zone completed at $z$, search sessions $z+5$ through $z+60`.
The first session $t$ is an event when:

1. $L_t \le S_z+0.25ATR_z$;
2. $C_t \ge S_z$;
3. no close from $z+1$ through $t-1$ is below $S_z-0.5ATR_z$;
4. all required 60 forward sessions would exist within the relevant analysis
   partition (checked as availability only; outcomes remain unread).

After an event, suppress any event for the same asset and detector variant for 60
sessions. If no event occurs by $z+60$, the zone expires. A session qualifying under
multiple detector variants remains one economic event with multiple variant labels;
it is not duplicated when estimating effective sample size.

## Structural validation and blinding

The feasibility artifact may contain only zone/event identifiers, asset, dates,
variant, boundaries known at the event, pre-event features, and structural flags.
It must not contain returns, lows, highs, drawdowns, violations, or prices after the
event close.

Before event counting is accepted:

- deterministic unit fixtures must prove no future bar changes an earlier zone or
  event;
- a seeded sample of `40` zones is rendered only through completion close $z`;
- each sampled zone is checked against the five mechanical detector conditions;
- any mismatch invalidates the run; subjective chart attractiveness cannot remove
  or promote a detector;
- duplicate economic events across variants are identified before reporting counts.

## Matching contract reserved for power and the later event study

Each actual event will later receive up to `5` same-symbol controls. A control date
must be in the same calendar year, have no detected event within `±60` sessions, and
have 60 forward sessions available. Matching uses only pre-date features:

- 60-session return;
- ATR(14) divided by close;
- 60-session realised volatility;
- SPY close relative to its 200-session moving average;
- calendar month encoded cyclically.

Features are standardised using development data only. Controls are nearest by
Mahalanobis distance with a `0.25` pooled-standard-deviation caliper on each numeric
feature, without replacement within an event and reusable across different events.
Events with fewer than `3` controls are unmatched and fail the matching-coverage
check; the caliper may not be relaxed after counts are seen.

## Minimum effect and prospective power

Business minimum effect: a `3 percentage-point` reduction in median 60-session
adverse excursion, with no more than a `1 percentage-point` loss in median
60-session forward return. At one equal-weight ETF sleeve, these correspond to
approximately `25 bp` less whole-portfolio excursion versus at most `8.3 bp`
return sacrifice; the effect is also about `8.8×` the locked `34 bp` round-trip
friction. These are Stage 9A research hurdles chosen before outcome access, not
estimates of likely performance or loss limits.

Target power is `80%` at family-wise one-sided $\alpha=0.05$ across the eight
correlated detector variants. Prospective power must use `10,000` deterministic
common-calendar circular moving-block resamples and single-step Westfall–Young
max-statistic calibration. For variant $v$, the favourable statistic is
$T_v=-\operatorname{median}(D_v)$, where $D_v$ is the actual-or-simulated matched
adverse-excursion difference. Each null resample recentres $D_v$ by its observed
median; the common resampled calendar blocks preserve cross-variant and
cross-asset dependence. Adjusted p-values compare each $T_v$ with the resampled
maximum across retained variants.

Block length is estimated on the development pseudo-event daily panel using the
corrected circular-block selector of Patton, Politis, and White (2009), then
rounded upward to the first value in `{10, 20, 40, 60}` not below the estimate
(`60` if the estimate is larger). The implementation must reproduce a published
reference implementation on fixed fixtures before use. The selected value is
recorded before any actual-event outcome access and then used for circular blocks.

Nuisance dispersion is estimated only from **pseudo-events**: seeded dates sampled
without using detector labels, subject to the same asset/calendar availability and
matching rules. Actual detected event dates must not be joined to forward outcomes.
The simulation uses the exact deduplicated event counts and calendar-cluster pattern
but injects the locked `−0.03` adverse-excursion shift into every retained variant.
Run `1,000` Monte Carlo datasets; family-level power is the proportion with at least
one adjusted p-value below `0.05`. Report its binomial Monte Carlo standard error.
Code must also demonstrate that the minimum attainable adjusted p-value is below
`0.05` at `10,000` resamples.

## Feasibility gates

All must pass:

| Gate | Requirement |
|---|---|
| Mechanical validity | Zero leakage/fixture/structural-audit failures |
| Event breadth | Events in at least `8/12` assets and `8` distinct calendar years |
| Matching coverage | At least `90%` of deduplicated events have `≥3` admissible controls |
| Concentration | No asset or calendar year contributes more than `25%` of deduplicated events |
| Detector prevalence | Each retained variant labels between `0.5%` and `15%` of eligible completion dates |
| Power | Simulated power `≥80%` for the locked 3-point effect after family-wise correction |
| Reproducibility | Byte-identical artifact and decision on an independent rerun |

A variant outside the prevalence range is mechanically degenerate and excluded
from the later event-study family, but remains logged as an attempted variant. If
every variant is excluded, or the pooled breadth/matching/power gates fail, the
decision is `not evaluable`; thresholds are not relaxed.

## Multiplicity, dependence, and trial ledger

- One family: eight detector variants, one reserved primary estimand.
- Common resample indices preserve cross-variant and calendar dependence.
- The later outcome test must use the same Westfall–Young family and cannot revert
  to eight independent tests or choose the smallest unadjusted p-value.
- Secondary return, violation, and favourable-excursion quantities are safeguards
  or descriptive unless separately powered and preregistered.
- Append one `preregistered_no_results` attempt with `variant_count=8` and one
  dependence group before execution. Amendments and implementation-debug runs are
  appended, never hidden.

## Implementation and artifact contract

Before execution create `research/experiments/consolidation-support-feasibility-v1.json`
containing every constant above, canonical JSON serialization, deterministic seeds,
code version, data fingerprint, and protocol-relative path. Record its SHA-256 here:

`90d31fb192ca9f7864a2d2f2565ebf018483d7f620422b5d1accb2d1b027a62b`

This is SHA-256 of recursively key-sorted, compact UTF-8 JSON with
`ensure_ascii=false` and no trailing newline. The locked development-data SHA-256
inside the specification is
`86eeb197919baad820d07c450b546245962ce9ae76404b339fdc7d7738f74ccc`
for `38,976` ordered rows from `2006-02-06` through `2018-12-31`.

**Pre-execution amendment 1 (2026-08-19).** The original data fingerprint used
SQLite CLI decimal formatting and could not be reproduced byte-for-byte by the
Python runner. Before any detector/event execution, it was replaced by incremental
binary hashing of ordered symbol/date, big-endian IEEE-754 OHLC doubles, and signed
64-bit volume. Original specification SHA-256
`024c66c0c35b06fc8f6620d9a985d4e82427b80ad8b199fe478c177dac474b8d` and data
SHA-256 `eda1663d72e1b418656175bec64dc971f013afab5dbee8cc7ffd995d687b698e`
remain in the attempts ledger; no research threshold changed.

Outputs must be atomic and live under
`output/research/consolidation-support-feasibility-v1/<fingerprint>/`:

- `manifest.json`: spec, code/data fingerprints, timestamps, environment;
- `structural-events.jsonl`: pre-event-only records;
- `feasibility.json`: counts, breadth, concentration, matching coverage, power;
- `audit.json`: fixture, leakage, blinding, reproducibility checks;
- `decision.json`: exactly one permitted feasibility decision and reasons.

No artifact may contain an actual-event forward outcome. Any accidental outcome
join contaminates the run and yields `invalid`.

## Lock checklist

- Block selector: corrected Patton–Politis–White method locked; implementation and
  reference-fixture verification are mandatory execution checks.
- Economic threshold: 3-point adverse-excursion MDE and 1-point return-sacrifice
  limit locked as explicit research hurdles; they are not inferred from outcomes.
- Machine-readable spec/data fingerprint/attempt row/SHA-256: locked and recorded.

## Method references

- Politis and White, “Automatic Block-Length Selection for the Dependent
  Bootstrap,” *Econometric Reviews* 23 (2004),
  [DOI](https://doi.org/10.1081/ETC-120028836).
- Patton, Politis, and White, correction (2009),
  [DOI](https://doi.org/10.1080/07474930802459016).
- Westfall and Troendle, “Multiple Testing with Minimal Assumptions” (2008),
  [DOI](https://doi.org/10.1002/bimj.200710456).
