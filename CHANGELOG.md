# Changelog

All notable changes to the `mise-en-place` plugin are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/); the
plugin uses [SemVer](https://semver.org/): MAJOR for contract-breaking,
MINOR for behavior additions, PATCH for fixes that don't change behavior.

## [0.5.1] — 2026-05-20

Clarifies Principle 5 (Justified Action / Five Whys) with an explicit binding rule for destructive operations: the **canonical-state-verification iteration** is mandatory in the forward chain before `git tag`, schema migration, deployment, or any irreversible operation. Patch release — no new behavior, no API change, no contract restructure; existing principle's application made operational.

Empirical motivation: the canonical-state-divergence failure-mode class (untracked files aborting `git pull`, stale local main, framework-convention mismatches, deferred file skeletons) produced five documented incidents across the 2026-05-20 ADR-016 rollout (four during the rollout itself per ADR-016 §"Consequences" eighth point + memory `feedback_canonical_state_canvas.md`) plus one external instance (kirk-stub-realistic v0.2.3 mis-tag, 2026-05-20). All five share shape: local state silently diverged from canonical; operation succeeded structurally; the divergence shipped. Auditability note: the four ADR-016-documented incidents and the memory file live in the private `kavara-mirepoix-internal` repo and are not directly inspectable from this public repository; the kirk-stub-realistic v0.2.3 anchor is the publicly verifiable one via that repo's tag history.

The Layer 1 release-pipeline wrapper `UlyssesModel/on-loop/bin/on-loop-tag` (PR #2, 2026-05-20) is the reference implementation for the discipline applied to `git tag` operations. The shell script's eight pre-flight checks are the canonical pattern; future destructive-op tools follow the same shape.

### Changed

- **`skills/mise-en-place/references/contract.md` §5 Forward** — new sub-section "Mandatory iteration for destructive operations" adds the canonical-state-verification rule as a binding part of the forward Five Whys chain whenever the proposed action is destructive or irreversible. Cross-references the on-loop-tag reference implementation.
- **`skills/mise-en-place/references/contract.md` §6b `migrate` mode #5 override** — explicit reference to the canonical-state-verification iteration as mandatory before applying the migration.
- **`skills/mise-en-place/references/contract.md` §6b `ship` mode #5 override** — explicit reference to the canonical-state-verification iteration as mandatory before destructive operations in the ship path (tag creation, release publication, image push).
- **`.claude-plugin/plugin.json`** — version 0.5.0 → 0.5.1.

### Not changed

- Principle 5 text itself (the forward + backward + posture sub-disciplines) is unchanged. v0.5.1 only adds the mandatory-iteration sub-section.
- Mode signature table, mode-override paragraphs for `build`/`explore`/`harden`/`firefight`/`review`/`refactor` — unchanged.
- Section numbering (5/6/7/8) — unchanged.
- Addenda — unchanged. The Multi-agent review addendum (#5 per v0.4.0) does not move; new amendment is at the principle layer.
- LICENSE attribution — unchanged.
- CI validator — unchanged. The Principle 5 invariant check still asserts `## 5. Justified Action` heading exists; the new sub-section is below the heading.

### Sequencing

| Version | Subject | Status |
|---|---|---|
| v0.4.0 | Addendum #5: Multi-agent review | Shipped 2026-05-15 |
| v0.5.0 | Principle 5: Justified Action | Shipped 2026-05-20 (PR #6) |
| **v0.5.1** | **Principle 5 clarification: canonical-state-verification iteration for destructive ops** | **This release** |
| v0.6.0 | Addendum #6: DDD vocabulary discipline (ADR-014 Follow-up 2) | Future |

### Follow-up

- `UlyssesModel/on-loop` README cross-reference (one-line addition under the "Safe release tagging" section pointing back at mise-en-place §5 Forward) lands in a small follow-up PR after this release stabilizes. Tracked as part of the v0.5.1 rollout discipline.

### Architectural authority

ADR-016 (`adrs/ADR-016-mise-en-place-principle-5.md` in `kavara-mirepoix-internal`) authorizes Principle 5; v0.5.1 is a clarification within that authorization, not a new architectural commitment. No new ADR required per ADR-014's three-criteria gate (not hard-to-reverse beyond the existing v0.5.0 contract; not surprising-without-context given the canonical-state-canvas memory; trade-off is between explicit binding rule and implicit-inference-from-principle-text — chose explicit per ADR-016's eighth consequence lesson). Auditability note: ADR-014 and ADR-016 themselves live in the private `kavara-mirepoix-internal` repo and are not directly inspectable from this public repository; the three-criteria gate is summarized inline above so public-repo readers can evaluate the no-new-ADR call on its merits.

## [0.5.0] — 2026-05-20

Adds the fifth foundational principle: **Justified Action / Five Whys**. The principle is Mirepoix-augmented from Amazon's Well-Architected framework, elevated to the same structural layer as Karpathy's four (the "fixed invariants" tier). Architectural authority: [ADR-016 in kavara-mirepoix-internal](https://github.com/UlyssesModel/kavara-mirepoix-internal/blob/main/adrs/ADR-016-mise-en-place-principle-5.md).

The principle covers both forward justification (articulate the why-chain before substantive work) and backward causal analysis (apply five whys to failures, refusing "human error" as a terminal explanation). The discipline is procedural: blame the system, never the operator; five iterations is the floor, not a ceiling.

### Added

- **Principle 5 — Justified Action** (new Section 5 in `skills/mise-en-place/references/contract.md`). Forward and backward applications, posture rules, mode-specific overrides for all eight modes.
- **#5 column** in the mode signature table. Five-principle matrix replaces the prior four-principle matrix.
- **New load-bearing oddity** in MODES.md: `firefight` is the only mode where #5 defers entirely (causal analysis happens in the postmortem, not during the incident).
- **`firefight` postmortem now requires the five-whys causal chain**, not just a chronology. Codified in the mode's postcondition.
- **`review` mode reviewers (including multi-agent review per v0.4.0 addendum #5) now apply Principle 5 to findings** — every flagged finding traces to at least one iteration of why. "This looks wrong" is insufficient without one iteration of why beneath it.
- **CI invariant check** (`validate_plugin.py` extension): asserts contract.md contains the "## 5. Justified Action" heading. Stdlib-only, follows the existing 22-test pattern (now 28 tests including the new `TestPrinciple5Invariant` class).
- **LICENSE attribution** for Five Whys (Amazon's Well-Architected framework) added alongside the existing Karpathy attribution.

### Changed

- **Contract sectioning renumbered**: Section 5 (Modes) → 6, Section 6 (Mirepoix Addenda) → 7, Section 7 (Acceptance Test) → 8. The v0.4.0 addendum #5 (Multi-agent review) is preserved verbatim in the new Section 7.
- **MODES.md cross-references** updated from §5b to §6b throughout. The two `ship` and `review` mode cross-refs to the Multi-agent review addendum updated from §6 to §7.
- **README.md "four principles" framing** restructured to "five principles, eight modes, five addenda."
- **SKILL.md activation flow** now surfaces Principle 5 alongside the active-mode elicitation. "Sections 1-4" → "Sections 1-5"; "Section 5b" → "Section 6b"; "Section 6" addenda reference → "Section 7."
- **plugin.json description** updated to enumerate five principles + five addenda.

### Sequencing context

| Version | Subject | Date |
|---|---|---|
| v0.3.0 | Slash command surface | 2026-05-09 |
| v0.4.0 | Addendum #5: Multi-agent review | 2026-05-15 |
| **v0.5.0** | **Principle 5: Justified Action (this release)** | **2026-05-20** |
| v0.6.0 | Addendum #6: DDD vocabulary discipline (ADR-014 Follow-up 2) | Future |

### Notes for operators

- Existing memory of "Karpathy four" remains correct — the four principles are unchanged. The addition is "Karpathy four PLUS Kavara's fifth."
- Existing memory of "Section 5 is Modes" is invalidated; Modes is now Section 6. The brief friction is acceptable per ADR-016's first consequence; the alternative (calling the new principle "Section 4.5") was rejected as structurally awkward.
- Operators in `explore` mode can defer the why-chain to the mode-exit writeup; in `firefight`, the chain is deferred to the postmortem; everywhere else, the chain is active.
- Multi-agent review (addendum #5 from v0.4.0) and Principle 5 reinforce each other: reviewers articulate why-chains for findings (one iteration floor per `review` mode override); the operator reconciles disagreements via "act on finding" default rooted in why-chain analysis.

### Architectural authority

[ADR-016 — mise-en-place Principle 5 — Justified Action](https://github.com/UlyssesModel/kavara-mirepoix-internal/blob/main/adrs/ADR-016-mise-en-place-principle-5.md) is the canonical decision. The fork-shaped commitment is explicit and ADR-authorized per ADR-014's Generic Domain principle ("Vocabulary divergence from upstream is itself an ADR-worthy decision").

## [0.4.0] — 2026-05-15

Promotes the multi-agent review face-off pattern to addendum #5 of the
behavioral contract. Behavior addition; no breaking change.

### Added
- **Addendum #5: Multi-agent review** (`PR #5`). When the project being
  operated on declares a reviewer list, high-stakes review and gate work
  dispatches to those reviewers in parallel and requires unanimous APPROVE —
  any REQUEST_CHANGES blocks the phase. The reviewer-identifier vocabulary
  stays project-defined (typically a `## Multi-agent review` section in the
  project's `CLAUDE.md`); the contract specifies the dispatch and
  reconciliation shape only. Added to
  `skills/mise-en-place/references/contract.md` §6 alongside the four
  starter addenda.
- **`MODES.md` cross-references** (`PR #5`). One-sentence pointers in the
  `review` and `ship` mode sections noting the multi-agent dispatch when
  the project declares a reviewer list. The modes themselves are unchanged —
  the addendum operates on top of modes, not as one.
- **`SKILL.md` enumeration update** (`PR #5`). The "What to load" section
  now lists five starter addenda (Skills, Evaluation packs, Meta-agent
  decomposition, ADRs, Multi-agent review) instead of four.
- **`README.md` enumeration update** (`PR #5`). The opening bullet that
  names the four Mirepoix-native addenda now names five.

### Notes
- **Promotion criteria.** The pattern meets all three gates from §6:
  *universally applicable* (any review work benefits — gates, PRs, design
  reviews, ADR reviews), *foundational* (review is part of every coding
  workflow), *non-obvious* (single-reviewer dispatch is the default agent
  behavior; parallel dispatch with unanimity is not).
- **Empirical evidence.** Promoted on the strength of two PR-level
  face-offs in `UlyssesModel/kavara-mirepoix-internal`:
  - **PR #11** (codex-teammate spec) — Codex caught vocabulary
    inconsistencies and deliverables-convention compliance gaps that the
    first reviewer had APPROVE'd past.
  - **PR #12** (codex-events / Issue #10) — Codex caught a
    verdict-vocabulary mix (source vs. gate-normalized), an ADR-005
    audit-envelope violation, a state-machine completeness bug (3-of-5
    rescue states), and three missing fields. The first reviewer had
    APPROVE'd without raising any of these.
  - Two-for-two on real architectural issues caught by the second
    reviewer. Earned promotion to the contract.
- **No implementation in this plugin.** The contract codifies the
  behavioral commitment; dispatch and reconciliation live in downstream
  tooling (on-loop, future Kavara extensions). This is a markdown-only
  release.
- **Version bump.** `0.3.0` → `0.4.0` in both
  `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
  MINOR per SemVer (behavior addition).

## [0.3.0] — 2026-05-09

Adds the slash-command surface that the skill description has always promised.

### Added
- **`/mise-en-place` slash command** (`PR #4`). The skill description in
  `skills/mise-en-place/SKILL.md` has always referenced typing
  `/mise-en-place` or `/mise-en-place mode [name]` as activation paths,
  but the plugin shipped without a `commands/` entry — meaning the
  slash form returned `Unknown command` and the only working invocation
  was natural-language ("activate the mise-en-place skill"). This adds
  `commands/mise-en-place.md` so the slash form now resolves correctly.
  - `/mise-en-place` (no args) — default elicitation flow per the skill.
  - `/mise-en-place mode <name>` (one of the eight) — direct activation
    in the named mode without re-eliciting.
  - Anything else after `/mise-en-place` — treated as operator
    commentary; the agent confirms intent.

  Surfaces the contract in the same shape skills already do; the skill
  remains the source of truth for the eight modes and the contract
  semantics. The slash command is a thin invocation wrapper.

## [0.2.0] — 2026-05-09

First behavior-changing release since the initial commit. Combines the
placeholder fix, the CI validator that prevents the same class of bug
from recurring, and the MODES.md quick-reference card.

### Added
- **CI validator** (`PR #1`). New `.github/workflows/validate.yml` and
  `.github/scripts/validate_plugin.py` run on every push and PR-to-main.
  Three checks: JSON manifest validity, SKILL.md frontmatter integrity
  (rejects XML-like tags in description fields), and relative-reference
  resolution for backtick-quoted `.md` citations inside SKILL.md bodies.
  22 unittest cases. Stdlib only — no install step.
- **`MODES.md`** (`PR #2`). Quick-reference card at the repo root for
  the eight Mirepoix operating modes (`build`, `explore`, `harden`,
  `ship`, `firefight`, `review`, `migrate`, `refactor`). Layout: top
  comparison table for the scan layer, eight short anchored cards for
  deep-linking. The contract at
  `skills/mise-en-place/references/contract.md` §5b remains the source
  of truth; this page is the index.
- **Cross-links to MODES.md** (`PR #2`). New "Modes" section in
  `README.md` between Usage and Invariants, plus a row in the
  Repository-structure table. One pointer line appended in
  `skills/mise-en-place/SKILL.md` after the activation bullets.

### Fixed
- **Placeholder syntax in SKILL.md description** (commit `fcb93f5`,
  pre-version-bump). Replaced `<name>` and `<mode>` (XML-like, tripped
  Cowork's plugin validator) with `[name]` and `[mode]`. The new CI
  validator above prevents this regression class from recurring.

### Notes
- Version was not bumped at the time of `fcb93f5` or `PR #1`. This is
  the first cumulative bump since `0.1.0`. Going forward, behavior
  changes bump the version in the same PR — see candidate addendum
  tracking in operator memory.

## [0.1.0] — 2026-05-08

Initial release.

### Added
- The Mirepoix behavioral contract (`skills/mise-en-place/SKILL.md`
  and `skills/mise-en-place/references/contract.md`): four principles,
  eight modes, four starter addenda.
- Plugin manifest (`.claude-plugin/plugin.json`) and marketplace
  manifest (`.claude-plugin/marketplace.json`).
- Repo-root `mise-en-place.md` symlink to the contract for browse
  convenience.
- `LICENSE` (proprietary, Kavara) with upstream Karpathy attribution.
