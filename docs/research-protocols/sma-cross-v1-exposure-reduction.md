# SMA Cross v1 — exposure-reduction feasibility and test v1

Status: executed and closed as `not_material_or_not_consistent`. See the
[result](../research-results/sma-cross-v1-exposure-reduction.md).

Selection authority: [Stage 9A Cycle 2, Candidate
A](../research-candidates/2026-08-19-cycle-2.md), jointly designed against
[Candidate B](../research-candidates/2026-08-19-cycle-2.md)'s
volatility-managed-exposure mechanism as its required control. Candidate A's
full operationalization record lives in that same Cycle 2 selection record;
no separate standalone hypothesis file exists for it.

## Decision this protocol may make

This is a **no-trade characterization and significance test**, not a portfolio
backtest. It may output only:

- `material and consistent`: the SMA-state partition shows a statistically and
  economically material `Δσ`/`ΔMDD` reduction, beats the volatility-state placebo,
  and is consistent across at least `8/12` assets on both statistics;
- `not material or not consistent`: gates fail on materiality, significance, the
  placebo comparison, or cross-asset consistency;
- `invalid`: implementation, leakage, warm-up, or reproducibility checks fail.

It may not output `reject`, `revise`, `continue research`, an entry signal, a stop,
a position size, or a portfolio-level return/Sharpe claim. `material and
consistent` permits one separately fingerprinted executable-expression protocol
(Candidate A's expression (b)/(c)); it is not itself that protocol.

## Claim and primary estimand

For a single long-only asset, restricting exposure to sessions where a trailing
state is "on" produces lower realized annualized volatility and lower maximum
drawdown than continuous exposure, without requiring the rule to also raise
compound return. Two trailing states are tested side by side, on equal footing,
because the falsifier requires the SMA-state result to beat a volatility-only
placebo, not merely beat continuous exposure:

- **Trend state** (Candidate A): $\text{State}^{\text{SMA}}_t = \mathbb{1}\{\mathrm{SMA}_{20}(t) > \mathrm{SMA}_{50}(t)\}$.
- **Volatility state** (Candidate B, as placebo control — not a separate
  candidate): $\text{State}^{\text{Vol}}_t = \mathbb{1}\{\sigma_{20}(t) \le \tilde\sigma_t\}$,
  where $\sigma_{20}(t)$ is the trailing 20-session realized volatility and
  $\tilde\sigma_t$ is its own **expanding median from the start of the
  post-warm-up sample through $t$** — not a fixed external target level. This
  removes the need for a pinned `target_vol` or any leverage/weight-cap contract:
  the volatility state is exactly as self-referential as the SMA state, and both
  states can be tested with the same statistical procedure below.

For asset $i$, let $r_i(t)$ be the daily adjusted close-to-close log return. The
gated series for state $S \in \{\text{SMA}, \text{Vol}\}$ is
$r^S_i(t) = r_i(t)\cdot\mathbb{1}\{\text{State}^S_i(t-1)\}$ — the state computed
through the completed close at $t-1$ gates day $t$'s return, matching [ADR
0001](../adr/0001-execution-timing.md)'s signal/fill separation even though no
position is actually opened in this no-trade experiment. Primary estimand, per
asset and per state:

$$
\Delta\sigma^S_i = \sigma_{\text{ann}}(r^S_i) - \sigma_{\text{ann}}(r_i), \qquad
\Delta\mathrm{MDD}^S_i = \mathrm{MDD}(r^S_i) - \mathrm{MDD}(r_i),
$$

where $\sigma_{\text{ann}}$ annualizes by $\sqrt{252}$ and $\mathrm{MDD}$ is
computed on the cumulative compounded path. Lower (more negative) is favourable.
`ΔCAGR` is reported as a secondary, unscored guardrail only, per the operationalization record.

## Universe, data, and time partitions

- Assets: the 12 locked ETFs (`SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, DBC, XLK,
  XLF, XLE`), each tested independently — **no pooled or panel estimator**. This
  is a deliberate simplification: `research.py` has no panel-regression or
  permutation-null machinery, and building one was the gap that parked Cycle 2's
  cross-sectional-rotation candidate. Cross-asset consistency is instead assessed
  by a breadth count (see Gates), reusing only single-series tools.
