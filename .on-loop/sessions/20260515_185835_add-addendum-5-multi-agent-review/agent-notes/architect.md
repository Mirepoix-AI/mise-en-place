# Architect notes — Addendum #5: Multi-agent review

**Session:** `20260515_185835_add-addendum-5-multi-agent-review`
**Mode:** `build`
**Input:** `specs/multi-agent-review-addendum.md`
**Role:** translate the spec into drafted text and a deliverables checklist; do not edit source files.

The spec is the source of truth. These notes contain the drafted text the
coding agent should paste into the listed files, plus a one-line-per-file
checklist. The coding agent is expected to apply these edits near-mechanically.

---

## A. `contract.md` §6 — addendum #5, drafted

Insert this block in `skills/mise-en-place/references/contract.md` immediately
after the `### ADRs` addendum body and immediately before the
`### Candidates not yet promoted` section. The surrounding `---` separator
already sits between the addenda block and the candidates block; leave it
where it is.

```markdown
### Multi-agent review

When the project declares a reviewer list, high-stakes review and gate work
dispatches to those reviewers in parallel rather than to a single agent.
Reconciliation is unanimous APPROVE — any REQUEST_CHANGES blocks the phase.
The reviewer identifiers are project-defined (typically via a
`## Multi-agent review` section in the project's `CLAUDE.md`); this contract
specifies the dispatch and reconciliation shape, not the vocabulary.

Empirical basis: `UlyssesModel/kavara-mirepoix-internal#11` and `#12` —
two-for-two on real architectural issues caught by the second reviewer that
a single-reviewer pass had APPROVE'd past.
```

**Voice check:**
- The principle body is three sentences. The empirical pointer is a second
  short paragraph — split off because it is justification, not principle.
  This matches the shape of the `### Skills (slash-tree)` addendum, which
  also uses a short principle paragraph plus a short follow-on paragraph.
- The unanimity rule appears verbatim: "any REQUEST_CHANGES blocks the phase."
- "Reviewer identifiers declared by the project" is used; no enumeration of
  `claude` / `codex` / etc.
- The `CLAUDE.md` activation convention is illustrative ("typically via"),
  not prescriptive — matching the spec's "the contract is agnostic on syntax."

---

## B. `MODES.md` cross-references, drafted

The `review` and `ship` mode subsections in `MODES.md` (lines 56–59 and 45–48
in the current file) need one trailing sentence each, appended after the
existing body paragraph and before the `[Full contract →]` link.

### `review` — appended sentence

Insert this as a new paragraph after the existing body paragraph (which ends
with "exit `review` mode explicitly first.") and before the
`[Full contract →]` line:

```markdown
When the project declares a reviewer list, review work dispatches to those reviewers in parallel and requires unanimous APPROVE — see [contract §6 / Multi-agent review](skills/mise-en-place/references/contract.md#6-mirepoix-addenda).
```

### `ship` — appended sentence

Insert this as a new paragraph after the existing body paragraph (which ends
with "No assumed-green CI.") and before the `[Full contract →]` line:

```markdown
The ship gate also runs under multi-agent review when the project declares a reviewer list; any REQUEST_CHANGES blocks the merge — see [contract §6 / Multi-agent review](skills/mise-en-place/references/contract.md#6-mirepoix-addenda).
```

**Voice check:** one sentence each, both link back to the contract, neither
restructures the mode definition itself. The cross-ref points at §6
(the Addenda section) rather than a sub-anchor; the existing MODES.md
cross-refs target `#5b-the-eight-modes` at the section level, so this
matches.

---

## C. `CHANGELOG.md` entry, drafted

Insert this block at the top of the `### Added` section in `CHANGELOG.md`,
immediately under the file's existing header block (the lines ending
`...PATCH for fixes that don't change behavior.`) and before the existing
`## [0.3.0] — 2026-05-09` entry.

```markdown
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
```

**Notes for the coding agent on this entry:**
- The `PR #N` placeholder appears four times. Replace all four with the
  actual PR number once the PR is created. If preferred, the coding agent
  may leave them as `PR #N` and the operator can do a final find-replace
  before merging.
