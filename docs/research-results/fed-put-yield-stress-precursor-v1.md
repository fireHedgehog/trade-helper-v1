# Fed put: yield-stress precursor v1

Decision: **`not_evaluable`** (locked reading rule: `p<=0.10` evidence
present, `0.10<p<=0.30` weak, otherwise not evaluable). `p=0.989`.

Specification SHA-256:
`61eb422ef52275bb0947c8fe932f742e205c1aaa57fe665713734c6d9a06623f`.
Data SHA-256:
`64d4b8883905c47869dc73dbe9508937e1a48dd2011ae8a0be3809d0b509fe49`.

## Result

| Episode | Start | Max score in precursor window | Sign |
|---|---|---:|---|
| QE1 | 2008-11-25 | -2.72 | opposite |
| QE2 | 2010-11-03 | -2.43 | opposite |
| QE3 | 2012-09-13 | -2.31 | opposite |
| COVID QE | 2020-03-23 | -1.95 | opposite |

Observed mean statistic: **-2.35**. `4`/`4` episodes negative — every
real QE launch was preceded by a *low*, not high, yield-stress score.
`p=0.989`: `98.9%` of placebo windows drawn from the rest of history had
a *higher* score than the real pre-QE periods did.

## Disclosed, non-gating diagnostic: this is not a bare null, it is decisively opposite

The locked decision (`not_evaluable`) reports the pre-committed reading
rule honestly, but the pattern underneath is not an underpowered
non-result — it is consistent across all 4 episodes, same shape as
[Overnight Gap Continuation v1](overnight-gap-continuation-v1.md)'s
12/12 opposite-signed finding. Direct inspection of the underlying
series (non-gating, run after the locked p-value, exactly the "report
the episode table itself" rule in
[Thesis Track](../thesis-track-small-n.md)):

| Episode | `z(10Y)` at $t{-}1$ | `z(2Y)` at $t{-}1$ |
|---|---:|---:|
| QE1 | -2.22 | -2.10 |
| QE2 | -1.62 | -1.28 |
| QE3 | -1.38 | -1.08 |
| COVID QE | -2.95 | -2.83 |

Both ends fell together, sharply, before every real launch — not "10Y
high, 2Y contained." Historically, Fed QE has followed a **broad
flight-to-safety yield collapse** (recession/crisis fear, both ends
pricing cuts), not a long-end-specific yield spike.

## What this means for the motivating narrative

The user's own framing that started this candidate — 2Y contained, 10Y/30Y
elevated on term-premium/fiscal concerns — describes a curve shape with
**no precedent among the 4 real QE launches tested**. If the Fed did
respond to that shape with renewed balance-sheet expansion, it would be a
genuinely novel policy reaction, not a repeat of 2008/2010/2012/2020. This
result does not say that can't happen; it says this specific historical
test provides no support for expecting it to, and the historical pattern
actually runs the other way.

## Reproducibility

- Manifest, episode-results, decision artifacts:
  `output/research/fed-put-yield-stress-precursor-v1/61eb422ef52275bb0947c8fe932f742e205c1aaa57fe665713734c6d9a06623f/`.
- No trade, no cost, no position, no sleeve — forbidden outputs per the
  locked spec, none produced.

[Protocol](../research-protocols/fed-put-yield-stress-precursor-v1.md)
· [Machine specification](../../research/experiments/fed-put-yield-stress-precursor-v1.json)
· [Artifact README](../../output/research/README.md)
