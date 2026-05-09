# Security Agent Notes — validate-ci

Audit of the CI validation tooling implemented for spec
`specs/validate-ci.md`. The validator runs against the repo's own files
inside GitHub Actions; no external/network input, no untrusted operators
who lack repo write access.

## Scope reviewed

- `.github/scripts/validate_plugin.py` (469 lines)
- `.github/scripts/test_validate_plugin.py` (375 lines)
- `.github/workflows/validate.yml` (23 lines)

## Threat model summary

| Vector | Status |
|---|---|
| Path traversal via SKILL.md backtick references | No exploit — see [LOW] below |
| ReDoS / catastrophic backtracking in any regex | None of the four regexes admit super-linear backtracking |
| YAML frontmatter bypass of XML-tag check | No bypass — value is checked verbatim with `findall` |
| Fork-PR secret leakage via `pull_request` trigger | Not applicable — workflow uses `pull_request`, not `pull_request_target`; fork PRs run with read-only GITHUB_TOKEN and no secret access |
| Runner exhaustion / unbounded loops | All loops bounded by repo file count and file size on disk |

## Findings

### [LOW] Resolved-reference filesystem probe leaks via error message
- File: `.github/scripts/validate_plugin.py:378-382`
- Detail: `validate_skill_references` calls
  `(skill_md.parent / ref).resolve()` and then `.is_file()` on the
  result. A SKILL.md author who controls the input can craft `ref`
  values with `../../../...` traversal segments. The validator then
  stats arbitrary paths and, on failure, prints the resolved absolute
  path to stderr (`broken reference '...' (resolves to {resolved}, not
  found)`).
- Why this is LOW, not HIGH:
  1. Anyone who can write to `skills/*/SKILL.md` already has commit
     access to this repo, so they can simply read the runner filesystem
     by other means.
  2. The validator never **reads** the resolved file — it only stats it
     via `.is_file()`. No file contents are disclosed.
  3. Path-traversal candidates are pre-filtered by
     `_looks_like_local_reference`: a path whose first segment is not
     `.`, `..`, a single segment, or an existing sibling directory is
     dropped silently. So `../../../etc/passwd` passes
     (`..` is a recognized prefix), but the only side-effect is an error
     line containing the absolute path, which the attacker already
     supplied.
  4. The CI runner is ephemeral; stat-probing the runner's filesystem
     reveals nothing the GitHub-Actions image isn't public about.
- Reproduction (informational): create a SKILL.md citing
  `` `../../../etc/passwd` ``. Validator emits
  `broken reference '../../../etc/passwd' (resolves to /etc/passwd, not
  found)` (or matches and silently passes if the file exists). No data
  read.
- Mitigation (optional, not required): after resolving, assert
  `resolved.is_relative_to(repo_root)` and emit a distinct error class
  for out-of-tree references. Not a defect — documenting for the next
  operator.

### [LOW] `permissions:` not declared in workflow
- File: `.github/workflows/validate.yml:1-23`
- Detail: The workflow does not set top-level `permissions:`. The job
  inherits the repository default, which on a permissively configured
  repo could include `contents: write` and others. The validator does
  no API calls and no checkout writes, so the inherited permissions are
  unused — but a defense-in-depth posture would explicitly minimise
  them.
- Mitigation (optional): add at the top of the workflow file:
  ```yaml
  permissions:
    contents: read
  ```
  This caps the job's `GITHUB_TOKEN` regardless of repo defaults. Not a
  vulnerability today; recommend adding when convenient.

### [INFO] Hand-rolled YAML parser is regex/string-based, not pyyaml
- File: `.github/scripts/validate_plugin.py:156-234`
- Detail: The frontmatter parser is intentionally minimal — single-line
  `key: value` only. In the abstract, hand-rolled parsers can be
  bypassed; in practice, the bounded scope and the verbatim `findall`
  XML-tag check make a bypass impossible to construct without first
  expanding the supported subset.
- Per operator guardrail in `plan.md` §1–2, this is recorded as INFO,
  not escalated. The escape hatch (swap to `pyyaml`) is reserved for
  the moment the YAML subset expands to multi-line values, lists, or
  nested keys.
- Concrete bypass attempts considered and ruled out:
  | Attack | Result |
  |---|---|
  | Embed real `\n` in description value | Splits the line; second half flagged as malformed-or-key, not silently passed |
  | Embed escape sequence `\n` (literal backslash-n) | No interpretation; stays in the value string; `findall` still scans |
  | Surround value with quotes to hide tag: `description: "<test>"` | One pair of quotes stripped, then `XML_TAG_RE.findall` runs on `<test>` — flagged correctly |
  | Null byte / control char around tag | Not stripped from value; regex still matches `<[a-zA-Z]...>` substring |
  | Indent the description line | Flagged as malformed; missing-key error fires (hard fail, not silent pass) |
