# Changelog

All notable changes to the `mise-en-place` plugin are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/); the
plugin uses [SemVer](https://semver.org/): MAJOR for contract-breaking,
MINOR for behavior additions, PATCH for fixes that don't change behavior.

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
