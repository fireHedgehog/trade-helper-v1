# Exploration protocol

Status: required companion to Stage 9A; defines the non-evidential search layer.

## Purpose

Search and validation are separate machines. Search generates and screens candidate ideas cheaply; validation ([model-acceptance-standard.md](model-acceptance-standard.md)) adjudicates one preregistered claim at a time. No output of search carries evidence weight. Only a preregistered Stage 9B result may produce `reject`, `revise`, or `continue research`.

## The attempts ledger

`research/attempts.jsonl` is the authoritative memory of the search machine. Every search run appends one immutable record:

| Field | Requirement |
|---|---|
| `attempt_id` | Unique, permanent identifier. |
| `hypothesis_family` | The economic idea family (e.g. `cta`, `consolidation`, `momentum`). Legacy rows may use `strategy` until migrated. |
| `status` | `exploratory`, `contaminated_exploratory`, `preregistered_no_results`, `development_rejected_insufficient_evidence`, `audit_complete_no_material_defect`, `promoted`. |
| `scope` | Universe, sample, and window actually touched. |
| `result_used_for_defaults` | Whether any default parameter was taken from this run. |
| `variant_count` | Number of specifications or feature combinations actually evaluated. Legacy rows use `candidate_count`. |
| `dependence_group` | Identifier for trials sharing data, features, or construction choices. |
| `note` | Short justification; contamination or inspection history must be disclosed. |

Editing or deleting ledger entries to improve a statistic is contamination. Ledger row count is not $N_{\text{trials}}$: one row may contain many correlated variants, while amendments and audits may contain none. The acceptance protocol constructs and records a conservative effective-trial inventory from `variant_count`, dependence groups, and undocumented-search allowances.

## Search discipline

1. **Search budget.** Declare a per-period cap on exploratory runs and on variants per family. Exceeding the cap is logged, never hidden.
2. **Screen rule.** A cheap screen (in-sample or walk-forward-light) may kill ideas; it may never promote them. Promotion to 9A requires a stated economic mechanism, distinct information, data readiness, and falsifiability — scored under 9A, not by screen performance.
3. **No-touch rule.** Any data inspected during search becomes contaminated for that family's confirmation set. Validation must use untouched point-in-time data.
4. **Multiplicity inheritance.** All logged search and validation variants enter the trial inventory. The correction must reflect dependence and the actual selection statistic; no independent-normal shortcut is binding.
5. **Machine-learning and feature search.** Any ML or high-dimensional search must preregister, before results: feature family, search algorithm, nested validation topology (feature selection inside training folds), and multiplicity control. Unrestricted feature search is prohibited in validation; in search it is exploratory only and inherits the no-touch rule.
6. **Promotion path.** Search survivor → 9A scorecard → if prioritized, preregister per the [protocol template](research-protocol.md) → Stage 9B validation.

## What search may output

- Ideas, non-evidential ranked screens, rationale notes, and candidate nominations for 9A.

It may not output:

- `reject`, `revise`, or `continue research`; the word "alpha"; or any number with evidential status.

## Relationship to contracts

- Multiplicity and deflation: [model-acceptance-standard.md](model-acceptance-standard.md).
- Point-in-time data (macro): [ADR 0006](adr/0006-macro-data-contract.md).
- Thesis operationalization: [hypothesis-engineering.md](hypothesis-engineering.md).
- Immutable evidence: `docs/research-results/` and `output/research/`.
