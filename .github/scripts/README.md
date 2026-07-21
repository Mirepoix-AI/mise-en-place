# .github/scripts — Plugin validation

## What the validator checks

`validate_plugin.py` runs five checks against the repo on every CI invocation.

**1. JSON manifest validity** — both `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` must exist, parse as valid JSON, contain
required fields, and have kebab-case `name` values. The marketplace itself
requires a `description`; each entry in its `plugins` array must have `name`,
`source`, and `description`.

**2. Manifest parity** — the single marketplace entry must match the canonical
plugin manifest's `name` and `version`.

**3. SKILL.md frontmatter integrity** — for every `skills/*/SKILL.md`:
- frontmatter block (`--- ... ---`) is present and parses cleanly as flat
  single-line `key: value` pairs,
- `name` and `description` keys are present,
- `description` contains no XML-like tags matching `<[a-zA-Z][a-zA-Z0-9_-]*>`.

This check exists specifically to catch a regression introduced in commit
`fcb93f5`, where angle-bracket placeholders in the description caused
Cowork's plugin validator to reject the plugin.

**4. Relative reference integrity** — every backtick-quoted `.md` path in a
SKILL.md body that looks like a local file reference must resolve to an
existing file on disk. Absolute paths and URL-scheme strings are ignored.
Fenced code blocks are stripped before scanning to avoid false positives.

**5. Principle 5 invariant** — the canonical contract must retain its exact
`## 5. Justified Action` heading per ADR-016.

## Running locally

```sh
# Run the validator from repo root:
python3 .github/scripts/validate_plugin.py

# Run against a specific repo root (useful in worktrees):
python3 .github/scripts/validate_plugin.py --repo-root /path/to/repo

# Run the test suite (including Cowork archive-content regression tests):
python3 -m unittest discover .github/scripts -p 'test_*.py' -v

# Run the same official strict validation used in CI:
npx --yes @anthropic-ai/claude-code@2.1.216 plugin validate . --strict

# Build and inspect the Cowork archive:
python3 scripts/build_cowork_bundle.py --output /tmp/mise-en-place.plugin
python3 scripts/build_cowork_bundle.py --check /tmp/mise-en-place.plugin
```

## Error message format

Errors are printed to stderr, one per line:

```
<relative-path>: <human-readable description>
```

Examples:
```
.claude-plugin/plugin.json: missing required field 'version'
skills/mise-en-place/SKILL.md: description contains XML-like tag <name>
skills/mise-en-place/SKILL.md: broken reference 'references/contract.md' (resolves to /abs/path, not found)
```

Exit codes: `0` = pass, `1` = one or more validation failures, `2` = internal error.

## The `_looks_like_local_reference` heuristic

Check 3 only validates backtick-quoted `.md` paths that look like local
references. A path is considered local if:

- it is a bare filename with no `/` (e.g. `` `notes.md` ``),
- it starts with `./` or `../`, or
- its first path segment exists as a directory next to the SKILL.md file.

This filter prevents external lineage citations such as
`` `forrestchang/andrej-karpathy-skills/CLAUDE.md` `` from being flagged as
broken references.

**Known false-negative:** a typo'd first segment — for example
`` `Reference/contract.md` `` (capital R) when only `references/` exists — will
not match any sibling directory. The heuristic returns "not local" and the
validator silently skips the reference instead of reporting it as broken.
This boundary is documented in detail in `coding.md` (see agent-notes) and is
covered by `TestLooksLikeLocalReference.test_capitalised_first_segment_is_not_local_false_negative_risk`.

## When to swap the hand-rolled YAML reader

The frontmatter parser handles flat single-line `key: value` pairs only. It
rejects multi-line scalars, nested keys, and list values. If the SKILL.md
frontmatter ever needs those constructs, replace the hand-rolled parser with
`pyyaml` and accept the `pip install pyyaml` step in CI. Do not reach for
`pyyaml` before that point — the current skill files only use simple scalars,
and keeping stdlib-only removes the install step from the workflow entirely.

## Known LOW security finding: path traversal

The reference integrity check resolves user-supplied paths from SKILL.md
against the filesystem. A path such as `../../etc/passwd.md` would be resolved
and checked for existence. In the current threat model — a private repo, no
untrusted SKILL.md content, no write path — this is LOW severity and deferred.

If the threat model changes (e.g. the validator runs against externally
contributed SKILL.md files), add an `is_relative_to(repo_root)` guard in
`validate_skill_references` before the `is_file()` check to reject any
resolved path that escapes the repo root.

## Workflow triggers

The `validate.yml` workflow runs on:
- every `push` to any branch,
- every pull request targeting `main`.

The job also runs the pinned official Claude Code validator with `--strict`,
builds and validates the Cowork archive, and runs the unittest suite. The test
step uses `if: always()` so test results are reported even when an earlier
validation step fails.
