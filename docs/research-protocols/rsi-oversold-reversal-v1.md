# RSI(14) oversold-crossing short-horizon reversal v1

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/rsi-oversold-reversal-v1.md).

Selection authority: [Stage 9A Cycle 3, Candidate
A](../research-candidates/2026-08-19-cycle-3.md).
Parent design: the existing unvalidated `RsiReversion` prototype in
`backend/app/strategies.py` (period `14`, `buy_below 30`, `sell_above 70`) —
this protocol reuses its parameterization but replaces its trading-state logic
with a discrete crossing-event study, per the Cycle 3 record's mechanism
argument for why an event study is the required first step.

## Decision this protocol may make

This is a **no-trade event study and significance test**, not a portfolio
backtest. It may output only:

- `material_and_consistent`: the RSI-crossing event shows a statistically and
  economically material forward-return bounce, beats the frequency-comparable
  raw-decline placebo, and is consistent across at least `8/12` assets;
- `not_material_or_not_consistent`: gates fail on event count, materiality,
  significance, the placebo comparison, or cross-asset consistency;
- `invalid`: implementation, leakage, warm-up, or reproducibility checks fail.

It may not output `reject`, `revise`, `continue research`, an entry signal, a
stop, a position size, or a portfolio-level return/Sharpe claim.
`material_and_consistent` permits one separately fingerprinted
executable-expression protocol; it is not itself that protocol.

## Claim and primary estimand

A completed session where RSI(14) newly crosses from `≥30` to `<30` — a fresh
transition into oversold, not merely remaining there — is followed by a
positive mean forward `10`-session log return, distinguishable from (a) an
unconditional block-resampled null and (b) a frequency-comparable raw-decline
placebo carrying no RSI-specific information.

RSI is computed exactly as the existing `RsiReversion` prototype does — Wilder
smoothing via `ewm(alpha=1/14, adjust=False)` on clipped gains/losses — so this
protocol tests the same indicator already sitting unvalidated in the codebase,
not a new construction.

**Event.** For asset $i$, $\text{Event}_i(t) = \mathbb{1}\{\mathrm{RSI}_i(t) <
30 \wedge \mathrm{RSI}_i(t-1) \ge 30\}$, computed only from data through
completed close $t$. After a qualifying event, no further event is counted for
the same asset for `10` sessions (the cooldown equals the forward horizon, so
consecutive events never produce overlapping forward-return windows).

**Placebo event** (the required control, on equal footing, not a separate
candidate). $\text{Return}_{14,i}(t)$ is the trailing 14-session cumulative log
return. $\tilde{q}_{10,i}(t)$ is the expanding 10th-percentile of
$\text{Return}_{14,i}$ from the first post-warm-up session through $t$ — a
self-referential threshold, not an externally calibrated or full-sample-tuned
one, matching the same discipline as SMA Cross v1's volatility-state placebo.
$\text{Placebo}_i(t) = \mathbb{1}\{\text{Return}_{14,i}(t) \le
\tilde{q}_{10,i}(t)\}$, with the same `10`-session cooldown after each
qualifying placebo event.

**Forward return.** $R^{10}_i(t) = \sum_{h=1}^{10} r_i(t+h)$ (cumulative log
return over the `10` sessions following the event close). Primary estimand:
$\bar{R}^{10}_i = \text{mean}_{t \in \text{Event}_i} R^{10}_i(t)$, and
analogously for the placebo. Higher (positive) is favourable.

## Universe, data, and warm-up

- Assets: the 12 locked ETFs, adjusted daily OHLCV, full available history.
- Warm-up: the first `100` sessions of each asset's own history are excluded
  from event detection — generous for an EWM indicator that converges far
  faster than a 100-session window, matching this project's existing
  warm-up-disclosure convention (the 2026-08-19 audit's M1 finding on
  under-disclosed warm-up windows for exactly this class of indicator).
- Minimum event count: an asset with fewer than `15` qualifying RSI events
  after warm-up is excluded from the qualifying-asset count entirely (neither
  pass nor fail) — a reliability floor set before any event is counted, not a
  multiplicity correction. Report the excluded-asset count and reason
  honestly; do not silently drop it from the denominator without disclosure.

## Statistical test

Extend the block-resampling scaffold already proven in
`backend/app/research.py` (`circular_block_bootstrap_p_value`,
`sma_cross_bootstrap`) to an event-recomputing variant, avoiding Cycle 1's
caliper-matching failure mode entirely by never constructing a separate
matched control set:

1. Circularly block-resample the raw daily log-return series in `20`-session
   blocks (unchanged default), for one asset at a time.
2. Reconstruct a synthetic price path by compounding the resampled returns.
3. Recompute RSI, the event indicator, the placebo indicator, and both
   cooldowns on the **resampled path**, then compute
   $\bar{R}^{10}_{\text{resampled}}$ for both the event and placebo
   definitions on that resampled path.
