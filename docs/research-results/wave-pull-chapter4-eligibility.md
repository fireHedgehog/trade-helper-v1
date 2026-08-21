# Wave Pull — Chapter 4 eligibility score

Decision: **walked back to candidate status, not distinguishable from
chance**. Governed by [ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md).
Scripts:
[`score_wave_pull_tlt_chapter4.py`](../../backend/app/score_wave_pull_tlt_chapter4.py)
(§1, `TLT` solo) and
[`score_wave_pull_chapter4.py`](../../backend/app/score_wave_pull_chapter4.py)
(§2, all 12 assets).

## Result

- **`TLT` solo**: `68%` confidence interval on the 10-session forward
  return, case-resampled across `20` qualifying events: `[+1.22%, +2.40%]`,
  multiplier `0.674` — eligible on paper.
- **All 12 assets**: `2/11` eligible (`GLD`, `TLT`; `IEF` had zero
  qualifying events, not scoreable).

## Reading this result

`TLT` was pre-selected as the single best raw-`p` asset of `12` from Wave
Pull v1's own Chapters 1–3 test ([full result](wave-pull-v1.md)) *before*
the solo score was run — a winner's-curse selection the solo report did
not originally disclose or correct for. The symmetric 12-asset rescore
genuinely fixes the selection-bias objection an external critique
(2026-08-20) correctly raised — no more cherry-picking which asset to
show.

But [the eligibility-rule calibration](chapter4-eligibility-calibration-v1.md)
settles what `2/11` is actually worth: against a calibrated `19.08%`
per-asset chance rate, `2/11` is **not distinguishable from noise** — `2`
is in fact the single most probable outcome the null model predicts
(`P(X≥2)≈65%`, mode `=2`). An earlier same-session read of this result
("a second independent hit is harder to explain by chance") was checked
against the calibration and does not survive it; corrected here rather
than left standing.

`GLD`/`TLT`'s near-zero cross-correlation
([orthogonality v1](chapter4-orthogonality-v1.md), `r=0.02`) is real but
narrower evidence than that: it rules out `GLD` and `TLT` being a
disguised double-count of one redundant artifact (the failure mode seen
among Calendar Day-of-Week's correlated pairs), not that either reflects a
genuine effect — both "two real independent signals" and "two independent
noise false-positives" predict low correlation equally well.

Net: `GLD`/`TLT` remain clean, bias-free, decorrelated *candidates*
appropriately queued for Chapters 1–3's strict bar or out-of-sample
testing — the loosened `68%` screen doing its intended job of admitting
candidates for further scrutiny, not a verdict that nothing is there.

[Chapter 4 index](../research-program.md)
