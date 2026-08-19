# Consolidation support-recovery feasibility v1 — structural checkpoint

Status: incomplete feasibility result. No actual-event forward outcome, return,
drawdown comparison, P&L, or evidence decision was calculated.

Specification SHA-256:
`90d31fb192ca9f7864a2d2f2565ebf018483d7f620422b5d1accb2d1b027a62b`.
Development-data SHA-256:
`86eeb197919baad820d07c450b546245962ce9ae76404b339fdc7d7738f74ccc`.

## Permitted observation

The locked detector/event engine produced `274` deduplicated structural events on
the `2006-02-06`–`2018-12-31` development interval.

| Structural gate | Observation | State |
|---|---:|---|
| Asset breadth | `12/12` assets | Preliminary pass |
| Calendar breadth | `13` years | Preliminary pass |
| Largest asset concentration | `33/274 = 12.0%` (DBC) | Preliminary pass versus 25% ceiling |
| Largest year concentration | `33/274 = 12.0%` (2012) | Preliminary pass versus 25% ceiling |
| Locked input identity | Specification, data, rows all match | Pass |
| Actual-event forward outcomes accessed | `false` | Pass |
| Structural-event artifact SHA-256 | `05092007ff47ad959f1676d352e15d5aac9c1ba86aac19894de304ec4ec43d4c` | Byte-identical rerun verified |

Counts alone do not establish statistical power, useful support, reduced downside,
or a trading edge. The overall decision remains `null`.

## Remaining feasibility gates

- detector prevalence for every retained variant;
- pre-event matching coverage under the locked caliper;
- corrected automatic block-selector verification;
- pseudo-event nuisance dispersion and adjusted prospective power;
- complete structural audit and final `feasible`, `not evaluable`, or `invalid`
  decision.

[Protocol](../research-protocols/daily-consolidation-support-recovery-feasibility-v1.md)
· [Machine specification](../../research/experiments/consolidation-support-feasibility-v1.json)
· [Artifact README](../../output/research/README.md)
