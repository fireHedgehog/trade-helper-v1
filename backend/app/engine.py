"""Minimal backtest runner: local bars -> trades -> metrics (via backtesting.py).

Usage (from backend/):
    python -m app.backtest SPY                    # SMA Cross on SPY
    python -m app.backtest SPY --strategy "SMA Cross"

Assumptions (see README "Trading ground rules"):
- cash $100k, commission 0.1% per side, signals execute at next bar's open.
"""
import argparse
import sys

import pandas as pd
from backtesting import Backtest

from .store import load_bars
from .strategies import STRATEGIES

CASH = 100_000
COMMISSION = 0.001  # 0.1% per side — deliberate, so results aren't fantasy

METRICS = [
    "Start",
    "End",
    "Duration",
    "Exposure Time [%]",
    "Return [%]",
    "Buy & Hold Return [%]",
    "Max. Drawdown [%]",
    "Win Rate [%]",
    "Profit Factor",
    "Sharpe Ratio",
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
        return value
    if hasattr(value, "item"):  # numpy scalars
        return value.item()
    return str(value)


def backtest_payload(
    symbol: str,
    strategy_name: str,
    params: dict | None = None,
    start: str | None = None,
    end: str | None = None,
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
    if len(bars) < 60:
        raise RuntimeError(f"window has only {len(bars)} bars — need at least 60")
    strategy = STRATEGIES[strategy_name]
    bt = Backtest(
        to_ohlc(bars),
        strategy,
        cash=CASH,
        commission=COMMISSION,
        finalize_trades=True,  # close the last open trade so stats are complete
    )
    stats = bt.run(**(params or {}))
    metrics = {
        metric: _plain(stats[metric]) for metric in METRICS if metric in stats
    }
    trades = [
        {
            "entry_date": str(row.EntryTime)[:10],
            "entry_price": round(float(row.EntryPrice), 2),
            "exit_date": str(row.ExitTime)[:10],
            "exit_price": round(float(row.ExitPrice), 2),
            "size": int(row.Size),
            "pnl": round(float(row.PnL), 2),
            "return_pct": round(float(row.ReturnPct) * 100, 2),
        }
        for row in stats._trades.itertuples(index=False)
    ]
    equity_frame = stats._equity_curve
    step = max(1, len(equity_frame) // 500)
    equity = [
        {"date": str(index)[:10], "equity": round(float(row.Equity), 2)}
        for index, row in equity_frame.iloc[::step].iterrows()
    ]
    return {
        "symbol": symbol,
        "strategy": strategy_name,
        "metrics": metrics,
        "trades": trades,
        "equity": equity,
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
