# Model acceptance and candidate priority

Status: required Stage 9A gate; design work only until Stage 8 is complete and research is explicitly resumed.

## Purpose

No strategy is selected because it is familiar, recently discussed, popular, or attractive in an exploratory backtest. Stage 9A ranks candidates before their results are known and defines what evidence permits advancement. Passing permits further validation; it never means safe, proven, or approved for trading.

## Candidate scorecard

First complete the [hypothesis-engineering record](hypothesis-engineering.md). Then record each item as `0` weak, `1` plausible, or `2` strong, with a short justification and cited evidence. Score before implementation and comparative performance inspection.

| Dimension | Required question |
|---|---|
| Rationale | What behavioural, structural, or risk-premium mechanism could persist? |
| Product relevance | Which passive alternative matches the business objective, and how could the candidate improve it after costs and risk? |
| Distinct information | What does it add beyond previously tested signals? |
| Data readiness | Is point-in-time, bias-controlled data available at the required resolution? |
| Implementability | Are timing, liquidity, turnover, costs, capacity, and portfolio constraints credible? |
| Falsifiability | What result would reject the idea, and can one finite experiment produce it? |
| Research restraint | Is the search family small enough to control multiplicity and preserve confirmation data? |
| Diversification | Could the return or risk pattern improve the portfolio rather than duplicate its exposure? |

Reject candidates with unavailable point-in-time data, an unfalsifiable rationale, unbounded search, or no credible implementation. Among eligible candidates, prefer the simpler and more independently testable design. The score ranks research effort; it does not estimate alpha. Macro candidates must additionally satisfy [ADR 0006](adr/0006-macro-data-contract.md) clauses 2–9 before scoring; without point-in-time vintage data the `Data readiness` score is `0` by construction.

## Required preregistration

Before computing comparative results, lock the hypothesis and failure mechanism; universe and provenance; suitable primary benchmark and estimand; signal, fill, holding, and portfolio rules; parameter/search inventory; minimum detectable effect $\delta$ and target power $1-\beta$ where estimable; costs and stress levels; validation topology; dependence treatment; multiplicity policy; minimum information requirement; acceptance thresholds; and untouched confirmation data. Publish a fingerprint of the immutable specification.

Thresholds are model-specific and must be justified by the objective, expected payoff distribution, sample power, and implementation burden. There is no universal minimum Sharpe ratio, win rate, p-value, or maximum drawdown that validates every strategy.

## Evidence gate

### Research validity

- No look-ahead, survivorship, universe-selection, or execution-timing contamination.
- Sufficient independent observations and regimes for the declared inference.
- All attempted variants recorded; multiplicity and dependence handled as preregistered.
- Reproducible artifacts, data fingerprint, configuration, code version, and deterministic seed.

Any material failure invalidates the experiment; attractive performance cannot rescue it.

### Economic and implementation validity

- Net performance includes locked costs and adverse cost/slippage stress.
- Comparison uses a preregistered benchmark that passes the ADR 0005 suitability audit. Passive ETF-12 v1, SPY, and cash remain diagnostic references when comparable.
- Effect size is economically material, not merely statistically detectable.
- Results are not dominated by one asset, period, regime, or trade.
- Nearby admissible parameters and walk-forward folds show acceptable stability.
- Turnover, exposure, cash drag, concentration, liquidity, settlement, and rejected orders are reported.

### Risk and statistical evidence

Report total return, CAGR, volatility, Sharpe, Sortino, maximum drawdown, recovery duration, Calmar, downside/tail loss, win rate with payoff ratio, trade count, exposure, turnover, costs, fold/asset/regime dispersion, confidence intervals, adjusted significance, and sensitivity results. Interpret the metrics jointly:

- win rate without payoff ratio is not a profitability test;
- Sharpe can conceal skew, serial dependence, and tail loss;
- maximum drawdown is one realised path, not a future loss bound;
- a p-value is not the probability that a strategy is true;
- backtest significance is not permission to trade.

## Verification risks and method selection

Stage 9B must address each risk below, but the protocol chooses methods appropriate to its estimand, sample, and selection process. A method is not mandatory merely because it is sophisticated; justify use or non-use before results. For estimands with only a handful of dependent regime episodes rather than a large quasi-independent sample, see [Thesis Track](thesis-track-small-n.md) instead of the block-bootstrap default below.

### Trial-count deflation