- Date is `2026-05-15` per the session id and operator memory's current
  date. If the merge slips to a later day, the coding agent should
  update the date to the merge day to match the 0.3.0/0.2.0/0.1.0 dating
  convention (entries are dated by release, not by draft).

---

## D. `SKILL.md` update, drafted

In `skills/mise-en-place/SKILL.md`, the "What to load" section currently
reads (line 49):

```markdown
3. The four starter addenda (Section 6) — Skills, Evaluation packs, Meta-agent decomposition, ADRs.
```

Replace it with:

```markdown
3. The five starter addenda (Section 6) — Skills, Evaluation packs, Meta-agent decomposition, ADRs, Multi-agent review.
```

That is the only change required in `SKILL.md`. The frontmatter, activation
flow, switching block, postconditions, invariants, and reference sections
stay untouched. (Verified: no other line in `SKILL.md` enumerates the
addendum count or names.)

---

## E. `README.md` update, drafted

In `README.md`, the bullet at line 9 currently reads:

```markdown
- **Four Mirepoix-native addenda** — skill invocation over freeform reasoning, evaluation packs as verifiers, meta-agent decomposition before shape-shifting, ADRs that precede architectural commitments.
```

Replace it with:

```markdown
- **Five Mirepoix-native addenda** — skill invocation over freeform reasoning, evaluation packs as verifiers, meta-agent decomposition before shape-shifting, ADRs that precede architectural commitments, and multi-agent review when the project declares a reviewer list.
```

That is the only change required in `README.md`. The repository-structure
table, Install, Usage, Modes, Invariants, Lineage, CI, Status, and License
sections stay untouched.

---

## F. Version bumps

Both manifests currently report `"version": "0.3.0"`. Update both to
`"version": "0.4.0"`:

- `.claude-plugin/plugin.json` line 3: `"version": "0.3.0",` → `"version": "0.4.0",`
- `.claude-plugin/marketplace.json` line 12: `"version": "0.3.0",` → `"version": "0.4.0",`

No other fields in either manifest change. The validator
(`.github/scripts/validate_plugin.py`) checks JSON validity, kebab-case
names, and required-field presence — none of those are affected by a
version bump.

---

## G. Deliverables checklist (for the coding agent)

Apply each change exactly as drafted in sections A–F above. One bullet per
file; one line per change.

- [ ] `skills/mise-en-place/references/contract.md` — insert addendum #5 block (section A above) after the `### ADRs` addendum and before `### Candidates not yet promoted`.
- [ ] `MODES.md` — append the one-sentence cross-ref (section B) to the `### review` subsection, between its body paragraph and its `[Full contract →]` link.
- [ ] `MODES.md` — append the one-sentence cross-ref (section B) to the `### ship` subsection, between its body paragraph and its `[Full contract →]` link.
- [ ] `CHANGELOG.md` — insert the `## [0.4.0] — 2026-05-15` block (section C) above the existing `## [0.3.0] — 2026-05-09` entry; replace the four `PR #N` placeholders with the real PR number once known.
- [ ] `skills/mise-en-place/SKILL.md` — update the "What to load" enumeration on line 49 (section D) from "four starter addenda … ADRs." to "five starter addenda … ADRs, Multi-agent review."
- [ ] `README.md` — update the opening bullet on line 9 (section E) from "Four Mirepoix-native addenda" to "Five Mirepoix-native addenda" with the trailing clause appended.
- [ ] `.claude-plugin/plugin.json` — bump `"version"` from `"0.3.0"` to `"0.4.0"`.
- [ ] `.claude-plugin/marketplace.json` — bump `"version"` (under `plugins[0]`) from `"0.3.0"` to `"0.4.0"`.

The spec also lists `specs/multi-agent-review-addendum.md` as a deliverable;
that file already exists in the worktree at HEAD and needs no further
modification by the coding agent.

**CI verification:** after editing, run
`python3 .github/scripts/validate_plugin.py` from the worktree root. Three
things must pass: JSON validity of both manifests, no XML-like tags in
`SKILL.md` frontmatter description, and resolution of all backtick-quoted
`.md` references in `SKILL.md`. None of the drafted changes introduce new
backtick `.md` references inside `SKILL.md` (the only `SKILL.md` change is
to the addenda enumeration string, which contains no `.md` filename), so
check #3 should not regress.

