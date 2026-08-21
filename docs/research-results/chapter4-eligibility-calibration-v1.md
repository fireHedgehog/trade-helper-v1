# Chapter 4 eligibility-rule calibration v1

Status: methodology validation, not a research candidate — measures the
Chapter 4 eligibility construction's own false-positive rate under a known
null, same discipline as
[event-bootstrap-calibration-v1](event-bootstrap-calibration-v1.md).
Script:
[`calibrate_chapter4_eligibility.py`](../../backend/app/calibrate_chapter4_eligibility.py).
Full artifact:
[`calibration-report.json`](../../output/research/chapter4-eligibility-calibration-v1/calibration-report.json).

## Motivation

A pasted external critique (2026-08-20) argued Calendar Day-of-Week's
`6/12` is close to what pure chance would produce at a `68%` band, and
separately that `TLT`'s solo Wave Pull report suffers "winner's curse."
Rather than argue the arithmetic analytically, this measures it directly:
`300` replications of zero-mean GARCH(1,1) synthetic null data, each
eligibility construction run unmodified, empirical false-eligible rate
reported with a Wilson `95%` CI.

## Result

- **Two-sample** (Day-of-Week-shape), single independent null asset:
  `16.25%` false-eligible (`95%` CI `[15.08%, 17.49%]`, `n=3,600`) —
  matches a one-sided-normal-tail approximation almost exactly, **not**
  the critique's `32%` figure; the critique's own number does not survive
  this check.
- **Case-resample** (Wave-Pull-shape), single independent null asset:
  `19.08%` (`95%` CI `[17.70%, 20.54%]`, `n=2,945`).
- **Case-resample, selected winner of 12** (the single best of `12`
  independent null assets by observed mean — mirroring exactly how `TLT`
  was chosen): `84.67%` false-eligible (`95%` CI `[80.15%, 88.30%]`,
  `n=300`). This is the critique's winner's-curse concern, measured
  directly, and it is worse than the critique itself estimated: a
  best-of-`12` selection clears Chapter 4's bar under pure noise more
  often than not.

## Reading this result

A first pass at interpreting these numbers against the real `6/12` and
`2/11` results was itself run through independent adversarial verification
(four reviewers, two per claim, working from the raw numbers rather than
from each other's framing) before being written down, matching this
project's standing practice of checking pasted critiques empirically
rather than arguing about them — applied for once to a first-pass reading
of its own results, not just to an outside critique. Two corrections
resulted:

1. **Wave Pull's `2/11`** — corrected against the `19.08%` calibrated null
   (`P(X≥2 of 11)≈65%`, the modal outcome) — see
   [Wave Pull's eligibility record](wave-pull-chapter4-eligibility.md).
2. **Day-of-Week's `6/12` is not the settled "real, elevated" result it
   initially looked like, either.** Positive correlation among the `6`
   winners (see [orthogonality v1](chapter4-orthogonality-v1.md)) inflates
   the variance of an extreme count under the null — it makes `6` *more*
   likely by chance, not less, the opposite of the direction needed to
   defend the naive `p≈0.7%` reading. Correcting for only the `3` known
   winner-vs-winner pairs (treating the other `51` of `66` possible pairs
   as uncorrelated, an assumption not actually verified) still leaves the
   result notable (`p≈1.5%–2.5%`), but that assumption is unverified and
   optimistic — financial assets often cluster by category even below the
   `0.5` flagging threshold, and if unmeasured correlation among the `9`
   non-winning assets is non-trivial, a defensible correction pushes the
   tail probability as high as `~17%–21%`, coin-flip range. This
   unresolved range is what motivated building the rigorous
   correlation-aware joint-null test directly rather than continuing to
   argue from a partial correction — see
   [Calendar Day-of-Week's eligibility record](calendar-dow-chapter4-eligibility.md)
   for that test's result.

[Chapter 4 index](../research-program.md)
