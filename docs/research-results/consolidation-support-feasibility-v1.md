# Consolidation support-recovery feasibility v1

Decision: **not evaluable**. This is not a rejection of consolidation support
recovery. The locked comparison design could not construct an admissible control
set, so prospective power and actual-event outcomes were not evaluated.

Specification SHA-256:
`90d31fb192ca9f7864a2d2f2565ebf018483d7f620422b5d1accb2d1b027a62b`.
Development-data SHA-256:
`86eeb197919baad820d07c450b546245962ce9ae76404b339fdc7d7738f74ccc`.

## Result

The no-look-ahead detector/event engine produced `274` deduplicated structural
events on the `2006-02-06`–`2018-12-31` development interval.

| Gate | Observation | State |
|---|---:|---|
| Locked input identity | Specification, data, and rows match | Pass |
| Asset breadth | `12/12` assets | Pass |
| Calendar breadth | `13` years | Pass |
| Largest asset concentration | `33/274 = 12.0%` (DBC) | Pass |
| Largest year concentration | `33/274 = 12.0%` (2012) | Pass |
| Detector prevalence | `6/8` variants retained; two sparse variants excluded | Pass |
| Matching coverage | `0/274` events have at least three controls | **Fail** |
| Prospective power | Not run after mandatory matching failure | Not reached |
| Actual-event forward outcomes accessed | `false` | Pass |

The matching funnel contained `66,161` same-symbol/same-year candidate dates,
`16,489` after the locked event-exclusion window, and zero dates inside the
`0.25` pooled-standard-deviation caliper on every feature. Required coverage was
90%. The protocol forbids relaxing that caliper after counts are observed.

The final result is therefore `not_evaluable`, not `reject`, `revise`, or evidence
of no effect. It establishes that feasibility protocol v1 cannot answer the
reserved outcome question. A different comparison design must be justified and
preregistered as a new attempt; it cannot repair v1 retrospectively.

## Reproducibility and blinding

- Structural-event artifact SHA-256:
  `500082efee5bccab3bc837e828cea31a46412e33b4e16f1eabf67af68bcef4aa`.
- Decision artifact SHA-256:
  `64fb45b8878a5cc0b0ea665a202d17eeb77cdc4a101fe77d451161abb93bd839`.
- The structural rerun was byte-identical.
- Artifacts contain no actual-event forward outcome, return, drawdown, P&L, or
  post-event price field.

[Protocol](../research-protocols/daily-consolidation-support-recovery-feasibility-v1.md)
· [Machine specification](../../research/experiments/consolidation-support-feasibility-v1.json)
· [Artifact README](../../output/research/README.md)
