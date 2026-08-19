# Wave Pull v1 — impulse-pullback continuation vs. plain-breakout placebo

Decision: **not material or not consistent**. A fourth negative result this
session, and a fourth distinct shape — worth reading on its own terms, not
folded into the prior three.

Specification SHA-256:
`618a482ae4866887d13b38d84679a98b7343fe2e4e983e29ead6a249f49050c1`.
Data SHA-256: `a45bce859cdeee705a06cdea9c03f1bf0f31cff501d5f66c2e544d8f13fb64ab`.

## Result

| Gate | Observation | State |
|---|---:|---|
| Locked specification identity | Verified before execution | Pass |
| Minimum event count (`≥15`) | `11/12` assets eligible; `IEF` excluded with `0` qualifying events | Disclosed |
| Materiality + significance, after Holm | `0/11` eligible assets | **Fail** |
| Breadth (`≥8` of eligible required) | `0/11` | **Fail** |
| Placebo comparison | `4/11` assets | See design note — separation was clean this time |
| Actual costs or execution accessed | `false` | Pass (no-trade experiment) |

`IEF` (intermediate Treasury) had exactly zero sessions where an `8`-session
`≥6%` move ever occurred — a low-volatility instrument simply never produced
the precondition. This is disclosed as designed, not silently dropped or
worked around; the protocol's own risk section anticipated exactly this.

## What's different about this result

**The event/placebo separation was clean**, unlike TA Breakout v1. The
impulse precondition filtered aggressively — event counts ran `20`–`140` per
asset against placebo counts of `362`–`626`, roughly a `5`–`20×` ratio. The
impulse requirement is doing real, substantial filtering work here, which
makes the placebo comparison meaningful in a way TA Breakout's wasn't.

**One asset came closer to raw significance than anything else tested this
session.** `TLT`'s raw p-value was `0.032` — the first time any single asset
crossed the conventional `0.05` line before correction, across all four
experiments. It does not survive Holm correction (adjusted `p = 0.350`), and
it rests on only `20` qualifying events — thin enough that this reads as a
noteworthy near-miss on a small sample, not a result approaching the
materiality bar.

**Several equity assets showed a mean forward return in the *wrong*
direction.** `EEM` (`-1.03%`), `XLF` (`-1.29%`), `QQQ` (`-0.63%`), `XLK`
(`-0.58%`) all had negative mean forward returns following the event — none
individually significant, but worth stating plainly rather than only
reporting the positive cases. The four assets that did show a positive,
placebo-beating effect (`DBC`, `GLD`, `TLT`, `XLE`) are commodities,
duration, and energy — a pattern that may be noise given the sample sizes
involved, but is recorded here descriptively rather than silently omitted.

## Reading this result

This is not a power problem the way RSI was (event counts were often larger
here), not a confound the way SMA Cross was (no single placebo explanation
sweeps the board), and not a weak-test problem the way TA Breakout was (the
separation was clean). It is closest to: a real test, cleanly separated from
its placebo, that simply did not find a material, reliable effect — with one
small-sample near-miss (`TLT`) worth watching only in the sense that it is
not itself evidence, and a directionally adverse pattern on several equity
assets that is disclosed, not a basis for any claim.

Per this protocol's own decision vocabulary, only `material_and_consistent`,
`not_material_or_not_consistent`, or `invalid` may be output here.

## Reproducibility and blinding

- Per-asset artifact:
  [`output/research/wave-pull-v1/618a482a.../per-asset-results.json`](../../output/research/wave-pull-v1/618a482ae4866887d13b38d84679a98b7343fe2e4e983e29ead6a249f49050c1/per-asset-results.json).
- Decision artifact:
  [`decision.json`](../../output/research/wave-pull-v1/618a482ae4866887d13b38d84679a98b7343fe2e4e983e29ead6a249f49050c1/decision.json).
- No cost, execution, position, or portfolio-level field is present in any
  artifact.
- Data fingerprinted fresh at execution time; not guaranteed to reproduce
  bit-for-bit on a different machine's fetch.

[Protocol](../research-protocols/wave-pull-v1.md) ·
[Selection record (Cycle 4)](../research-candidates/2026-08-19-cycle-4.md) ·
[Machine specification](../../research/experiments/wave-pull-v1.json)
