# Reviewer Agent Notes — validate-ci

Final review gate. Read-only; the code under review lives in the worktree at
`.claude/worktrees/validate-ci`.

## Findings

### [NIT] Resolved-path component of the broken-reference error message bypasses the as-posix discipline
- File: `.github/scripts/validate_plugin.py:380-382`
- Detail: The architect blueprint §6.6 / §6 risks list says "use
  `.as_posix()` explicitly when formatting error paths" so error messages
  stay platform-stable. The `_rel` helper does this for the SKILL.md
  side, but the resolved absolute path is rendered with the default
  `__fspath__` (`f"{resolved}"`), which would produce backslashes on a
  Windows runner. The workflow pins `ubuntu-latest`, so this is moot
  today; flagging only because the blueprint called it out.
- Suggested fix (deferred): `f"... resolves to {resolved.as_posix()}, not found"`.
- Not a blocker — runner is locked to Linux and the spec does not require
  cross-platform error-string stability.

### [NIT] Broken-reference errors are emitted per occurrence rather than per unique reference
- File: `.github/scripts/validate_plugin.py:373-383`
- Detail: The destructive AC#3 walk-through (and the testing agent's
  observation) shows that renaming `references/contract.md` produces 4
  identical error lines because the body cites it in 4 backtick spans.
  Functionally correct — every miss is reported — but noisy in CI.
  Deduplication (a `set()` of refs before existence check) would keep
  the same coverage with less console noise.
- Suggested fix (deferred): `for ref in dict.fromkeys(refs):` (preserves
  order, dedupes).
- Not a blocker — testing agent already classified this as LOW. No spec
  requirement violated.

### [NIT] `_looks_like_local_reference` first-segment heuristic has a documented capital-R false-negative
- File: `.github/scripts/validate_plugin.py:331-353`
- Detail: A SKILL.md that cites `Reference/contract.md` (capital R typo)
  when only `references/` exists as a sibling silently passes the
  validator. The coding agent documented this as the deliberate
  AC#1-vs-blueprint reconciliation; the testing agent added an explicit
  test that pins the behavior; the documentation agent surfaced it in
  `.github/scripts/README.md`. The bounded-scope rationale is honest:
  the heuristic adds a filter (rejects more candidates than the
  blueprint), and the only way to relax it is a richer "external
  citation vs typo'd local ref" distinction, which is out of scope for
  this spec.
- I considered recommending a tightening (e.g. always validate
  `*/*.md` refs unless first segment matches a known external-citation
  allow-list), but that would re-open AC#1 — the existing
  `forrestchang/...` lineage citation in the live SKILL.md is exactly
  the case the heuristic was added to handle, and any tighter rule
  either re-fails AC#1 or introduces a per-skill allow-list that the
  spec doesn't ask for.
- Recommendation: keep as-is. The false-negative is documented in three
  places (coding.md, testing.md, scripts/README.md) and pinned by a
  test. If a future skill author types `Reference/...` instead of
  `references/...`, the validator won't catch it — but PR review will.

### [NIT] `permissions:` not declared in workflow
- File: `.github/workflows/validate.yml:1-23`
- Detail: Security agent surfaced this as defense-in-depth. The
  workflow inherits repo-default permissions; the validator makes no
  API calls and writes nothing. Adding `permissions: contents: read`
  at the top would cap the `GITHUB_TOKEN` regardless of repo defaults.
  Not a vulnerability today.
- Suggested fix (deferred): add to workflow file:
  ```yaml
  permissions:
    contents: read
  ```

## Spec compliance check

| AC | Status | Evidence |
|---|---|---|
| #1 — validator exits 0 on HEAD | PASS | re-ran in worktree: exit 0, `[validate_plugin] PASS`, `2 manifests, 1 skills` |
| #2 — `<test>` injection → exit 1 with file + tag | PASS | re-ran with `<operator>` injected, exit 1, error line `skills/mise-en-place/SKILL.md: description contains XML-like tag <operator>` |
| #3 — rename `references/contract.md` → exit 1 with broken-ref message | PASS | re-ran with rename, exit 1, error line `skills/mise-en-place/SKILL.md: broken reference 'references/contract.md' (resolves to ..., not found)` (×4 — see [NIT] above) |
| #4 — `unittest discover` exit 0 with ≥5 tests covering listed cases | PASS | 22 tests, all green; the 5 spec-named cases (valid manifests, invalid JSON, missing required fields, XML tag, broken ref) are all present and pass |
| #5 — workflow runs on push + PR-to-main | PASS | `.github/workflows/validate.yml` triggers `on: push` + `on: pull_request: branches: [main]`. Verified post-merge in CI per spec. |

