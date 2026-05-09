# Implementation plan — validate-ci

Source spec: `specs/validate-ci.md`
Architect blueprint: `.on-loop/sessions/20260509_025649_validate-ci/agent-notes/architect.md`
Branch / worktree: `on-loop/validate-ci` @ `.claude/worktrees/validate-ci`

## Operator-set guardrails (read first, downstream agents)

1. **Stdlib only — no `pip install`.** The hand-rolled YAML reader is intentional. If you find yourself wanting `pyyaml`, stop — the spec already names it as the future-escape only when the YAML subset outgrows single-line `key: value`.
2. **Bounded-scope mitigation defends the regex parser.** Security agent: yes, regex-based YAML is fragile in the abstract. The mitigation is the bounded subset. Don't recommend swapping to a real parser unless input shape genuinely expands.
3. **Do not validate the root-level `mise-en-place.md`.** It's a symlink to `skills/mise-en-place/references/contract.md`. Following it would double-count. The validator's `find_skill_files` already scopes to `skills/*/SKILL.md`, which excludes the symlink — keep it that way.

## Files to create

| Path | Builder | Notes |
|------|---------|-------|
| `.github/scripts/validate_plugin.py` | coding | Entry point; pure-function checks; `main()` aggregates. |
| `.github/scripts/test_validate_plugin.py` | coding | `unittest`; ≥16 cases per blueprint §4; uses `tempfile.TemporaryDirectory`. |
| `.github/workflows/validate.yml` | coding | Per blueprint §5; pin `python-version: '3.11'`; run validator then tests; `if: always()` on the test step so both report. |

No other files modified.

## Implementation order (single agent, sequential)

1. Write `.github/scripts/validate_plugin.py` with the function decomposition from blueprint §1 (constants, `find_skill_files`, `parse_frontmatter`, `validate_plugin_json`, `validate_marketplace_json`, `extract_md_references`, `validate_skill_frontmatter`, `validate_skill_references`, `main(argv)` with optional `--repo-root` flag).
2. Write `.github/scripts/test_validate_plugin.py` covering the 16 cases mapped in blueprint §4. Tests must:
   - Use `tempfile.TemporaryDirectory` for fixtures.
   - Never read or mutate the real repo.
   - Assert on exact error-message substrings from the blueprint §1 format table.
3. Write `.github/workflows/validate.yml` per blueprint §5.

## Verification (testing agent)

Run inside the worktree:

- `python3 .github/scripts/validate_plugin.py` → exit 0 (AC#1).
- Inject `<test>` into `skills/mise-en-place/SKILL.md` description, re-run → exit 1, message contains `description contains XML-like tag <test>` (AC#2). Restore.
- Rename `skills/mise-en-place/references/contract.md` → re-run → exit 1, message contains `broken reference 'references/contract.md'` (AC#3). Restore.
- `python3 -m unittest discover .github/scripts -p 'test_*.py'` → exit 0, ≥5 tests pass (AC#4). Local interpreter is `python3.12` (3.11+ — spec floor).
- AC#5 (workflow on real GitHub) is verified post-merge in CI.

Test the validator-rejection regressions destructively but non-destructively: copy the file, mutate the copy, point the validator at a temp dir — OR mutate in-place and `git checkout` to restore. Whichever is cleaner; do not leave the worktree dirty.

## Error-message format contract (locked — tests assert on this)

```
{repo_relative_path}: {check_name}: {detail}
```

Specific substrings tests must pass for:

- `description contains XML-like tag <{tag}>` — AC#2
- `broken reference '{ref}'` — AC#3
- `missing required field '{field}'` — AC#4
- `invalid JSON` — AC#4
- `not kebab-case`

## Constraints (do not relax)

- Python 3.11+, stdlib only. No external imports beyond `argparse`, `json`, `pathlib`, `re`, `sys`, `io`, `tempfile`, `unittest`.
- `actions/checkout@v4` and `actions/setup-python@v5` exact versions.
- Triggers: `push` (any branch) + `pull_request` against `main`.
- Validator exits 1 on any failure; exit 2 reserved for unhandled exceptions.
- Path printing: use `Path.relative_to(REPO_ROOT).as_posix()` for cross-platform-stable error lines (blueprint §6.6).

## Out of scope

Per spec §"Out of scope": markdown linting, commit/branch conventions, external link checking, complex YAML.
Also: do **not** add validation of root-level `mise-en-place.md` (symlink — see guardrail #3).

## Risks / open items the testing agent should confirm

- `if: always()` on test step — recommended yes; coding agent please include.
- Conservative reference matcher ignores `[text](path.md)` — flagged in operator notes; not a defect.
- Symlinks at the discovery root: `find_skill_files` globs `skills/*/SKILL.md`, doesn't follow root-level symlinks — correct by construction.

## Acceptance-criterion traceability

| AC | Verified by |
|----|-------------|
| #1 | CI step "Run validator" + local pre-flight `python3 .github/scripts/validate_plugin.py` |
| #2 | Test `test_xml_tag_in_description_fails` + spec-described manual injection |
| #3 | Test `test_broken_reference_fails` + spec-described rename |
| #4 | `python -m unittest discover .github/scripts -p 'test_*.py'` |
| #5 | First push of this branch reports pass/fail in PR checks UI |
