# Factor zoo academic anomalies v1 — a different family, not more reversal variants

Status: screening scan, non-evidential — same standing as
[factor-zoo-v1](factor-zoo-v1.md). Deliberately a *different* factor
family from the reversal-shaped WQ101/classic-indicator cluster already
closed ([factor-zoo-cost-sensitivity-v1](factor-zoo-cost-sensitivity-v1.md)):
illiquidity, lottery-demand, low-volatility, liquidity-spread, and
skewness preference, each a distinct, real-citation economic story, not
five more reversal-effect variants.
Engine: [`factor_zoo.py`](../../backend/app/factor_zoo.py)
`ACADEMIC_ANOMALIES`. Run:
[`run_factor_zoo_academic_anomalies.py`](../../backend/app/run_factor_zoo_academic_anomalies.py).
Source survey:
[open-source-factor-source-backlog.md](../brainstorm/2026-08-21-open-source-factor-source-backlog.md).

## Method

Five factors, each with a real citation, evaluated with the same harness
and universe as factor-zoo-v1 (live rescan against current
`data/market.db`, same disclosed caveat): Amihud (2002) illiquidity, MAX
effect (Bali-Cakici-Whitelaw 2011), a low-volatility/Betting-Against-Beta
proxy (Blitz-van Vliet 2007 / Frazzini-Pedersen 2014, simplified to
realized volatility — no benchmark series for a true rolling beta), the
Corwin-Schultz (2012) high-low spread estimator, and an idiosyncratic
skewness proxy (Boyer-Mitton-Vorkink 2010's economic story via realized
skewness, not the paper's own fitted cross-sectional model).

`max_effect` and `expected_skewness_proxy` are expected to score a
**negative** IC-IR under this harness's "high reading = long" convention
— each paper's own predicted sign (lottery-demand overpricing), not a
misdirection the way the classic TA indicators needed correcting.

Orthogonality checked against each other plus `atr_normalized`
(factor-zoo-v1's one prior survivor), same `|r|≥0.5` rule already used
project-wide. The two non-redundant, non-null survivors (`amihud_illiquidity`,
and — checked as a matter of course — `max_effect` before its redundancy
was found) were also cost-checked at this project's standard 32bps
round-trip rate, same mechanism as
[factor-zoo-cost-sensitivity-v1](factor-zoo-cost-sensitivity-v1.md).

## Result

| Factor | IC-IR | Sharpe @0bps | Sharpe @32bps | Redundant with |
|---|---:|---:|---:|---|
| `low_volatility` | `0.015` | `0.78` | `0.27` | `atr_normalized` (`r=0.98`), `max_effect` (`r=0.88`) |
| `amihud_illiquidity` | `0.015` | `0.70` | `0.29` | none (`|r|<0.45` vs. all four others) |
| `max_effect` | `0.002` | `0.73` | `0.05` | `atr_normalized` (`r=0.81`), `low_volatility` (`r=0.88`) |
| `expected_skewness_proxy` | `-0.007` | `0.33` | not checked (near-null already) | none |
| `corwin_schultz_spread` | `-0.018` | `-0.005` | not checked (clean null already) | none |

Full numbers:
[academic-anomalies-report.json](../../output/research/factor-zoo-academic-anomalies-v1/academic-anomalies-report.json).

## Reading this result

**Two of five are the same effect wearing different formulas, not two new
findings.** `low_volatility` correlates `0.98` with `atr_normalized` —
essentially the same volatility-level information twice. `max_effect`
correlates `0.81`–`0.88` with both — a high-MAX stock is mechanically
often also a high-realized-volatility stock, so this "different" academic
anomaly turns out to be a third measurement of the same thing, not a new
one. Both facts only became visible by actually checking correlation, not
by trusting five different paper citations to mean five different
information sources — the exact gap between "many factors" and "real
breadth" this project's own orthogonality discipline exists to catch.

**`amihud_illiquidity` is the one genuinely new, still-alive finding
here.** Uncorrelated with everything else tested (`|r|<0.45` against all
four, including `atr_normalized`), and it degrades gracefully under this
project's standard transaction cost (`0.70→0.29`) the way a real,
slower-turnover factor is expected to — not the reversal cluster's
collapse-and-sign-flip. This is now a **second** surviving Chapter 4
candidate alongside `atr_normalized`, from a genuinely different economic
story (illiquidity premium, not volatility).

**The two remaining are honest nulls, not a methodology failure.**
`corwin_schultz_spread` and `expected_skewness_proxy` both score
essentially zero IC-IR (`-0.018`, `-0.007`) and (for spread) a
statistically-flat Sharpe (`-0.005`) — not evidence these effects are
fake in general (both are well-replicated in the literature elsewhere),
but evidence they carry little exploitable signal in this specific
universe/window/instrument set, at zero and clearly not worth a cost
check given the near-zero starting point.

**Consequence**: Chapter 4 now has two live, independently-sourced
candidates (`atr_normalized`, `amihud_illiquidity`), each needing its own
clause 1 (mechanism) and clause 2 (cross-validated point estimate +
uncertainty band) before a formal proposal — `amihud_illiquidity`'s own
regime-concentration check (ADR 0007 clause 5) is not yet run, named here
as the next step for it specifically.

[Chapter 4 index](../research-program.md) ·
[Factor zoo v1](factor-zoo-v1.md) ·
[Cost sensitivity v1](factor-zoo-cost-sensitivity-v1.md)
