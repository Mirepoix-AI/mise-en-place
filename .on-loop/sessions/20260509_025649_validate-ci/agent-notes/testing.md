# Testing Agent Notes — validate-ci

## Summary

All four testable acceptance criteria verified against the worktree at
`on-loop/validate-ci`. No regressions. One new test class added
(`TestLooksLikeLocalReference`, 5 tests) to explicitly cover the coding
agent's deviation. Total test count increased from 17 to 22; all pass.

---

## Test Results

- Total: 22
- Passed: 22
- Failed: 0
- Skipped: 0
- Coverage: not instrumented (stdlib unittest, no coverage plugin)

---

## Task A — Unit-test suite

Exit code: **0**

17 original tests + 5 added by this agent = 22 tests.
- All tests use `tempfile.TemporaryDirectory` fixtures.
- No test touches real repo paths (`skills/`, `.claude-plugin/`, etc.).
- `_TempRootTest` base class allocates a fresh `tmp` dir per test and cleans
  it up in `tearDown`. Verified by inspection: every test that creates files
  calls `_write(path, ...)` where `path` is under `self.root` (the temp dir),
  never a hard-coded worktree path.

---

## Task B — AC#1: validator green on HEAD

Exit code: **0**

```
[validate_plugin] checking 2 manifests, 1 skills
[validate_plugin] PASS
```

---

## Task C — AC#2: XML-like tag injection

Injected `<test>` into `skills/mise-en-place/SKILL.md` description line.

Exit code: **1**

Relevant output line on stderr:
```
skills/mise-en-place/SKILL.md: description contains XML-like tag <test>
```

The substring `description contains XML-like tag <test>` is present as required.

Restored with `git checkout -- skills/mise-en-place/SKILL.md`. Post-restore
`git diff skills/mise-en-place/SKILL.md` was empty. Validator returned exit 0 after
restore.

---

## Task D — AC#3: broken reference

Renamed `skills/mise-en-place/references/contract.md` →
`skills/mise-en-place/references/contract.md.bak`.

Exit code: **1**

Output contains 4 identical error lines (SKILL.md references `references/contract.md`
in 4 distinct backtick spans in the body):
```
skills/mise-en-place/SKILL.md: broken reference 'references/contract.md' (resolves to ..., not found)
```

The substring `broken reference 'references/contract.md'` is present as required.

The dangling root-level symlink `mise-en-place.md -> skills/mise-en-place/references/contract.md`
did NOT produce any extra errors — all 4 errors originate from the SKILL.md body,
not from the symlink. `find_skill_files` correctly scopes to `skills/*/SKILL.md`.

Restored with `mv contract.md.bak contract.md`. Validator returned exit 0 after restore.

---

## Task E — Coding-agent deviation analysis

### Filter behavior confirmed

`_looks_like_local_reference(ref, skill_dir)` works as documented:

| ref | skill_dir contains `references/`? | Result | Validated? |
|---|---|---|---|
| `references/contract.md` | yes | True | yes (correct) |
| `forrestchang/andrej-karpathy-skills/CLAUDE.md` | no `forrestchang/` | False | skipped (correct — external citation) |
| `notes.md` (single segment) | n/a | True | yes |
| `./notes.md` (explicit `./`) | n/a | True | yes |
| `../sibling/notes.md` (explicit `../`) | n/a | True | yes |

### False-negative risk: capital-R typo

`_looks_like_local_reference("Reference/contract.md", skill_dir)` returns **False**
because no `Reference/` directory exists next to SKILL.md (only lowercase `references/`).
The validator therefore silently skips this reference — it will NOT flag
`Reference/contract.md` as broken even though it is.

This is a known boundary of the heuristic. The filter cannot distinguish
between "a 2-segment external citation that happens to look local" and
"a typo'd local path whose first segment doesn't exist yet". The coding agent
documented this in decision §1; the behavior is intentional for AC#1
compatibility. Operators should be aware that a first-segment typo (wrong case
or spelling) will be silently ignored.

**No fix recommended for this phase** — it is a documented limitation, not a
bug in the AC-required behavior.

### New test case added

Added class `TestLooksLikeLocalReference` (5 test methods) to
`.github/scripts/test_validate_plugin.py`:

