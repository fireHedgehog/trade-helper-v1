"""Versioned metadata for the data products and strategies already in use.

This is deliberately a small code-owned registry, not a universal research
ontology. New entries require a real ingestion path or executable strategy.
"""

from __future__ import annotations

from copy import deepcopy


DATASETS = {
    "yahoo-adjusted-daily-ohlcv-v1": {
        "name": "Yahoo adjusted daily OHLCV",
        "provider": "Yahoo Finance via yfinance",
        "information_class": "own/cross-asset market data",
        "schema_version": "bars-v1",
        "cadence": "US market session",
        "timezone": "exchange session; stored as YYYY-MM-DD",
        "point_in_time": "snapshot fingerprinted; provider revision history unavailable",
        "revision_policy": "full auto-adjusted history is republished; experiments bind the consumed snapshot fingerprint",
        "licence": "provider terms; local research use only",
        "research_use": "strategy bars and descriptive market context",
        "quality_state": "validated adjusted OHLCV; not execution-grade accounting",
        "freshness_rule": "latest expected completed US weekday session (holiday-aware calendar pending)",
    },
    "fred-final-revised-display-v1": {
        "name": "FRED final-revised display series",
        "provider": "Federal Reserve Bank of St. Louis FRED",
        "information_class": "macro and policy releases",
        "schema_version": "bars-compat-v1",
        "cadence": "varies by series",
        "timezone": "observation date only; release datetime not stored",
        "point_in_time": "no — final-revised values",
        "revision_policy": "current FRED history replaces prior displayed values; revision vintages are not retained",
        "licence": "source-specific FRED series terms",
        "research_use": "descriptive display only; prohibited from inference and signals under ADR 0006",
        "quality_state": "display-compatible values; not point-in-time research data",
        "freshness_rule": "provider/release-specific; market-session freshness does not apply",
    },
    "trading-economics-us-calendar-v1": {
        "name": "US macro release calendar",
        "provider": "Trading Economics public calendar page",
        "information_class": "macro release schedule and current forecast display",
        "schema_version": "macro-calendar-v1",
        "cadence": "external page; cached for six hours",
        "timezone": "provider display time; canonical timezone not persisted",
        "point_in_time": "no archived forecast history",
        "revision_policy": "not persisted; latest fetched page only",
        "licence": "provider terms; verify before operational use",
        "research_use": "descriptive upcoming-event display only",
        "quality_state": "best-effort scrape; absence or parsing failure is explicit",
        "freshness_rule": "six-hour in-process cache; not an authoritative as-of source",
    },
}


