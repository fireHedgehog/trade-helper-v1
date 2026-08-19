# CTA v2 — pooled vol-scaled trend overlay v1

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/cta-v2-pooled-trend-overlay.md).

Selection authority: [Stage 9A Cycle 2, Candidate
C](../research-candidates/2026-08-19-cycle-2.md), picked up directly per that
record's [2026-08-20
update](../research-candidates/2026-08-19-cycle-2.md#update-2026-08-20-candidate-c-cta-v2-picked-up-directly).
No separate standalone hypothesis file exists for it.

## Decision this protocol may make

This is a **no-trade, no-cost characterization and significance test**, not a
portfolio backtest. It may output only:

- `material and consistent`: the primary lookback variant's net-of-benchmark
  excess return clears materiality and Holm-corrected significance, **and**
  beats the direction-blind volatility-only placebo on the same statistic;
- `not material or not consistent`: any of the above gates fail;
- `invalid`: implementation, leakage, warm-up, or reproducibility checks fail.

It may not output `reject`, `revise`, `continue research`, an entry signal, a
stop, a position size, or a costed/executable portfolio return. `material and
consistent` permits one separately fingerprinted executable-expression
protocol (with real costs, whole-share sizing, and settlement); it is not
itself that protocol.

## Claim and primary estimand

A continuous, volatility-normalized trend-strength signal, combined long-only
and vol-scaled across all 12 locked ETFs into one pooled, unlevered portfolio,
has a mean daily return that materially and significantly exceeds Passive
ETF-12 v1's mean daily return, net of no costs on either side. Three lookback
variants are tested as a small, preregistered neighbourhood-robustness family;
only the primary variant can trigger `material and consistent` — the other two
are reported as robustness context, never a second path to a positive
decision, to close off variant cherry-picking entirely rather than merely
discourage it.

**Signal**, per asset $i$ and completed close $t$, deliberately close-price-only
— the same simplification every prior close-derived candidate this session
made (TA Breakout, Wave Pull) to avoid a second high/low-dependent
volatility proxy alongside the one already locked for the placebo below:

$$
\text{Trend}_i(t) = \frac{\text{close}_i(t) - \mathrm{SMA}_{n}(t)}{\sigma_{20,i}(t)}
$$

where $\sigma_{20,i}(t)$ is the trailing 20-session close-to-close log-return
standard deviation — the **exact same estimator** already locked for SMA
Cross v1's volatility-state placebo, used here as both the trend-signal's
normalizer and the vol-scaling weight's denominator, so one volatility
concept governs the whole candidate rather than two different ones. This
replaces Cycle 2's original "$\div$ 20-day ATR" phrasing, which assumed
high/low access no function in this module has; the substitution is recorded
here rather than silently made, per this project's own erratum convention.

| Variant | $n$ (SMA lookback) | Role |
|---|---:|---|
| A | 150 | Secondary, robustness only |
| **B** | **252** | **Primary** — the literal SMA lookback already named in Cycle 2's Candidate C record |
| C | 350 | Secondary, robustness only |

**Weight construction**, per variant, locked precisely because Cycle 2's own
record left this unpinned:

$$
\text{score}_i(t) = \frac{\max(\text{Trend}_i(t),\,0)}{\sigma_{20,i}(t)}, \qquad
w_i(t) = \begin{cases} \dfrac{\text{score}_i(t)}{\sum_j \text{score}_j(t)} & \text{if } \sum_j \text{score}_j(t) > 0 \\ 0 & \text{otherwise} \end{cases}
$$

`score` is not additionally clipped: a long-only, sum-normalized weight is
already bounded in $[0,1]$ per asset by construction, so no separate cap is
needed to prevent a single extreme reading from exceeding full portfolio
weight. Weights are always long-only and sum to at most $1.0$ (no leverage).
If every asset's trend signal is non-positive on a given day, the portfolio
holds $100\%$ cash that day at zero yield, matching [ADR
0003](../adr/0003-research-statistics.md)'s locked zero-cash-yield
convention.

**Portfolio return**, using $t-1$ weights to gate day $t$'s return, matching
[ADR 0001](../adr/0001-execution-timing.md) even though no position is opened
in this no-trade test:

$$
r_{\text{portfolio}}(t) = \sum_i w_i(t-1)\, r_i(t)
$$

**Benchmark.** A further simplification of ADR 0005's real, whole-share,
costed Passive ETF-12 v1
(`portfolio_benchmark.py::simulate_passive_benchmark`): a continuous,
no-cost, **daily-rebalanced** equal-weight index, $r_{\text{benchmark}}(t) =
\frac{1}{12}\sum_i r_i(t)$ — the simple cross-sectional mean of the 12
assets' daily log returns. Using the real annually-rebalanced, whole-share,
costed engine here would compare a cost-free strategy side against a costed
benchmark side, biasing the excess return in an unpredictable direction, and
tracking annual-rebalance weight drift without real position accounting adds
implementation surface this no-trade comparison does not need. Daily
rebalancing needs no drift or position tracking at all and is trivially
easy to verify correct. The real, costed, annually-rebalanced benchmark
remains the comparator for any later executable-expression protocol.

**Primary estimand**: mean daily excess return of the primary variant's
portfolio over the benchmark, $\mathbb{E}[r_{\text{portfolio}}(t) -
r_{\text{benchmark}}(t)]$, tested one-sided (favourable is positive).

## Universe, data, and time partitions

- Assets: the 12 locked ETFs (`SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, DBC,
  XLK, XLF, XLE`) — pooled, not per-asset independent. Unlike every prior
  candidate this session, the estimand is a single portfolio-level series, so
  there is no per-asset breadth gate; see Gates for the non-gating
  concentration diagnostics that replace it.
- Input: adjusted daily OHLCV governed by [ADR 0002](../adr/0002-market-data-contract.md).
- Common start: the pooled sample begins `350` trading sessions after `DBC`'s
  first stored session (the latest-inception locked asset, `2006-02-06`) —
  the widest lookback across all three variants (secondary variant C's
  `SMA_350`), so every variant's signal is fully warmed up from the sample's
  first evaluated day, not just the primary. This still keeps `2008` inside
  the evaluated sample (`DBC` inception plus `350` sessions lands in mid-2007),
  the same rationale SMA Cross v1 already established for this universe.
- Sample: full available common history through the specification's data-lock
  date. This is a feasibility-and-significance test on development data, not a
  held-out confirmation test; no `reject`/`revise`/`continue research` claim
  attaches until a preregistered, untouched-data confirmation run exists.
- `auto_adjust=True` re-fetch caveat: the data fingerprint below binds the
  exact bars this run used; a later re-fetch may not reproduce it bit-for-bit.

## Statistical test

No new bootstrap machinery is required. The estimand is a single pooled daily
excess-return series — structurally identical in shape to CTA v1's original
per-symbol excess-return statistic, just computed from a portfolio-weighted
series instead of a per-symbol one. `circular_block_bootstrap_p_value` and
`holm_adjust` in `backend/app/research.py` are reused **completely
unchanged** — no state-recomputation is needed the way SMA Cross v1's `Δσ`/
`ΔMDD` estimand required, because nothing here depends on how a threshold
state would look on a resampled path; the null directly concerns the mean of
the realized excess-return series itself.

For each of the 3 variants and the placebo (4 series total):

1. Compute the realized daily excess-return series over the full common
   sample.
2. Run `circular_block_bootstrap_p_value` with `block_bars=20`,
   `resamples=5000`, `seed=17291` — the project's already-locked defaults,
   unchanged here for consistency with every other candidate this session.
3. Apply `holm_adjust` across the 3-variant lookback family (the placebo is
   not part of this family — it is compared directly via the placebo rule
   below, the same treatment SMA Cross v1 gave its own placebo).

## Required placebo: direction-blind volatility-only weighting

$$
w^{\text{placebo}}_i(t) = \frac{1/\sigma_{20,i}(t)}{\sum_j 1/\sigma_{20,j}(t)}
$$

Every asset always receives a positive weight — no trend information enters
this construction at all, only inverse-volatility scaling, using the exact
same $\sigma_{20}$ estimator as the strategy side. This is the direct
portfolio-level analogue of SMA Cross v1's volatility-state placebo, and is
**required**, not optional: Cycle 2's own Cross-candidate findings named this
mechanism as a rival explanation for Candidate C's own result and required it
be shared, not separately re-litigated.

A bare point-estimate comparison (primary mean `>` placebo mean) is exactly
the gate Overnight-Gap's pre-lock review found gives little real
discriminating power between two correlated statistics, and added a paired
significance test to fix. The same fix applies here at no extra
implementation cost, because — unlike Overnight-Gap's sparse, path-dependent
event definitions — both series here are already realized, precomputed daily
excess-return series: the primary-minus-placebo difference series is fed
into `circular_block_bootstrap_p_value` completely unchanged, exactly as any
other single realized series would be. Falsifier: the placebo's mean daily
excess return equals or exceeds the primary variant's, **or** the paired
difference is not distinguishable from zero at `p ≤ 0.05` — either failure
means the trend signal adds nothing beyond generic volatility-timing,
directly mirroring SMA Cross v1's own falsifier logic, applied at the
portfolio level and strengthened by Overnight-Gap's lesson.

## Gates

All must pass for `material and consistent`; any failure is `not material or
not consistent`:

| Gate | Requirement |
|---|---|
| Materiality (primary variant only) | Mean daily excess return $\times\ 252 \ge +1.0$ percentage point (annualized-equivalent) |
| Significance (primary variant only) | Holm-adjusted $p \le 0.05$ across the 3-variant family |
| Placebo | Primary variant's mean daily excess return strictly exceeds the direction-blind placebo's **and** the primary-minus-placebo difference series clears `p ≤ 0.05` on the same bootstrap procedure |
| Reproducibility | Byte-identical excess-return series, p-values, and weight-share diagnostics on an independent rerun against the same fingerprinted data |

Materiality (`+1.0` annualized percentage point) is a Stage 9A research
hurdle chosen before outcome access: low enough not to demand an
unrealistically large edge from a no-cost characterization test, high enough
to sit clearly above this project's own locked round-trip cost defaults (`10
bp` commission/side, `2 bp` spread, `5 bp` slippage) so a `material and
consistent` result would still plausibly survive costs in a later executable
expression, not merely clear a noise floor. It is not relaxed after the value
is seen.

**Non-gating diagnostics, disclosed regardless of outcome:**

- **Regime concentration**: mean daily excess return excluding `2008`,
  excluding `2020`, and excluding `2022` separately, to disclose whether the
  primary variant's result depends on one crisis episode.
- **Asset-weight concentration**: each asset's mean weight share over the
  full sample, to disclose whether the portfolio is effectively concentrated
  in one or two instruments rather than genuinely diversified across the
  12-name, 6-cluster universe.
- **Secondary variants A and C**: reported with their own Holm-adjusted
  p-values and materiality checks for robustness context — cannot themselves
  produce `material and consistent`.

## Multiplicity, dependence, and trial ledger

- One family: the 3-variant lookback neighbourhood, Holm-corrected together.
  The placebo is a separate, required comparison, not a fourth family member
  (matching SMA Cross v1's treatment of its own placebo).
- No further parameter search (weight-clip thresholds, alternative
  vol-scaling estimators, alternative rebalance timing) is run in this first
  experiment; any such change is a new, independently justified protocol.
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl`
  with `variant_count=4` (3 lookback variants plus the required placebo) and
  dependence group `cta-v2-pooled-trend-overlay` before execution.

## Implementation and artifact contract

Before execution:

1. Add `cta_v2_trailing_vol`, `cta_v2_signal_matrix`, `cta_v2_weight_matrix`,
   `cta_v2_placebo_weight_matrix`, `cta_v2_portfolio_return`,
   `cta_v2_benchmark_return`, and `cta_v2_bootstrap` to
   `backend/app/research.py`, reusing `circular_block_bootstrap_p_value` and
   `holm_adjust` unchanged for both the primary significance test and the
   primary-vs-placebo paired test. Add unit tests proving: no future bar
   affects an earlier weight value; an all-non-positive-trend day produces
   exactly zero portfolio return; the placebo's weights always sum to `1.0`;
   and a synthetic panel with a planted, favourable, low-noise trend effect
   produces a materially
   different bootstrap result than an independent-noise panel of the same
   shape (the same planted-effect sanity pattern used by every prior
   candidate's bootstrap this session).
2. `research/experiments/cta-v2-pooled-trend-overlay.json` is created and
   locked, containing every constant above (lookback variants, weight
   construction, benchmark construction, materiality threshold, block
   length, resample count, seed), canonical JSON serialization matching the
   existing convention, and honestly `null` data-fingerprint fields pending
   step 3. Locked specification SHA-256:

   `958a3c838778f32cfb562090309b21f42826394517f0f5f68020ac0067f2382e`
3. Fetch the 12-ETF universe if not already current, then compute and record
   the development-data SHA-256 using the existing ordered-binary hashing
   convention — this step happens after data exists on the executing
   machine, not before; this document's specification is locked independent
   of that fingerprint.

Outputs live under
`output/research/cta-v2-pooled-trend-overlay/<spec-fingerprint>/`:

- `manifest.json`: spec, code/data fingerprints, timestamps, environment;
- `variant-results.json`: one record per lookback variant plus the placebo —
  mean daily excess return, raw and Holm-adjusted p-values, annualized
  materiality figure;
- `diagnostics.json`: the non-gating regime- and asset-weight-concentration
  breakdowns;
- `decision.json`: exactly one permitted decision and the gate table that
  produced it.

No artifact may contain a costed return, Sharpe ratio, or executable-signal
field — this protocol tests a no-cost characterization claim, not a trading
rule.

## Lock checklist

- Weight construction is fully pinned (long-only score, sum-normalization,
  all-cash-day convention) — resolves the "how, exactly, is exposure sized"
  gap Cycle 2's record left open.
- The placebo shares Candidate B's exact volatility estimator, not a
  re-derived one — resolves the "this placebo must be shared, not separately
  re-litigated" requirement Cycle 2's own Cross-candidate findings named.
- Only the primary variant (`SMA_252`/`ATR_20`, the literal specification
  already in Cycle 2's record) can produce a positive decision — closes off
  variant cherry-picking across the 3-member lookback family by construction,
  not merely by discouragement.
- The benchmark is deliberately a simplified, continuous, no-cost
  construction rather than the real costed engine, stated and justified
  explicitly rather than silently assumed comparable.
- No new bootstrap machinery is required — the significance test reuses
  `circular_block_bootstrap_p_value` and `holm_adjust` completely unchanged,
  keeping this candidate's actual statistical-implementation cost lower than
  Cycle 2's original record assumed.
- Materiality threshold, gate table, and lookback family locked before any
  data access.

## Method references

- Moskowitz, Ooi, and Pedersen, "Time Series Momentum," *Journal of Financial
  Economics* 104 (2012), [DOI](https://doi.org/10.1016/j.jfineco.2011.11.003) —
  the own-asset trend-continuation mechanism this candidate pools across
  instruments and folds to address CTA v1's power limitation.
- Politis and Romano, "The Stationary Bootstrap," *Journal of the American
  Statistical Association* 89 (1994), [DOI](https://doi.org/10.2307/2290993) —
  general justification for the block-resampling method already reused
  unchanged here.
