# CTA trend walk-forward v1: methodology audit

Audit date: `2026-08-18`. Conclusion: no material implementation defect found; rejection stands.

## Reproduction

- Experiment fingerprint: `40a79707811b6d13f92fa88a87a9e5251a72d0d5ffa58a2709e027f7bbc0bafd`.
- Cache artifacts: `756`.
- Independent rerun produced byte-identical evidence.
- Evidence SHA-256: `d82a251e6abcab363667b543ab2dabc5e70ae3fe62294ec597896e828c61f2e8`.

## Strongest observed validation candidate

Fold 14, validation `2022-02-10` through `2023-02-10`: entry lookback `100`, exit lookback `40`, trend MA `200`, ATR period `14`, ATR multiple `3`, no take-profit.

| Quantity | Independently reproduced value |
|---|---:|
| Daily observations | `252` |
| Maximum series difference | `0` |
| Mean daily excess return | `0.0000662497895997702` |
| Median cumulative symbol excess | `0` |
| Closed trades | `8` |
| Raw p-value | `0.2513497300539892` |
| Bootstrap-null standard deviation | `0.00010586` |
| Holm-adjusted p-value | `1.0` |

Ten of 14 folds had no candidate with positive mean validation excess. Fold 2 had one; folds 4, 12, and 14 had `10/54`, `10/54`, and `31/54`, respectively. Candidate exposure ranged approximately `6%–62%`; closed trades ranged `8–36` per candidate/fold. Thus the engine did trade, but observed advantages were weak and non-robust after multiplicity control.

## Scope

The audit checked calendar separation, candidate enumeration, excess-return construction, bootstrap determinism, Holm correction, fallback behaviour, and artifact identity. It supports the narrow conclusion that this long-only ETF CTA experiment was insufficient. It does not imply that institutional CTA, diversified futures trend following, or every trend specification underperforms.