STRATEGIES = {
    "CTA Trend": {
        "strategy_id": "cta-trend",
        "type": "Time-Series",
        "version": "v1-rejected",
        "family": "time-series trend / breakout",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "rejected_v1",
            "label": "Rejected v1",
            "summary": "No CTA v1 validation survivor; retained for study, not recommendation.",
        },
    },
    "SMA Cross": {
        "strategy_id": "sma-cross",
        "type": "Time-Series",
        "version": "prototype-v1",
        "family": "time-series trend / moving average",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "not_material_or_not_consistent",
            "label": "Closed — not material or consistent",
            "summary": (
                "Chapter 1 §3: a volatility-only placebo matched or beat the "
                "SMA-state result on 12/12 assets — a fully explained confound, "
                "not an unconfirmed effect."
            ),
        },
    },
    "Donchian Trend": {
        "strategy_id": "donchian-trend",
        "type": "Time-Series",
        "version": "prototype-v1",
        "family": "time-series trend / breakout",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "unvalidated",
            "label": "Unvalidated",
            "summary": "Canonical mechanics exist; preregistered evidence gate pending.",
        },
    },
    "S/R Bounce": {
        "strategy_id": "support-resistance-bounce",
        "type": "Time-Series",
        "version": "prototype-v1",
        "family": "classical technical analysis / support-resistance",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "exploratory",
            "label": "Exploratory classical TA",
            "summary": "Quantified support/resistance prototype; no accepted edge claim.",
        },
    },
    "Fib Retrace": {
        "strategy_id": "fib-retrace",
        "type": "Time-Series",
        "version": "prototype-v1",
        "family": "classical technical analysis / retracement",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "exploratory_poor_result",
            "label": "Exploratory poor result",
            "summary": "Historical SPY prototype materially trailed buy-and-hold; no accepted edge claim.",
        },
    },
    "Wave Pull": {
        "strategy_id": "wave-pull",
        "type": "Time-Series",
        "version": "prototype-v1",
        "family": "price action / impulse-pullback",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "not_material_or_not_consistent",
            "label": "Closed — not material or consistent",
            "summary": (
                "Chapter 1 §6: clean null on the locked impulse-pullback "
                "construction. Chapter 4 rescore across all 12 assets found "
                "2/11 eligible, not distinguishable from calibrated chance "
                "(GLD/TLT remain clean candidates, not confirmed effects)."
            ),
        },
    },
    "RSI Reversion": {
        "strategy_id": "rsi-reversion",
        "type": "Time-Series",
        "version": "prototype-v1",
        "family": "time-series mean reversion",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "not_material_or_not_consistent",
            "label": "Closed — not material or consistent",
            "summary": (
                "Chapter 1 §4: a genuine power limitation (36-56 events/asset) "
                "-- the design could not have told either way, which is "
                "different from having shown the effect is small."
            ),
        },
    },
    "ATR Vol Premium": {
        "strategy_id": "atr-vol-premium",
        "type": "Time-Series",
        "version": "prototype-v1",
        "family": "time-series volatility premium",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "exploratory",
            "label": "Exploratory — own-history execution of a screened factor",
            "summary": (
                "Own-history, single-asset translation of factor-zoo-v1's "
                "cross-sectional atr_normalized finding (Sharpe 0.84, "
                "cost-checked and regime-checked clean, Chapter 4 Sec.5/Sec.5c) "
                "-- a new, independently-designed protocol, not a retry: no "
                "per-symbol entry/exit rule existed before this. No "
                "preregistered falsification experiment has run against this "
                "specific design yet."
            ),
        },
    },
}

# (decision, artifact) per strategy for research_contract below -- the real
# closed Chapter 1-4 verdict where one exists, "not evaluable" where no
# locked protocol has run yet. Kept separate from STRATEGIES/HYPOTHESES so
# each stays a plain description, not a derivation site (ADR 0009).
DECISIONS: dict[str, tuple[str, str | None]] = {
    "CTA Trend": ("rejected", "docs/research-results/cta-trend-wf-v1.md"),
    "SMA Cross": (
        "not_material_or_not_consistent",
        "docs/research-results/sma-cross-v1-exposure-reduction.md",
    ),
    "Donchian Trend": ("not evaluable", None),
    "S/R Bounce": ("not evaluable", None),
    "Fib Retrace": ("not evaluable", None),
    "Wave Pull": (
        "not_material_or_not_consistent",
        "docs/research-results/wave-pull-v1.md",
    ),
    "RSI Reversion": (
        "not_material_or_not_consistent",
        "docs/research-results/rsi-oversold-reversal-v1.md",
    ),
    "ATR Vol Premium": ("not evaluable", None),
}


# Professional taxonomy (docs/strategy-library.md "Type taxonomy"), exactly
# these three -- no fourth bucket. A methodology/meta-study (calibration,
# orthogonality) inherits its type from what it evaluates, not from its own
# machinery: both existing ones evaluate time-series Chapter 1 candidates,
# so both are "Time-Series".
STUDY_TYPES = {"Time-Series", "Cross-Sectional", "Macro"}

