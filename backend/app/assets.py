"""Small product-owned asset-role boundary for stored market symbols."""

MARKET_CONTEXT_SYMBOLS = frozenset({"GC=F", "CL=F", "^TNX"})

# FRED series are stored in the bars table (one value duplicated across
# open/high/low/close) for schema reuse, not because they are OHLC prices.
# Some series (e.g. GDP growth) are legitimately negative in a contraction.
FRED_MANAGED_SERIES = frozenset(
    {
        "DGS2",
        "DGS10",
        "DFEDTARU",
        "CPIAUCSL",
        "PCEPILFE",
        "PAYEMS",
        "UNRATE",
        "ICSA",
        "A191RL1Q225SBEA",
        "RSXFSN",
    }
)


def is_strategy_symbol(symbol: str) -> bool:
    """Only equity/ETF bars belong to the long-only strategy workspace."""
    return symbol not in MARKET_CONTEXT_SYMBOLS and symbol not in FRED_MANAGED_SERIES
