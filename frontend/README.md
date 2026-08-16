# frontend/

Static web UI for trade-helper-v1. Served by the backend — **no build step, no framework yet**.

## What it does (planned)

- Show stored daily closing prices (table + chart).
- **"Fetch now"** button that triggers the backend's daily fetch.
- Later: run backtests and view results.

## Tech choices (keep it lean)

- **Plain HTML + CSS + vanilla JS** first. Single `index.html`.
- Chart library when needed: `lightweight-charts` or `Chart.js` via CDN (no bundler).
- **Upgrade to React/Vite only if** the UI grows beyond a few pages — do not preemptively.

## Layout (planned)

    frontend/
    ├── README.md
    └── index.html     # single page, calls the backend API

## How it's served

The backend mounts this folder as static files, so locally the UI lives at
`http://localhost:8000/` — no separate dev server needed.
