"""Small product-owned asset-role boundary for stored market symbols."""

MARKET_CONTEXT_SYMBOLS = frozenset({"GC=F", "CL=F", "^TNX"})


def is_strategy_symbol(symbol: str) -> bool:
    """Only equity/ETF bars belong to the long-only strategy workspace."""
    return symbol not in MARKET_CONTEXT_SYMBOLS
