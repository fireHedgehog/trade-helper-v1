"""Run Fed put: yield-stress precursor v3.

Usage (from backend/):
    python -m app.run_fed_put_yield_stress_precursor_v3

Implements docs/research-protocols/fed-put-yield-stress-precursor-v3.md.
Amends v2 (closed not_evaluable) -- only the z-score lookback changes
(756 -> 5040 sessions, ~3yr -> ~20yr); same score formula, same 6
episodes, same machinery. Thesis Track evidence-layer output only
(not_evaluable / weak_evidence / evidence_present) -- no trade, no
Stage 9B authorization, no signal.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import numpy as np

from .run_experiment import _atomic_json
from .store import load_bars
from .thesis_track import thesis_track_p_value, trailing_zscore, yield_stress_score

ROOT = Path(__file__).parents[2]
SPEC_PATH = ROOT / "research/experiments/fed-put-yield-stress-precursor-v3.json"
SPEC_SHA256 = "fb1aa71f36715f66c2bb854d1614aa2b5108e25b44cd10d81b6c16a1bf0a0616"


def canonical_spec_sha256(spec: dict) -> str:
    encoded = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_locked_spec(spec: dict) -> None:
    spec_sha = canonical_spec_sha256(spec)
    if spec_sha != SPEC_SHA256:
        raise RuntimeError(f"locked specification identity failed: expected {SPEC_SHA256}, got {spec_sha}")


def load_aligned_yields(spec: dict) -> tuple[dict, list[str]]:
    symbols = list(spec["universe"])
    bars = {symbol: load_bars(symbol) for symbol in symbols}
    common_dates = sorted(set.intersection(*(set(df["date"]) for df in bars.values())))
    aligned = {
        symbol: bars[symbol].set_index("date").loc[common_dates].reset_index()
        for symbol in symbols
    }
    return aligned, common_dates


def data_sha256(spec: dict, aligned: dict) -> str:
    digest = hashlib.sha256()
    for symbol in list(spec["universe"]):
        for row in aligned[symbol].itertuples(index=False):
            digest.update(symbol.encode() + b"\0" + str(row.date).encode() + b"\0")
            digest.update(struct.pack(">d", row.close))
    return digest.hexdigest()


def _date_index(dates: list[str], target: str) -> int:
    """Index of the last trading day <= target."""
    candidates = [i for i, d in enumerate(dates) if d <= target]
    if not candidates:
        raise ValueError(f"no trading day on or before {target}")
    return candidates[-1]


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    validate_locked_spec(spec)

    aligned, dates = load_aligned_yields(spec)
    data_sha = data_sha256(spec, aligned)

    lookback = spec["score"]["lookback_sessions"]
    window = spec["estimand"]["precursor_window_sessions"]
    buffer = spec["inference"]["exclusion_buffer_sessions"]
    resamples = spec["inference"]["resamples"]
    seed = spec["inference"]["seed"]

    y2 = aligned["DGS2"]["close"].to_numpy(dtype=float)
    y10 = aligned["DGS10"]["close"].to_numpy(dtype=float)
    z2 = trailing_zscore(y2, lookback)
    z10 = trailing_zscore(y10, lookback)
    score = yield_stress_score(z10, z2)

    offset = lookback
    truncated_score = score[offset:]
    n_dates = len(truncated_score)
    last_index_truncated = n_dates - 1

    def statistic_for_window(start: int, end: int) -> float:
        return float(np.max(truncated_score[start:end]))

    episode_windows = []
    excluded_ranges = []
    episode_records = []
    for episode in spec["episodes"]:
        start_idx = _date_index(dates, episode["start"]) - offset
        end_idx = (
            _date_index(dates, episode["end"]) - offset
            if episode["end"] is not None
            else last_index_truncated
        )
        precursor_start, precursor_end = start_idx - window, start_idx
        if precursor_start < 0:
            raise RuntimeError(f"{episode['name']}: precursor window predates available lookback-adjusted history")
        episode_windows.append((precursor_start, precursor_end))
        excluded_ranges.append((precursor_start - buffer, end_idx + buffer))
        episode_records.append({
            "name": episode["name"], "start": episode["start"], "end": episode["end"],
            "fed_framing": episode["fed_framing"],
        })

    real_statistics = [statistic_for_window(s, e) for s, e in episode_windows]
    for record, stat in zip(episode_records, real_statistics):
        record["max_score_in_precursor_window"] = stat

    result = thesis_track_p_value(
        real_statistics, statistic_for_window,
        n_dates=n_dates, window_length=window, excluded_ranges=excluded_ranges,
        resamples=resamples, seed=seed,
    )

    p_value = result["p_value"]
    if p_value <= 0.10:
        decision = "evidence_present"
    elif p_value <= 0.30:
        decision = "weak_evidence"
    else:
        decision = "not_evaluable"

    output = ROOT / "output/research/fed-put-yield-stress-precursor-v3" / SPEC_SHA256
    _atomic_json(
        output / "manifest.json",
        {
            "experiment_id": spec["experiment_id"],
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "common_date_start": dates[0],
            "common_date_end": dates[-1],
            "common_date_count": len(dates),
            "no_trade": True,
            "actual_costs_or_execution_accessed": False,
        },
    )
    _atomic_json(
        output / "episode-results.json",
        {"episodes": episode_records, "n_episodes": len(episode_records)},
    )
    _atomic_json(
        output / "decision.json",
        {
            "decision": decision,
            "spec_sha256": SPEC_SHA256,
            "data_sha256": data_sha,
            "observed_mean_statistic": result["observed_mean_statistic"],
            "p_value": p_value,
            "resamples": result["resamples"],
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "data_sha256": data_sha,
                "decision": decision,
                "p_value": p_value,
                "observed_mean_statistic": result["observed_mean_statistic"],
                "episodes": episode_records,
            },
            sort_keys=True,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
