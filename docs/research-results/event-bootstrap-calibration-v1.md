# Event-recompute bootstrap Type-I error calibration v1

Status: complete. Methodology validation, not a research candidate — no
market data was used, no economic hypothesis was tested, and this record
carries no Stage 9A/9B decision vocabulary (`material_and_consistent` /
`not_material_or_not_consistent` / `invalid` do not apply here).

Motivated by an external research memo reviewed 2026-08-20 — see
[docs/brainstorm/2026-08-20-ensemble-factor-vocabulary.md](../brainstorm/2026-08-20-ensemble-factor-vocabulary.md) —
which flagged that the event-recomputing bootstrap extension used by five
closed candidates (SMA Cross v1, RSI oversold reversal, TA Breakout v1,
Wave Pull v1, Overnight Gap Continuation v1) had never had its Type-I error
rate verified. Each candidate's own planted-effect unit test proves the
bootstrap *can* detect a real effect; none of them prove that, under a
genuinely true null, the empirical rejection rate at the nominal `α = 0.05`
is actually close to 5%.

## Method

300 independent synthetic null return series (GARCH(1,1): `α = 0.08`,
`β = 0.90`, target unconditional daily volatility `1%`, zero mean at every
step by construction — realistic volatility clustering, no genuine
directional predictability of any kind), each `3,000` bars long. Each
candidate's own production bootstrap function in `backend/app/research.py`
was called unmodified against every synthetic series. Two deliberate,
disclosed deviations from each candidate's locked production parameters:
`resamples` reduced from `5,000` to `1,000` per call (checking the
*rejection rate* across many replications does not need the same inner
precision as computing one real decision's p-value), and series length
fixed at `3,000` bars (shorter than most real per-asset histories for the
12 locked ETFs, `5,165`–`8,445` rows — if anything conservative for the
event-count-sensitive candidates, which see more qualifying events on a
real, longer history than they do here). `block_bars` and every
candidate's own event-definition parameters (RSI period/threshold,
breakout window, impulse threshold, gap quantile) are unchanged.
ETF-12 rotation, Calendar Turn-of-Month, Calendar Day-of-Week, and CTA v2
are not tested here — they resample an already-realized series with no
per-resample state/event recomputation, much closer to textbook
Politis–Romano stationary-bootstrap usage, and do not share this exposure.

Script: `backend/app/calibrate_event_bootstraps.py`. Artifact:
[`output/research/event-bootstrap-calibration-v1/calibration-report.json`](../../output/research/event-bootstrap-calibration-v1/calibration-report.json).
Wall clock: `2,933` seconds (`~49` minutes) for the full 300-replication run.

## Result

| Candidate | Statistic | Usable replications | Rejections at `α=0.05` | Empirical Type-I rate | Wilson 95% CI |
|---|---|---:|---:|---:|---:|
| SMA Cross v1 | `Δσ` | 300 | 1 | `0.33%` | `[0.06%, 1.86%]` |
| SMA Cross v1 | `ΔMDD` | 300 | 1 | `0.33%` | `[0.06%, 1.86%]` |
| RSI oversold reversal | event | 291 (9 insufficient) | 8 | `2.75%` | `[1.40%, 5.33%]` |
| TA Breakout v1 | event | 300 | 8 | `2.67%` | `[1.36%, 5.17%]` |
| Wave Pull v1 | event | 242 (**58 insufficient**) | 0 | `0.00%` | `[0.00%, 1.56%]` |
| Overnight Gap Continuation v1 | event | 300 | 7 | `2.33%` | `[1.13%, 4.74%]` |
| Overnight Gap Continuation v1 | gap-vs-placebo | 300 | 7 | `2.33%` | `[1.13%, 4.74%]` |

## Reading this result

