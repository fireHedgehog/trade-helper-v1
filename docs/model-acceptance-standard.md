# Model acceptance and candidate priority

Status: required Stage 9A gate; design work only until Stage 8 is complete and research is explicitly resumed.

## Purpose

No strategy is selected because it is familiar, recently discussed, popular, or attractive in an exploratory backtest. Stage 9A ranks candidates before their results are known and defines what evidence permits advancement. Passing permits further validation; it never means safe, proven, or approved for trading.

## Candidate scorecard

Record each item as `0` weak, `1` plausible, or `2` strong, with a short justification and cited evidence. Score before implementation.

| Dimension | Required question |
|---|---|
| Rationale | What behavioural, structural, or risk-premium mechanism could persist? |
| Product relevance | How could it improve Passive ETF-12 v1 after costs and risk? |
| Distinct information | What does it add beyond previously tested signals? |
| Data readiness | Is point-in-time, bias-controlled data available at the required resolution? |
| Implementability | Are timing, liquidity, turnover, costs, capacity, and portfolio constraints credible? |
| Falsifiability | What result would reject the idea, and can one finite experiment produce it? |
| Research restraint | Is the search family small enough to control multiplicity and preserve confirmation data? |
| Diversification | Could the return or risk pattern improve the portfolio rather than duplicate its exposure? |

Reject candidates with unavailable point-in-time data, an unfalsifiable rationale, unbounded search, or no credible implementation. Among eligible candidates, prefer the simpler and more independently testable design. The score ranks research effort; it does not estimate alpha. Macro candidates must additionally satisfy [ADR 0006](adr/0006-macro-data-contract.md) clauses 2–9 before scoring; without point-in-time vintage data the `Data readiness` score is `0` by construction.

## Required preregistration

Before computing comparative results, lock the hypothesis and failure mechanism; universe and provenance; primary benchmark and estimand; signal, fill, holding, and portfolio rules; parameter/search budget; trial-count budget $N_{\text{trials}}$; minimum detectable effect $\delta$ and target power $1-\beta$; costs and stress levels; walk-forward topology; dependence treatment; multiplicity policy; minimum information requirement; acceptance thresholds; and untouched confirmation data. Publish a fingerprint of the immutable specification.

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
- Comparison uses Passive ETF-12 v1; SPY and cash remain diagnostic references.
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

## Institutional verification layers

Mandatory reporting for any candidate reaching Stage 9B. Each layer removes one mechanism by which a false edge can survive a naive backtest.

### Trial-count deflation

The attempts ledger (`research/attempts.jsonl`) is the authoritative trial count $N_{\text{trials}}$ for a hypothesis family. Because the maximum observed statistic grows with the number of trials, apply selection-bias correction (Bailey & López de Prado, 2014). Under $N$ independent trials the expected maximum Sharpe is approximately

$$E[\max \widehat{SR}] \approx \sqrt{2 \ln N},$$

and the Deflated Sharpe Ratio is

$$\mathrm{DSR} = \Phi\!\left(\frac{(\widehat{SR} - SR_0)\sqrt{n-1}}{\sqrt{1 - \gamma_3\,\widehat{SR} + \frac{\gamma_4 - 1}{4}\,\widehat{SR}^2}}\right),$$

with $SR_0 = E[\max \widehat{SR}]$, and $\gamma_3$, $\gamma_4$ the skewness and excess kurtosis of the return series. Every logged variant must be counted; deleting or editing ledger entries to improve a statistic is contamination. When $N_{\text{trials}}$ is unreported, the result cannot claim adjusted significance. Treat $t < 3$ as weak (Harvey, Liu & Zhu, 2016); for many or correlated candidates prefer FDR control (Benjamini & Hochberg, 1995) or dependence-valid stepwise methods (Romano & Wolf, 2005).

### Backtest-overfitting diagnostics

Report the probability of backtest overfitting via combinatorially symmetric cross-validation (CSCV) over the walk-forward folds (Bailey, Borwein, López de Prado & Zhu, 2017), using the logit performance-degradation measure $\lambda$. A PBO estimate above the preregistered ceiling is grounds for `revise` regardless of headline performance.

### Power pre-commitment

Before evaluation, declare the minimum detectable effect $\delta$ and target power $1-\beta$ for the primary estimand. If the sample cannot deliver the declared power at the declared effect size, the preregistered outcome is `not evaluable` — never `reject` or `continue`. A "cash fallback / zero trades" outcome is `insufficient evidence`, not evidence of absence.

### Cost and capacity realism

Report gross-of-cost and net-of-cost performance, the break-even cost

$$c^* = \frac{\bar\alpha_{\text{gross}}}{\bar\tau},$$

where $\bar\alpha_{\text{gross}}$ is mean gross excess return and $\bar\tau$ is mean annual one-way turnover, and the capacity ceiling at which market impact erodes net edge to zero. The strategy is not institutionally viable if $c^*$ is below the locked cost model (ADR 0003) or if the capacity ceiling is below the intended research scale.

### Alpha decomposition

Report against the primary benchmark (Passive ETF-12 v1): active return, tracking error, and information ratio

$$\mathrm{IR} = \frac{\bar{r}_{\text{active}}}{\sigma(r_{\text{active}})},$$

plus the residual alpha $\hat\alpha$ from a factor regression of strategy excess returns on the benchmark and, where applicable, common factors. An edge claim requires residual alpha distinct from factor beta; outperformance fully explained by benchmark or factor exposure is not independent edge.

### Regime and sub-sample stability

Report the primary statistic split by regime (e.g. bull/bear, rate cycle, volatility regime) and by sub-sample, with a structural-break check (Chow, 1960; Bai–Perron, 1998). A result concentrated in one regime or unstable across sub-samples is `revise` or `reject` territory.

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
