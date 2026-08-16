# frontend/

Static web UI for trade-helper-v1. Served by the backend — **no build step, no framework yet**.

## What it does

Three views behind a sidebar nav:

- **Today** — strategy tabs → pick cards (planned).
- **Symbol Explorer** ✅ — searchable symbol picker (typeahead), Lightweight Charts: candles, volume, per-strategy overlays (SMA / Donchian + ATR stop), entry/exit markers, 3M–10Y/ALL range buttons + zoom controls, range-aware metrics, equity curve, trades table, editable strategy params with reset.
- **Strategy Lab** — pick strategy, edit params, run (planned).
- **Macro** — event calendar + macro cards + regime filter (planned).

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

## Layout

    frontend/
    ├── README.md
    └── index.html     # single page: nav + Explorer view (chart, metrics, trades) ✅

## How it's served

The backend mounts this folder as static files, so locally the UI lives at
`http://localhost:8000/` — no separate dev server needed.