The attempts ledger (`research/attempts.jsonl`) is the provenance index, not automatically the numerical trial count. Each attempt must record the number of variants, selection stages, shared data, and dependence group; amendments and audits are records but are not independent strategy trials. Construct a conservative trial inventory before choosing a correction.

Selection bias grows with the effective number and dispersion of tried strategies. Where Sharpe selection is the relevant process, estimate the Deflated Sharpe Ratio using the published Bailey–López de Prado procedure and the observed distribution/dependence of trials; do not substitute the rough independent-normal extreme-value mnemonic $\sqrt{2\ln N}$ as the binding null Sharpe. For hypothesis tests, use preregistered family-wise, false-discovery, or dependence-valid stepwise control appropriate to the family. Unreported searches preclude an adjusted-significance claim.

### Backtest-overfitting diagnostics

Use CSCV/PBO only when comparable strategy variants produce a suitable performance matrix and the recombination assumptions fit the design. Otherwise use nested or purged time-series validation, parameter-stability analysis, and an untouched confirmation set. The protocol must state which overfitting mechanism is being tested and why the selected diagnostic is valid; CSCV cannot be mechanically applied “over walk-forward folds.”

### Power pre-commitment

Before evaluation, declare the minimum economically relevant effect and assess prospective precision or power where a defensible sampling model exists. If the data cannot distinguish that effect, the outcome is `not evaluable` or `insufficient evidence`, never evidence of absence. A cash fallback/zero-trade path reports failure of the selection rule plus insufficient OOS performance information. CTA v1 retains its historical `reject` label because that consequence was locked before evaluation; future protocols use this clarified taxonomy.

### Cost and capacity realism

Report gross-of-cost and net-of-cost performance and, where turnover is well defined, the break-even cost

$$c^* = \frac{\bar\alpha_{\text{gross}}}{\bar\tau},$$

where $\bar\alpha_{\text{gross}}$ is mean gross excess return and $\bar\tau$ is mean annual one-way turnover. Estimate capacity only when volume, participation, instrument, and impact assumptions support it; otherwise report capacity as unmeasured and restrict the claim to the intended small research scale.

### Alpha decomposition

Report against the preregistered primary benchmark: active return, tracking error, and information ratio

$$\mathrm{IR} = \frac{\bar{r}_{\text{active}}}{\sigma(r_{\text{active}})},$$

plus exposure decomposition appropriate to the candidate. Factor regression is diagnostic when factors and sample size are defensible; it is not a universal proof of “true alpha.” Outperformance explained by an intended exposure may still be useful, but must not be described as independent alpha.

### Regime and sub-sample stability

Report chronological and economically justified sub-samples without inventing regimes after observing results. Apply formal break tests only when their model, breakpoint treatment, and sample size are suitable. Concentration in one regime limits the claim; it does not automatically reject a strategy whose hypothesis was explicitly regime-conditional.

### Exploratory (non-evidential) tier

Exploration is a separate, explicitly non-evidential layer. Its outputs carry no acceptance weight, never enter the candidate pipeline, and are logged in the attempts ledger with `exploratory` or `contaminated_exploratory` status. Only a preregistered Stage 9B result may produce `reject`, `revise`, or `continue research`. Quick screens may kill ideas cheaply; they cannot promote them.

**Estimation refinements.** Apply data-driven calibration: HAC automatic bandwidth with fixed-b critical values; bootstrap block length selected automatically; unknown-breakpoint tests when the break date is not fixed a priori. Central references in ADR 0006.

## Decisions

- `reject`: the locked claim fails or the experiment is invalid.
- `revise`: evidence exposes a new, independently motivated hypothesis; create a new version and new search budget.
- `continue research`: every preregistered gate passes; run the untouched confirmation test once.
- `eligible for operational validation`: confirmation passes; only then consider bounded paper trading to test data, state, and execution operations.

Paper trading does not prove alpha and zero losses are not an acceptance condition. Define a loss budget, observation horizon, reconciliation rules, and stop conditions before it begins. Live or broker-connected trading requires a separate decision and remains out of scope.

## Candidate-selection record

For each Stage 9 cycle, preserve the complete scored candidate table, conflicts of interest, rejected candidates and reasons, chosen candidate, preregistered protocol fingerprint, experiment ledger, decision, and links to immutable evidence. A later agent must be able to reconstruct what was known before results were observed.
