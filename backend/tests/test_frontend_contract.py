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


def test_data_refresh_distinguishes_resume_from_forced_scopes() -> None:
    assert "Resume / refresh needed" in HTML
    assert "Force refresh core" in HTML
    assert "Force refresh all Yahoo" in HTML
    assert "skips symbols already current" in HTML
    assert "server restart loses this progress display, not published rows" in HTML


def test_watchlist_snapshot_is_recoverable_and_empty_save_is_explicit() -> None:
    assert "Restore snapshot symbols" in HTML
    assert "showing ${snapshotSymbols.length} recoverable symbols" in HTML
    assert "Historical run snapshots remain recoverable" in HTML
    assert "if (!symbols.length && !window.confirm" in HTML


def test_symbol_research_evaluates_all_accordions_without_mixing_chart_markers() -> None:
    assert "async function loadResearchAccordions(symbol)" in HTML
    assert "Evaluating latest state for every model" in HTML
    assert "Uses the parameter values shown above" in HTML
    assert "chart markers remain limited to the selected model" in HTML
    assert "loadResearchAccordions(symbol)" in HTML


def test_classical_ta_is_identifiable_without_renaming_the_backend_contract() -> None:
    assert "Classical TA · S/R Bounce" in HTML
    assert "strategy.evidence?.summary" in HTML
    assert "value=\"${escapeHtml(s.name)}\"" in HTML


def test_symbol_research_guide_and_dossier_are_not_cramped() -> None:
    assert "width: 380px" in HTML
    assert "height: 96px; min-height: 96px" in HTML
    assert ".guide-title { font-size: 15px" in HTML
    assert ".research-accordion p { font-size: 12px" in HTML


def test_current_model_observation_precedes_reference_rules() -> None:
    guide = HTML[HTML.index('<div class="guide" id="guide">'):HTML.index('</div>', HTML.index('<div class="guide-chart"'))]

    assert guide.index('id="guide-now"') < guide.index('id="guide-rules"')
    assert "guide-now { color: var(--green); font-weight: 650" in HTML


def test_metadata_is_rendered_from_backend_contracts() -> None:
    assert 'id="dataset-catalog"' in HTML
    assert "dataset.point_in_time" in HTML
    assert "meta.parameter_schema" in HTML
    assert "strategy.evidence?.label" in HTML
    assert 'id="lab-strategy-contract"' in HTML
    assert "function renderLabStrategyContract()" in HTML
    assert "renderLabStrategyContract();" in HTML
    assert "const STRATEGY_EVIDENCE" not in HTML