**No candidate shows evidence of an inflated (anti-conservative) Type-I
error rate.** Every empirical rejection rate sits at or below the nominal
`5%`; for SMA Cross v1 and Wave Pull v1, the entire Wilson 95% confidence
interval sits below `5%` — the machinery is not merely "not obviously
broken," it is measurably conservative for those two. RSI and TA
Breakout's confidence intervals extend just past `5%` at the upper bound,
consistent with correct calibration (nominal `5%` is inside the interval,
not excluded by it). This directly answers the memo's concern: there is no
evidence the block-bootstrap machinery has been silently producing more
false "significant" results than its stated `α` implies.

**This is good news for trusting the five closed nulls at face value, with
one honest caveat worth stating precisely rather than glossing over.** A
conservative test is the safer direction to be wrong in when interpreting
an observed "fail to reject" as a genuine null — it was not, on this
evidence, rejecting spuriously often. But conservative calibration under
the null is frequently, though not universally, associated with *reduced
power* to detect a true effect at the same nominal `α`. This study measured
Type-I error only; it did not measure power at the specific, modest effect
sizes relevant to any of these five candidates' real results. Whether each
candidate's "not material or not consistent" reflects a genuinely absent
effect, or a real-but-modest effect this machinery's *actual* (as opposed
to nominal) sensitivity could not reach, remains partially open — the same
distinction the 2026-08-19 audit already drew for CTA v1, now a live
question for these five candidates too, in the safer (under-rejecting, not
over-rejecting) direction. A power calibration — inject a known, modest
planted effect across many replications and measure detection rate,
mirroring the CTA v1 audit's own approach — is the natural companion study
and is not yet run.

**Wave Pull's `58/300` (`~19%`) insufficient-event exclusion rate is a
separate, corroborating finding, not a calibration defect.** It quantifies
something the real result already disclosed qualitatively: the impulse
precondition (an `8`-session `≥6%` move) is genuinely rare, sparse enough
that a meaningful fraction of otherwise-reasonable 3,000-bar histories
under general volatility conditions never clear the event floor at all —
consistent with the real result's own disclosed exclusion (`IEF`, zero
qualifying events) and its comparatively thin real event counts
(`15`–`140` per asset).

**SMA Cross v1's `Δσ` and `ΔMDD` rejected on the identical single
replication (`1/300` for both).** Expected, not a bug: both statistics are
computed from the same gated return series, so they are highly correlated
by construction — an unusually favourable draw tends to move both
together, which is exactly the two-statistics-same-family multiplicity
treatment the locked protocol already accounts for.

## What this changes and doesn't change

This does not reopen any of the five closed results — none produced a
`material_and_consistent` decision that this finding would now cast doubt
on; if anything, this strengthens confidence that their nulls were not
false positives waiting to happen. It also does not resolve the deeper
question the memo actually raised: whether a *properly-powered, ensemble-
style* test of the same underlying information would find something these
per-asset event studies could not. CTA v2 already partially answers a
version of that question for the trend-continuation family; this
calibration answers a narrower, purely mechanical question about the
testing machinery itself, and answers it in the reassuring direction. A
power calibration of the same five candidates is the logical next check if
this thread is picked up again, not run as part of this exercise.

## Reproducibility

- Full artifact:
  [`output/research/event-bootstrap-calibration-v1/calibration-report.json`](../../output/research/event-bootstrap-calibration-v1/calibration-report.json)
  — includes the exact null-generator parameters, per-candidate replication
  counts, and wall-clock time.
- No market data, no `data/market.db` dependency — fully reproducible on
  any machine from `backend/app/calibrate_event_bootstraps.py` alone with
  no data prerequisites, unlike every other result in this directory.
- Deterministic per-replication seeds (`900000 + replication_index`); a
  rerun at the same replication count reproduces byte-identical inputs to
  each bootstrap call, though the reported rates themselves are Monte Carlo
  estimates with the disclosed Wilson intervals, not exact quantities.

[Script](../../backend/app/calibrate_event_bootstraps.py) ·
[Brainstorm motivation](../brainstorm/2026-08-20-ensemble-factor-vocabulary.md)
