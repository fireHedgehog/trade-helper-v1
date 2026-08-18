"""Explicit first portfolio universe and risk classifications.

Membership matches the locked CTA Trend v1 research universe. Classifications
are operational risk labels, not data-derived features and not tuned groupings.
"""

from __future__ import annotations

from .portfolio_execution import AssetClassification


PORTFOLIO_UNIVERSE_ID = "locked-etf-12-v1"
PORTFOLIO_COMMON_START = "2006-02-06"

PORTFOLIO_CLASSIFICATIONS = {
    "SPY": AssetClassification("Broad US equity", "US equity"),
    "QQQ": AssetClassification("US growth equity", "US equity"),
    "IWM": AssetClassification("US small-cap equity", "US equity"),
    "EFA": AssetClassification("Developed ex-US equity", "International equity"),
    "EEM": AssetClassification("Emerging-market equity", "International equity"),
    "TLT": AssetClassification("US Treasury", "Long-duration Treasury"),
    "IEF": AssetClassification("US Treasury", "Intermediate Treasury"),
    "GLD": AssetClassification("Precious metals", "Gold"),
    "DBC": AssetClassification("Broad commodities", "Commodities"),
    "XLK": AssetClassification("Technology equity", "US equity"),
    "XLF": AssetClassification("Financial equity", "US equity"),
    "XLE": AssetClassification("Energy equity", "US equity"),
}

PORTFOLIO_SYMBOLS = tuple(PORTFOLIO_CLASSIFICATIONS)
