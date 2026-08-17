"""Canonical backtest runner: local bars -> trades -> marked-to-market metrics.

Usage (from backend/):
    python -m app.backtest SPY                    # SMA Cross on SPY
    python -m app.backtest SPY --strategy "SMA Cross"

Assumptions (see README "Trading ground rules"):
- cash $100k, commission 0.1% per side, signals execute at next bar's open.
"""
import argparse
import math
import sys

import pandas as pd

from .execution import metrics as execution_metrics
from .execution import simulate
from .store import load_bars
from .strategies import STRATEGIES, STRATEGY_PARAMS

CASH = 100_000
COMMISSION = 0.001  # 0.1% per side — deliberate, so results aren't fantasy
SPREAD = 0.0002  # 2 bps quoted spread; each fill pays half
SLIPPAGE = 0.0005  # 5 bps adverse movement per fill
ANNUAL_CASH_YIELD = 0.0  # configurable; zero is conservative and reproducible

METRICS = [
    "Start",
    "End",
    "Duration",
    "Exposure Time [%]",
    "Return [%]",
    "Buy & Hold Return [%]",
    "Exposure-Matched Benchmark [%]",
    "CAGR [%]",
    "Annual Volatility [%]",
    "Downside Deviation [%]",
    "Sortino Ratio",
    "Calmar Ratio",
    "Max. Drawdown [%]",
    "Max. Drawdown Duration [bars]",
    "Win Rate [%]",
    "Profit Factor",
    "Sharpe Ratio",
    "Expectancy [$]",
    "Expectancy [%]",
    "Annual Turnover [x]",
    "# Trades",
]


def to_ohlc(bars: pd.DataFrame) -> pd.DataFrame:
    """bars (our SQLite shape) -> backtesting.py expected DataFrame."""
    df = bars.copy()
    df = df.set_index(pd.to_datetime(df["date"]))
    df = df[["open", "high", "low", "close", "volume"]]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    return df


def _plain(value):
    """Convert numpy/timestamp values into plain JSON-friendly types."""
    if value is None or isinstance(value, (int, float, str, bool)):
        return None if isinstance(value, float) and math.isnan(value) else value
    if hasattr(value, "item"):  # numpy scalars
        item = value.item()
        return None if isinstance(item, float) and math.isnan(item) else item
    return str(value)


def backtest_payload(
    symbol: str,
    strategy_name: str,
    params: dict | None = None,
    start: str | None = None,
    end: str | None = None,
    commission: float = COMMISSION,
    spread: float = SPREAD,
    slippage: float = SLIPPAGE,
    annual_cash_yield: float = ANNUAL_CASH_YIELD,
) -> dict:
    """Full result: metrics + trades + equity curve — what the chart viewer renders.

    start/end slice the bars window (YYYY-MM-DD) so metrics reflect the selected regime.
    """
    bars = load_bars(symbol)
    if bars.empty:
        raise RuntimeError(f"no bars for {symbol} — run fetch first")
    if start:
        bars = bars[bars["date"] >= start]
    if end:
        bars = bars[bars["date"] <= end]
    return backtest_bars_payload(
        bars.reset_index(drop=True), symbol, strategy_name, params,
        commission=commission, spread=spread, slippage=slippage,
        annual_cash_yield=annual_cash_yield,
    )


def backtest_bars_payload(
    bars: pd.DataFrame,
    symbol: str,
    strategy_name: str,
    params: dict | None = None,
    *,
    commission: float = COMMISSION,
    spread: float = SPREAD,
    slippage: float = SLIPPAGE,
    annual_cash_yield: float = ANNUAL_CASH_YIELD,
) -> dict:
    """Run the canonical engine on supplied bars (I/O-free and testable)."""
    if len(bars) < 60:
        raise RuntimeError(f"window has only {len(bars)} bars — need at least 60")
    if strategy_name not in STRATEGIES:
        raise KeyError(strategy_name)
    resolved_params = {
        key: value["default"] for key, value in STRATEGY_PARAMS[strategy_name].items()
    }
    resolved_params.update(params or {})
    simulation = simulate(
        bars,
        strategy_name,
        resolved_params,
        initial_cash=CASH,
        commission=commission,
        spread=spread,
        slippage=slippage,
        annual_cash_yield=annual_cash_yield,
    )
    stats = execution_metrics(
        simulation, bars, CASH, annual_cash_yield=annual_cash_yield
    )
    metric_values = {metric: _plain(stats[metric]) for metric in METRICS if metric in stats}
    metric_values["Open Position"] = stats.get("Open Position", False)
    metric_values["Pending Order"] = stats.get("Pending Order")
    trades = [
        {
            "entry_date": trade["entry_date"],
            "entry_price": round(float(trade["entry_price"]), 2),
            "exit_date": trade["exit_date"],
            "exit_price": round(float(trade["exit_price"]), 2),
            "size": int(trade["size"]),
            "pnl": round(float(trade["pnl"]), 2),
            "return_pct": round(float(trade["return_pct"]), 2),
            "exit_reason": trade["exit_reason"],
        }
        for trade in simulation.trades
    ]
    step = max(1, len(simulation.equity) // 500)
    equity = [
        {"date": row["date"], "equity": round(float(row["equity"]), 2)}
        for row in simulation.equity[::step]
    ]
    open_position = None
    if simulation.position.state in {"long", "exit_pending"}:
        open_position = {
            "state": simulation.position.state,
            "entry_date": simulation.position.entry_date,
            "entry_price": round(float(simulation.position.entry_price), 2),
            "stop": round(float(simulation.position.stop), 2)
            if simulation.position.stop is not None
            else None,
            "target": round(float(simulation.position.target), 2)
            if simulation.position.target is not None
            else None,
            "pending_reason": simulation.position.pending_reason,
        }
    return {
        "symbol": symbol,
        "strategy": strategy_name,
        "metrics": metric_values,
        "trades": trades,
        "equity": equity,
        "open_position": open_position,
        "assumptions": {
            "initial_cash": CASH,
            "commission_per_side": commission,
            "quoted_spread": spread,
            "slippage_per_fill": slippage,
            "annual_cash_yield": annual_cash_yield,
            "signal_timing": "completed close",
            "fill_timing": "next available open",
            "stop_model": "close signal, next-open fill",
        },
    }


def run_backtest(
    symbol: str,
    strategy_name: str,
    params: dict | None = None,
    start: str | None = None,
    end: str | None = None,
) -> dict:
    return backtest_payload(symbol, strategy_name, params, start, end)["metrics"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a backtest from local bars")
    parser.add_argument("symbol", nargs="?", default="SPY")
    parser.add_argument("--strategy", default="SMA Cross", choices=list(STRATEGIES))
    parser.add_argument("--start", default=None, help="window start (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="window end (YYYY-MM-DD)")
    args = parser.parse_args()

    try:
        result = run_backtest(args.symbol, args.strategy, start=args.start, end=args.end)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(f"{args.symbol} — {args.strategy}")
    for key, value in result.items():
        print(f"  {key:<18} {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