- `test_single_segment_ref_is_local` — single-segment → True
- `test_explicit_relative_prefix_is_local` — `./` and `../` → True
- `test_existing_first_segment_is_local` — `references/contract.md` when
  `references/` dir exists → True
- `test_three_segment_external_citation_is_not_local` — `forrestchang/...` →
  False (the actual external citation in SKILL.md)
- `test_capitalised_first_segment_is_not_local_false_negative_risk` — documents
  the capital-R typo scenario: `Reference/contract.md` → False; no `Reference/`
  dir exists, so the validator silently skips it

All 5 new tests pass.

---

## Tests Written

### Unit Tests (added this phase)

- `.github/scripts/test_validate_plugin.py` (modified) — added
  `TestLooksLikeLocalReference` (5 methods) covering the `_looks_like_local_reference`
  heuristic filter, including the 3-segment external citation case and the
  capital-R false-negative risk

### Pre-existing Tests (verified, not modified)

- `.github/scripts/test_validate_plugin.py` — 17 original tests:
  - `TestPluginJson` (3): valid JSON, invalid JSON, missing required field
  - `TestMarketplaceJson` (2): kebab-case enforcement, non-empty plugins array
  - `TestFrontmatterParser` (3): basic kv pairs, missing closing delimiter, CRLF tolerance
  - `TestSkillFrontmatter` (2): XML tag in description, missing description
  - `TestReferences` (5): inline md path extraction, fenced block skip, URL/absolute filter, broken ref, valid ref
  - `TestMain` (2): returns 1 on error, returns 0 on clean repo

---

## Decisions

- Added `TestLooksLikeLocalReference` as a separate class rather than adding
  individual methods to `TestReferences`, because the new tests target the private
  heuristic directly (`vp._looks_like_local_reference(...)`) while `TestReferences`
  tests the public `validate_skill_references` function end-to-end.
- Did not modify `validate_plugin.py` — the false-negative risk is a documented
  boundary, not a defect, and fixing it is out of scope for the testing phase.

---

## Files Modified

- `.github/scripts/test_validate_plugin.py` — added `TestLooksLikeLocalReference`
  class (5 test methods); renumbered the `main()` integration test section comment
  from "16" to "17" for consistency

---

## Issues Found

- **[LOW] AC#3 emits 4 errors for the same broken reference** — `references/contract.md`
  appears in 4 backtick spans in `SKILL.md` body, so the validator emits 4 identical
  error lines rather than 1. This is technically correct (it reports every occurrence),
  not a bug, but could be noisy. Deduplication is out of scope for this spec.

- **[LOW] False-negative risk for typo'd first path segment** — `Reference/contract.md`
  (capital R) is silently skipped instead of validated. Documented in Task E above.
  No code fix recommended; the behavior is intentional per coding agent decision §1.

---

## Failures Detail

None. All 22 tests pass. All ACs verified green.

---

## Worktree State at End

```
On branch on-loop/validate-ci
Untracked files: .github/  .on-loop/  specs/
nothing added to commit but untracked files present
```

No dirty tracked files. Worktree is in the same state as when the testing
agent was dispatched, except for the addition of this notes file and the
appended changes.log entry. Both are under `.on-loop/` (untracked).

---

## Recommendations for Next Agent

- **Security agent**: review that the XML-tag regex `<[a-zA-Z][a-zA-Z0-9_-]*>` is
  sufficient — it only catches opening tags (not `</tag>` or self-closing `<tag/>`).
  For the spec's stated purpose (catching angle-bracket placeholders like `<name>`)
  this is fine. Mention in review if the scope should expand.
- **Known test gap**: tilde-fenced code blocks (`~~~`) are not stripped before
  reference extraction. The architect blueprint mentions this; the repo doesn't
  use `~~~` today. No test covers this edge case.
- **Symlinked SKILL.md files** are not tested. Out of current scope per coding notes.
- **`Reference/contract.md` false-negative**: if this class of typo is a concern,
  a future mitigation would be to validate all multi-segment refs regardless of
  whether the first segment exists, then emit a distinct warning class for
  "might be an external citation" vs "definitely broken". Not recommended for this
  phase.
