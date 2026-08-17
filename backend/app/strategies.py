"""Signal rules. Each strategy is a `backtesting.py` Strategy subclass.

Conventions:
- Sensible default params (the Strategy Lab edits these live).
- Signals computed on bar N execute at bar N+1's open — no lookahead bias.
- Every strategy ships with explicit exits.
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


class DonchianTrend(Strategy):
    """Turtle-style breakout: long on an N-day high breakout.

    Exits: M-day low breakout OR a trailing stop = close - atr_mult × ATR
    (whichever hits first). The ATR stop never moves down while in a trade.
    """

    n_entry = 55
    n_exit = 20
    atr_period = 14
    atr_mult = 3.0

    def init(self):
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        close = pd.Series(self.data.Close)
        self.upper = self.I(
            lambda: high.rolling(self.n_entry).max().shift(1), name="donchian_high"
        )
        self.lower = self.I(
            lambda: low.rolling(self.n_exit).min().shift(1), name="donchian_low"
        )
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)
        self.atr = self.I(
            lambda: tr.ewm(alpha=1 / self.atr_period, adjust=False).mean(), name="ATR"
        )
        self.stop = None

    def next(self):
        close = self.data.Close[-1]
        if not self.position and close > self.upper[-1]:
            self.buy()
            self.stop = close - self.atr_mult * self.atr[-1]
        elif self.position:
            self.stop = max(self.stop, close - self.atr_mult * self.atr[-1])
            if close < self.lower[-1] or close < self.stop:
                self.position.close()
                self.stop = None


class RsiReversion(Strategy):
    """Mean reversion: long when RSI drops below the oversold line,
    exit when it recovers above the overbought line.
    """

    period = 14
    buy_below = 30
    sell_above = 70

    def init(self):
        close = pd.Series(self.data.Close)
        delta = close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / self.period, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / self.period, adjust=False).mean()
        self.rsi = self.I(
            lambda: 100 - 100 / (1 + gain / loss.replace(0, 1e-12)), name="RSI"
        )

    def next(self):
        if not self.position and self.rsi[-1] < self.buy_below:
            self.buy()
        elif self.position and self.rsi[-1] > self.sell_above:
            self.position.close()


class SrBounce(Strategy):
    """Classic support/resistance bounce: buy when price tests and holds the
    N-day support, exit when it reaches the N-day resistance or breaks the
    support by more than atr_mult × ATR. This is the first of the classic-TA
    validity series (Fibonacci / wave ideas queued).
    """

    n_window = 20
    atr_period = 14
    atr_mult = 3.0

    def init(self):
        low = pd.Series(self.data.Low)
        high = pd.Series(self.data.High)
        close = pd.Series(self.data.Close)
        self.support = self.I(
            lambda: low.shift(1).rolling(self.n_window).min(), name="support"
        )
        self.resistance = self.I(
            lambda: high.shift(1).rolling(self.n_window).max(), name="resistance"
        )
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)
        self.atr = self.I(
            lambda: tr.ewm(alpha=1 / self.atr_period, adjust=False).mean(), name="ATR"
        )

    def next(self):
        close = self.data.Close[-1]
        support = self.support[-1]
        resistance = self.resistance[-1]
        if not self.position:
            # Dipped to support today and closed back above it -> support held.
            if close > support and self.data.Low[-1] <= support:
                self.buy()
        else:
            if self.data.High[-1] >= resistance:
                self.position.close()
            elif close < support - self.atr_mult * self.atr[-1]:
                self.position.close()


# Registry used by the backtest CLI, the API, and the Strategy Lab.
STRATEGIES = {
    "SMA Cross": SmaCross,
    "Donchian Trend": DonchianTrend,
    "S/R Bounce": SrBounce,
    "RSI Reversion": RsiReversion,
}


def _int(default, lo, hi):
    return {"type": "int", "default": default, "min": lo, "max": hi}


def _float(default, lo, hi, step=0.5):
    return {"type": "float", "default": default, "min": lo, "max": hi, "step": step}


STRATEGY_PARAMS = {
    "SMA Cross": {
        "n_fast": _int(20, 2, 250),
        "n_slow": _int(50, 5, 400),
    },
    "Donchian Trend": {
        "n_entry": _int(55, 10, 250),
        "n_exit": _int(20, 5, 120),
        "atr_period": _int(14, 2, 100),
        "atr_mult": _float(3.0, 1.0, 10.0),
    },
    "S/R Bounce": {
        "n_window": _int(20, 5, 120),
        "atr_period": _int(14, 2, 100),
        "atr_mult": _float(3.0, 1.0, 10.0),
    },
    "RSI Reversion": {
        "period": _int(14, 2, 50),
        "buy_below": _int(30, 5, 49),
        "sell_above": _int(70, 51, 95),
    },
}
