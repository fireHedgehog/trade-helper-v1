# Daily Consolidation Zone v1 — draft research design

Status: design only; not preregistered, implemented, tuned, or validated. This document preserves the next research starting point without authorizing an experiment or UI signal.

## Scope and claim boundary

This programme asks whether objectively detected daily-price consolidation zones contain useful information about subsequent downside risk, forward return, or breakout continuation. It does not test genuine High Volume Nodes: daily Yahoo OHLCV reports total session volume, not volume-at-price. HVN research requires trustworthy intraday trade or volume-profile data.

Existing `S/R Bounce` is not evidence for or against this hypothesis. It uses rolling extremes, not consolidation detection.

## Economic hypotheses

Test independently; do not combine after observing results.

1. Zone support: after a completed consolidation, a later test-and-recovery of its lower zone boundary produces smaller forward maximum drawdown without materially reducing forward return versus matched observations.
2. Zone breakout: a qualified close above the upper zone boundary produces positive forward excess return versus constant exposure.
3. Failed breakout: a close back inside the zone after a qualified breakout predicts weaker forward return than breakouts that remain accepted above the zone.

The rationale is behavioural and microstructural but not assumed true: repeated transactions and attention may anchor participants to a price region; volatility compression may precede expansion; clustered orders may create temporary reactions. These mechanisms require empirical discrimination from ordinary trend and volatility effects.

## Detector available at close `t`

Use trailing data only. No pivot or zone may depend on bars after `t`.

For candidate window `W`, calculate:

- range width `R_t = (max(H_{t-W+1:t}) − min(L_{t-W+1:t})) / median(C_{t-W+1:t})`;
- ATR-normalised width `A_t = (max(H) − min(L)) / ATR_14,t`;
- realised-volatility ratio `V_t = σ(r_{t-W+1:t}) / σ(r_{t-2W+1:t-W})`;
- boundary-touch counts using a predeclared tolerance around upper and lower quantiles;
- time spent inside the candidate zone and maximum single-session gap.

A consolidation must satisfy locked thresholds for duration, normalised width, volatility compression, minimum touches, and containment. Zone boundaries should use predeclared robust quantiles or clustered confirmed pivots rather than hand-drawn lines. Candidate windows, thresholds, and tolerances form a finite search family and require multiplicity control.

## Events and timing

- Support recovery: session low intersects the lower zone and the completed close returns inside/above it.
- Breakout: completed close exceeds the upper zone by a locked percentage or ATR buffer; optional time/volume confirmation is a separate candidate family.
- Failed breakout: within a locked number of sessions, a completed close returns inside the old zone.
- Any executable entry generated at close `N` fills at next available open `N+1` under [ADR 0001](../adr/0001-execution-timing.md).

Stops are not “somewhere below support.” Competing stop families—failed-zone close, lower-zone buffer, confirmed swing support, or ATR distance—must be preregistered and tested as separate rules. Gap and cost assumptions follow existing ADRs.

## Staged evaluation

### A. Detector validation

Before P&L, audit zones visually on a blinded deterministic sample and quantify duration, width, touch count, overlap, asset concentration, and regime distribution. Reject detectors that label nearly all/no observations or encode look-ahead.

### B. Event study

For non-overlapping events, report 20- and 60-session forward return, maximum adverse excursion, maximum favourable excursion, and probability of zone violation. Compare with matched same-symbol observations conditioned on market trend, recent return, volatility, and calendar period. Cluster inference by symbol and calendar block.

### C. Executable strategy

Only if the event study survives its locked gate, simulate next-open entries, whole shares, costs, portfolio capacity, and passive benchmarks. Test zone-support and zone-breakout strategies separately. Evaluate return, drawdown/recovery, exposure, turnover, trade count, stability, and cost sensitivity.

## Data and universe

- Development: adjusted daily OHLCV under [ADR 0002](../adr/0002-market-data-contract.md), initially the locked long-lived ETF universe to limit current-constituent survivorship.
- Equity extension: requires a point-in-time universe including delisted/removed securities; the current 500-symbol list is unsuitable for a historical claim.
- Confirmation: genuinely future or independently point-in-time data untouched by detector/threshold selection.
- HVN extension: blocked until intraday volume-at-price provenance and corporate-action treatment are specified.

## Statistical controls

- Preregister finite detector and rule grids; fingerprint specification and data.
- Use purged/embargoed time-series folds because long windows and forward outcomes overlap.
- Control the family across windows, thresholds, filters, horizons, entry types, and stops.
- Use dependence-aware clustered or moving-block resampling; report effect sizes and intervals, not p-values alone.
- Run placebo zones and matched controls to distinguish the label from generic trend/low-volatility effects.
- Lock rejection, revision, and continuation gates after feasibility/power analysis but before outcome inspection.

## Required decisions before implementation

1. Primary hypothesis: support recovery or breakout.
2. Primary estimand and horizon.
3. Zone-boundary algorithm and detector grid.
4. Matched-control construction.
5. Search-family size and multiplicity method.
6. Portfolio benchmark and economically meaningful minimum effect.
7. Confirmation dataset and contamination boundary.

Until these are locked, the UI may show a `Consolidation Zone — research pending` placeholder but no entry marker, rank, confidence, or stop.

## Literature anchors

- Support/resistance definitions are qualitative and depend on prior bounces and time scale: [Scientific Reports, 2014](https://doi.org/10.1038/srep04487).
- Algorithmic zone construction can separate bounce frequency from profitable trading and expose analyst subjectivity: [Expert Systems with Applications, 2021](https://doi.org/10.1016/j.eswa.2021.115893).
- Data-snooping controls materially change which technical rules appear profitable: [Journal of Financial Econometrics, 2005](https://doi.org/10.1093/jjfinec/nbi026).
