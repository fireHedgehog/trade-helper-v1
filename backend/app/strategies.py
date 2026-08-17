"""Signal rules. Each strategy is a `backtesting.py` Strategy subclass.

Conventions:
- Sensible default params (the Strategy Lab edits these live).
- Signals computed on bar N execute at bar N+1's open — no lookahead bias.
- Every strategy ships with explicit exits.
"""
import pandas as pd
from backtesting import Strategy


class CtaTrend(Strategy):
    """Managed-futures-style trend follower (long-only here).

    Entry: close breaks the prior N-day high AND trades above the trend
    average (trend filter) -> in at the next open, even at all-time highs.
    Exits: M-day low breakout (trend changed), a trailing ATR stop, and an
    optional ATR take-profit (atr_tp_mult = 0 disables it).
    """

    n_entry = 100
    n_exit = 40
    trend_ma = 100
    atr_period = 14
    atr_mult = 5.0
    atr_tp_mult = 0.0

    def init(self):
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        close = pd.Series(self.data.Close)
        self.upper = self.I(
            lambda: high.shift(1).rolling(self.n_entry).max(), name="cta_high"
        )
        self.lower = self.I(
            lambda: low.shift(1).rolling(self.n_exit).min(), name="cta_low"
        )
        self.trend = self.I(
            lambda: close.rolling(self.trend_ma).mean(), name="cta_trend"
        )
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)
        self.atr = self.I(
            lambda: tr.ewm(alpha=1 / self.atr_period, adjust=False).mean(), name="ATR"
        )
        self.stop = None
        self.tp = None

    def next(self):
        close = self.data.Close[-1]
        if not self.position:
            trend_ok = not pd.isna(self.trend[-1]) and close > self.trend[-1]
            if close > self.upper[-1] and trend_ok:
                self.buy()
                self.stop = close - self.atr_mult * self.atr[-1]
                self.tp = (
                    close + self.atr_tp_mult * self.atr[-1]
                    if self.atr_tp_mult > 0
                    else None
                )
        else:
            self.stop = max(self.stop, close - self.atr_mult * self.atr[-1])
            if close < self.lower[-1]:
                self.position.close()
            elif close < self.stop:
                self.position.close()
            elif self.tp is not None and close >= self.tp:
                self.position.close()


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


class FibRetrace(Strategy):
    """Fibonacci retracement (quantified approximation): after a swing high
    pulls back to a swing low, buy when the close recovers above the chosen
    fib retracement level. Stop at the pullback low, target at the swing high.

    Approximation note: swings are rolling N/M-day extremes, not hand-drawn
    chartist swings — the idea is measured, the aesthetics are not.
    """

    n_swing = 60
    m_pullback = 10
    fib = 0.618

    def init(self):
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        h = high.shift(1).rolling(self.n_swing).max()
        l = low.shift(1).rolling(self.m_pullback).min()
        self.swing_high = self.I(lambda: h, name="swing_high")
        self.pullback_low = self.I(lambda: l, name="pullback_low")
        self.level = self.I(lambda: l + self.fib * (h - l), name="fib_level")

    def next(self):
        close = self.data.Close[-1]
        if not self.position:
            if (
                self.swing_high[-1] > self.pullback_low[-1]
                and close > self.level[-1]
                and self.data.Close[-2] <= self.level[-2]
            ):
                self.buy()
                self.stop = self.pullback_low[-1]
                self.target = self.swing_high[-1]
        elif close <= self.stop or close >= self.target:
            self.position.close()


class WavePull(Strategy):
    """Impulse-pullback ("wave-lite"): after a strong impulse up, buy the first
    breakout of the following pullback. Quantified stand-in for wave counting —
    stop at the pullback low, take profit at 2× the entry risk.
    """

    impulse_bars = 8
    impulse_pct = 6.0
    pullback_bars = 3

    def init(self):
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        self.impulse = self.I(
            lambda: close / close.shift(self.impulse_bars) - 1 >= self.impulse_pct / 100,
            name="impulse",
        )
        self.breakout = self.I(
            lambda: high.shift(1).rolling(self.pullback_bars).max(), name="pullback_high"
        )
        self.pullback_low = self.I(
            lambda: low.shift(1).rolling(self.pullback_bars).min(), name="pullback_low"
        )

    def next(self):
        close = self.data.Close[-1]
        if not self.position:
            if self.impulse[-1] and close > self.breakout[-1]:
                self.buy()
                risk = self.breakout[-1] - self.pullback_low[-1]
                self.stop = self.pullback_low[-1]
                self.target = self.breakout[-1] + 2 * risk
        elif close <= self.stop or close >= self.target:
            self.position.close()


# Registry used by the backtest CLI, the API, and the Strategy Lab.
# Order matters: the first entry is the default selection everywhere.
STRATEGIES = {
    "CTA Trend": CtaTrend,
    "SMA Cross": SmaCross,
    "Donchian Trend": DonchianTrend,
    "S/R Bounce": SrBounce,
    "Fib Retrace": FibRetrace,
    "Wave Pull": WavePull,
    "RSI Reversion": RsiReversion,
}


def _int(default, lo, hi):
    return {"type": "int", "default": default, "min": lo, "max": hi}


def _float(default, lo, hi, step=0.5):
    return {"type": "float", "default": default, "min": lo, "max": hi, "step": step}


