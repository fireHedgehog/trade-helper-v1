# 2026-08-19 — strategy taxonomy, benchmark questions, research tracks

> Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight. Distilled from an author–agent heuristic session; not a contract.

Working model recorded today: a two-class strategy taxonomy, the open benchmark/universe questions, and research-track ideas from the session. The taxonomy is a working frame for discussion, not a settled contract; every open item is written as a question.

## 1. Strategy taxonomy (working model)

### Class A — Price action

Input: daily OHLCV on the locked 12-ETF universe only; no orthogonal data.

**A1. Folk / traditional charting**
- In library: `S/R Bounce`, `Fib Retrace`, `Wave Pull` — all placeholders, no accepted edge claim.
- Evidence base: weak-to-mixed; data-snooping risk (2005 JFE reference in repo).
- Open: can any folk pattern be given a testable mechanism, or are these permanently placeholders? Should folk entries stay labelled non-signal in the UI?

**A2. Mechanism-backed / journal-published**
- Time-series momentum / trend — `CTA v1` fully tested, rejected on this bar; `Donchian Trend`, `SMA Cross` are trend-family placeholders.
- Cross-sectional momentum / rotation — not yet implemented; mechanism distinct from CTA's absolute time-series trend.
- Volatility-managed / risk-scaled exposure — not yet implemented; pure price, low cost.
- Reversal / mean reversion — `RSI Reversion` in library, not validated.
- Open: is the evidence-ordered priority (rotation > vol-managed > consolidation-zone v1 > reversal) right? Does a 12-ETF universe have enough breadth for cross-sectional rotation to be testable at all?

### Class B — Orthogonal-data thesis

Input: data beyond OHLCV. Pending until the relevant data class is acquired.

**B1. Continuous data streams**
- Examples: oil price, US10Y yield, CDS spreads, FRED macro series.
- Shape: bar-like daily feeds; still need vintage/data-contract discipline (ADR 0006-class).
- Open: which series justify acquisition first? Does the existing FRED pipeline already cover some of them?

**B2. Non-continuous PIT data**
- Examples: financial statements (quarterly, restated, breakpoint-stamped), consensus estimates.
- Shape: discrete, event-stamped; requires true PIT vintage handling; the harder class.
- Open: which thesis ideas map to which data class, and which justify the cost? Is B2 realistic at individual scale, or is B1 the achievable first step?

## 2. Benchmark & universe — open questions

- Why is the benchmark Passive ETF-12 v1? Was the benchmark itself validated, or inherited? Which hypothesis does it serve — is there an unanswered hypothesis behind the choice?
- Is 12-ETF concentration a defect or a feature? Is there any test that answers this, or only opinion?
- What does the cash-fallback fold design do to the evidence — correct semantics, or silent deflation/inflation?
- Which hypotheses in the universe audit remain unanswered, and which are we not even asking?

## 3. Research-track ideas from the session (candidates to improve the APP)

- **Operationalization layer.** Between brainstorm and 9A: `Claim / Mechanism / Market-belief proxy / Reality proxy / Gap / Falsifier`. 9A should judge an already-operationalized hypothesis, not convert natural language into a formula. SMA Cross and Burry-style ideas can share the same 9A with very different hypothesis-engineering difficulty.
- **Thesis Track.** For sparse, event-driven ideas (n ≈ 17, not n ≈ 5,000): preregistered immutable thesis record — timestamp, what market believes, what I believe, why different, what must happen, falsifier, horizon, trade expression, maximum acceptable loss. Immutable; amendments only, and an amendment pollutes the original. No bootstrap/Holm significance is claimed on such samples.
- **Generalization rule.** Test the generalized claim, not the single observation: "when market-implied 5Y growth exceeds a PIT estimate by >Xσ, subsequent returns deteriorate" — not "NVDA is overpriced." This is the bridge that lets a thesis eventually enter the systematic machine.
- **Alpha ≠ trade expression.** Separate layers: thesis → valuation/probability → expression → risk. The same thesis can be expressed as short stock / put / put-spread / relative trade / no trade; expression choice changes timing and path.
- **Machine philosophy.** The machine does not require every edge to be algorithmic; it requires every capital decision to be falsifiable. Human generates thesis → machine forces discipline (guards against "I meant that all along" memory rewriting).
- **Mechanism trap (H1–H5).** "Low PE" can be temporary-shock overreaction, underestimated recovery, forced selling, valuation-dispersion mean reversion, or permanent deterioration — five mechanisms, five measurements. Observable-first factor backtests cannot tell which mechanism is being tested.
- **Edge-persistence question.** "Why has this edge not been arbitraged away?" is the real test. Answers like career risk, leverage/shorting constraints, capacity, or long holding periods make an edge durable even when widely known (Burry's 2005 CDS: public data, different inference). Trade edges decay; edge-generation processes can persist.

## 4. Author state

- Bottleneck: running any existing placeholder is unlikely to win — none has an accepted edge claim; the only fully executed candidate (CTA v1) was rejected. Open: is this a calibration or a bias? Would one cheap candidate change the estimate, and would the answer be accepted either way?

## Promotion status

- None promoted. This memo is non-evidential; if any question matures into a hypothesis: exploration-protocol → 9A → preregistration → 9B.
