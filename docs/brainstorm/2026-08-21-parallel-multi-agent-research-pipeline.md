Brainstorm · non-evidential · loaded only on explicit request · no acceptance weight.

# Parallel multi-agent research pipeline ("industrialized assembly line")

Raised 2026-08-21, after Chapter 4's first pass closed and ADR 0008 (bounded
paper trading, plus Track B) was drafted. User's framing: since no chapter
in [research-program.md](../research-program.md) is ever "closed" — they're
explicitly living/extensible — could multiple parallel agents (potentially
across multiple accounts/sessions) each own a different chapter or task
concurrently: one kept falsifying new Chapter 1 candidates, another ranking
Chapters 1–3's closed candidates by IC (information coefficient) from high
to low and feeding the best into Chapter 4 systematically, another working
Chapter 5's operational build-out — a real "industrialized assembly line"
instead of one agent working sequentially.

User's own framing of timing: this is real, wanted eventually ("I would
eventually detangle it to be independent microservices"), but explicitly a
foreseeable-future item, "at least half a year" out — not something to
build now. Parked here rather than acted on.

## The core risk, named before parking

Independent *production* (running detector scripts, scoring independent
candidates, locking independent specs) parallelizes safely — each writes
its own output file, no shared state. The risk is entirely in the *shared
ledger*: `research-program.md`'s chapter tables, `docs/README.md`'s
checkpoint, `CHANGELOG.md`, `backend/app/version.py`. The 2026-08-21 audit
(three parallel lenses: numbering/versions, cross-references,
redundancy/bloat) found and fixed real drift — 11 broken links, a stale ADR
status header, future-tense text describing already-scored candidates, a
17-versions-stale roadmap line — produced by *one* agent working
sequentially across one long session. Several agents writing to the same
ledger files concurrently, without coordination, would produce the same
class of defect at a larger scale and a harder-to-untangle one: numbering
collisions (two agents both claiming the next `§N` in the same chapter),
version-bump races, and git merge conflicts on the same lines.

## The shape of a safe version, if this gets picked up later

**Parallel production, single integration** — not full parallel writes to
the shared ledger:

- Independent agents run in isolated environments (git worktrees — the
  `isolation: "worktree"` option already available to this session's Agent
  tool is a natural fit) so concurrent code/detector changes don't collide.
  `data/market.db` is gitignored and won't come along automatically with a
  worktree checkout; each worktree needs its own copy, or a shared
  read-only mount — an unresolved detail, not yet designed.
- Each agent produces a self-contained result: a locked spec, a result
  file, a candidate write-up — never edits `research-program.md`,
  `docs/README.md`, `CHANGELOG.md`, or `version.py` directly.
- One integration pass (one agent, one session, sequential) folds each
  finished result into the shared ledger, one at a time — the same
  discipline already used throughout this project's single-agent sessions,
  just performed as a distinct final step rather than interleaved with
  production.
- This is the same shape a real assembly line actually has: parallel
  production stations feeding one final inspection/assembly line, not
  several stations bolting parts onto the same chassis at once.

## Separate, smaller idea worth doing without solving any of the above

Rank Chapters 1–3's closed candidates by IC (or whatever comparable
per-candidate statistic each closed result already reports) from high to
low, and feed the highest-ranked into Chapter 4's scoring pipeline
systematically, rather than the ad hoc pickup order used so far (CTA v2,
Wave Pull, Calendar Day-of-Week). This doesn't require solving the
multi-agent/parallelization question — it's a single-agent, mechanical
next step, independently useful. Not started as of this memo.