STRATEGY_PARAMS = {
    "CTA Trend": {
        "n_entry": _int(100, 10, 250),
        "n_exit": _int(40, 5, 150),
        "trend_ma": _int(100, 20, 400),
        "atr_period": _int(14, 2, 100),
        "atr_mult": _float(5.0, 1.0, 10.0),
        "atr_tp_mult": _float(0.0, 0.0, 20.0, 1.0),
    },
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
    "Fib Retrace": {
        "n_swing": _int(60, 20, 250),
        "m_pullback": _int(10, 3, 60),
        "fib": _float(0.618, 0.2, 0.9, 0.05),
    },
    "Wave Pull": {
        "impulse_bars": _int(8, 3, 30),
        "impulse_pct": _float(6.0, 1.0, 25.0, 0.5),
        "pullback_bars": _int(3, 1, 15),
    },
    "RSI Reversion": {
        "period": _int(14, 2, 50),
        "buy_below": _int(30, 5, 49),
        "sell_above": _int(70, 51, 95),
    },
}


# Human explanations shown in the Strategy guide panel in the Explorer.
STRATEGY_INFO = {
    "CTA Trend": {
        "tagline": "Managed-futures-style trend following: ride breakouts that are confirmed by the long-term trend.",
        "entry": "Close above the highest high of the last N days AND above the trend average → buy at the next open (works even at all-time highs).",
        "exit": "Close below the lowest low of the last M days (trend changed), or the trailing ATR stop, or an optional ATR take-profit.",
        "chart": "Blue dashed = N-day high (entry level), pink dashed = M-day low (trend-exit level), purple = trend average, red = trailing ATR stop.",
        "params": {
            "n_entry": "Breakout lookback in days — higher = fewer, bigger trends.",
            "n_exit": "Trend-exit lookback in days — how much pullback ends the trade.",
            "trend_ma": "Trend filter: entries only above this moving average.",
            "atr_period": "ATR smoothing period for stop sizing.",
            "atr_mult": "Trailing stop distance in ATR multiples below the close.",
            "atr_tp_mult": "Optional take-profit in ATR multiples (0 = disabled, ride the trend).",
        },
    },
    "SMA Cross": {
        "tagline": "Classic trend-following: trade with the direction of the two moving averages.",
        "entry": "Fast average crosses ABOVE the slow average → buy at the next open.",
        "exit": "Fast average crosses BELOW the slow average → exit at the next open.",
        "chart": "Orange line = fast average, purple = slow average. A 'cross' is where the two lines intersect — that is the signal. Green ▲ = entries, red ▼ = exits.",
        "params": {
            "n_fast": "Fast average length in days (lower = more sensitive, more whipsaws).",
            "n_slow": "Slow average length in days (higher = slower trend, fewer signals).",
        },
    },
    "Donchian Trend": {
        "tagline": "Turtle-style breakout: ride trends that make new highs.",
        "entry": "Close above the highest high of the last N days → buy at the next open.",
        "exit": "Close below the lowest low of the last M days, OR below the trailing ATR stop.",
        "chart": "Blue dashed = N-day high (entry level), pink dashed = M-day low (exit level), red = trailing ATR stop.",
        "params": {
            "n_entry": "Lookback in days for the breakout high.",
            "n_exit": "Lookback in days for the exit low.",
            "atr_period": "ATR smoothing period.",
            "atr_mult": "Stop distance in multiples of ATR below the close.",
        },
    },
    "S/R Bounce": {
        "tagline": "Classic support/resistance: buy where support held before, sell where resistance rejected.",
        "entry": "Price dips to the N-day support and closes back above it → buy at the next open.",
        "exit": "Price touches the N-day resistance, or closes below support by atr_mult × ATR.",
        "chart": "Blue dashed = N-day resistance, pink dashed = N-day support. Entries happen near the support line, exits near resistance.",
        "params": {
            "n_window": "Lookback in days for the support/resistance levels.",
            "atr_period": "ATR smoothing period.",
            "atr_mult": "Breakdown buffer below support, in ATR units.",
        },
    },
    "Fib Retrace": {
        "tagline": "Fibonacci retracement: buy the pullback of an up-swing at a fib level.",
        "entry": "After a swing high (N-day high) pulls back to a swing low (M-day low), buy when the close recovers above the fib retracement level of that pullback.",
        "exit": "Stop below the pullback low; take profit at the swing high.",
        "chart": "The fib level is where entry happens. Approximation note: swing high/low are rolling N/M-day extremes, not chartist hand-drawn swings.",
        "params": {
            "n_swing": "Lookback for the swing high.",
            "m_pullback": "Lookback for the pullback low.",
            "fib": "Retracement level: 0.382 / 0.5 / 0.618 (classic) / 0.786.",
        },
    },
    "Wave Pull": {
        "tagline": "Impulse-pullback ('wave-lite'): after a strong impulse, buy the first breakout of the pullback.",
        "entry": "Close rises at least impulse_pct% over impulse_bars days, then breaks above the pullback's recent high.",
        "exit": "Stop below the pullback low; take profit at 2× the entry risk.",
        "chart": "Entry markers appear right after pullbacks that follow strong impulses. This is a quantified stand-in for wave counting, not Elliott analysis itself.",
        "params": {
            "impulse_bars": "Bars the impulse is measured over.",
            "impulse_pct": "Minimum % move that counts as an impulse.",
            "pullback_bars": "Recent bars defining the pullback high/low.",
        },
    },
    "RSI Reversion": {
        "tagline": "Mean reversion: buy fear, sell the recovery.",
        "entry": "RSI drops below the oversold line → buy at the next open.",
        "exit": "RSI recovers above the overbought line → exit at the next open.",
        "chart": "RSI is not drawn on the price chart — the entry markers cluster after sharp drops, when RSI is oversold.",
        "params": {
            "period": "RSI smoothing period (2 = very sensitive, 14 = classic).",
            "buy_below": "Oversold threshold.",
            "sell_above": "Overbought exit threshold.",
        },
    },
}