- No action required.

### [INFO] Action pins are major-version tags, not commit SHAs
- File: `.github/workflows/validate.yml:14,16`
- Detail: `actions/checkout@v4` and `actions/setup-python@v5` are pinned
  to mutable major-version tags. GitHub recommends commit-SHA pinning
  for the strongest supply-chain posture. Both are first-party
  GitHub-published actions; the spec explicitly mandates these exact
  tag pins.
- This is INFO because (a) the spec requires it, (b) both actions are
  first-party trusted publishers, and (c) the threat model — a CI job
  reading repo files and printing to stderr — has no secrets, no
  external network access, and a read-only token from forks.
- No action required.

### [INFO] `pull_request` event scope (fork-PR trigger)
- File: `.github/workflows/validate.yml:5-6`
- Detail: The workflow triggers on `pull_request` (default activity
  types: `opened`, `synchronize`, `reopened`), which **does** include
  PRs from forks. Critically, the workflow does **not** use
  `pull_request_target`. GitHub's platform guarantee for `pull_request`
  is that fork PRs run with a read-only `GITHUB_TOKEN` and no access to
  repository secrets. The validator does not reference any secrets, so
  even if the platform guarantee were weaker, no secret would be in
  scope to leak.
- The risk profile commonly attached to fork PRs (secret exfiltration,
  malicious workflow-file injection) does not apply here. The workflow
  file at the time of run is the **base ref's** version for
  `pull_request_target` — but for plain `pull_request`, the workflow
  runs the head-ref version of the validator script with no secrets,
  which is the intended behaviour.
- No action required.

## Concrete attack attempts that did NOT find an issue

I tried each of the suggested attack classes from the dispatch
instructions:

1. **Path traversal that lets the resolver stat files outside the
   repo** — possible (e.g. `../../../etc/passwd`), but no information
   disclosure beyond the attacker-supplied path string. Captured as
   [LOW] above.
2. **Regex with catastrophic backtracking under a specific input** —
   none of `KEBAB_RE`, `XML_TAG_RE`, `MD_REFERENCE_RE`,
   `FENCED_BLOCK_RE`, `URL_SCHEME_RE`, `FRONTMATTER_KEY_RE` admit
   nested quantifiers over overlapping character classes (the classic
   `(a+)+` pattern). All run linearly on adversarial input.
3. **A specific malformed input that bypasses the XML-tag check** —
   none. The check runs `XML_TAG_RE.findall` on the verbatim value
   string, so any `<word>` substring at any position is caught. Quoted
   values, embedded escape sequences, and control characters do not
   change this.
4. **Workflow misconfiguration that leaks repo secrets via fork PR** —
   not present. Workflow uses `pull_request`, not `pull_request_target`;
   no secrets are referenced.
5. **Unbounded loop / memory consumption proportional to attacker
   input** — none. File reads load entire SKILL.md into memory but a
   100MB+ SKILL.md is caught at PR-review time, and runner RAM (7GB)
   absorbs realistic adversarial inputs.

## Compliance Notes

This is a CI validator, not a data-handling system. SOC2/PCI/GDPR
compliance frameworks have no direct application here. The relevant
hygienic concerns — supply-chain integrity (action pins), least
privilege (workflow permissions), and tamper-resistance of the
validation logic itself — are addressed by the [INFO] and [LOW]
findings above.

## Dependency Audit

- Python 3.11 (pinned via `actions/setup-python@v5` config).
  Stdlib-only, no `pip install` step. No third-party dependencies to
  audit.
- `actions/checkout@v4` — first-party, current major; no known
  outstanding CVEs as of audit date (2026-05-08).
- `actions/setup-python@v5` — first-party, current major; no known
  outstanding CVEs as of audit date.

## Decisions

- Path-traversal finding kept at LOW because the attacker model (must
  already have repo write access) and the absent file-read primitive
  collapse the impact to "stat-probe leaks attacker's own input".
- Hand-rolled YAML parser kept at INFO per the operator guardrail in
  `plan.md`. Bounded scope is the explicit mitigation; the escape hatch
  (`pyyaml`) is reserved.

## Recommendations for Next Agent

- **Documentation agent**: when documenting the validator, surface the
  two LOW-severity defense-in-depth opportunities (explicit
  `permissions: contents: read` on the workflow, optional
  `is_relative_to(repo_root)` guard on resolved references) as future
  hardening items, not active defects.
- **Build agent**: no action needed — the validator is self-contained
  and the workflow already runs `unittest discover` to gate on the
  test suite.

## Verdict

VERDICT: PASS
