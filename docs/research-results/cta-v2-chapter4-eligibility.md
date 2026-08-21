# CTA v2 — Chapter 4 eligibility score

Decision: **not eligible**. Governed by [ADR 0007](../adr/0007-risk-budgeted-ensemble-acceptance.md),
not Stage 9A's vocabulary — this asks "is the uncertainty band narrow
enough to size small," not "is this proven." Script:
[`score_cta_v2_chapter4.py`](../../backend/app/score_cta_v2_chapter4.py).

## Result

`68%`-coverage confidence interval on the daily excess return (case-
resampled): `[-0.0035%, +0.0204%]`, annualized lower bound `-0.88%`. Even
at Chapter 4's deliberately loosened one-sigma bar, the interval still
spans zero — confidence multiplier `0.0`, no position sized.

## Reading this result

Consistent with CTA v2's own raw `p=0.231` under its Stage 9A null test
([full result](cta-v2-pooled-trend-overlay.md)) — not a contradiction, a
cross-check: a raw p that far from significant implies a wide-enough
interval to plausibly include zero at `68%` coverage too. This is Chapter
4 working as designed, not failing — being the strongest candidate in
[Chapter 6's triage](../research-program.md)
does not guarantee clearing even a lower bar, and checking that honestly
was the entire point of building this before opening a new falsification
thread.

[Chapter 4 index](../research-program.md)
