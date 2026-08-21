# Ensemble-construction engine — smoke test (exploratory)

Status: exploratory, not a Stage 9A candidate. Answers the user's own
framing directly: "2 factor is not enough i know, but at least > 1 so can
do a smoke test of new facility work or not." Combines the two real
signals this project has (`atr_normalized`, `amihud_illiquidity`) through
[ensemble-construction-engine-v1.md](../ensemble-construction-engine-v1.md)'s
real implementation (`backend/app/ensemble.py`), on real point-in-time
data, for the most recent available session — not a made-up numeric
example.

## Result — the facility works

| Check | Observation |
|---|---|
| As-of date | `2026-08-20` |
| Eligible universe | `494` symbols |
| Long / short group size | `98` / `98` (symmetric) |
| Gross exposure | `100.00%` of equity — exact, no added leverage |
| Net exposure | `~0%` (`-6.5e-15`, floating-point noise) — market-neutral by construction |
| `amihud_illiquidity` confidence multiplier | `0.33` (contributes to the composite score) |
| `atr_normalized` confidence multiplier | `0.0` (contributes nothing — see finding below) |

Every constraint in [ADR 0010](../adr/0010-long-short-ensemble-construction.md)
§1 held on real data: exact `100%` gross, effectively `0%` net, symmetric
minimum-breadth groups. Because `atr_normalized`'s own confidence
multiplier came out `0.0`, the resulting book is driven entirely by
`amihud_illiquidity` — a real, correct behavior of the alpha model (a
zero-confidence signal is weighted to exactly zero, not partially), not a
bug, though it means this run is not really evidence of two-signal
diversification.

## A real bug, caught and fixed during the smoke test

First run: `long_count = 0`, `short_count = 99`, gross exposure `NaN`.
Traced to a real data-completeness gap the eligibility mask hadn't
covered: a symbol can have real point-in-time S&P 500 membership *and* a
valid factor score on a given date while still lacking a complete
252-session return history (a recently-added member — e.g. `PSKY`, added
`2025-08-08`). `shrinkage_covariance`'s `np.cov` call propagates `NaN`
from an incomplete column into that symbol's diagonal, silently poisoning
every long-side position that happened to include one. Fixed by requiring
a complete trailing return history as its own eligibility condition,
separate from having a valid factor score — `5` symbols correctly
excluded on this run. This is exactly what a smoke test is supposed to
surface: not "does the arithmetic work on a clean toy example," but "does
the facility handle real, ragged, incomplete data without silently
producing a wrong number."

## Secondary finding: `atr_normalized`'s cross-sectional form does not survive point-in-time correction

Not the subject of this smoke test, but a real, disclosable result that
fell out of building it: scoring `atr_normalized` as a pure cross-sectional
factor (same `factor_zoo.evaluate_factor` quintile-spread methodology
[factor-zoo-v1 §5](factor-zoo-v1.md) used, Sharpe `0.84`) but masked to
real point-in-time S&P 500 membership instead of today's-membership
survivorship-biased universe:

| Metric | Value |
|---|---:|
| Sharpe | `-0.012` |
| CAGR | `-3.54%` |
| Block-bootstrap observed daily EV mean | `-1.25e-5` |
| Block-bootstrap EV lower bound (68%) | `-1.93e-4` |
| Confidence multiplier | `0.0` |

The same pattern [CS-01](cross-sectional-momentum-v1.md) found for
individual-stock momentum: a positive factor-zoo screen result computed on
today's-membership data does not necessarily survive real point-in-time
correction. This is **not** evidence against `atr_normalized` generally —
"ATR Vol Premium" (the Tier A strategy, [surveyed separately](atr-vol-premium-survey-v1.md))
is a genuinely different claim (an asset's own-history ATR percentile
predicting its own forward return, not a cross-sectional rank against
other stocks on the same day) and is unaffected by this finding. It does
mean `atr_normalized`'s cross-sectional appearance in the original 27-factor
screen should be read with the same residual-survivorship caveat CS-01
disclosed, not treated as confirmed.

## What this does and does not establish

Does: prove the ensemble engine's three components work together, end to
end, on real data, with all ADR 0010 constraints holding exactly. Does:
disclose a real cross-sectional-`atr_normalized` finding as a byproduct.
Does not: constitute a two-signal diversification test (one signal
contributed zero weight) — that needs a second, independently-positive
cross-sectional candidate, which `atr_normalized`'s cross-sectional form
is not, per the finding above. Does not: authorize any real (even paper)
sizing — exploratory only, same status as every other Chapter 4 result
this session.

## Reproducibility

- Artifact: `output/research/ensemble-smoke-test-v1/result.json`.
- `backend/app/run_ensemble_smoke_test.py`, `backend/app/ensemble.py`
  (engine), `backend/tests/test_ensemble.py` (12 unit tests against the
  design doc's own acceptance checklist).

[Ensemble-construction engine v1 (design)](../ensemble-construction-engine-v1.md) ·
[ADR 0010](../adr/0010-long-short-ensemble-construction.md) ·
[amihud_illiquidity Chapter 4 result](amihud-illiquidity-chapter4-v1.md) ·
[ATR Vol Premium survey](atr-vol-premium-survey-v1.md)
