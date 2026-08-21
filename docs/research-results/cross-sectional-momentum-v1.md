# Cross-sectional equity momentum v1 (CS-01) — point-in-time re-baseline

Decision: **`not_material_or_not_consistent`**. Pooled Spearman rank
correlation between formation rank and forward rank clears the `0.10`
materiality floor (`0.146`) but fails significance decisively against the
joint-panel block-resampled null (`p = 0.999`) — under this null design, an
equal-or-higher correlation appears in essentially every resample, meaning
the observed value is fully compatible with what shared market/regime
co-movement alone produces, not evidence of stock-specific rank
persistence.

Specification SHA-256:
`46cdf4b44aed563a15cac53b9c9b2fdc22c4be4f2ca6bec5b94243fd044d5ce5`.
Data SHA-256:
`04957c3152f7d6698653e89b9e97a893e9d2a73e62586b71b607652c670e01bb`
(independently reproduced byte-identical across three separate runs).

## Result

| Check | Observation | State |
|---|---:|---|
| `rebalance_date_count > 0` | `300` | Pass |
| `observed_correlation` finite | `0.1462` | Pass |
| `p_value` finite, in `[0,1]` | `0.9985` | Pass |
| Materiality gate (`≥0.10`) | `0.1462` | **Met** |
| Significance gate (`p≤0.05`) | `0.9985` | **Failed** |

Universe: `501` symbols with both a real point-in-time S&P 500 membership
interval and at least one stored bar — narrower than the feasibility
check's `495` (S&P 500 ∪ Nasdaq-100 ∪ XL ETFs) on purpose: no point-in-time
membership data exists for Nasdaq-100 or the XL ETFs, so they are excluded
rather than silently treated as always-eligible. Aligned calendar:
`2001-01-02` to `2026-08-20` (`6,446` sessions, SPY's own trading
calendar), `126`-session formation, `21`-session holding, `21`-session
rebalance spacing — identical parameters to the feasibility check, no new
peek.

**This is the first confirmatory attempt at this estimand with real
point-in-time membership**, superseding [ETF-12 rotation](etf12-cross-sectional-rotation-v1.md)
(`N=12`, clean null, `ρ=0.045`) and [the feasibility
check](cross-sectional-equity-momentum-feasibility-v1.md) (`N=495`, engine
only, non-evidential) at real breadth with real entry/exit timing: `134`
genuine point-in-time S&P 500 additions since `2019-01-01` were correctly
excluded from rebalance dates before their real join date (e.g. `TSLA`,
added `2020-12-21`, contributes nothing to any rank before that date under
this design — the prior survivorship-biased design would have included it
retroactively).

## Residual limitation — disclosed, not fully resolved

Real point-in-time *membership* now exists; real point-in-time *price
history* for every historical member does not. Of `1,206` symbols ever
recorded as an S&P 500 member since 1996, `705` have zero stored bars in
this project's database (delisted, acquired, or renamed before this
project ever fetched their prices) and are absent from this universe
entirely — a narrower, but real, residual survivorship bias, distinct from
the reverse-survivorship contamination this run does fix (see the
[protocol](../research-protocols/cross-sectional-momentum-v1.md)'s §2 for
the full accounting: `33` real historical exits and `2` genuine re-entries
are captured within the `501`-symbol universe, mostly pre-`2019`). This
does not change the reading of a null result — a null is unaffected by
which direction the residual bias could have pushed — but would matter if
this run had instead come back positive.

## What this does and does not establish

Does: directly answers a question this project has asked itself explicitly
this session ("why do other quants find something and we find null") for
this specific estimand — even at real breadth, with the reverse-survivorship
contamination fixed, plain pooled cross-sectional rank correlation between
6-month formation and 1-month forward return shows no material,
distinguishable-from-chance effect in this universe/period. Does not:
rule out cross-sectional momentum as a phenomenon generally — the high
resampled-null correlations observed here are consistent with a design
limitation (a raw, non-market-neutral, non-beta-adjusted rank correlation
is dominated by common-factor co-movement, a well-known critique of this
exact naive design in the literature) rather than proof momentum is absent
in this universe. A market-neutral or beta-adjusted re-design would be a
new, independently justified estimand, not a retry of this one.

## Reproducibility

- Manifest, rebalance-results, and decision artifacts:
  `output/research/cross-sectional-momentum-v1/46cdf4b44aed563a15cac53b9c9b2fdc22c4be4f2ca6bec5b94243fd044d5ce5/`.
- Independently reproduced three times; the third run's data fingerprint
  matched the second exactly. The first run's fingerprint function had a
  real bug (hashing raw, unaligned bars rows rather than the exact aligned
  data the bootstrap consumed) that was caught by this project's own
  reproducibility gate, fixed, and re-verified before this result was
  written up — the statistical result itself (correlation, p-value) was
  identical across every run, including the buggy-fingerprint one; only the
  fingerprint was wrong, never the computation.
- No trade, no cost, no position, no sleeve, no sharpe — forbidden outputs
  per the locked spec, none produced.

[Protocol](../research-protocols/cross-sectional-momentum-v1.md) ·
[Operationalization record](../research-hypotheses/cross-sectional-momentum-v1.md) ·
[Selection record](../research-candidates/2026-08-21-cycle-7.md) ·
[Machine specification](../../research/experiments/cross-sectional-momentum-v1.json) ·
[Artifact README](../../output/research/README.md)
