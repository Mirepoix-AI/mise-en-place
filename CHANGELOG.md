# Changelog

All notable changes to the `mise-en-place` plugin are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/); the
plugin uses [SemVer](https://semver.org/): MAJOR for contract-breaking,
MINOR for behavior additions, PATCH for fixes that don't change behavior.

## [0.4.0] — 2026-05-15

Promotes the multi-agent review face-off pattern to addendum #5 of the
behavioral contract. Behavior addition; no breaking change.

### Added
- **Addendum #5: Multi-agent review** (`PR #N`). When the project being
  operated on declares a reviewer list, high-stakes review and gate work
  dispatches to those reviewers in parallel and requires unanimous APPROVE —
  any REQUEST_CHANGES blocks the phase. The reviewer-identifier vocabulary
  stays project-defined (typically a `## Multi-agent review` section in the
  project's `CLAUDE.md`); the contract specifies the dispatch and
  reconciliation shape only. Added to
  `skills/mise-en-place/references/contract.md` §6 alongside the four
  starter addenda.
- **`MODES.md` cross-references** (`PR #N`). One-sentence pointers in the
  `review` and `ship` mode sections noting the multi-agent dispatch when
  the project declares a reviewer list. The modes themselves are unchanged —
  the addendum operates on top of modes, not as one.
- **`SKILL.md` enumeration update** (`PR #N`). The "What to load" section
  now lists five starter addenda (Skills, Evaluation packs, Meta-agent
  decomposition, ADRs, Multi-agent review) instead of four.
- **`README.md` enumeration update** (`PR #N`). The opening bullet that
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