# Tier B (ADR 0009): studies whose own locked protocol authorizes no cost,
# execution, or live position. Never eligible for STRATEGIES/live signals --
# adding one here is the entire onboarding step for a closed characterization
# result; it must never also appear in backend/app/strategies.py.
#
# "type" (one of STUDY_TYPES): every entry has one, deferred or not --
# it is registry metadata, not a display-readiness gate. "name"/"summary"
# (docs/strategy-library.md Step 2b): human-facing fields for the Strategy
# Management record surface. Present only on studies actually onboarded
# there -- see DEFERRED_FROM_RECORD below for the ones intentionally left
# out for now, and why.
CHARACTERIZATION_STUDIES = {
    "cta-v2-pooled-trend-overlay": {
        "chapter": "1 §10",
        "type": "Time-Series",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/cta-v2-pooled-trend-overlay.md",
        "artifact": "output/research/cta-v2-pooled-trend-overlay/958a3c838778f32cfb562090309b21f42826394517f0f5f68020ac0067f2382e/variant-results.json",
        "name": "CTA v2 — Pooled Vol-Scaled Trend Overlay",
        "summary": (
            "Properly-powered pooled retest of CTA v1's own trend-following "
            "thesis across 12 instruments and the full sample; beats the "
            "benchmark and placebo on point estimate, but fails the "
            "bootstrap significance test and depends materially on 2008."
        ),
    },
    "consolidation-support-feasibility-v1": {
        "chapter": "1 §2",
        "type": "Time-Series",
        "decision": "not_evaluable",
        "result_doc": "docs/research-results/consolidation-support-feasibility-v1.md",
        "artifact": None,
        "name": "Consolidation Support-Recovery Feasibility",
        "summary": (
            "Not a rejection -- the locked comparison design could not "
            "construct an admissible matched-control set (0/274 events had "
            "3+ controls), so prospective power was never evaluated."
        ),
    },
    "ta-breakout-v1": {
        "chapter": "1 §5",
        "type": "Time-Series",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/ta-breakout-v1.md",
        "artifact": None,
        "name": "TA Breakout — Resistance Breakout vs. Placebo",
        "summary": (
            "Rejected-resistance breakout vs. a raw new-high placebo, "
            "1,477 events across 12 assets; 0/12 cleared materiality and "
            "significance after correction."
        ),
    },
    "calendar-turn-of-month-v1": {
        "chapter": "1 §7",
        "type": "Time-Series",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/calendar-turn-of-month-v1.md",
        "artifact": None,
        "name": "Calendar — Turn-of-Month Effect",
        "summary": (
            "Turn-of-month daily-return differential vs. a block-resampled "
            "null; 0/12 assets cleared materiality and significance "
            "together -- a mixed-sign, null result."
        ),
    },
    "calendar-day-of-week-v1": {
        "chapter": "1 §8",
        "type": "Time-Series",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/calendar-day-of-week-v1.md",
        "artifact": None,
        "name": "Calendar — Day-of-Week (Monday) Effect",
        "summary": (
            "Monday return differential vs. a block-resampled null; "
            "direction matched the literature (9/12 assets negative) but "
            "0/12 survived correction."
        ),
    },
    "overnight-gap-continuation-v1": {
        "chapter": "1 §9",
        "type": "Time-Series",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/overnight-gap-continuation-v1.md",
        "artifact": None,
        "name": "Overnight Gap Continuation",
        "summary": (
            "Tests whether an overnight gap continues into the next "
            "session -- the most decisive negative of its batch: 12/12 "
            "assets moved opposite the hypothesized direction."
        ),
    },
    "etf12-cross-sectional-rotation-v1": {
        "chapter": "2 §1",
        "type": "Cross-Sectional",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/etf12-cross-sectional-rotation-v1.md",
        "artifact": None,
        "name": "ETF-12 Cross-Sectional Rotation",
        "summary": (
            "Rank-continuation (relative-strength rotation) across the 12 "
            "locked ETFs; pooled rank correlation was small (0.045) and "
            "statistically unremarkable (p=0.266) -- the cleanest negative "
            "of its batch."
        ),
    },
    "cross-sectional-equity-momentum-feasibility-v1": {
        "chapter": "2 §2",
        "type": "Cross-Sectional",
        "decision": "engine_feasible",
        "result_doc": "docs/research-results/cross-sectional-equity-momentum-feasibility-v1.md",
        "artifact": None,
        "name": "Cross-Sectional Equity Momentum — Engine Feasibility",
        "summary": (
            "Not a claim about real momentum -- confirms the same "
            "rotation-testing engine proven at 12 ETFs also runs correctly "
            "at real 495-symbol equity scale, ahead of a properly disclosed "
            "confirmatory run."
        ),
    },
    "cta-v2-chapter4-eligibility": {
        "chapter": "4 §1",
        "type": "Time-Series",
        "decision": "not_eligible",
        "result_doc": "docs/research-results/cta-v2-chapter4-eligibility.md",
        "artifact": None,
        "name": "CTA v2 — Chapter 4 Eligibility Score",
        "summary": (
            "Sized under ADR 0007's looser one-sigma bar instead of a "
            "full-proof standard; the confidence interval still spans "
            "zero, so no position was sized."
        ),
    },
    "wave-pull-chapter4-eligibility": {
        "chapter": "4 §2",
        "type": "Time-Series",
        "decision": "not_distinguishable_from_chance",
        "result_doc": "docs/research-results/wave-pull-chapter4-eligibility.md",
        "artifact": None,
        "name": "Wave Pull — Chapter 4 Eligibility Score",
        "summary": (
            "Re-scored across all 12 assets (not just the pre-selected "
            "best one) to fix a winner's-curse critique; 2/11 eligible on "
            "paper, but the calibration study below shows that rate falls "
            "within pure-chance range."
        ),
    },
    "calendar-dow-chapter4-eligibility": {
        "chapter": "4 §3",
        "type": "Time-Series",
        "decision": "not_distinguishable_from_chance",
        "result_doc": "docs/research-results/calendar-dow-chapter4-eligibility.md",
        "artifact": None,
        "name": "Calendar Day-of-Week — Chapter 4 Eligibility Score",
        "summary": (
            "6/12 assets look eligible individually, but a "
            "correlation-aware joint-null test (accounting for overlap "
            "among the winners) puts the real chance of this at "
            "p≈0.13-0.14 -- not distinguishable from chance."
        ),
    },
    "factor-zoo-academic-anomalies-v1": {
        "chapter": "4 §5d",
        "type": "Cross-Sectional",
        "decision": "screening_scan_non_evidential",
        "result_doc": "docs/research-results/factor-zoo-academic-anomalies-v1.md",
        "artifact": "output/research/factor-zoo-academic-anomalies-v1/academic-anomalies-report.json",
        "name": "Factor Zoo — Academic Anomalies (Illiquidity, Lottery-Demand, Low-Vol, Spread, Skewness)",
        "summary": (
            "5 named academic anomalies, a different family from the "
            "reversal cluster. 2 of 5 (low_volatility, max_effect) turned "
            "out redundant with atr_normalized (r=0.81-0.98) -- same "
            "effect, different formula. amihud_illiquidity is genuinely "
            "independent and survives this project's standard "
            "transaction cost (Sharpe 0.70->0.29) -- a second live "
            "Chapter 4 candidate. corwin_schultz_spread and "
            "expected_skewness_proxy are clean, honest nulls."
        ),
    },
    "factor-zoo-regime-concentration-v1": {
        "chapter": "4 §5c",
        "type": "Cross-Sectional",
        "decision": "regime_concentration_clear",
        "result_doc": "docs/research-results/factor-zoo-regime-concentration-v1.md",
        "artifact": "output/research/factor-zoo-regime-concentration-v1/regime-concentration-report.json",
        "name": "Factor Zoo — Regime Concentration (atr_normalized)",
        "summary": (
            "ADR 0007 clause 5 check, same calculation as CTA v2's own "
            "closed result: unlike CTA v2 (where excluding 2008 flipped "
            "the sign), no single year's exclusion flips atr_normalized's "
            "positive mean across all 8 sample years -- clause 5 closed "
            "cleanly, clauses 1 and 2 remain before a Chapter 4 proposal."
        ),
    },
    "factor-zoo-cost-sensitivity-v1": {
        "chapter": "4 §5b",
        "type": "Cross-Sectional",
        "decision": "not_material_after_cost",
        "result_doc": "docs/research-results/factor-zoo-cost-sensitivity-v1.md",
        "artifact": "output/research/factor-zoo-cost-sensitivity-v1/cost-sensitivity-report.json",
        "name": "Factor Zoo — Cost Sensitivity (Reversal Cluster)",
        "summary": (
            "Charges this project's own standard round-trip cost on "
            "quintile turnover; every reversal-cluster factor "
            "(alpha034/033/009/028/004/026) flips to a deeply negative "
            "Sharpe -- confirms the bid-ask-bounce artifact by "
            "measurement. atr_normalized survives the same check, "
            "degrading mildly -- a second, independent confirmation "
            "beyond its earlier orthogonality check."
        ),
    },
    "chapter4-eligibility-calibration-v1": {
        "chapter": "4 §4",
        "type": "Time-Series",
        "decision": "methodology_validation",
        "result_doc": "docs/research-results/chapter4-eligibility-calibration-v1.md",
        "artifact": "output/research/chapter4-eligibility-calibration-v1/calibration-report.json",
        "name": "Chapter 4 Eligibility Rule — Calibration Check",
        "summary": (
            "Methodology check, not a strategy: measures the eligibility "
            "test's own false-positive rate on 300 synthetic null "
            "replications (16-19% false-eligible) -- answers an external "
            "critique by measurement instead of argument."
        ),
    },
    "chapter4-orthogonality-v1": {
        "chapter": "4 §—",
        "type": "Time-Series",
        "decision": "methodology_measurement",
        "result_doc": "docs/research-results/chapter4-orthogonality-v1.md",
        "artifact": None,
        "name": "Chapter 4 Orthogonality Screen",
        "summary": (
            "Methodology check, not a strategy: pairwise-correlates every "
            "nominally-eligible Chapter 4 signal; found 3 of 28 pairs "
            "materially redundant, mostly within Calendar Day-of-Week's "
            "own winners."
        ),
    },
    "factor-zoo-v1": {
        "chapter": "4 §5",
        "type": "Cross-Sectional",
        "decision": "screening_scan_non_evidential",
        "result_doc": "docs/research-results/factor-zoo-v1.md",
        "artifact": "output/research/factor-zoo-v1/scan-report.json",
    },
    "fed-put-yield-stress-precursor-v1": {
        "chapter": "3 §1",
        "type": "Macro",
        "decision": "not_evaluable",
        "result_doc": "docs/research-results/fed-put-yield-stress-precursor-v1.md",
        "artifact": None,
        "name": "Fed Put — Yield-Stress Precursor v1",
        "summary": (
            "Tests whether a yield-curve stress score rises before a Fed QE "
            "launch (4 episodes, 2008-2020); not evaluable (p=0.989) -- "
            "every real QE was preceded by a LOW score, the opposite of the "
            "hypothesis, not a null."
        ),
    },
    "fed-put-yield-stress-precursor-v2": {
        "chapter": "3 §2",
        "type": "Macro",
        "decision": "not_evaluable",
        "result_doc": "docs/research-results/fed-put-yield-stress-precursor-v2.md",
        "artifact": None,
        "name": "Fed Put — Yield-Stress Precursor v2",
        "summary": (
            "Same test extended to 6 episodes, including 2 actions the Fed "
            "itself did not brand \"QE\"; not evaluable (p=0.981) -- still "
            "6/6 opposite-signed, unchanged by the two additions."
        ),
    },
    "fed-put-yield-stress-precursor-v3": {
        "chapter": "3 §3",
        "type": "Macro",
        "decision": "not_evaluable",
        "result_doc": "docs/research-results/fed-put-yield-stress-precursor-v3.md",
        "artifact": None,
        "name": "Fed Put — Yield-Stress Precursor v3",
        "summary": (
            "Same 6 episodes rescored with a 20-year lookback instead of "
            "3-year; not evaluable (p=0.885) -- one episode (2025 RMP) "
            "flipped sign exactly as a disclosed structural note predicted, "
            "the other five did not."
        ),
    },
}

