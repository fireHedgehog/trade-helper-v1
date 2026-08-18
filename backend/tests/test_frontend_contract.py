"""Static regression checks for the zero-build frontend product contract."""

from pathlib import Path


HTML = (Path(__file__).parents[2] / "frontend" / "index.html").read_text()


def test_today_exposes_the_daily_workflow_in_dependency_order() -> None:
    labels = [
        "Step 1 · Data",
        "Step 2 · Watchlist",
        "Step 3 · Discovery",
        "Step 4 · Comparison",
    ]

    positions = [HTML.index(label) for label in labels]

    assert positions == sorted(positions)
    assert "Review / refresh data" in HTML
    assert "Update watched status" in HTML
    assert "Run full-universe candidates" in HTML
    assert "Run portfolio comparison" in HTML


def test_today_semantic_states_have_text_and_colour_contracts() -> None:
    for token in (
        "state-positive",
        "state-negative",
        "state-warning",
        "state-info",
        "state-neutral",
    ):
        assert token in HTML

    for explicit_state in (
        "Market data unavailable",
        "Not evaluated",
        "Run failed",
        "Data needs review",
        "Data current",
    ):
        assert explicit_state in HTML


def test_today_navigation_is_read_only_until_an_action_is_clicked() -> None:
    apply_view = HTML[HTML.index("function applyView"):HTML.index("function showView")]

    assert "loadTodayStored()" in apply_view
    assert "runTodaySnapshot" not in apply_view
    assert "startDataRefresh" not in apply_view
    assert "runTodayPortfolio" not in apply_view

    assert "$('#today-review-data').addEventListener('click', () => showView('data'))" in HTML
    assert "$('#today-refresh').addEventListener('click', () => runTodaySnapshot('watchlist'))" in HTML
    assert "$('#today-run-discovery').addEventListener('click', () => runTodaySnapshot('all'))" in HTML
