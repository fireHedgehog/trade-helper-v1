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
            "status": "baseline_only",
            "label": "Baseline only",
            "summary": "Learning control; no accepted portfolio edge claim.",
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
            "status": "unvalidated",
            "label": "Unvalidated",
            "summary": "Prototype mechanics exist; independent research evidence pending.",
        },
    },
    "RSI Reversion": {
        "strategy_id": "rsi-reversion",
        "version": "prototype-v1",
        "family": "time-series mean reversion",
        "information_profile": ["own-asset market data"],
        "required_datasets": ["yahoo-adjusted-daily-ohlcv-v1"],
        "evidence": {
            "status": "unvalidated",
            "label": "Unvalidated",
            "summary": "No protective-stop portfolio contract or accepted validation.",
        },
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
    _is_locked_cta = _name == "CTA Trend"
    _metadata["research_contract"] = {
        "hypothesis": HYPOTHESES[_name],
        "execution": "completed close N signal; next available open N+1 fill",
        "scoreboard_benchmark": "same-symbol buy-and-hold median; descriptive comparison only",
        "validation_design": (
            "Locked CTA v1 walk-forward record; the interactive scoreboard is not that experiment"
            if _is_locked_cta
            else "No preregistered validation experiment; interactive scoreboard is exploratory only"
        ),
        "decision": "rejected" if _is_locked_cta else "not evaluable",
        "artifact": (
            "docs/research-results/cta-trend-wf-v1.md" if _is_locked_cta else None
        ),
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