---

## H. Concerns / open questions

1. **PR number placeholder strategy.** The CHANGELOG block uses `PR #N` four
   times. The cleanest workflow: coding agent leaves the placeholders;
   PR-author does a final find-and-replace before merging. Alternative:
   the coding agent writes the actual PR number after `gh pr create`
   returns it. Default to the placeholder approach unless the operator
   indicates otherwise — it keeps the diff out of the PR-creation race
   condition.

2. **`MODES.md` anchor target.** The drafted cross-refs link to
   `skills/mise-en-place/references/contract.md#6-mirepoix-addenda`. The
   existing MODES.md cross-refs all target `#5b-the-eight-modes`. Verified
   the heading text in `contract.md` is `## 6. Mirepoix Addenda`, which
   GitHub will slugify as `#6-mirepoix-addenda`. The standard library used
   for Markdown-on-GitHub anchors lowercases and replaces spaces with
   hyphens; the leading "6. " becomes `6-`. This anchor should resolve,
   but the operator may want to double-check by previewing the rendered
   markdown after merge. If preferred, the addendum #5 H3 could carry its
   own anchor via an explicit heading, but H3 anchors in GitHub-flavored
   markdown are auto-generated the same way — `#multi-agent-review` should
   also resolve and would target the addendum directly.

3. **Voice precedent on empirical references.** Addenda #1–4 don't carry
   empirical pointers in the contract text (they were stipulated at
   0.1.0). The spec's `Notes for the architect` block is explicit that
   the empirical reference *must* be in the contract text, not just the
   CHANGELOG. The drafted text puts the empirical pointer in a separate
   short paragraph after the principle, so the principle reads cleanly
   on its own and the empirical pointer reads as justification. This is
   a small precedent-setting choice. If the operator wants the empirical
   pointer folded into the principle paragraph or omitted entirely, that
   would change the draft.

4. **"Candidates not yet promoted" cleanup.** The spec doesn't ask for it,
   but worth noting: the `multi-agent handoff protocol` candidate
   mentioned at the bottom of §6 (line 242) is *near* but not the same as
   multi-agent review. Handoff is sequential (agent A finishes, agent B
   picks up); review is parallel (agents A and B both review the same
   artifact, results reconcile). The drafted addendum is about the
   parallel/reconciliation pattern; the handoff candidate is untouched.
   If the operator wants the candidate line updated for clarity (e.g.,
   reword to "multi-agent handoff protocol (distinct from addendum #5's
   parallel review)"), flag it for a follow-up — out of scope for this
   PR.

5. **`mise-en-place.md` symlink.** The repo-root symlink resolves to
   `skills/mise-en-place/references/contract.md`. No action needed —
   editing the contract file naturally surfaces through the symlink. The
   CI validator already knows not to follow it (per the operator-memory
   note `project_mise_en_place_symlinks.md` and `find_skill_files`'s
   one-level glob in `validate_plugin.py`).

---

## Voice and length self-check

- [x] Addendum subsection in `contract.md` draft: principle paragraph is
      three sentences, empirical paragraph is two sentences. Under the
      three-sentence cap for the principle.
- [x] "Reviewer identifiers declared by the project" used; no
      enumeration of specific reviewer identifiers.
- [x] Unanimity rule stated verbatim: "any REQUEST_CHANGES blocks the
      phase."
- [x] Empirical references (`PR #11`, `PR #12`,
      `UlyssesModel/kavara-mirepoix-internal`) appear in the contract
      text, not just the CHANGELOG.
- [x] `MODES.md` cross-refs are one sentence each.
- [x] No reviewer-identifier hardcoding anywhere in the drafted text.
- [x] No mention of on-loop, upstream contribution, or implementation
      details inside the contract addendum — only the behavioral
      commitment.
- [x] Backward-compatible: a project whose `CLAUDE.md` doesn't declare
      the convention sees no change. Phrasing is "when the project
      declares a reviewer list" — opt-in by construction.
