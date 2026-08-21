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
}


# Tier B (ADR 0009): studies whose own locked protocol authorizes no cost,
# execution, or live position. Never eligible for STRATEGIES/live signals --
# adding one here is the entire onboarding step for a closed characterization
# result; it must never also appear in backend/app/strategies.py.
CHARACTERIZATION_STUDIES = {
    "cta-v2-pooled-trend-overlay": {
        "chapter": "1 §10",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/cta-v2-pooled-trend-overlay.md",
        "artifact": "output/research/cta-v2-pooled-trend-overlay/958a3c838778f32cfb562090309b21f42826394517f0f5f68020ac0067f2382e/variant-results.json",
    },
    "consolidation-support-feasibility-v1": {
        "chapter": "1 §2",
        "decision": "not_evaluable",
        "result_doc": "docs/research-results/consolidation-support-feasibility-v1.md",
        "artifact": None,
    },
    "ta-breakout-v1": {
        "chapter": "1 §5",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/ta-breakout-v1.md",
        "artifact": None,
    },
    "calendar-turn-of-month-v1": {
        "chapter": "1 §7",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/calendar-turn-of-month-v1.md",
        "artifact": None,
    },
    "calendar-day-of-week-v1": {
        "chapter": "1 §8",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/calendar-day-of-week-v1.md",
        "artifact": None,
    },
    "overnight-gap-continuation-v1": {
        "chapter": "1 §9",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/overnight-gap-continuation-v1.md",
        "artifact": None,
    },
    "etf12-cross-sectional-rotation-v1": {
        "chapter": "2 §1",
        "decision": "not_material_or_not_consistent",
        "result_doc": "docs/research-results/etf12-cross-sectional-rotation-v1.md",
        "artifact": None,
    },
    "cross-sectional-equity-momentum-feasibility-v1": {
        "chapter": "2 §2",
        "decision": "engine_feasible",
        "result_doc": "docs/research-results/cross-sectional-equity-momentum-feasibility-v1.md",
        "artifact": None,
    },
    "fed-put-yield-stress-precursor-v1": {
        "chapter": "3 §1",
        "decision": "not_evaluable",
        "result_doc": "docs/research-results/fed-put-yield-stress-precursor-v1.md",
        "artifact": None,
    },
    "fed-put-yield-stress-precursor-v2": {
        "chapter": "3 §2",
        "decision": "not_evaluable",
        "result_doc": "docs/research-results/fed-put-yield-stress-precursor-v2.md",
        "artifact": None,
    },
    "fed-put-yield-stress-precursor-v3": {
        "chapter": "3 §3",
        "decision": "not_evaluable",
        "result_doc": "docs/research-results/fed-put-yield-stress-precursor-v3.md",
        "artifact": None,
    },
    "cta-v2-chapter4-eligibility": {
        "chapter": "4 §1",
        "decision": "not_eligible",
        "result_doc": "docs/research-results/cta-v2-chapter4-eligibility.md",
        "artifact": None,
    },
    "wave-pull-chapter4-eligibility": {
        "chapter": "4 §2",
        "decision": "not_distinguishable_from_chance",
        "result_doc": "docs/research-results/wave-pull-chapter4-eligibility.md",
        "artifact": None,
    },
    "calendar-dow-chapter4-eligibility": {
        "chapter": "4 §3",
        "decision": "not_distinguishable_from_chance",
        "result_doc": "docs/research-results/calendar-dow-chapter4-eligibility.md",
        "artifact": None,
    },
    "chapter4-eligibility-calibration-v1": {
        "chapter": "4 §4",
        "decision": "methodology_validation",
        "result_doc": "docs/research-results/chapter4-eligibility-calibration-v1.md",
        "artifact": "output/research/chapter4-eligibility-calibration-v1/calibration-report.json",
    },
    "chapter4-orthogonality-v1": {
        "chapter": "4 §—",
        "decision": "methodology_measurement",
        "result_doc": "docs/research-results/chapter4-orthogonality-v1.md",
        "artifact": None,
    },
    "factor-zoo-v1": {
        "chapter": "4 §5",
        "decision": "screening_scan_non_evidential",
        "result_doc": "docs/research-results/factor-zoo-v1.md",
        "artifact": "output/research/factor-zoo-v1/scan-report.json",
    },
}


HYPOTHESES = {
    "CTA Trend": "A long-only breakout with a trend filter and volatility-scaled exit may improve benchmark-relative risk-adjusted outcomes after costs.",
    "SMA Cross": "A fast/slow moving-average state may provide a simple trend-following learning control.",
    "Donchian Trend": "A long-only channel breakout with channel and ATR exits may capture persistent trends.",
    "S/R Bounce": "A prior rolling support test followed by a close back above support may identify a repeatable next-open long entry.",
    "Fib Retrace": "A quantified retracement after an impulse may identify a repeatable next-open long entry.",
    "Wave Pull": "A quantified impulse and pullback sequence may identify a repeatable next-open long entry.",
    "RSI Reversion": "An oversold RSI state may identify a repeatable short-horizon long mean-reversion entry.",
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
    no live signal, no API route yet. Registry only until the Research
    Record surface named in ADR 0009's Consequences is built."""
    return [
        {"study_id": key, **deepcopy(value)}
        for key, value in CHARACTERIZATION_STUDIES.items()
    ]
