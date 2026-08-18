[Project home](../README.md) · [Docs](../docs/README.md) · [Roadmap](../docs/roadmap.md) · [Changelog](../CHANGELOG.md)

# frontend/

Static web UI for trade-helper-v1. Served by the backend — **no build step, no framework yet**.

## What it does

Four views behind a sidebar nav:

- **Today** ✅ — historical post-signal statistics, locked shared-capital
  portfolio replay, current entry/exit cards, and regime state. The portfolio
  panel shows actual account-sized positions and refuses strategies without a
  protective stop.
- **Symbol Explorer** ✅ — searchable symbol picker (typeahead), Lightweight Charts: candles, volume, per-strategy overlays (SMA / Donchian + ATR stop), entry/exit markers, 3M–10Y/ALL range buttons + zoom controls, range-aware metrics, equity curve, trades table, editable strategy params with reset.
- **Strategy Lab** ✅ — compare strategies and edit/save parameter sets.
- **Macro** ✅ — event calendar, macro cards, and regime filter.

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
    └── index.html     # single page: Today, Explorer, Lab, and Macro ✅

## How it's served

The backend mounts this folder as static files, so locally the UI lives at
`http://localhost:8000/` — no separate dev server needed.