# User-directed (0.76.2): postponing macro ever meant postponing it from
# Today/Symbol Research/Strategy Lab -- those pages require a real,
# dense, per-day executable signal to draw chart markers against, and
# these precursor studies score a handful of discrete historical QE-launch
# episodes (4-6 across ~18 years), not a daily series -- there is nothing
# to mark on a daily chart, not a reason to hide the result. Strategy
# Management carries no such requirement, so all 3 Fed put studies are
# onboarded there now. Only factor-zoo-v1 (27-factor screen) stays
# deferred -- not yet clearly explained to the user, not a rejection.
# Revisit and give it "name"/"summary" plus drop it from this set when
# it's actually time.
DEFERRED_FROM_RECORD = {
    "factor-zoo-v1",
}

# GitHub blob base for Strategy Management's "source" links -- so a result
# doc is reachable even from a shared/deployed instance, not just a local
# checkout. Branch-relative (not commit-pinned) like every other in-repo
# doc cross-link; update if the repo ever moves or renames its default branch.
RESEARCH_REPO_BASE = "https://github.com/fireHedgehog/trade-helper-v1/blob/main"


HYPOTHESES = {
    "CTA Trend": "A long-only breakout with a trend filter and volatility-scaled exit may improve benchmark-relative risk-adjusted outcomes after costs.",
    "SMA Cross": "A fast/slow moving-average state may provide a simple trend-following learning control.",
    "Donchian Trend": "A long-only channel breakout with channel and ATR exits may capture persistent trends.",
    "S/R Bounce": "A prior rolling support test followed by a close back above support may identify a repeatable next-open long entry.",
    "Fib Retrace": "A quantified retracement after an impulse may identify a repeatable next-open long entry.",
    "Wave Pull": "A quantified impulse and pullback sequence may identify a repeatable next-open long entry.",
    "RSI Reversion": "An oversold RSI state may identify a repeatable short-horizon long mean-reversion entry.",
    "ATR Vol Premium": "A symbol's own volatility rising into the elevated end of its trailing range may identify a repeatable long entry, capturing the same volatility-premium effect factor-zoo-v1 found cross-sectionally.",
}


