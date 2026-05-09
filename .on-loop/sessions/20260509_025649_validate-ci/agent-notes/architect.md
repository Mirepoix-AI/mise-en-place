# Architect Blueprint: validate-ci

**Spec source:** `specs/validate-ci.md`
**Session:** `20260509_025649_validate-ci`
**Branch / worktree:** `on-loop/validate-ci` @ `.claude/worktrees/validate-ci`
**Date:** 2026-05-08

## Summary

Three deliverables, stdlib-only, no install step:

| Path | Role |
|------|------|
| `.github/scripts/validate_plugin.py` | Validator entry point. Exits 0/1. |
| `.github/scripts/test_validate_plugin.py` | `unittest` suite, runnable with `python -m unittest discover`. |
| `.github/workflows/validate.yml` | GitHub Actions workflow on push + PR-to-main. |

Design center: each check function is independently callable (for testability) and returns a list of error strings; the entry-point aggregates errors, prints them, and exits 1 if any list is non-empty.

---

## 1. `validate_plugin.py` — module / function decomposition

### Constants

```python
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]  # repo root from .github/scripts/
PLUGIN_JSON   = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SKILLS_DIR    = REPO_ROOT / "skills"

KEBAB_RE          = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
XML_TAG_RE        = re.compile(r"<[a-zA-Z][a-zA-Z0-9_-]*>")
MD_REFERENCE_RE   = re.compile(r"`([^`\n]+?\.md)`")  # see Section 3
```

`REPO_ROOT` is computed from `__file__` so the script works whether invoked from repo root, `.github/scripts/`, or via `python -m`. Tests override it by passing explicit paths into the check functions — no global mutation.

### Public functions (all pure: take paths, return `list[str]` of errors)

```python
def validate_plugin_json(path: pathlib.Path) -> list[str]:
    """Check 1a. Required: name, version, description. name must be kebab-case."""

def validate_marketplace_json(path: pathlib.Path) -> list[str]:
    """Check 1b. Required top-level: name, owner, plugins (non-empty list).
       Each plugin entry: name, source, description. Top-level name kebab-case.
       Each plugin entry's name must also be kebab-case."""

def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, list[str]]:
    """Return (parsed_dict, errors). None dict means frontmatter missing/malformed."""

def validate_skill_frontmatter(skill_md: pathlib.Path) -> list[str]:
    """Check 2. Frontmatter present, parses, has name+description, no XML-like tag in description."""

def extract_md_references(body: str) -> list[str]:
    """Return raw matched relative paths from inline backtick-quoted .md references in body."""

def validate_skill_references(skill_md: pathlib.Path) -> list[str]:
    """Check 3. Every backtick-quoted relative .md reference resolves to an existing file."""

def find_skill_files(skills_dir: pathlib.Path) -> list[pathlib.Path]:
    """Return sorted skills/*/SKILL.md paths. Returns [] if skills_dir missing."""

def main(argv: list[str] | None = None) -> int:
    """Entry point. Aggregates all check errors, prints them, returns exit code."""

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

### Exit-code contract

- `0` — no errors from any check.
- `1` — one or more errors. All errors are printed (don't stop at first failure; emit the full list so a single CI run reveals everything).
- `2` — reserved for internal/unexpected exceptions (uncaught `Exception` bubbles to a top-level handler in `main`). Not used in normal validation; documented for clarity.

### Error-message format (single source of truth)

Every error line uses one of these exact templates so tests can assert on substrings:

```
{repo_relative_path}: {check_name}: {detail}
```

Examples:

- `.claude-plugin/plugin.json: missing required field 'version'`
- `.claude-plugin/plugin.json: invalid JSON: Expecting property name enclosed in double quotes (line 3 column 3)`
- `.claude-plugin/marketplace.json: plugins[0]: missing required field 'source'`
- `.claude-plugin/plugin.json: name 'Mise_En_Place' is not kebab-case`
- `skills/mise-en-place/SKILL.md: frontmatter missing (no leading '---' delimiter)`
- `skills/mise-en-place/SKILL.md: missing required frontmatter key 'description'`
- `skills/mise-en-place/SKILL.md: description contains XML-like tag <name>`
- `skills/mise-en-place/SKILL.md: broken reference 'references/contract.md' (resolves to {abs}, not found)`

Paths printed in errors are repo-relative (computed via `path.relative_to(REPO_ROOT)`) for human readability and grep-ability.

### Output style

`main` prints:

```
[validate_plugin] checking 2 manifests, N skills
... per-error lines on stderr ...
[validate_plugin] FAIL: 4 error(s)         # or PASS
```

Per-error lines go to **stderr**. Summary goes to **stdout**. CI shows both; tests can capture either with `unittest.mock.patch('sys.stderr', io.StringIO())`.

---

## 2. Frontmatter parser design

### Supported subset

Only what `skills/*/SKILL.md` actually uses today: a flat block of single-line `key: value` pairs. The parser is intentionally minimal — when richer YAML is needed, the spec calls for swapping to `pyyaml`.

### Algorithm

1. The file must start with `---` on its own line (line 1, after stripping a UTF-8 BOM if present).
2. Read subsequent lines until the next line that is exactly `---` (the closing delimiter).
3. For each line in between:
   - **Strip** trailing `\r` (CRLF tolerance).
   - **Skip** lines that are empty or contain only whitespace.
   - **Skip** lines whose first non-whitespace character is `#` (YAML comment).
   - Otherwise, split on the **first** `:`:
     - Left of `:` is the key. `.strip()`. Must match `^[A-Za-z_][A-Za-z0-9_-]*$` — otherwise emit error `malformed frontmatter line: '{raw}'`.
     - Right of `:` is the value. `.strip()`. If wrapped in matching `'...'` or `"..."`, strip exactly one pair of quotes. No escape-sequence interpretation — values are stored verbatim.
4. Duplicate keys are an error: `duplicate frontmatter key '{key}'`.

### Rejected on sight

- No closing `---` before EOF → `frontmatter not terminated (no closing '---')`.
- Indented continuation lines (`  more text`) → `malformed frontmatter line: '{raw}'` (we don't parse multi-line scalars).
- Lines starting with `-` (lists), `[` / `{` (flow), or containing `: ` followed by an indented next-line block scalar → all flagged as malformed.
- A key with no colon → malformed.
- Empty key (line starts with `:`) → malformed.

### Return contract

```python
parse_frontmatter(text) -> tuple[dict[str, str] | None, list[str]]
```

- `(dict, [])` — clean parse.
- `(dict_partial, [errors...])` — best-effort dict (whatever parsed cleanly) + errors. Caller decides whether to keep going.
- `(None, [errors...])` — frontmatter missing entirely or unterminated; nothing usable.

Caller (`validate_skill_frontmatter`) merges errors and only does the XML-tag check if `description` parsed cleanly.

---

## 3. Reference-extraction regex

### Proposed regex

```python
MD_REFERENCE_RE = re.compile(r"`([^`\n]+?\.md)`")
```

After matching, filter results in Python:

- Reject matches starting with `/` (absolute path).
- Reject matches matching `^[a-zA-Z][a-zA-Z0-9+.\-]*://` (URL scheme: `http://`, `file://`, etc.).
- Reject matches containing whitespace after stripping (defensive — a real path with a space is a smell, but safer to skip than false-flag).
- Keep the rest. Resolve via `(skill_md.parent / match).resolve()`. Existence check via `.is_file()` (so a directory matching `foo.md/` is still a miss).

### Why this regex

- Single backtick on each side matches Markdown inline-code spans, which is exactly how the existing SKILL.md cites `references/contract.md`.
- `[^`\n]+?` keeps the match within one inline span and one line — refuses to bridge across newlines or unmatched backticks.
- Lazy quantifier (`+?`) plus `.md` literal at the end prevents greedy gobbling across multiple inline spans on the same line.

### False-positive analysis

| Pattern | Matched? | Acceptable? |
|---|---|---|
| `` `references/contract.md` `` (inline code, real ref) | yes | yes — desired |
| `` ```bash\nls *.md\n``` `` (fenced code block) | no | yes — fenced blocks use **triple** backticks; our regex requires single, and `[^`\n]` refuses backticks inside |
| `` `code with `nested` backticks` `` | only the inner span | acceptable; nested inline backticks aren't valid CommonMark anyway |
| `[link text](path.md)` (Markdown link) | no | acceptable — out of scope per spec ("backtick-quoted") |
| `` `https://example.com/page.md` `` | matched, then filtered out | yes — URL scheme filter rejects |
| `` `/abs/path.md` `` | matched, then filtered out | yes — leading-slash filter rejects |
| `` `foo.md.bak` `` | no | yes — must end exactly in `.md` |
| `` `FOO.MD` `` | no | yes — case-sensitive `.md`. SKILL.md convention is lowercase. |

**Fenced-block edge case:** if someone writes a fenced code block whose contents contain `` `something.md` `` (single-backtick spans nested inside a triple-backtick block), our regex will match the inner span and try to resolve it. Mitigation: pre-strip fenced code blocks before regex application:

```python
FENCED_BLOCK_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
body_for_refs = FENCED_BLOCK_RE.sub("", body)
```

Apply this before `MD_REFERENCE_RE`. Tilde-fenced blocks (`~~~`) are not currently used in the repo; document but don't strip.

---

## 4. Test coverage map (`test_validate_plugin.py`)

Uses `unittest`, `tempfile.TemporaryDirectory`, and direct calls to the public functions. Tests build minimal fixture trees inside the temp dir and pass paths in — they **never** read or mutate the real repo, satisfying "do NOT mutate the real repo from tests."

Pattern for every test:

```python
class TestX(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
    def tearDown(self):
        self._tmp.cleanup()
```

### Required cases (acceptance criterion #4 → at least 5)

| # | Test method | Asserts | Spec criterion |
|---|---|---|---|
| 1 | `TestPluginJson.test_valid_plugin_json_passes` | Write a complete plugin.json fixture; `validate_plugin_json(path)` returns `[]`. | AC#4: "valid manifests" |
| 2 | `TestPluginJson.test_invalid_json_returns_error` | Write `"{not json"`; result contains `invalid JSON`. | AC#4: "invalid JSON" |
| 3 | `TestPluginJson.test_missing_required_field` | Drop `version`; result contains `missing required field 'version'`. | AC#4: "missing required fields" |
| 4 | `TestMarketplaceJson.test_valid_and_kebab_case_enforced` | Valid passes; `name: "Bad_Name"` fails with `not kebab-case`. | AC#4: "valid manifests" + extra |
| 5 | `TestMarketplaceJson.test_plugins_array_must_be_nonempty` | `plugins: []` returns error referencing empty array. | extra coverage |
| 6 | `TestFrontmatterParser.test_basic_kv_pairs` | `parse_frontmatter` returns expected dict, no errors. | parser coverage |
| 7 | `TestFrontmatterParser.test_missing_closing_delim` | Returns `(None, [...])` with not-terminated error. | parser coverage |
| 8 | `TestFrontmatterParser.test_crlf_and_blank_lines_tolerated` | `\r\n` line endings + blank lines parse cleanly. | edge case |
| 9 | `TestSkillFrontmatter.test_xml_tag_in_description_fails` | Build SKILL.md with `description: ... <test> ...`; expect error `description contains XML-like tag <test>`. | AC#4: "XML-like tag in description" + AC#2 |
| 10 | `TestSkillFrontmatter.test_missing_description_fails` | Drop description from frontmatter; expect missing-key error. | extra coverage |
| 11 | `TestReferences.test_extract_finds_inline_md_paths` | Body contains `` `references/contract.md` `` → returned in list. | extractor coverage |
| 12 | `TestReferences.test_extract_skips_fenced_block` | Fenced block containing inline `.md` → not in returned list. | extractor edge case |
| 13 | `TestReferences.test_extract_filters_urls_and_absolute` | `` `https://x/y.md` `` and `` `/abs/foo.md` `` filtered out. | extractor edge case |
| 14 | `TestReferences.test_broken_reference_fails` | SKILL.md cites `references/missing.md` not on disk; expect `broken reference` error. | AC#4: "broken relative reference" + AC#3 |
| 15 | `TestReferences.test_resolved_reference_passes` | Reference resolves to a real file in temp tree → no errors. | happy path |
| 16 | `TestMain.test_main_returns_1_on_any_error` | Set up a temp tree where one SKILL.md has bad description; monkey-patch `REPO_ROOT` (or use a CLI flag — see open question) and assert `main()` returns 1. | AC#1+#2 in test form |

Mandatory minimum is 5; we're targeting ~16 for real coverage. The five spec-listed cases are rows 1, 2, 3, 9, 14 — explicitly mapped above.

### Test infrastructure note

To allow `main()` to be tested without monkey-patching globals, propose a small CLI surface:

```
python validate_plugin.py [--repo-root PATH]
```

Default = `pathlib.Path(__file__).resolve().parents[2]`. Tests pass `--repo-root <tmpdir>`. Implementation: parse with `argparse` (stdlib). This keeps prod invocation unchanged (`python .github/scripts/validate_plugin.py` per AC#1) while making `main()` testable.

---

## 5. Workflow YAML structure (`.github/workflows/validate.yml`)

```yaml
name: validate

on:
  push:
  pull_request:
    branches: [main]

jobs:
  validate:
    name: validate plugin manifests and skills
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run validator
        run: python .github/scripts/validate_plugin.py
      - name: Run tests
        run: python -m unittest discover .github/scripts -p 'test_*.py' -v
```

Decisions:
- **Single job, two steps** (validator + tests). Both must pass for the job to pass. Run validator first; if it fails, tests still run (default GHA behavior `if: success()` — we explicitly drop `if:` so tests run regardless, but we may add `if: always()` to the test step if we want explicit guarantee).  Open question below.
- **Python 3.11 pinned**, matching the spec's "Python 3.11+" floor. Pinning the floor avoids surprises if the GHA runner default version drifts.
- **No matrix.** Single OS, single Python. The validator is pure stdlib and trivially deterministic; matrix would be over-engineering.
- **No caching.** No dependencies to cache.
- **`runs-on: ubuntu-latest`** — fine, no platform-sensitive code (we check file existence and parse text).

---

## 6. Edge cases and risks

### 6.1 Symlinks

The repo has `mise-en-place.md -> skills/mise-en-place/references/contract.md` at the root.

- **Skill discovery** uses `skills/*/SKILL.md` glob — symlinks at the repo root are not in `skills/`, so they're invisible to discovery. No risk.
- **Reference resolution** uses `(skill_md.parent / ref).resolve()` then `.is_file()`. `Path.is_file()` follows symlinks. So a SKILL.md that referenced `../../mise-en-place.md` would correctly resolve through the symlink. Acceptable.
- **Pitfall:** if `references/contract.md` were ever moved and the root symlink dangled, `skills/mise-en-place/SKILL.md` references would still resolve directly (they don't go through the symlink). The dangling root symlink is out of scope for this validator and not flagged.

### 6.2 Missing `skills/` directory

`find_skill_files` returns `[]` when `skills/` doesn't exist. No hard error; main loop simply iterates zero files. The summary line still prints (`checking 2 manifests, 0 skills`). Rationale: future spinoff projects might use this validator with no skills. Spec doesn't require failing on missing skills dir.

### 6.3 Empty frontmatter

A SKILL.md with `---\n---\n` parses to `({}, [])`. Then `validate_skill_frontmatter` flags missing `name` and `description`. Two errors emitted. Correct behavior.

### 6.4 CRLF line endings

`parse_frontmatter` strips trailing `\r` per line. Reading via `path.read_text(encoding="utf-8")` already normalizes CRLF on Windows when `newline` is None (the default), but we keep the explicit strip for safety on bytes-decoded input.

### 6.5 Multi-byte characters

All file reads use `encoding="utf-8"`. Description fields with em-dashes, smart quotes, etc., parse fine. The XML-tag regex operates on Unicode strings (`re` defaults to Unicode); `[a-zA-Z]` will not match non-ASCII letters, which matches the spec's regex literally (the spec writes `<[a-zA-Z][a-zA-Z0-9_-]*>`).

### 6.6 BOM at file start

Strip a leading `﻿` from frontmatter input before the `---` check. Prevents a Windows-saved file from failing the "must start with `---`" rule for cosmetic reasons.

### 6.7 Repo-relative path printing

`path.relative_to(REPO_ROOT)` raises `ValueError` if the path isn't under `REPO_ROOT`. In tests we override `REPO_ROOT` so this is fine, but the helper should fall back to `str(path)` if `relative_to` raises. Trivial guard.

### 6.8 Glob ordering

`find_skill_files` sorts results so error output is deterministic across runs and platforms (macOS HFS vs Linux ext4 ordering differs).

### 6.9 `actions/checkout@v4` and submodules / LFS

The repo has no submodules and no LFS. Default checkout settings suffice.

### 6.10 Validator self-test risk

If the validator itself has a bug that prints success when it shouldn't, AC#1 (passes today) won't catch it. The test suite (AC#4) is the safety net; testing agent must verify red→green for each check by deliberately breaking fixtures.

---

## 7. Acceptance-criterion traceability

| AC | Statement (paraphrased) | Satisfied by |
|----|-------------------------|---|
| AC#1 | Validator exits 0 on current HEAD | `validate_plugin.py` `main()` returns 0 when run against the worktree as it stands. Manual sanity-check during build; covered indirectly by CI step "Run validator" passing. |
| AC#2 | Adding `<test>` to mise-en-place SKILL.md description → exits 1 with file + tag in message | `validate_skill_frontmatter` + `XML_TAG_RE`; error message format `skills/mise-en-place/SKILL.md: description contains XML-like tag <test>`. Test row #9 (`test_xml_tag_in_description_fails`) asserts exact substring. |
| AC#3 | Renaming `references/contract.md` → exits 1 with broken-reference message | `validate_skill_references` + `extract_md_references`; error message `skills/mise-en-place/SKILL.md: broken reference 'references/contract.md' ...`. Test row #14 (`test_broken_reference_fails`). |
| AC#4 | `python -m unittest discover .github/scripts -p 'test_*.py'` exits 0 with ≥ 5 tests covering listed cases | `test_validate_plugin.py` containing rows #1–16 above; the 5 spec-named cases are rows #1, #2, #3, #9, #14. |
| AC#5 | Workflow runs on real GitHub push and reports pass/fail | `.github/workflows/validate.yml` with `on: push` + `on: pull_request: branches: [main]`. Job `validate` shows in checks UI. |

---

## Open questions / risks for downstream agents

1. **Tests step `if:` clause.** Should the test step run when the validator step fails? Recommended: yes, use `if: always()` so a single PR run reveals both validator failures and test regressions. Coding agent — please add it.
2. **`--repo-root` flag in `main`.** Above I propose adding it for testability. If the testing agent objects (prefers monkey-patching `REPO_ROOT`), drop the flag. Either path works; the testability requirement is what matters.
3. **Tilde-fenced code blocks.** Not stripped by `FENCED_BLOCK_RE`. The repo doesn't use them today. If a future skill author uses `~~~`, false positives could appear. Document in a code comment so the next operator notices.
4. **Symlinked SKILL.md.** If anyone ever creates `skills/foo/SKILL.md` as a symlink to another file, `glob` returns the link and `read_text` follows it. Treat as fine — but flag in code review if it ever happens.
5. **Reference matching is conservative.** We only match inline backtick `.md` references. Markdown `[text](path.md)` links are out of scope per spec. If a SKILL.md author starts using link syntax for cross-references, this validator silently lets broken links through. Mention in operator notes.
6. **Determinism on Windows runners.** We pin `ubuntu-latest`. If the workflow ever expands to a matrix, re-test path-separator handling — `pathlib` is portable, but error-message strings include forward slashes via `relative_to(...).as_posix()` (recommend the coding agent use `.as_posix()` explicitly when formatting error paths).
7. **Repo-root guard.** Computing `REPO_ROOT = parents[2]` assumes the script lives at `.github/scripts/`. If the script is ever moved, the constant breaks silently. Consider adding a runtime check that `REPO_ROOT / ".claude-plugin"` exists and emitting a clear error if not.
