# frontend/

Static web UI for trade-helper-v1. Served by the backend — **no build step, no framework yet**.

## What it does (planned)

Three views behind a sidebar nav:

- **Today** — strategy tabs → pick cards (entry, exit, confidence bar, "why" one-liner).
- **Symbol Explorer** — symbol dropdown, chart with technicals + algorithm-drawn S/R levels, backtest results rail (win rate, profit factor, max drawdown, trades, equity curve).
- **Strategy Lab** — pick strategy, edit params (defaults + reset), pick symbol + range, run backtest.
- **"Fetch now"** button that triggers the backend's daily fetch.

## Tech choices (keep it lean)

- **Plain HTML + CSS + vanilla JS** first. Single `index.html`.
- **Charting: TradingView Lightweight Charts** (pinned version, via CDN — no bundler).
- **Upgrade to React/Vite only if** the UI grows beyond a few pages — do not preemptively.

## Charting (how backtest visuals map to the library)

The backend computes everything; the frontend only draws. A backtest returns JSON:

- candles → `CandlestickSeries`
- volume → `HistogramSeries`
- entry/exit events → `setMarkers()` (arrows with text, e.g. `LONG @ 189.40`)
- ATR exit / support / resistance levels → `createPriceLine()` (algorithm-drawn, never user-drawn)
- custom shapes (if ever needed) → v5 custom primitives

## Layout (planned)

    frontend/
    ├── README.md
    └── index.html     # single page, calls the backend API

## How it's served

The backend mounts this folder as static files, so locally the UI lives at
`http://localhost:8000/` — no separate dev server needed.
