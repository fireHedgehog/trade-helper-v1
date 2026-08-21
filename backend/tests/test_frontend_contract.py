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
    assert '<details class="panel workflow-collapsible" id="today-manual-workflow">' in HTML
    assert '<details class="panel workflow-collapsible" id="today-pipeline-workflow">' in HTML
    assert "<details class=\"panel workflow-collapsible\" id=\"today-manual-workflow\" open" not in HTML
    assert "<details class=\"panel workflow-collapsible\" id=\"today-pipeline-workflow\" open" not in HTML


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
    assert "previewDailyPipeline" not in apply_view

    assert "$('#today-review-data').addEventListener('click', () => showView('data'))" in HTML
    assert "$('#today-refresh').addEventListener('click', () => runTodaySnapshot('watchlist'))" in HTML
    assert "$('#today-run-discovery').addEventListener('click', () => runTodaySnapshot('all'))" in HTML
    assert "$('#today-plan-pipeline').addEventListener('click', previewDailyPipeline)" in HTML
    assert "Daily pipeline · Recommended routine" in HTML
    assert "It replaces manual Steps 1–3" in HTML
    assert "portfolio comparison remains a separate Step 4 action" in HTML
    assert "Provider pacing alone requires at least" in HTML
    assert "Daily discovery coverage excludes" in HTML
    assert "Formal experiments use their own locked coverage gate" in HTML
    assert "$('#today-run-pipeline').addEventListener('click', runDailyPipeline)" in HTML
    assert 'id="today-run-pipeline" disabled' in HTML
    assert 'id="today-pipeline-results" hidden' in HTML
    assert "new run #${row.run_id}" in HTML
    assert "reused run #${resultId}" in HTML
    assert "stored ${run.created_at || 'unknown'}" in HTML
    assert "$('#today-view-candidates').addEventListener('click'" in HTML


def test_data_refresh_distinguishes_resume_from_forced_scopes() -> None:
    assert "Resume / refresh needed" in HTML
    assert "Force refresh core" in HTML
    assert "Force refresh all Yahoo" in HTML
    assert "skips symbols already current" in HTML
    assert "Job identity, item outcomes, and timestamps are stored in SQLite" in HTML
    assert "Published rows and this job record survived" in HTML


def test_watchlist_snapshot_is_recoverable_and_empty_save_is_explicit() -> None:
    assert "Restore snapshot symbols" in HTML
    assert "contains ${snapshotSymbols.length} historical symbols available through Restore snapshot symbols" in HTML
    assert "Watchlist empty · historical run #${stored.run.id} is recoverable" in HTML
    assert "const effectiveSymbols = savedSymbols" in HTML
    assert "Historical run snapshots remain recoverable" in HTML
    assert "if (!symbols.length && !window.confirm" in HTML


def test_today_never_mixes_full_universe_runs_into_watchlist_state() -> None:
    assert "&scope=watchlist`)" in HTML
    assert "Suggested default basket selected for ${strategy}, but not saved" in HTML
    assert "unsaved changes. Click “Save as strategy watchlist”" in HTML


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
    assert "Definition and result inspection are separate" in HTML
    assert 'id="lab-run-state"' in HTML
    assert "interactive scoreboard is not that experiment" not in HTML
    assert "research_contract?.decision" in HTML
    assert "Select at least one symbol before calculating." in HTML
    assert "Complete with failures" in HTML
    assert "const STRATEGY_EVIDENCE" not in HTML


def test_macro_is_display_only_with_labeled_untested_heuristic_only() -> None:
    assert 'id="macro-contract"' in HTML
    assert "Point-in-time vintages: unavailable" in HTML
    assert "provenance per card" in HTML
    assert "revision_status" in HTML
    assert "not signal eligible" in HTML
    # An equity-direction chip may appear, but only ever as a disclosed, labeled
    # hypothesis (ADR 0006 Consequences, "Textbook heuristic display") — never as
    # a bare, unqualified claim of fact.
    assert "Equity read is a textbook hypothesis, not a research result." in HTML
    assert "Hypothesis: ${h.read} (untested)" in HTML
    assert "good for equities" not in HTML
    assert "bad for equities" not in HTML
