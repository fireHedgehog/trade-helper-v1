# Audits

Status: non-contract leaf. Point-in-time reviews of the codebase and research
methodology — not evidence, not a decision, not a preregistration, not a research
result. Zero acceptance weight. A finding becomes actionable only when separately
triaged into the roadmap, backlog, or a versioned ADR/protocol amendment. Loaded
only on explicit author request ("recall audit …"); ignored during ordinary resume,
planning, implementation, and research work. Do not load or re-audit this folder
unless the user explicitly asks for an audit or names a finding.

Purpose: external/self-review record upstream of the machine. An audit grants
nothing on its own — a defect becomes a fix via the normal roadmap; a methodology
critique becomes a decision only via the same preregistration/ADR discipline
everything else here requires. This folder exists so review work has somewhere to
live without being mistaken for [research-results](../research-results/) (locked
evidence) or [brainstorm](../brainstorm/) (idea generation upstream of hypothesis
engineering) — an audit reviews what already exists against what the project
claims about itself, at one point in time and one version. It is scoped to that
version; it does not track the codebase as it changes.

Template: `YYYY-MM-DD-topic.md`, first line:

> Audit · non-contract leaf · point-in-time review against vX.Y.Z · loaded only on
> explicit request · no acceptance weight until findings are separately triaged.

## Index

| Date | Version reviewed | Topic | File |
|---|---|---|---|
| 2026-08-19 | 0.37.1 | Methodology and implementation audit — CTA v1 power analysis; ADR/product-contract conformance across research, execution, and API layers | [2026-08-19-methodology-and-implementation-audit.md](2026-08-19-methodology-and-implementation-audit.md) |