for _name, _metadata in STRATEGIES.items():
    _decision, _artifact = DECISIONS[_name]
    _metadata["research_contract"] = {
        "hypothesis": HYPOTHESES[_name],
        "execution": "completed close N signal; next available open N+1 fill",
        "scoreboard_benchmark": "same-symbol buy-and-hold median; descriptive comparison only",
        "validation_design": (
            "Locked walk-forward/significance record exists; the interactive "
            "scoreboard is not that experiment"
            if _artifact
            else "No preregistered validation experiment; interactive scoreboard is exploratory only"
        ),
        "decision": _decision,
        "artifact": _artifact,
    }


def dataset_for_provider(provider: str) -> str:
    if provider == "fred":
        return "fred-final-revised-display-v1"
    if provider == "yahoo":
        return "yahoo-adjusted-daily-ohlcv-v1"
    raise ValueError(f"unknown data provider: {provider}")


def dataset_registry() -> list[dict]:
    return [{"dataset_id": key, **deepcopy(value)} for key, value in DATASETS.items()]


def strategy_metadata(name: str) -> dict:
    return deepcopy(STRATEGIES[name])


def characterization_studies() -> list[dict]:
    """Tier B (ADR 0009): read-only, non-executable research studies --
    no live signal. Full registry, including entries deferred from the
    Strategy Management surface -- see research_record_entries()."""
    return [
        {"study_id": key, **deepcopy(value)}
        for key, value in CHARACTERIZATION_STUDIES.items()
    ]


def research_record_entries() -> list[dict]:
    """Strategy Management / Research Record surface (ADR 0009's named
    gap, docs/strategy-library.md Step 2b): every onboarded Tier B study
    -- excludes DEFERRED_FROM_RECORD -- with a ready-to-use github_url so
    the frontend never has to know the repo's shape."""
    return [
        {
            "study_id": key,
            "github_url": f"{RESEARCH_REPO_BASE}/{value['result_doc']}",
            **deepcopy(value),
        }
        for key, value in CHARACTERIZATION_STUDIES.items()
        if key not in DEFERRED_FROM_RECORD
    ]