- Input: adjusted daily OHLCV governed by [ADR 0002](../adr/0002-market-data-contract.md).
- Warm-up: the first `252` sessions of each asset's own clean history are excluded
  from both the SMA-50 and the volatility-expanding-median computation. This is
  long enough for both indicators to be stable (`50`-session SMA, plus room for
  $\tilde\sigma_t$ to stop being dominated by its first few values) and short
  enough that 2008 remains inside the evaluated sample for every asset, including
  `DBC` (2006 inception, per Cycle 1's development-window precedent).
- Sample: full available history per asset through the specification's data-lock
  date. This is a feasibility-and-significance test on development data, not a
  held-out confirmation test; no claim of "evidence" attaches until a
  preregistered, untouched-data confirmation run exists, per [model acceptance
  standard](../model-acceptance-standard.md).
- `auto_adjust=True` re-fetch caveat: the data fingerprint below binds the exact
  bars this run used; a later re-fetch may not reproduce it bit-for-bit
  (`auto_adjust` rebases on every new dividend), so any rerun must record its own
  fingerprint rather than assume reproduction.

## Statistical test

Extend `circular_block_bootstrap_p_value` in `backend/app/research.py` — reuse its
existing centering-and-circular-block-resample scaffold (`block_bars=20`, the
project's already-locked default, unchanged here) — from resampling a
precomputed return series to a **state-recomputing** variant:

1. Circularly block-resample the raw daily return series $r_i(t)$ in `20`-session
   blocks, exactly as the existing function does.
2. Reconstruct a synthetic price path by compounding the resampled returns from an
   arbitrary base.
3. Recompute both trailing states ($\mathrm{SMA}_{20}/\mathrm{SMA}_{50}$; expanding-median
   $\sigma_{20}$) on the **resampled path**, not the original — the null is "no
   informative relationship between trailing state and subsequent regime beyond
   what generic block-preserved serial dependence produces," not "returns are
   i.i.d."
4. Compute $\Delta\sigma^S_{\text{resampled}}$ and $\Delta\mathrm{MDD}^S_{\text{resampled}}$
   on the resampled, state-recomputed path, for both states.
5. One-sided p-value: the fraction of `5,000` resamples with
   $\Delta\sigma^S_{\text{resampled}} \le \Delta\sigma^S_i$ (observed), and
   separately for $\Delta\mathrm{MDD}$ — the mirror of the existing function's
   `>=`-counting convention, flipped because favourable here is negative, not
   positive. Add-one correction, matching the existing function.
6. Apply `holm_adjust` (unchanged, already in `research.py`) within each state's
   own family of `12` assets × `2` statistics (`24` tests), not across states —
   the two states are separate claims, not one family, and are compared directly
   via the placebo rule below rather than pooled into one correction.

No panel regression, permutation-null library, or new dependency is required; this
is a bounded extension of one existing function plus reuse of the existing Holm
implementation.

## Gates

All must pass for `material and consistent`; any failure is `not material or not
consistent`, not partial credit:

| Gate | Requirement |
|---|---|
| Materiality (SMA state) | Holm-adjusted-significant `Δσ ≤ −3` percentage points annualized **and** `ΔMDD ≤ −5` percentage points, at `α = 0.05` |
| Breadth | Both materiality conditions hold in at least `8/12` assets |
| Placebo | For each asset meeting materiality, the SMA state's `Δσ` and `ΔMDD` are each more favourable (more negative) than the volatility state's own `Δσ`/`ΔMDD` on the same asset — the SMA state must add something beyond the volatility-state placebo, not merely equal it |
| Concentration | No single asset accounts for the entire breadth count in isolation from the rest — at minimum `3` of the `6` distinct `cluster` values in `portfolio_universe.py:PORTFOLIO_CLASSIFICATIONS` must each contribute at least one qualifying asset |
| Reproducibility | Byte-identical `Δσ`/`ΔMDD`/p-value artifact on an independent rerun against the same fingerprinted data |

Materiality thresholds (`3`-point `Δσ`, `5`-point `ΔMDD`) are Stage 9A research
hurdles chosen before outcome access, sized to be clearly distinguishable from
noise on a single-asset multi-decade sample, not an estimate of likely benefit.
They are not relaxed after counts are seen.

## Multiplicity, dependence, and trial ledger

- Two families, tested independently: the SMA state's `12 × 2` tests, and the
  volatility-state placebo's `12 × 2` tests. Each is Holm-corrected within itself.
- No SMA-window grid is run in this first experiment (`20/50` only, matching the
  existing unvalidated `SmaCross` prototype's parameters) — a neighbourhood
  robustness check (e.g. `10/30`, `50/100`) is explicitly deferred to a separate,
  independently justified amendment if this result is `material and consistent`,
  not bundled into this run's search family.
- Append one `preregistered_no_results` attempt to `research/attempts.jsonl` with
  `variant_count=2` (one state family, one placebo family) and dependence group
  `sma-cross-v1-exposure-reduction` before execution.

## Implementation and artifact contract

Before execution:

1. Extend `circular_block_bootstrap_p_value` (or add a sibling function) in
   `backend/app/research.py` for the state-recomputing procedure above; add unit
   fixtures proving no future bar affects an earlier state value.
2. `research/experiments/sma-cross-v1-exposure-reduction.json` is created and
   locked, containing every constant above (states, warm-up, block length,
   resample count, materiality thresholds, breadth/placebo/concentration rules),
   canonical JSON serialization (recursively sorted keys, compact separators,
   `ensure_ascii=false`, no trailing newline), and a deterministic seed. Its
   `data` block's fingerprint fields are `null`, honestly, pending step 3. Locked
   specification SHA-256:

   `3c7e8be2a5fb636a8234bf982e42862412143213f9f42f592a93babcc9956238`

   **Pre-execution amendment 1 (2026-08-19).** The original concentration gate
   said "`2` of `4` asset-class clusters," paraphrasing the mechanism from
   memory rather than reading `portfolio_universe.py:AssetClassification`
   directly. The actual `cluster` field has `6` distinct values (US equity,
   International equity, Long-duration Treasury, Intermediate Treasury, Gold,
   Commodities), not `4`. Corrected to "`3` of `6`" before any data access or
   execution; no threshold's practical strictness changed materially (roughly
   half of the actual clusters, same as originally intended). Original
   specification SHA-256 `5bee965b775645681149049e3ecf43a618b4e71b225bc97b53b88b62b6ebf4ae`
   remains in the attempts ledger.
3. Fetch the 12-ETF universe if not already current, then compute and record the
   development-data SHA-256 using the existing ordered-binary hashing convention
   from `run_consolidation_feasibility.py`'s `development_data_sha256` — **this
   step happens after data exists on the executing machine, not before**; this
   document's specification is locked independent of that fingerprint.

Outputs live under
`output/research/sma-cross-v1-exposure-reduction/<spec-fingerprint>/`:

- `manifest.json`: spec, code/data fingerprints, timestamps, environment;
- `per-asset-results.jsonl`: one record per asset per state — `Δσ`, `ΔMDD`, raw
  and Holm-adjusted p-values, placebo comparison outcome;
- `decision.json`: exactly one permitted decision and the gate table that
  produced it.

No artifact may contain a portfolio-level return, Sharpe, or executable-signal
field — this protocol tests a risk-shape claim, not a trading rule.

## Lock checklist

- Both trailing states are self-referential (no external `target_vol`, no
  leverage/weight-cap contract) — resolves the unpinned-parameter gap Cycle 2
  found in Candidate B's raw operationalization.
- Warm-up fixed at `252` sessions per asset, keeping 2008 inside the evaluated
  sample for every asset including `DBC` — resolves the undefined-warm-up gap
  Cycle 2 found.
- No SMA-window grid in this run — resolves the under-specified multiplicity
  surface Cycle 2 flagged.
- Statistical procedure reuses and bounded-extends one existing function
  (`circular_block_bootstrap_p_value`) rather than requiring new panel or
  permutation infrastructure — keeps this candidate's actual cost close to what
  its Cycle 2 score assumed, unlike the book-level expression of Candidate B or
  Candidate C, which do need new infrastructure and remain out of scope here.
- Materiality thresholds and gate table locked before any data access.

## Method references

- Politis and Romano, "The Stationary Bootstrap," *Journal of the American
  Statistical Association* 89 (1994), [DOI](https://doi.org/10.2307/2290993) —
  general justification for block-resampling under serial dependence, the same
  family of method already in use via `circular_block_bootstrap_p_value`.
