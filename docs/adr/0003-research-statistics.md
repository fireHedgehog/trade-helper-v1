# ADR 0003: Research statistics

Status: accepted; CTA v1 adds the stricter preregistration in [research-protocol.md](../research-protocol.md).

## Separate estimands

1. Trade performance: realized next-open strategy trades after costs.
2. Post-signal outcome: fixed 20-bar forward return after a signal.

These answer different questions and must not be pooled.

## Fixed assumptions

- Commission: `10 bp` per side.
- Quoted spread: `2 bp`; half-spread applied per fill.
- Slippage: `5 bp` per fill.
- Cash yield: `0` unless a versioned contract changes it.
- Reference exposure: constant exposure to the same adjusted asset series.

## Post-signal inference

Select observations at least 20 bars apart per symbol. Use `1,000` deterministic resamples clustered by calendar month. With fewer than three month clusters, report Wilson/normal approximations and a limitation. Flag `n < 30` as insufficient precision.

Report sample size, hit rate with interval, mean and median forward return, uncertainty method, and dependence limitations. Do not translate a p-value into the probability that a strategy is true.

## Consequences

Claims are conditional on timing, costs, universe, sampling, and dependence assumptions. Multiple candidate tests require an explicit family-wise error policy; CTA v1 uses Holm adjustment.
