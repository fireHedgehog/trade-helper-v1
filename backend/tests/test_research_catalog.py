"""Contracts for the research metadata registry, including the ADR 0009
Tier A (executable) / Tier B (characterization-only) separation."""

from pathlib import Path

from app.research_catalog import (
    CHARACTERIZATION_STUDIES,
    DATASETS,
    DECISIONS,
    DEFERRED_FROM_RECORD,
    RESEARCH_REPO_BASE,
    STRATEGIES,
    STRATEGY_ORIGINS,
    STUDY_TYPES,
    characterization_studies,
    dataset_for_provider,
    library_entries,
    research_record_entries,
)
from app.strategies import STRATEGIES as EXECUTABLE_STRATEGIES

REPO_ROOT = Path(__file__).resolve().parents[2]

_KNOWN_DECISIONS = {
    "rejected",
    "not evaluable",
    "not_material_or_not_consistent",
}


def test_every_executable_strategy_has_versioned_metadata() -> None:
    assert set(STRATEGIES) == set(EXECUTABLE_STRATEGIES)
    for name, metadata in STRATEGIES.items():
        assert metadata["strategy_id"]
        assert metadata["origin"] in STRATEGY_ORIGINS, name
        assert metadata["type"] in STUDY_TYPES, name
        assert metadata["version"]
        assert metadata["family"]
        assert metadata["information_profile"]
        assert metadata["evidence"]["status"]
        assert metadata["required_datasets"]
        assert metadata["research_contract"]["hypothesis"]
        assert metadata["research_contract"]["execution"].endswith("N+1 fill")
        assert metadata["research_contract"]["decision"] in _KNOWN_DECISIONS
        assert set(metadata["required_datasets"]) <= set(DATASETS), name


def test_research_contract_decision_is_not_hardcoded_and_matches_evidence() -> None:
    """ADR 0009: decision must be derived per strategy, not a two-value
    hardcode -- at least one closed strategy other than CTA Trend must
    carry a real (non-"not evaluable") decision, and every strategy with a
    closed decision must carry its result artifact."""
    non_cta_decisions = {
        name: metadata["research_contract"]["decision"]
        for name, metadata in STRATEGIES.items()
        if name != "CTA Trend"
    }
    assert len(set(non_cta_decisions.values())) > 1, non_cta_decisions
    for name, metadata in STRATEGIES.items():
        contract = metadata["research_contract"]
        if contract["decision"] == "not evaluable":
            assert contract["artifact"] is None, name
        else:
            assert contract["artifact"], name
            assert (REPO_ROOT / contract["artifact"]).is_file(), name
            assert metadata["evidence"]["status"].startswith(contract["decision"][:10]), name


def test_cta_trend_is_the_only_rejected_strategy() -> None:
    assert STRATEGIES["CTA Trend"]["research_contract"]["decision"] == "rejected"
    assert STRATEGIES["CTA Trend"]["research_contract"]["artifact"]
    for name, metadata in STRATEGIES.items():
        if name != "CTA Trend":
            assert metadata["research_contract"]["decision"] != "rejected", name


def test_decisions_registry_covers_exactly_the_executable_strategies() -> None:
    assert set(DECISIONS) == set(STRATEGIES)


def test_characterization_studies_never_overlap_executable_strategies() -> None:
    """ADR 0009's core invariant: a Tier B study must never also be a
    Tier A executable strategy -- that would fabricate a live signal for
    a study whose own locked protocol authorized no execution."""
    assert set(CHARACTERIZATION_STUDIES).isdisjoint(set(STRATEGIES))


def test_characterization_studies_result_docs_and_artifacts_exist() -> None:
    for study_id, entry in CHARACTERIZATION_STUDIES.items():
        assert entry["chapter"], study_id
        assert entry["type"] in STUDY_TYPES, study_id
        assert entry["decision"], study_id
        result_doc = REPO_ROOT / entry["result_doc"]
        assert result_doc.is_file(), study_id
        if entry["artifact"] is not None:
            assert (REPO_ROOT / entry["artifact"]).is_file(), study_id


def test_characterization_studies_accessor_matches_registry() -> None:
    studies = characterization_studies()
    assert {s["study_id"] for s in studies} == set(CHARACTERIZATION_STUDIES)
    for study in studies:
        assert study["result_doc"] == CHARACTERIZATION_STUDIES[study["study_id"]]["result_doc"]


def test_deferred_studies_are_exactly_the_undocumented_ones() -> None:
    """docs/strategy-library.md Step 2b: a study is either onboarded (has
    name+summary, not deferred) or explicitly deferred (named in
    DEFERRED_FROM_RECORD) -- never silently missing one or the other."""
    for study_id, entry in CHARACTERIZATION_STUDIES.items():
        if study_id in DEFERRED_FROM_RECORD:
            assert "name" not in entry, study_id
            assert "summary" not in entry, study_id
        else:
            assert entry.get("name"), study_id
            assert entry.get("summary"), study_id


def test_research_record_excludes_deferred_studies() -> None:
    entries = research_record_entries()
    ids = {entry["study_id"] for entry in entries}
    assert ids == set(CHARACTERIZATION_STUDIES) - DEFERRED_FROM_RECORD
    assert ids.isdisjoint(DEFERRED_FROM_RECORD)


def test_research_record_entries_are_display_ready() -> None:
    for entry in research_record_entries():
        assert entry["name"], entry["study_id"]
        assert entry["summary"], entry["study_id"]
        assert entry["chapter"], entry["study_id"]
        assert entry["type"] in STUDY_TYPES, entry["study_id"]
        assert entry["decision"], entry["study_id"]
        assert entry["github_url"] == f"{RESEARCH_REPO_BASE}/{entry['result_doc']}"
        assert entry["github_url"].startswith("https://github.com/")


def test_library_entries_include_every_tier_a_and_onboarded_tier_b() -> None:
    entries = library_entries()
    ids = {entry["id"] for entry in entries}
    tier_a_ids = {metadata["strategy_id"] for metadata in STRATEGIES.values()}
    onboarded_tier_b_ids = set(CHARACTERIZATION_STUDIES) - DEFERRED_FROM_RECORD
    assert tier_a_ids <= ids
    assert onboarded_tier_b_ids <= ids
    assert len(entries) == len(STRATEGIES) + len(onboarded_tier_b_ids)


def test_library_entries_are_fully_traceable_or_disclosed_as_not_yet() -> None:
    for entry in library_entries():
        assert entry["tier"] in {"A", "B"}, entry["id"]
        assert entry["type"] in STUDY_TYPES, entry["id"]
        assert entry["category"], entry["id"]
        assert entry["decision"], entry["id"]
        assert entry["summary"], entry["id"]
        if entry["tier"] == "B":
            assert entry["github_url"], entry["id"]
        if entry["tier"] == "A":
            assert entry["origin"] in STRATEGY_ORIGINS, entry["id"]
            # A Tier A strategy with no closed result yet has no artifact to
            # link -- github_url is None, not a broken/fabricated link.
            if entry["github_url"] is not None:
                assert entry["github_url"].startswith("https://github.com/"), entry["id"]


def test_current_provider_mapping_is_explicit() -> None:
    assert dataset_for_provider("yahoo") == "yahoo-adjusted-daily-ohlcv-v1"
    assert dataset_for_provider("fred") == "fred-final-revised-display-v1"


def test_fred_registry_forbids_signal_use_without_point_in_time_data() -> None:
    fred = DATASETS["fred-final-revised-display-v1"]
    assert fred["point_in_time"].startswith("no")
    assert "descriptive display only" in fred["research_use"]
