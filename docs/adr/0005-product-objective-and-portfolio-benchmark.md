# ADR 0005: Product objective and portfolio benchmark

Status: accepted with explicit limitations; Passive ETF-12 v1 implemented in `0.25.0`; suitability audit required before Stage 9B.

## Objective

The product is a local research decision assistant. Its business question is whether a strategy improves a feasible long-only portfolio relative to passive ownership after costs and risk, sufficiently to justify further research.

## Primary benchmark: Passive ETF-12 v1

- Locked 12-ETF universe defined by the active protocol.
- Initial equity `$100,000`; strict common sessions.
- Equal target weight `1/12` per asset.
- Establish at the first common open; rebalance annually at the first common-session open.
- Whole shares, adjusted prices, the same trading costs, residual cash, `T+1` sale proceeds, and zero cash yield as the strategy portfolio.
- No leverage, shorts, borrowing, or discretionary substitutions.

Changing universe, weighting, rebalance timing, costs, calendar, or cash treatment creates a new benchmark version.

## Rationale and limitations

ETF-12 is a reproducible, investable reference portfolio over the assets used by CTA v1. Equal weighting prevents one instrument from mechanically dominating that project-specific comparison and uses the same account mechanics as the strategy. It was not derived as an optimal allocation and is not claimed to represent the global market portfolio, the user's ideal strategic allocation, or an independently validated source of return.

Its limitations are material: overlapping broad and sector equity exposures, arbitrary `1/12` weights, inception-based selection of surviving ETFs, zero cash yield, and no explicit liability, tax, currency, or investor-risk objective. A benchmark does not need to demonstrate alpha or pass a strategy p-value; it must be specified in advance, investable, measurable, and appropriate for the decision being evaluated. Choosing a benchmark after seeing which one is easiest to beat is prohibited.

Before the first Stage 9B experiment, Stage 9A must audit:

- the business objective and risk budget the comparator represents;
- universe coverage, overlap, concentration, and point-in-time availability;
- weighting and rebalancing rationale;
- consistency with the candidate's investable opportunity set and trade expression;
- sensitivity to credible alternative passive comparators;
- whether ETF-12 remains primary or becomes a diagnostic reference for that protocol.

The research universe and benchmark are separate decisions. A candidate may require a different point-in-time universe or a versioned primary benchmark, but the change must be justified before results and ETF-12 retained as a diagnostic reference where comparable.

## Secondary references

SPY buy-and-hold and cash are diagnostic references for existing results. A future protocol may promote a better-matched comparator only through the pre-result suitability audit and a new versioned contract.

## Evaluation dimensions

- Return: total return and CAGR.
- Risk: maximum drawdown, recovery, and Calmar ratio.
- Implementation: exposure, turnover, costs, rejected orders, and cash drag.
- Evidence: trade count, uncertainty, stability across folds/assets/regimes, stress sensitivity, and multiplicity control.

## Consequences

A strategy is not useful merely because it is profitable or has lower drawdown. It must improve the locked objective with evidence strong enough for the declared research stage.

## Reference principle

CFA benchmark guidance describes useful benchmarks as unambiguous, investable, measurable, appropriate, specified in advance, and accountable. ETF-12 satisfies the mechanical criteria but its appropriateness remains conditional on the candidate and business objective; that is the purpose of the Stage 9A audit.

- CFA Institute, *Portfolio Performance Evaluation* curriculum summary (2020), benchmark validity criteria.
