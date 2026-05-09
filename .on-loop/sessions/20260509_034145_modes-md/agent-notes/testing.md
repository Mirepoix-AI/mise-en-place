# Testing Agent Notes

## Summary

Docs-only change: `MODES.md` (new, 74 lines), `README.md` (additive `## Modes` section + repo-structure table row), `skills/mise-en-place/SKILL.md` (one pointer line appended). All five verification tasks completed. Three tasks pass cleanly; two have minor findings that do not rise to RETRY-CODE level.

## Test Results

- Validator: PASS (exit 0) — 2 manifests + 1 skill checked, no new errors
- Unittest suite: PASS (exit 0) — 22 tests, OK
- Git surgical check: PASS — exactly 3 production-file paths changed
- Cross-link integrity: PASS — all targets exist, all anchors resolve correctly
- Drift check: PARTIAL (low-severity findings, see below)
- Glance test: PASS

## Task A — Validator + unittest (AC #6)

Both exit 0. The validator did not trip on MODES.md (root-level, not under `skills/`) or on the SKILL.md addition (Markdown link syntax `[label](path)`, not backtick-wrapped). The SKILL.md pointer line is in a blockquote; the validator's reference-integrity regex does not match it.

## Task B — Surgical-changes verification (AC #7)

`git status -s` output:
```
 M .on-loop/index.json       ← orchestrator-owned; out of scope
 M README.md
 M skills/mise-en-place/SKILL.md
?? .on-loop/sessions/20260509_034145_modes-md/   ← orchestrator audit trail; out of scope
?? MODES.md
```

`git diff --stat` shows exactly 3 changed paths in production scope:
- `.on-loop/index.json` — orchestrator-owned (session registry update); confirmed not in coding agent's scope
- `README.md` — 5 insertions
- `skills/mise-en-place/SKILL.md` — 2 insertions

`MODES.md` appears as untracked (new file). Three production files match the plan exactly.

**PASS.**

## Task C — Cross-link integrity

### Internal anchors (MODES.md table → in-page cards)

All eight card headers follow the pattern `### \`mode\`` exactly. GitHub auto-slugs these to `#mode` via the standard algorithm (lowercase, strip non-alphanumeric except hyphens, collapse). Verified programmatically:

| Header | Slug | Table link | Status |
|--------|------|-----------|--------|
| `### \`build\`` | `#build` | `#build` | OK |
| `### \`explore\`` | `#explore` | `#explore` | OK |
| `### \`harden\`` | `#harden` | `#harden` | OK |
| `### \`ship\`` | `#ship` | `#ship` | OK |
| `### \`firefight\`` | `#firefight` | `#firefight` | OK |
| `### \`review\`` | `#review` | `#review` | OK |
| `### \`migrate\`` | `#migrate` | `#migrate` | OK |
| `### \`refactor\`` | `#refactor` | `#refactor` | OK |

No slug collisions. No `#build-1` or `#build-default` issues.

### Repo-relative path targets

| Source file | Link path | Resolved to | Exists |
|-------------|-----------|-------------|--------|
| `MODES.md` | `skills/mise-en-place/references/contract.md` | worktree root + that path | OK |
| `README.md` | `./MODES.md` | worktree root/MODES.md | OK |
| `README.md` | `skills/mise-en-place/references/contract.md` | worktree root + that path | OK |
| `skills/mise-en-place/SKILL.md` | `../../MODES.md` | normalizes to worktree root/MODES.md | OK |
| `skills/mise-en-place/SKILL.md` | `references/contract.md` | worktree root/skills/mise-en-place/references/contract.md | OK |

### Section anchor `#5b-the-eight-modes` in contract.md

The contract.md header is `### 5b. The eight modes`. GitHub slugging: lowercase → `5b. the eight modes`; strip non-alphanumeric except hyphens → `5b the eight modes`; spaces to hyphens → `5b-the-eight-modes`. Verified programmatically: slug matches the anchor used in all MODES.md and SKILL.md links.

**PASS. No broken links.**

## Task D — Drift check

| Mode | SKILL.md activation bullet | Contract §5b first line | MODES.md tagline |
|---|---|---|---|
| `build` | "default. Implementing intent. Karpathy four at full strength." | "The Karpathy four at full strength. Caution over speed. Most work lives here." | "Default. Karpathy four at full strength." |
| `explore` | "divergent, generative. Output is a decision, not a merge." | "Generating options, sketching directions, testing assumptions. The output of `explore` is a decision (or an ADR), not a merge." | "Divergent, generative. Output is a decision." |
| `harden` | "industrial-strength. The path that handles money or runs at 3am." | "Production-grade defensive coding. The path that handles money, runs at 3am, or sits behind the FIX-engine router." | "Industrial-strength. Defensive code is a feature." |
| `ship` | "final mile before merge or release. Tighter gates." | "Same four principles as `build`, but with tighter gates:" | "Final mile. Tighter gates than \`build\`." |
| `firefight` | "incident, hot-fix, outage. Speed over elegance." | "Speed and clarity over elegance. The principles bend, but the rationale is preserved:" | "Incident, hot-fix, outage. Speed over elegance." |
| `review` | "read-only. Surface, don't fix." | "Reading, critiquing, advising. No writes." | "Read-only. Surface, don't fix." |
| `migrate` | "irreversible change. Schema, API, data, major dep bumps." | "Schema changes, API contract changes, data backfills, major dependency bumps — anything where rollback isn't a code-only operation." | "Irreversible change. Verify state empirically." |
| `refactor` | "behavior-preserving structural change. Large diff by design." | "Reshape without changing what the code does. The diff is large by design." | "Behavior-preserving structural change. Large diff by design." |

