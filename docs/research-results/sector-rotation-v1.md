# Sector-level cross-sectional momentum v1 (GICS sector rotation) — result

Decision: **`not_material_or_not_consistent`**. Pooled Spearman rank
correlation between GICS-sector formation rank and forward rank is
slightly **negative** (`-0.019`) and fails both gates decisively — it
neither clears the `0.10` materiality floor nor approaches significance
(`p = 0.895`) against the joint-panel block-resampled null. Unlike
[CS-01](cross-sectional-momentum-v1.md), this is not a borderline case
(materiality met, significance failed) — both gates fail cleanly.

Specification SHA-256:
`bad8d34725bbd62f9bd77ce660d81150aac52623e47b06eb8ee29fd5dc49465a`.
Data SHA-256:
`c435ab8cb511b87d3b25af4952bedf75d3135dd5e1f7dddff7f4a2c13291ebc6`
(independently reproduced byte-identical on the first rerun).

## Result

| Check | Observation | State |
|---|---:|---|
| `rebalance_date_count > 0` | `294` | Pass |
| `observed_correlation` finite | `-0.0189` | Pass |
| `p_value` finite, in `[0,1]` | `0.8946` | Pass |
| Materiality gate (`≥0.10`) | `-0.0189` | **Failed** |
| Significance gate (`p≤0.05`) | `0.8946` | **Failed** |

`11` GICS sectors, `501`-symbol S&P 500 universe (same point-in-time
membership as CS-01), `2001-01-02` to `2026-08-20` aligned calendar,
`252`-session formation (~12 months), `21`-session holding, `21`-session
rebalance spacing — independently chosen for this estimand, not copied
from CS-01's `126`/`21`.

This directly tests the user's own stated observation ("long chips, short
software" — sector-level leadership, not individual-stock momentum) at the
aggregate GICS-sector level, avoiding CS-01's structural inability to test
it at all (CS-01 never formed a "chips" or "software" group). The answer
is: at a 12-month lookback / 1-month-forward cadence, pooled across `11`
sectors and `25` years, sector leadership does not persist into the next
month in a way distinguishable from a temporally-scrambled null — if
anything the point estimate leans slightly toward rotation (negative
correlation) rather than persistence, though far too weak to call that a
finding either.

## Coverage note — one real, disclosed data-quality wrinkle

`Real Estate` was carved out as its own GICS sector only in `2016`; before
that, real estate names were classified under Financials. This shows up
directly in the coverage stats: `Real Estate` has `368` sparse dates (fewer
than `2` eligible members) versus `0` for every other sector, concentrated
in the pre-2016 era of the `25`-year window. This does not change the
reading of the result (a null is unaffected by which direction a coverage
gap could have pushed one sector among eleven), but it is a real, disclosed
limitation of applying today's `11`-sector GICS taxonomy across a period
before that taxonomy existed in its current form.

## Disclosed limitation — today's GICS classification, not point-in-time

Per the protocol's §2: a stock reclassified between GICS sectors at some
point in its real history is attributed to its *current* sector for its
*entire* price history in this design. A null result is unaffected by this
limitation in either direction — it would only matter for interpreting a
positive result, which this is not.

## What this does and does not establish

Does: directly answers a specific, named claim ("sector leadership
persists over roughly a year, then rotates") using real point-in-time
membership and real sector labels, at the exact aggregation level the
claim was actually about — unlike CS-01, which tested a structurally
different claim. Does not: rule out sector rotation as a real, tradeable
phenomenon at other horizons, other groupings (e.g. GICS Sub-Industry,
finer than Sector — "Semiconductors" specifically, not the broader
"Information Technology"), or using a different estimand (e.g. absolute
trend within a sector rather than cross-sectional rank against other
sectors). Those would be new, independently justified candidates, not a
retry of this one.

## Reproducibility

- Manifest, rebalance-results, and decision artifacts:
  `output/research/sector-rotation-v1/bad8d34725bbd62f9bd77ce660d81150aac52623e47b06eb8ee29fd5dc49465a/`.
- Independently reproduced byte-identical on the first rerun (no
  fingerprint bug this time — learned directly from CS-01's fingerprint
  fix earlier the same day, this run's fingerprint hashes the aligned
  sector-index levels directly, never raw unaligned rows).
- No trade, no cost, no position, no sleeve, no sharpe — forbidden outputs
  per the locked spec, none produced.

[Protocol](../research-protocols/sector-rotation-v1.md) ·
[Operationalization record](../research-hypotheses/sector-rotation-v1.md) ·
[Selection record](../research-candidates/2026-08-21-cycle-8.md) ·
[Machine specification](../../research/experiments/sector-rotation-v1.json) ·
[Artifact README](../../output/research/README.md)
