# Implementation plan — Addendum #5: Multi-agent review

**Session:** `20260515_185835_add-addendum-5-multi-agent-review`
**Mode:** `build`
**Source spec:** `specs/multi-agent-review-addendum.md`
**Architect notes:** `.on-loop/sessions/20260515_185835_add-addendum-5-multi-agent-review/agent-notes/architect.md`

## Scope

Markdown-only sub-phase. Promotes the multi-agent review face-off pattern from downstream Kavara experiment to the fifth addendum of the Mirepoix behavioral contract. Bump version `0.3.0` → `0.4.0` (MINOR per SemVer; behavior addition).

## Steps

The architect produced drafted text for every change. The coding agent applies them mechanically.

1. **Contract.md** — insert addendum #5 block (architect §A) after `### ADRs`, before `### Candidates not yet promoted`. Verify: §6 now lists five addenda; addenda #1–4 are untouched.

2. **MODES.md** — append one-sentence cross-refs (architect §B) to `### review` and `### ship` subsections. Verify: both link to `contract.md#6-mirepoix-addenda`; no other lines in `MODES.md` change.

3. **CHANGELOG.md** — insert `## [0.4.0] — 2026-05-15` block (architect §C) above the existing `## [0.3.0]` entry. Leave `PR #N` placeholders for now — operator can find-replace post-merge.

4. **SKILL.md** — update the one line in "What to load" (architect §D) from "four starter addenda … ADRs." to "five starter addenda … ADRs, Multi-agent review." Verify: frontmatter and all other sections unchanged.

5. **README.md** — update the one bullet at line 9 (architect §E) from "Four Mirepoix-native addenda" to "Five Mirepoix-native addenda" with the trailing clause appended.

6. **`.claude-plugin/plugin.json`** — bump `"version"` from `"0.3.0"` to `"0.4.0"`.

7. **`.claude-plugin/marketplace.json`** — bump `"version"` (under `plugins[0]`) from `"0.3.0"` to `"0.4.0"`.

8. **CI verification** — run `python3 .github/scripts/validate_plugin.py` from worktree root. All three checks must pass: JSON validity, frontmatter integrity (no XML-like tags), backtick-quoted `.md` reference resolution in `SKILL.md`.

## Acceptance criteria

- All seven file changes applied per architect drafts (no editorializing, no scope creep).
- CI validator exits zero.
- `git diff --stat` shows changes only to the seven listed files.
- No code added — this is a markdown-only and JSON-manifest-only release.

## Out of scope

- Implementing the dispatch / reconciliation logic (downstream tooling concern).
- Modifying the eight modes structurally.
- Cleaning up the `multi-agent handoff protocol` candidate line in §6 (distinct concern — flagged for separate consideration).
- Contributing the pattern upstream to `joestein/on-loop`.

## Risks

- **MODES.md anchor target** — drafted cross-refs use `#6-mirepoix-addenda`. GitHub auto-slugification should resolve correctly, but unverified until rendered. Operator may want to preview after merge.
- **CHANGELOG `PR #N` placeholders** — appear four times. Coding agent leaves them; operator does the final substitution at PR creation or merge.
