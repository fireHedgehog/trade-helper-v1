# Policy exposure / industrial-policy factor

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.
> Distilled from an external note (2026-08-20). Explicitly idea-stage —
> "not even memo yet" in the user's own words; captured here only so it
> isn't lost, not to advance it. Motivating example: CHIPS Act 2024 →
> Intel's market value roughly doubled — development/motivation evidence
> only, never confirmation (rule below).

## Reframing

Not: "government supported firm X, X later rose" (one anecdote). Instead:

$$PolicyShock_t + FirmExposure_{i,t} \rightarrow RelativeReturn_{i,t:t+h}$$

— a cross-sectional event-study factor, same "change the estimand, not
the trigger" discipline as the [cross-sectional
library](2026-08-20-cross-sectional-experiment-ideas.md).

## Core pieces

- **Exposure, continuous not binary**: `Grant+TaxCredit+ContractValue /
  MarketCap` (or `/EnterpriseValue`) — proportional shock, not raw
  dollars ($5B/$30B firm ≠ $5B/$2T firm).
- **Surprise over level**: `PolicySurprise = RealizedPolicy -
  ExpectedPolicy`, same logic as earnings surprise — a large but fully
  anticipated policy may move nothing.
- **Diffusion tiers**: direct beneficiary → tier-1 supplier → tier-2 →
  unrelated control. Hypothesis: $CAR_{direct} > CAR_{tier1} >
  CAR_{tier2}$, or the inverse (market misallocates first, diffuses
  later) — a policy-flavored lead-lag/diffusion design, same shape as
  [CS-08 leadership diffusion](2026-08-20-cross-sectional-experiment-ideas.md).
- **Multi-stage timing**: proposal → legislative approval → award →
  funding agreement → disbursement → milestone. Which stage actually
  carries the information? Not assumable, testable.
- **Industrial-policy put**: does strategic importance (semiconductors,
  defense, grid, critical minerals) itself lower left-tail risk or
  improve financing access — a persistent state variable, not an event
  trade.
- **Price-confirmation interaction**: $E[R\mid PolicyHigh,MomentumHigh]$
  vs. $E[R\mid PolicyHigh,MomentumLow]$ — does price already confirming
  the policy narrative predict continuation, or does weak confirmation
  mean underreaction? Direction must be preregistered, not picked after.

## The sharpest catch in the source note: policy endogeneity

Government intervention is not random — reverse causality is the live
risk: `PoorCompanyCondition → GovernmentSupport`, not
`GovernmentSupport → PoorReturns`, can produce the same observed
correlation. Needs matched controls / pre-trend matching / diff-in-diff,
not a bare event study. This is the mechanism-validity risk to solve
first, before any exposure-scoring work.

## Hypothesis family (H1-H6 in the source note)

Direct repricing (`CAR ~ Exposure`); exposure intensity (`CAR ~
SupportIntensity`); surprise dominance (surprise explains more variance
than raw size); supply-chain diffusion (tiered spillover); price
confirmation (policy × momentum interaction); strategic downside
protection (`StrategicImportance → DownsideRisk↓`). Each needs its own
protocol, falsifier, confirmation set — not one bundled "policy trade"
claim.

## Scope note (user-directed, 2026-08-20)

Deliberately excludes Treasury/fiscal policy generally and "leader
announcements" specifically — not gated by any ADR, just not yet a formed
idea. Distinct from [Fed
put](2026-08-19-fed-put-long-end-reversal.md), which is Fed/monetary
policy only (an independent agency, unlike fiscal policy which swings
with the administration).

## Governance rule from the source note, worth keeping verbatim

> Historical examples that inspired the hypothesis must not silently
> become confirmation evidence.

CHIPS Act/Intel is hypothesis-generation evidence. A real test needs
multiple events, multiple firms, explicit controls — this project's own
no-touch rule, restated for policy events specifically.
