# Academic anomalies — Chapter 4 evaluation, point-in-time universe (exploratory)

Status: exploratory, ahead of [ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md)
clauses 1/2 formal sign-off. [Factor zoo academic anomalies v1](factor-zoo-academic-anomalies-v1.md)
closed `low_volatility`/`max_effect` as "redundant with `atr_normalized`"
and `corwin_schultz_spread`/`expected_skewness_proxy` as clean nulls — all
four using today's-membership data, no Chapter 4 evaluation. Since
`atr_normalized`'s own cross-sectional form just failed point-in-time
correction ([ensemble-smoke-test-v1.md](ensemble-smoke-test-v1.md)),
"redundant with `atr_normalized`" stopped being a reason to leave the
other two unexamined on their own merits. Re-scored all four masked to
real point-in-time S&P 500 membership, via Sharpe/CAGR/Calmar and a
block-bootstrap EV confidence interval — no p-value, per this project's
post-2026-08-21 rule.

## Result

| Factor | Sharpe (correct direction) | CAGR | Confidence multiplier | Verdict |
|---|---:|---:|---:|---|
| `max_effect` | `+0.40`* | `+10.7%`* | `0.56` | **New live candidate** |
| `expected_skewness_proxy` | `+0.92`* | `+8.9%`* | `0.81` | **New live candidate, strongest yet** |
| `low_volatility` | `-0.16` | `-6.4%` | `0.0` | Still not a candidate — CI straddles zero |
| `corwin_schultz_spread` | `-11.07` | `-68.1%` | `0.0` | Decisively, catastrophically wrong-signed (see below) |

\* `max_effect` and `expected_skewness_proxy` are literature-predicted to
score a negative raw Sharpe under this harness's "high reading = long"
convention (lottery-demand overpricing — the real trade is long *low*
readings). Sharpe/CAGR above are reported in the corrected (flipped)
direction, matching how the confidence multiplier was computed; the raw
harness output was `-0.40`/`-0.92` respectively.

## Two new, genuinely independent candidates

Pairwise correlation of daily spread returns (all three in their
correctly-signed direction), `6,385` overlapping days:

| | `amihud_illiquidity` | `max_effect` | `expected_skewness_proxy` |
|---|---:|---:|---:|
| `amihud_illiquidity` | `1.00` | `-0.42` | `-0.02` |
| `max_effect` | `-0.42` | `1.00` | `0.35` |
| `expected_skewness_proxy` | `-0.02` | `0.35` | `1.00` |

Every pair is below this project's own `|r| ≥ 0.5` redundancy threshold
(`factor_zoo.CHAPTER4_REDUNDANCY_THRESHOLD`). `amihud_illiquidity` and
`max_effect` are even moderately *negatively* correlated — genuinely
diversifying, not just independent. Three real, positive, point-in-time-
corrected, cost-charged candidates now exist for the ensemble — the
breadth the smoke test's single-signal run could not test.

## `corwin_schultz_spread`: a real finding, not a bug — checked directly

Confidence multiplier `0.0` understates how decisive this is: Sharpe
`-11.07`, CAGR `-68.1%`, max drawdown effectively total. Investigated
before writing this up, because a Sharpe this extreme is not a plausible
real factor return at face value: no single day in `6,444` sessions is
worse than `-6.9%` (the worst is `2020-03-18`); `77` days are worse than
`-2%`, concentrated in `2001`, `2008-09`, `2020`, and `2025` — real crisis
periods, not a data glitch. The catastrophic figure is genuine compounding
of a persistently, moderately negative daily mean over `25` years, not one
corrupted print. Read plainly: buying high-Corwin-Schultz-spread
(illiquid-by-quoted-spread) stocks and shorting low-spread ones was a real
disaster, especially in crises — flight-to-quality dynamics hit the
"illiquid" side hardest exactly when the strategy is long it, the opposite
of the illiquidity-premium story the literature predicts. This is a
genuine contrast with `amihud_illiquidity`, whose own (dollar-volume-based)
illiquidity proxy showed the *expected* positive premium — two different
illiquidity measures, opposite real-world signs. A "buy liquid, short
illiquid" flipped version of this specific proxy is a plausible, different,
independently-justified candidate for later — not silently substituted
here.

## What this does and does not establish

Does: identify two new, real, independent Chapter 4 candidates via the
same disciplined pipeline `amihud_illiquidity`'s own evaluation used.
Does: resolve `low_volatility`'s status independently of its
now-questionable "redundant with `atr_normalized`" original reasoning —
still not a candidate, this time confirmed directly. Does: disclose a
decisive, investigated (not assumed-safe) negative finding for
`corwin_schultz_spread`. Does not: constitute clause 1/2 sign-off for
either new candidate — same raw-material status as every other Chapter 4
result this session.

## Reproducibility

- Artifacts: `output/research/academic-anomalies-chapter4-v1/manifest.json`,
  `result.json`.
- `backend/app/run_academic_anomalies_chapter4.py` — reuses
  `factor_zoo.evaluate_factor` and `run_amihud_illiquidity_chapter4.build_masked_panel`
  unmodified; new logic is the correct-direction sign flip for the two
  literature-predicted-negative factors.

[Factor zoo academic anomalies v1 (original screen)](factor-zoo-academic-anomalies-v1.md) ·
[amihud_illiquidity Chapter 4 result](amihud-illiquidity-chapter4-v1.md) ·
[Ensemble smoke test (byproduct: `atr_normalized` cross-sectional finding)](ensemble-smoke-test-v1.md) ·
[ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md)
