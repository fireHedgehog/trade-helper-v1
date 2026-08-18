# Frontend

Static HTML, CSS, and vanilla JavaScript served by FastAPI; no build step or separate development server. The backend computes research results, while the browser presents persisted state and starts only explicit user actions.

## Views

| View | Responsibility |
|---|---|
| Today | Freshness/actions, watched lifecycle, full-universe candidates, intersections, warnings |
| Symbol Research | Typeahead symbol selection, chart, model accordions, signal/risk/evidence context |
| Strategy Lab | Versioned definitions, watchlists, evidence boundaries, and explicitly exploratory session comparisons |
| Macro | ADR 0006 display-only context with explicit provenance and unavailable point-in-time capabilities |
| Data Management | Coverage, expected-session freshness, selected refresh, progress, failures |

Navigation must be read-only. Backtest, refresh, universe scan, and strategy evaluation each require a distinct action. Empty, not-run, stale, running, failed, and completed-with-no-candidates are different states.

Strategy Lab must not present its in-memory scoreboard as a formal experiment. Locked decisions and artifact paths come from backend research metadata; prototype strategies remain `not evaluable` until a preregistered experiment produces an immutable result.

## Implementation

`index.html` contains the single-page application. TradingView Lightweight Charts is pinned via CDN for candles, volume, markers, and price levels. Introduce a framework only if state complexity makes the current design materially unsafe to maintain.

Stage 8B defines the semantic UI tokens and Today command centre. Its four permanent actions appear in dependency order—data, watchlist, discovery, portfolio—but remain independent manual triggers. Future scheduling must call the same durable pipeline described in the workspace specification.

Run the backend and open <http://127.0.0.1:8000/>. The pending product contract is [workspace-redesign.md](../docs/workspace-redesign.md).

Run `scripts/browser-smoke.sh` from the repository root while the backend is running. It exercises navigation and deterministic not-run, empty, running, interrupted, partial-failure, and failed states without provider writes or strategy computation.

[Project](../README.md) · [Checkpoint](../docs/README.md) · [Roadmap](../docs/roadmap.md)