4. One-sided p-value: the fraction of `5,000` resamples with
   $\bar{R}^{10}_{\text{resampled}} \ge \bar{R}^{10}_i$ (observed), plus the
   existing add-one correction — the direct, unflipped convention (favourable
   is positive here, unlike SMA Cross v1's negative-favourable statistics).
5. Apply `holm_adjust` (unchanged) across the `12`-asset family for the event
   statistic only; the placebo is compared directly per asset, not
   Holm-corrected as a second family, mirroring SMA Cross v1's design.

No panel regression, permutation-null library, or new dependency is required.

## Gates

| Gate | Requirement |
|---|---|
| Minimum event count | Asset has `≥15` qualifying RSI events after warm-up |
| Materiality | $\bar{R}^{10}_i \ge +0.5\%$ **and** Holm-adjusted $p \le 0.05$ |
| Breadth | Materiality holds in at least `8` of the assets with sufficient event count |
| Placebo | $\bar{R}^{10}_i$ (event) `>` $\bar{R}^{10}_i$ (placebo) on the same asset — RSI must add something beyond a generic magnitude-matched decline |
| Concentration | At least `3` of the `6` distinct `cluster` values in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` must each contribute at least one qualifying asset |
| Reproducibility | Byte-identical forward-return/p-value artifact on an independent rerun against the same fingerprinted data |

The `0.5%` materiality threshold and `15`-event minimum are Stage 9A research
hurdles chosen before outcome access; they are not relaxed after counts are
seen.

## Multiplicity, dependence, and trial ledger

- One family: the `12`-asset event-statistic Holm correction. The placebo
  comparison is a per-asset gate, not a second Holm-corrected family — it
  answers "does RSI add anything," not "is the placebo itself significant."
- Single locked RSI parameterization (`14`/`30`/`70`, matching the existing
  prototype) and single forward horizon (`10` sessions) — no grid in this
  first experiment. A horizon or parameter sweep is a separate, independently
  justified future attempt if this result is `material_and_consistent`.
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl`
  with `variant_count=1` and dependence group `rsi-oversold-reversal-v1`
  before execution.

## Implementation and artifact contract

1. Implement the event-recomputing bootstrap extension in
   `backend/app/research.py`, reusing the existing RSI formula verbatim from
   `RsiReversion`; add unit fixtures proving no future bar affects an earlier
   event or placebo value.
2. `research/experiments/rsi-oversold-reversal-v1.json` locks every constant
   above, canonical JSON serialization, and a deterministic seed. Its `data`
   block's fingerprint fields are `null` until computed at execution time,
   honestly, per the same convention as every prior locked spec. Locked
   specification SHA-256:

   `4e99621b45867b5ed7431d77f8bf642f6988ac48d3972ff9143548099cd5e0f8`
3. Fetch is not required — the 12-ETF universe already exists on this machine
   from Cycle 2's execution; the data fingerprint is still computed fresh at
   execution time and is not assumed to match any prior fingerprint.

Outputs live under `output/research/rsi-oversold-reversal-v1/<spec-fingerprint>/`:

- `manifest.json`: spec, code/data fingerprints, timestamps;
- `per-asset-results.json`: event count, placebo count, both mean forward
  returns, raw and Holm-adjusted p-values, per asset;
- `decision.json`: exactly one permitted decision and the gate table.

No cost, execution, position, or portfolio-level field is authorised in any
artifact — this is a no-trade characterization run throughout.

## Lock checklist

- Event and placebo are both self-referential (expanding quantile, no
  full-sample calibration) — same discipline that resolved SMA Cross v1's
  unpinned-parameter gap, applied from the start here rather than as a
  correction.
- Minimum event count set before any data access, closing the "too few
  observations to mean anything" gap that a pure significance/materiality
  gate alone would miss.
- No parameter or horizon grid in this run — one locked RSI parameterization,
  one locked forward horizon.
- Statistical procedure reuses and bounded-extends the same proven scaffold as
  Cycle 2's Candidate A rather than introducing new infrastructure — keeps
  this candidate's actual cost consistent with its Cycle 3 score.

## Method references

- Jegadeesh, "Evidence of Predictable Behavior of Security Returns," *Journal
  of Finance* 45 (1990), [DOI](https://doi.org/10.1111/j.1540-6261.1990.tb05110.x).
- Lehmann, "Fads, Martingales, and Market Efficiency," *Quarterly Journal of
  Economics* 105 (1990), [DOI](https://doi.org/10.2307/2937816).
- Politis and Romano, "The Stationary Bootstrap," *Journal of the American
  Statistical Association* 89 (1994), [DOI](https://doi.org/10.2307/2290993).
