"""Signal rules. Each strategy is a `backtesting.py` Strategy subclass.

Conventions:
- Sensible default params (the Strategy Lab will expose/edit these later).
- Signals computed on bar N execute at bar N+1's open — no lookahead bias.
- Every strategy ships with explicit exits (the entry signal reversing is an exit).
"""
import pandas as pd
from backtesting import Strategy


class SmaCross(Strategy):
    """Golden cross: fast SMA crosses above slow SMA -> go long; crosses back -> exit.

    The "hello world" of trend following. Purely a learning baseline, not a
    money maker — and that is exactly its job here.
    """

    n_fast = 20
    n_slow = 50

    def init(self):
        close = pd.Series(self.data.Close)
        self.fast = self.I(close.rolling(self.n_fast).mean, name="SMA_fast")
        self.slow = self.I(close.rolling(self.n_slow).mean, name="SMA_slow")

    def next(self):
        crossed_up = self.fast[-1] > self.slow[-1] and self.fast[-2] <= self.slow[-2]
        crossed_down = self.fast[-1] < self.slow[-1] and self.fast[-2] >= self.slow[-2]
        if crossed_up and not self.position:
            self.buy()
        elif crossed_down and self.position:
            self.position.close()


# Registry used by the backtest CLI and (later) the Strategy Lab.
STRATEGIES = {
    "SMA Cross": SmaCross,
}
