# Macro reaction-function narrative library (beyond "Fed put")

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.
> Distinct from, and broader than, [fed-put-long-end-reversal.md](2026-08-19-fed-put-long-end-reversal.md)
> (one narrow, already-scoped instance: purchase-flow-conditioned yield
> reversal) and [long-end-yield-shock.md](2026-08-19-long-end-yield-shock.md)
> (yield shocks breaking equity trend entries). This note is the wider
> family both of those sit inside.

## You don't need to resolve whether the put "really exists"

The stuck point — "I was not even sure if the put real exist... CPI 2% can
be postponed, does not mean they forget their faithful discipline" — is a
claim about Fed *intent*, which is exactly what the existing Fed-put memo
already excludes ("explicitly out: any claim about a specific Fed chair's
intentions... discretionary narrative, not a quantifiable input"). The good
news: intent doesn't need to be resolved to make this testable. The
mechanical channel is well-established finance theory with a name —
**equity duration**: growth stocks are long-dated cash-flow claims, so their
present value is mechanically more sensitive to the discount rate (real
yield) than a short-duration value stock's is, regardless of *why* the rate
moved (Dechow, Sloan & Soliman 2004; Weber 2018, "Cash Flow Duration and the
Term Structure of Equity Returns"). That's the formal version of "DFC
squish the edge of all delta growth" — a real, citable mechanism, not a
folk pattern.

## The state-variable set (all free)

| Variable | Free source | What narrative it quantifies |
|---|---|---|
| Real yield (10Y TIPS) / breakeven inflation | FRED (`DFII10`, `T10YIE`) | The actual DCF discount rate — the equity-duration channel above |
| Yield curve slope (2s10s or 3m10y) | FRED | Recession-risk regime (Estrella & Mishkin 1998) |
| Credit stress (HY OAS, Chicago Fed NFCI) | FRED | "How much stress before the Fed acts" |
| Gold | Yahoo (already fetchable) | Real-rate proxy and currency-debasement/credibility signal — your "Fed incompetency trade" (Erb & Harvey 2013, "The Golden Dilemma": gold moves inversely with real rates) |
| Oil (WTI/Brent) | FRED | Classic supply-shock-to-recession-risk channel (Hamilton) |
| DXY | Yahoo (already fetchable) | Global financial-conditions tightening proxy |
| Fed funds rate vs. Taylor-rule-implied rate | FRED (funds rate, CPI, unemployment) | Formalizes "CPI 2% can be postponed" as a measured gap, not a vibe — how far actual policy sits from a mechanical dual-mandate rule, with no claim about why |

## The naming discipline this needs before anything is a candidate

Same rule as the [cross-sectional idea library](2026-08-20-cross-sectional-experiment-ideas.md):
change the estimand, name it, then it's a candidate. A usable form of each
row above still needs its own $H_0$/$H_1$ pair, same shape as the existing
Fed-put and yield-shock memos — this note only supplies vocabulary and
literature, it does not promote anything. One real distinction to carry
into that step, per [ADR 0006](../adr/0006-macro-data-contract.md) clause
5: a **level** claim ("real yield's current value predicts growth/value
spread") is the strong, less-plausible-if-markets-are-efficient form; a
**surprise** claim ("unexpected CPI/NFP print moves it") is more
defensible but needs a consensus-forecast history to compute the surprise
— and consensus estimates are typically a paid feed (Bloomberg/Refinitiv).
The Philly Fed Survey of Professional Forecasters is a free but coarse
(quarterly) substitute; not resolved here, flagged for whoever formalizes
the first surprise-based candidate.

## The shared blocker — closed 2026-08-20, engineering only

[ADR 0006](../adr/0006-macro-data-contract.md) clauses 2-4 (ALFRED
point-in-time vintage ingestion) are now implemented and live-verified
(`app.macro_pit`, `0.60.0`/`0.61.0`) — the engineering gap every row here
shared is closed. This authorizes none of them: each still needs its own
$H_0$/$H_1$ pair, hypothesis-engineering record, and Stage 9A score
before any signal use. [Fed put](2026-08-19-fed-put-long-end-reversal.md)
(a related but distinct SOMA-holdings-precursor claim, not one of the 7
rows above) has since run through this path 3 times and closed
`not_evaluable` — real precedent for the discipline, not a result about
any of these 7 variables specifically.

## Not scored, not authorized

Nothing here has been through hypothesis engineering, the Stage 9A
scorecard, or preregistration. It broadens what "Fed put" was pointing at;
it does not replace the existing scoped memo, and it doesn't pick a winner
among these seven variables.
