[Project home](../README.md) · [Docs](../docs/README.md) · [Roadmap](../docs/roadmap.md) · [Changelog](../CHANGELOG.md)

# frontend/

Static web UI for trade-helper-v1. Served by the backend — **no build step, no framework yet**.

## What it does

Five views behind a sidebar nav:

- **Today** ✅ — immediately reads the last stored strategy snapshot and keeps
  persistent watched lifecycle separate from full-universe entry discovery.
  The discovery board has Intersections, Momentum, New Breakouts, and one tab
  per algorithm; each populated model tab represents a completed all-security
  scan and shows every entry-pending candidate. Watch updates, universe scans,
  and portfolio comparisons have separate explicit run buttons.
- **Symbol Research** ✅ — searchable symbol picker (typeahead), Lightweight
  Charts, strategy overlays, markers, range controls, metrics, equity, trades,
  editable parameters, and evidence-status strategy dossiers. Only Run Backtest
  calculates; selection and navigation are read-only.
- **Strategy Lab** ✅ — select/save a per-strategy watchlist, compare strategies,
  and edit/save parameter sets. Only Compute / refresh runs the scoreboard.
- **Macro** ✅ — event calendar, macro cards, and regime filter.
- **Data Management** ✅ — provider-separated inventory, expected-session
  freshness, type-to-filter coverage table, manual Yahoo refresh controls, and
  live per-symbol progress/failures.

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
        └── index.html     # single page: Today, Research, Lab, Macro, and Data ✅

## How it's served

The backend mounts this folder as static files, so locally the UI lives at
`http://localhost:8000/` — no separate dev server needed.
