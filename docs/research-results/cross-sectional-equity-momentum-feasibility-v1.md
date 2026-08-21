# Cross-sectional equity momentum feasibility v1

Decision: **`engine_feasible`**. This is not a claim about real
cross-sectional equity momentum — see the [locked
protocol](../research-protocols/cross-sectional-equity-momentum-feasibility-v1.md)'s
section 1 for the two independent, disclosed reasons this run cannot be
confirmatory (survivorship bias; a pre-lock parameter peek). It answers one
question only: does `etf12_rotation_bootstrap` — proven at `N=12` for ETF-12
rotation — also run correctly at real equity scale? Yes.

Specification SHA-256:
`482b84aef0479dff15b2ac489a82ab9cf542d9c59fe23bc82f9cca0fbc03f9b4`.
Data SHA-256:
`9085eaa5e1b1ffd45fa6b74bb41f3eaa3da8e82699964a640df40f3872c2db3e`.

## Result

| Check | Observation | State |
|---|---:|---|
| `rebalance_date_count > 0` | `85` | Pass |
| `observed_correlation` finite | `-0.0093` | Pass |
| `p_value` finite, in `[0,1]` | `0.9665` | Pass |
| all `2,000` resamples complete | yes | Pass |

Universe: `495` symbols (S&P 500 ∪ Nasdaq-100 ∪ 11 XL sector ETFs,
intersected with what `data/market.db` holds, restricted to symbols with a
first stored date on or before `2019-01-01` — see the protocol's section 3
for the exact `34` exclusions). Common date range: `2019-01-01` to
`2026-08-14` (`1,913` sessions, true set-intersection of trading dates, not
a min/max range). `126`-session formation, `21`-session holding, `21`-session
rebalance spacing.

**`engine_feasible`**: the panel-bootstrap engine scaled from `N=12` to
`N=495` — a `~41×` increase — with no code change beyond generalizing the
data-loading step (the bootstrap function itself, `etf12_rotation_bootstrap`,
was already asset-count-agnostic; nothing in it referenced 12 explicitly).
Wall-clock for `2,000` resamples: under two minutes.

The raw `observed_correlation` (`-0.0093`) and `p_value` (`0.9665`) are
recorded for transparency only. Per the protocol's forbidden-outputs list,
neither this document nor any future one may cite them as evidence for or
against real cross-sectional equity momentum: the universe is
survivorship-biased (today's index membership applied to 2019–2026
history), and a disclosed pre-lock timing probe already observed this
panel's correlation once under different (module-default) parameters
before any specification was locked. Both independently void confirmatory
status regardless of what number came out.

**Update, `0.81.0`**: CS-01's Tier 4 blocker no longer needed the assumed
vendor purchase — a free point-in-time membership source exists
([`universe_pit.py`](../../backend/app/universe_pit.py)). CS-01 itself has
since been executed as a real confirmatory attempt and closed
`not_material_or_not_consistent` — see
[cross-sectional-momentum-v1.md](cross-sectional-momentum-v1.md). CS-02/03/04/05/09
remain open.

## What this does and does not unblock

Does: proves the mechanical piece of the [cross-sectional idea
library](../brainstorm/2026-08-20-cross-sectional-experiment-ideas.md)'s
six breadth-dependent ideas (CS-01/02/03/04/05/09) works at real scale,
without waiting on the Tier 4 vendor-data decision. Does not: authorize any
of them as a Stage 9A candidate, substitute for point-in-time
survivorship-free universe data, or establish a sector/industry breadth
gate (none exists for equities in this codebase — see protocol section 3).
The next step for any real cross-sectional equity candidate is unchanged:
hypothesis-engineering note → Stage 9A score → preregistration, and
separately, the Tier 4 data purchase or an accepted survivorship-bias
caveat strong enough to survive that scoring.

## Reproducibility

- Manifest, rebalance-results, and decision artifacts:
  `output/research/cross-sectional-equity-momentum-feasibility-v1/482b84aef0479dff15b2ac489a82ab9cf542d9c59fe23bc82f9cca0fbc03f9b4/`.
- No trade, no cost, no position, no sleeve, no sharpe — forbidden outputs
  per the locked spec, none produced.

[Protocol](../research-protocols/cross-sectional-equity-momentum-feasibility-v1.md)
· [Machine specification](../../research/experiments/cross-sectional-equity-momentum-feasibility-v1.json)
· [Artifact README](../../output/research/README.md)
