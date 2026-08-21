# Ensemble-construction engine — 3-signal breadth test (exploratory)

Status: exploratory, not a Stage 9A candidate. Follow-up to
[ensemble-smoke-test-v1.md](ensemble-smoke-test-v1.md), which proved the
facility works but ended up single-signal (`atr_normalized`'s
cross-sectional confidence multiplier came out `0.0`). Since then, two new
independent candidates were found
([academic-anomalies-chapter4-v1.md](academic-anomalies-chapter4-v1.md)):
`max_effect` (confidence multiplier `0.56`) and `expected_skewness_proxy`
(`0.81`), both below this project's own `|r| ≥ 0.5` redundancy threshold
against `amihud_illiquidity` and each other. This is the real breadth test
v1 could not run — three independent, positive signals, combined for real.

## Result — all three signals actually contribute

| Check | Observation |
|---|---|
| As-of date | `2026-08-20` |
| Eligible universe | `494` symbols |
| Long / short group size | `98` / `98` (symmetric) |
| Gross exposure | `100.00%` — exact, no added leverage |
| Net exposure | `~0%` (`1.1e-14`, floating-point noise) |
| `amihud_illiquidity` confidence multiplier | `0.33` |
| `max_effect` confidence multiplier | `0.56` |
| `expected_skewness_proxy` confidence multiplier | `0.81` |

Unlike v1, no signal zeroed out — the composite score genuinely blends
three independent views this time. Top long picks (`FE`, `EVRG`, `L`,
`PNW`, `CNP` — several utilities) and top short picks (`TRV`, `AIZ`,
`CSX`, `DGX`, `MSI` — insurers, a railroad, diagnostics, industrials) look
like a real, diversified cross-section, not one factor's own obvious
picks repeated three times.

## What this does and does not establish

Does: prove the ensemble engine handles a genuine multi-signal case
correctly — confidence-weighted blending, symmetric groups, exact
constraint satisfaction, all on real data with three real (if still
exploratory) candidates. Does not: authorize any real deployment — none
of the three signals has cleared ADR 0007 clauses 1/2 yet. Does not:
apply sector/cluster concentration caps (ADR 0010 §5, still unimplemented
in `ensemble.py`) — the long side's utility concentration above is exactly
the kind of thing that cap would need to check.

## Reproducibility

- Artifact: `output/research/ensemble-smoke-test-v2/result.json`.
- `backend/app/run_ensemble_smoke_test_v2.py` — generalizes v1's script to
  N signals with correct-direction sign handling for
  literature-predicted-negative factors.

[Ensemble smoke test v1 (single-signal, facility proof)](ensemble-smoke-test-v1.md) ·
[Academic anomalies Chapter 4 (source of the 2 new candidates)](academic-anomalies-chapter4-v1.md) ·
[amihud_illiquidity Chapter 4 result](amihud-illiquidity-chapter4-v1.md)
