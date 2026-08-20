# Thesis Track: small-*n* regime-episode inference

Status: alternative verification method under
[model-acceptance-standard.md](model-acceptance-standard.md)'s "Verification
risks and method selection" — for estimands where the natural unit of
evidence is a handful of dependent regime episodes, not a large
quasi-independent daily sample. Block-bootstrap (`circular_block_bootstrap_p_value`,
used by every candidate to date) treats daily observations as the
resampling unit; that manufactures pseudo-replication here, exactly the
"row count is not effective *n*" risk ADR 0006 clause 6 already names for
macro data generally. This is that clause's own resolution for the
episode case, not a new principle.

## When this track applies

The claim's own falsifier can only fire a handful of times in available
history — e.g. "does long-end yield reversal follow sustained Fed
support," where "sustained support" happens in a small number of
multi-month regimes (QE programs, the 2024– buyback program), not
hundreds of independent daily crossings. If a candidate's event count is
in the hundreds+, use the standard block-bootstrap track instead — this
is not a general substitute for it.

## Design

1. **Episode definition, dated by policy record, not data.** Regime
   boundaries come from official program announcement/end dates (FOMC
   statements, Desk operational releases, Treasury refunding
   announcements) — never from a changepoint detected in the outcome
   series itself. Detecting boundaries from the yield data being tested
   is circular and forbidden by this track's own logic, not merely
   discouraged.
2. **One statistic per episode.** Collapse each episode to a single
   signed summary (e.g. peak-to-trough long-end yield reversal within the
   episode window). No within-episode daily statistic enters inference —
   that is exactly the pseudo-replication this track exists to avoid.
3. **Inference: randomization, not asymptotics.** With ~3-5 real episodes,
   no CLT- or bootstrap-percentile argument is valid. Build the null by
   drawing many placebo windows of the *same lengths* as the real
   episodes from the full available history (non-overlapping, dated
   independently of the outcome), computing the same statistic on each,
   and locating the real episodes' combined statistic in that empirical
   distribution — placebo-in-time inference, the small-treated-unit
   analogue of Abadie-Diamond-Hainmueller synthetic-control significance
   testing, not a bootstrap variant.
4. **Report the episode table itself.** At *n*≈3-5, the case-by-case
   table (dates, direction, magnitude per episode) is not supplementary —
   it is comparably informative to the aggregate statistic, and must ship
   alongside it, not be buried under a single p-value.

## Power pre-commitment (mandatory, before data)

State before touching data: at *n*≈3-5, even a unanimous-direction result
across every episode may not clear a conventional significance threshold
(a perfect sign match at *n*=4 gives two-sided *p*=0.125; *n*=5 gives
*p*=0.0625). Declare in advance what a null or non-significant-but-unanimous
result means — per [model-acceptance-standard.md](model-acceptance-standard.md#power-pre-commitment),
`not evaluable`/`insufficient evidence`, never silently reframed as
`reject`. This track is expected to be underpowered by construction; that
is a property of the estimand's own sample, not a design flaw to fix by
adding daily granularity back in.

## What this does not replace

Materiality, cost realism, regime/sub-sample stability, and every other
Stage 9B evidence-gate clause still apply unchanged. Only the significance
mechanism differs from the block-bootstrap default.
