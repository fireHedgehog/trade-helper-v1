"""Contracts for the deliberately small research metadata registry."""

from app.research_catalog import DATASETS, STRATEGIES, dataset_for_provider
from app.strategies import STRATEGIES as EXECUTABLE_STRATEGIES


def test_every_executable_strategy_has_versioned_metadata() -> None:
    assert set(STRATEGIES) == set(EXECUTABLE_STRATEGIES)
    for name, metadata in STRATEGIES.items():
        assert metadata["strategy_id"]
        assert metadata["version"]
        assert metadata["family"]
        assert metadata["information_profile"]
        assert metadata["evidence"]["status"]
        assert metadata["required_datasets"]
        assert set(metadata["required_datasets"]) <= set(DATASETS), name


def test_current_provider_mapping_is_explicit() -> None:
    assert dataset_for_provider("yahoo") == "yahoo-adjusted-daily-ohlcv-v1"
    assert dataset_for_provider("fred") == "fred-final-revised-display-v1"


def test_fred_registry_forbids_signal_use_without_point_in_time_data() -> None:
    fred = DATASETS["fred-final-revised-display-v1"]
    assert fred["point_in_time"].startswith("no")
    assert "descriptive display only" in fred["research_use"]
