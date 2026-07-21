# Spec: CI validation workflow for mise-en-place

## Goal

Add CI to the mise-en-place repo that catches the validator-rejection class of bug we hit in commit `fcb93f5` (XML-like tag in SKILL.md frontmatter description tripped Cowork's plugin validator). The CI runs on every push and PR and combines focused repository checks with Claude Code's official strict validator and a Cowork archive-content regression check.

## Checks

### 1. JSON manifest validity

Validate `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`:

- Both files exist.
- Both parse as valid JSON.
- `plugin.json` has required fields: `name`, `version`, `description`.
- `marketplace.json` has required fields: `name`, `description`, `owner`, `plugins` (non-empty array).
- Each entry in `marketplace.json`'s `plugins` array has `name`, `source`, `description`.
- The marketplace entry's `name` and `version` match `plugin.json`.
- The `name` field in both files is kebab-case (lowercase letters, numbers, hyphens only).

### 2. SKILL.md frontmatter integrity

For every `skills/*/SKILL.md` file in the repo:

- Frontmatter exists (between two `---` delimiters at the top of the file).
- Frontmatter parses as valid simple-YAML (single-line `key: value` pairs only — no nested structures expected at this stage).
- Required keys present: `name`, `description`.
- The `description` value contains no XML-like tags. Regex: `<[a-zA-Z][a-zA-Z0-9_-]*>`. Use `[name]` / `[mode]` placeholder syntax instead.

This is the bug from commit `fcb93f5`. Cowork's plugin validator rejected the SKILL.md description because it contained `<name>`. We replaced angle-bracket placeholders with square-bracket ones; CI should prevent regression.

### 3. Relative reference integrity

For every `skills/*/SKILL.md` file:

- Find all backtick-quoted relative paths in the body that look like file references — ends in `.md`, no leading `/`, no URL scheme.
- For each match, resolve the path relative to the SKILL.md's location.
- Confirm the resolved file exists in the repo.

This catches the kind of break we'd cause if someone moved `references/contract.md` without updating the SKILL.md references.

### 4. Official strict validation

Run `npx --yes @anthropic-ai/claude-code@2.1.216 plugin validate . --strict` so warnings accepted by the runtime cannot drift into a release.

### 5. Cowork archive contents

Build the documented `.plugin` archive and verify it contains both activation surfaces: `skills/mise-en-place/SKILL.md` and `commands/mise-en-place.md`, plus both manifests and the canonical contract.

## Implementation

### Files to create

| Path | Purpose |
|------|---------|
| `.github/workflows/validate.yml` | GitHub Actions workflow definition |
| `.github/scripts/validate_plugin.py` | Validation script (entry point) |
| `.github/scripts/test_validate_plugin.py` | Tests for the validation script |
| `scripts/build_cowork_bundle.py` | Reproducible Cowork archive builder and inspector |
| `.github/scripts/test_build_cowork_bundle.py` | Archive-content regression tests |

### Constraints

- **Python 3.11+, standard library only for repository-owned validation and packaging.** No `pip install` step. Use `json`, `pathlib`, `re`, and `zipfile`. For SKILL.md frontmatter parse a hand-rolled minimal-YAML reader that handles single-line `key: value` pairs only — that's all the frontmatter actually contains. The separately pinned Claude Code CLI is the official-validator dependency.
- **Tests use `unittest`** (stdlib), not pytest. Same dependency-minimization reasoning.
- **Validator exits 1 on any failure**, with a clear human-readable error message naming the file and the failing check (e.g. `skills/mise-en-place/SKILL.md: description contains XML-like tag <test>`).
- **Workflow uses `actions/checkout@v4` and `actions/setup-python@v5`.**

### Workflow triggers

- `push` to any branch.
- `pull_request` against `main`.

## Acceptance criteria

1. `python .github/scripts/validate_plugin.py` exits 0 on the current repo HEAD.
2. Temporarily adding `<test>` to `skills/mise-en-place/SKILL.md`'s frontmatter description, then re-running the validator, exits 1 with a message naming the file and the offending tag.
3. Temporarily renaming `skills/mise-en-place/references/contract.md` to something else, then re-running the validator, exits 1 with a message about the missing reference.
4. `python -m unittest discover .github/scripts -p 'test_*.py'` exits 0 with at least 5 test cases covering: valid manifests, invalid JSON, missing required fields, XML-like tag in description, broken relative reference.
5. `npx --yes @anthropic-ai/claude-code@2.1.216 plugin validate . --strict` exits 0.
6. The built Cowork archive contains `commands/mise-en-place.md` as well as the skill and manifest surfaces.
7. The workflow runs on a real GitHub push and reports pass/fail in the PR/commit checks UI.

## Out of scope

- Markdown linting on README.md and LICENSE.
- Commit-message or branch-name conventions.
- External-link checking (slow and flaky).
- Validating any future skills' more-complex YAML frontmatter (multi-line values, lists, nested keys). If/when that becomes needed, swap the hand-rolled parser for `pyyaml` and accept the install step.

## Lineage

Authored 2026-05-08 in response to commit `fcb93f5`, which is itself the regression-fix commit for the validator-rejection bug this CI is designed to prevent.