All five ACs verified.

## File-placement check

- `.github/scripts/validate_plugin.py` — correct
- `.github/scripts/test_validate_plugin.py` — correct
- `.github/workflows/validate.yml` — correct

No other files modified by the implementation/testing/security path.
Documentation agent added `.github/scripts/README.md` (new) and a 6-line
`CI` section in repo `README.md`. Build agent added `__pycache__/` to
`.gitignore`. Both adjacent additions are sensible and in scope.

## Constraints check

| Constraint | Status |
|---|---|
| Python 3.11+, stdlib only | PASS — imports are `argparse`, `json`, `pathlib`, `re`, `sys`, `typing.Optional`, `__future__.annotations`. Tests add `io`, `tempfile`, `unittest`, `contextlib`. No third-party. |
| Tests use `unittest` | PASS — `unittest.TestCase` + `unittest.main()` + `unittest discover` |
| Validator exits 1 on failure | PASS — `main()` returns 1 with errors, 0 clean, 2 reserved for uncaught exceptions |
| Error format `{path}: {check}: {detail}` | PASS — error lines match the contract; tests assert on the exact substrings |
| `actions/checkout@v4` and `actions/setup-python@v5` pinned | PASS |
| Triggers `push` + `pull_request: branches: [main]` | PASS |
| Python 3.11 pin in workflow | PASS |

## Test-honesty check

I read every test method in `test_validate_plugin.py` and verified:

- All 22 tests use `tempfile.TemporaryDirectory` and never read or
  mutate real-repo paths. The base class `_TempRootTest` creates a
  fresh tmp dir per test and cleans up in `tearDown`. The
  non-tempdir-using class (`TestFrontmatterParser`) operates on
  in-memory strings only.
- The 5 spec-named cases (AC#4) each assert on the exact error
  substring contracted in the architect blueprint §1, not on
  fuzzy-pass conditions like "any error returned". Specifically:
  `invalid JSON`, `missing required field 'version'`,
  `description contains XML-like tag <test>`,
  `broken reference 'references/missing.md'`, `not kebab-case`.
- The `TestLooksLikeLocalReference` class added by the testing agent
  pins all four boundary cases of the heuristic plus the documented
  capital-R false-negative. The test for the false-negative asserts
  `assertFalse` (i.e. it locks the current — possibly suboptimal —
  behavior), which is the right move: the spec accepts the heuristic
  as a deliberate boundary.
- `TestMain.test_main_returns_1_on_any_error` and
  `TestMain.test_main_returns_0_on_clean_repo` exercise the full
  `main(argv)` path including the `--repo-root` flag, redirecting
  stdout/stderr — properly hermetic.

No shallow tests. Coverage is honest.

## Documentation-accuracy check

- `.github/scripts/README.md` accurately describes:
  - the three checks (matches spec §1–3)
  - the local run commands (matches CLI surface)
  - the error message format and exit codes (matches `main()` behavior)
  - the `_looks_like_local_reference` heuristic and its capital-R
    false-negative (matches code + tests)
  - the pyyaml escape hatch (matches operator guardrail)
  - the deferred path-traversal hardening (matches security agent
    finding)
  - the workflow triggers and `if: always()` test step (matches yml)
- `README.md` CI section: 6 lines, accurate, links to the scripts
  README. Placed before "Status" as documentation agent decided —
  reasonable.

No documentation drift from code.

## Workflow correctness

- Triggers: `push` (any branch), `pull_request: branches: [main]` —
  per spec.
- `actions/checkout@v4` — exact version per spec.
- `actions/setup-python@v5` with `python-version: '3.11'` — exact
  version + pin per spec.
- Validator step runs first; test step has `if: always()` so a
  failing validator does not skip the tests (architect §5 / plan
  guidance honored).
- `runs-on: ubuntu-latest`, single job, no matrix, no caching — all
  appropriate for a pure-stdlib validator.

No workflow defects.

## Documented-deviation check (operator-flagged)

The `_looks_like_local_reference` heuristic is the only deviation from
the architect blueprint. I judge the bounded-scope rationale honest:

- **Why it was needed:** the live SKILL.md cites
  `forrestchang/andrej-karpathy-skills/CLAUDE.md` as a lineage
  reference. The blueprint's filter set (no leading `/`, no URL
  scheme, no whitespace) keeps it as a candidate; the validator then
  flags it broken; AC#1 fails. AC#1 is non-negotiable.