### Drift findings

**`harden` — LOW severity, acknowledged by coding agent.**
SKILL.md and contract both center on the use-case framing ("money paths, 3am paths"). MODES.md tagline shifts emphasis to the principle-shift insight: "Defensive code is a feature." This is the #2-inverts point — the most distinctive behavioral signal of the mode. The use-case framing does appear in the MODES.md card body ("Money paths, 3am paths, FIX-engine paths"), so it is not absent from the file. The tagline just prioritizes the principle over the scenario. This is a deliberate editorial choice by the coding agent, not an error. Judgment call: acceptable paraphrasing; no semantic gap.

**`migrate` — LOW severity, acknowledged by coding agent.**
SKILL.md lists examples (schema, API, data, dep bumps). Contract defines by rollback criterion ("anything where rollback isn't a code-only operation"). MODES.md tagline uses "Verify state empirically" — the #1-strengthened-plus shift. Again, the use-case framing and examples appear in the MODES.md card body and in the table's "When" column ("Schema, API contract, data backfill, major dep bump"). The tagline highlights the most-cited diagnostic the contract makes: empirical verification. Judgment call: acceptable emphasis shift; no semantic gap.

**`explore` — NEGLIGIBLE.**
MODES.md drops "not a merge" from the tagline ("Output is a decision" vs. "Output is a decision, not a merge"). This half-phrase appears in the card body ("The code is deletable by design") and in the "When" column ("Design alternatives, prototype-to-decide"). Not a semantic gap.

**All other modes: no drift. `firefight` and `review` are verbatim-or-near-verbatim across all three sources.**

**Overall drift verdict: PASS (no substantive semantic gaps; two acknowledged emphasis shifts are intentional and documented).**

## Task E — Glance test

- **Time to find `firefight` for a hot-fix:** The comparison table is on the third non-blank line of MODES.md (after the title and one-sentence intro). The `firefight` row reads "Incident, hot-fix, outage. Speed over elegance." — the word "hot-fix" is in the tagline and the word "breakage" is in the "When" column. A reader scanning the table finds this on row 5 of 8, with no prose to read first. Estimated time: under 10 seconds once the file is open.
- **Table on first screen:** Confirmed. The table begins at line 5 of the file, after the title (line 1) and one-sentence intro (lines 3-4, which wrap to ~2 lines). The full table fits on one screen.
- **Card length:** All eight cards are 2-4 non-blank lines (excluding header and "Full contract →" link line). Maximum is `refactor` at 4 lines. No card exceeds the 5-line ceiling. `build`, `harden`, `ship`, `review` are 2 lines each.

**PASS.**

## Decisions

- Drift findings for `harden` and `migrate` classified as LOW/acceptable because: (a) the coding agent documented the decision; (b) the use-case context appears in the card body and "When" column; (c) leading the tagline with the principle-shift is consistent with MODES.md's stated purpose as an index of behavioral distinctions, not a scenario index.
- `.on-loop/index.json` modification confirmed as orchestrator-owned (adds session registry entry). Not counted against AC #7.

## Files Modified

- `.on-loop/sessions/20260509_034145_modes-md/agent-notes/testing.md` — this file (created)

## Issues Found

- [LOW] `harden` tagline in MODES.md leads with the principle-shift ("Defensive code is a feature") rather than the use-case framing in SKILL.md ("money or 3am"). Intentional; use-case appears in card body. Not a blocker.
- [LOW] `migrate` tagline in MODES.md leads with empirical-verification point rather than SKILL.md's example list. Intentional; examples appear in table "When" column and card body. Not a blocker.
- [NEGLIGIBLE] `explore` tagline drops "not a merge" half-phrase. Covered in card body. Not a blocker.

## Recommendations for Next Agent

- Anchor slugs should be spot-checked in the rendered GitHub PR view before merge (programmatic verification passes, but GitHub's backtick handling in headers is worth a human eyeball on the PR).
- The "Full contract →" links all point to `#5b-the-eight-modes`, not per-mode anchors. This is intentional (per-mode anchors in contract.md are unstable). Reader must scroll ~4 lines in contract.md to find their mode. Acceptable per the plan's explicit decision; no fix needed unless the operator changes their mind.
