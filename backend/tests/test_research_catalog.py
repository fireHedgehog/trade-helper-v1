"""Contracts for the research metadata registry, including the ADR 0009
Tier A (executable) / Tier B (characterization-only) separation."""

from pathlib import Path

from app.research_catalog import (
    CHARACTERIZATION_STUDIES,
    DATASETS,
    DECISIONS,
    STRATEGIES,
    characterization_studies,
    dataset_for_provider,
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


def test_current_provider_mapping_is_explicit() -> None:
    assert dataset_for_provider("yahoo") == "yahoo-adjusted-daily-ohlcv-v1"
    assert dataset_for_provider("fred") == "fred-final-revised-display-v1"


def test_fred_registry_forbids_signal_use_without_point_in_time_data() -> None:
    fred = DATASETS["fred-final-revised-display-v1"]
    assert fred["point_in_time"].startswith("no")
    assert "descriptive display only" in fred["research_use"]