- **What the deviation does:** it tightens the filter — a candidate
  is treated as a local reference only if it is single-segment,
  starts with `./`/`../`, or its first segment exists as a sibling.
  Anything else is dropped silently.
- **What the deviation costs:** a typo'd first segment whose
  directory doesn't exist (e.g. `Reference/contract.md` when only
  `references/` exists) is silently skipped. This is the documented
  false-negative.
- **Is the cost documented prominently enough?** Yes —
  in `coding.md` decision §1, in `testing.md` Task E, in
  `.github/scripts/README.md` "The `_looks_like_local_reference`
  heuristic" section, and pinned by an explicit test
  (`test_capitalised_first_segment_is_not_local_false_negative_risk`).
  The README and the test name both literally contain the phrase
  "false-negative risk".
- **Should it be tightened?** Not in this phase. Any tightening
  re-fails AC#1 unless paired with an external-citation allow-list,
  which the spec doesn't ask for. If/when SKILL.md authors start
  using Markdown link syntax `[text](path.md)` for cross-references
  (out of current spec scope), the validator will need to grow a
  proper reference parser; until then, the heuristic is honest about
  its boundary.

## Files Reviewed

- `.github/scripts/validate_plugin.py` (469 lines) — reviewed in full
- `.github/scripts/test_validate_plugin.py` (375 lines) — reviewed in full
- `.github/workflows/validate.yml` (24 lines) — reviewed in full
- `.github/scripts/README.md` (107 lines) — reviewed in full
- `README.md` CI addition (6 lines) — reviewed
- `.gitignore` (added `__pycache__/`) — reviewed
- All five agent-notes files — read

## Commendations

- The `_looks_like_local_reference` reconciliation is exactly the right
  move: the coding agent identified the AC#1-vs-blueprint conflict,
  resolved it with a tightening (not a loosening), documented the cost
  in the docstring, and the testing agent then pinned the exact
  boundary with a named test. Three agents collaborated cleanly on
  what could have been a regression.
- The error-message contract (`{path}: {check}: {detail}`) is honored
  uniformly. Tests assert on exact substrings rather than counts,
  which means future refactors will catch wording drift.
- `_run_checks(repo_root)` is a clean seam for the integration test —
  `main()` wraps it with argparse + I/O + exit-code mapping, and the
  test exercises `main()` end-to-end via redirected stdio. Good
  separation of concerns.
- The frontmatter parser correctly handles colons in values (verified:
  `description: Activate, then apply: A, B, C.` parses cleanly because
  `str.partition(":")` splits only on the first occurrence).
- Security audit was thorough — concrete attack attempts enumerated
  and ruled out by construction, not handwave.
- Stdlib-only constraint preserved; no temptation to reach for
  pyyaml/click/pytest. Coding agent honored the operator guardrails.

## Recommendations for next stage (non-blocking)

1. Optional defense-in-depth: add `permissions: contents: read` to the
   workflow when convenient. Security agent surfaced this; it is not a
   defect today.
2. Optional polish: dedupe broken-reference errors so a SKILL.md with
   N citations of the same broken file emits 1 error, not N.
3. Optional cross-platform polish: `.as_posix()` on the resolved path
   in the broken-reference message, in case the workflow ever expands
   beyond `ubuntu-latest`.
4. Future tightening to consider if SKILL.md citations grow more
   complex: replace the heuristic with a parser that distinguishes
   "external citation" from "local file ref" via syntax (e.g. require
   `./` / `../` / sibling-path for local; treat anything with `://` or
   matching `^[a-z0-9-]+/[a-z0-9-]+/` as external). Out of current
   spec.

## Verdict

VERDICT: APPROVE
