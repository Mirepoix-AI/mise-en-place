# Implementation plan — MODES.md (locked after explore-mode decision)

Architect blueprint: `.on-loop/sessions/20260509_034145_modes-md/agent-notes/architect.md`
Mode: explore (SPEC) → **build** (CODE onward, after operator decision below)
Branch: `on-loop/modes-md` @ `.claude/worktrees/modes-md`

## Operator decisions (locked 2026-05-09)

| Decision | Choice |
|---|---|
| **Layout** | **D — Hybrid table+cards.** Top matrix + 8 short anchored cards. ~90-120 lines. |
| **README cross-link** | **New "Modes" section between Usage and Invariants + a row in the Repository structure table.** Both, additive. |
| **SKILL.md cross-link** | **Keep the activation bullets, append a single pointer line.** The bullets are part of the *spoken* activation prompt; don't demote them to a link. |
| **§5b matrix in MODES.md** | **Link to it; don't repeat. But inline the four "load-bearing oddities" bullets.** Comparative depth stays in contract; the most-cited insights stay in scan-layer reach. |

## Files to create / modify

| Path | Action | Notes |
|---|---|---|
| `MODES.md` | create | Layout D content per architect's sample. ~90-120 lines. |
| `README.md` | modify (additive) | New `## Modes` section between Usage and Invariants + row in Repository structure table. No other edits. |
| `skills/mise-en-place/SKILL.md` | modify (additive) | Append a single pointer line in the Activation flow section (after the eight bullets). Bullets are unchanged. |

No other files modified. Surgical (#3) holds.

## Content contract for MODES.md

1. **Title:** `# Modes`.
2. **Frontmatter (none):** MODES.md is not a skill file; no YAML frontmatter required. The validator only checks `skills/*/SKILL.md`, so MODES.md is out of scope for the frontmatter check anyway.
3. **One-paragraph intro:** what this file is and is not. Explicitly note: "this is the index; the contract is the source of truth — see [contract §5b](skills/mise-en-place/references/contract.md#5b-the-eight-modes)."
4. **Comparison table** (4 columns): Mode (linked to in-page anchor `#mode`), Tagline, When, Contract link. Eight rows.
5. **"Load-bearing oddities"** — quoted from contract §5b verbatim (4 bullets, ~6 lines). Source-of-truth invariant: if these change in the contract, change MODES.md too.
6. **Eight cards** — one per mode, in the same order as the contract: build, explore, harden, ship, firefight, review, migrate, refactor. Each card:
   - `### \`mode\`` header (so anchors auto-slug to `#build`, `#explore`, etc.)
   - 1-3 lines: the mode's headline shift + postcondition (if any).
   - `[Full contract →](skills/mise-en-place/references/contract.md#5b-the-eight-modes)` — single link pattern across all eight, pointing at the section, NOT per-mode anchors. (See risk #1 below.)
7. **Footer:** `> Source of truth: [contract §5b](skills/mise-en-place/references/contract.md#5b-the-eight-modes)`. Single line.

## Linking strategy (locked)

- **MODES.md → contract** uses the *real path* `skills/mise-en-place/references/contract.md`, not the root-level symlink `mise-en-place.md`. Reason: the symlink is for browse convenience; citations should be unambiguous. (Memory: `project_mise_en_place_symlinks.md`.)
- **All cross-links into contract.md use one anchor: `#5b-the-eight-modes`.** Not per-mode anchors inside contract.md. Reason: contract.md headers are `### \`firefight\` — incident, outage, hot-fix`, which GitHub slugs to `#firefight--incident-outage-hot-fix` (or similar), not `#firefight`. Editing contract.md headers is out of scope (#3). Linking to the section anchor is robust and lets the reader scroll the four lines to find their mode.
- **MODES.md → README and SKILL.md → MODES.md** use Markdown link syntax `[label](path)`, not backtick-wrapped paths. Reason: the validator's reference-integrity check only matches backtick-wrapped `.md` references — Markdown links bypass it cleanly. We avoid the validator entirely for cross-links between MODES.md and other docs.

## Pre-flight verification (testing agent)

1. Run the existing CI validator: `python3 .github/scripts/validate_plugin.py` → exit 0. The validator should NOT trip on MODES.md (it's at root, not under `skills/`) or on the SKILL.md addition (Markdown link syntax, not backtick).
2. Run the unittest suite: `python3 -m unittest discover .github/scripts -p 'test_*.py' -v` → exit 0.
3. Anchor check: every card header (`### \`mode\``) should slug to `#mode` in standard GitHub Markdown rendering. The implementer should preview at least one in their head; reviewer should confirm.
4. **Glance test (informal):** a reader unfamiliar with the project should be able to identify the right mode for a hot-fix in under 30 seconds from MODES.md alone. This is acceptance criterion #4 from the architect notes.

## Constraints (do not relax)

- Surgical (#3): only MODES.md (new), README.md (additive section + row), SKILL.md (one-line append). No formatting cleanup, no header reordering, no contract.md edits.
- "Glanceable, not a re-statement of the contract" — operator's own framing. The cards are 1-3 lines each. If a card grows past 5 lines, it's drifting toward re-statement.
- No emojis (operator preference; default behaviour).

## Out of scope

- Editing `contract.md` headers (even to make per-mode anchors work cleanly).
- Adding new modes or refining mode definitions.
- Promoting any "candidate not yet promoted" addendum (footer-as-surface, hooks listener-vs-gate) — they live in contract.md §6, not here. (Aligns with memory: `feedback_dont_promote_after_one_run.md`.)

## Risks (for testing/review)

1. **Anchor slug verification.** GitHub auto-slugs `### \`build\`` to `#build`. If something goes sideways (`#build-1`, `#build-default`), the in-page table links break silently. Reviewer should pull the rendered preview on PR and click each anchor.
2. **Tagline drift.** SKILL.md activation bullets, contract §5b first lines, and MODES.md taglines all describe the same eight modes in slightly different forms. Reviewer should diff the three — the three should agree to within obvious paraphrasing.
3. **One mode goes long.** `migrate` and `harden` have the most distinctive shifts; their cards may want 4-5 lines instead of 2. That's fine if it stays "glanceable" — but reviewer should sanity-check that no card balloons toward re-statement.

## Acceptance criteria

| AC | Verification |
|----|-------------|
| #1 MODES.md exists at repo root and renders | visual; `ls MODES.md` |
| #2 Layout D — table + 8 anchored cards | reviewer confirms structure |
| #3 README has new "Modes" section + repo-structure row | `git diff README.md` shows additive section + row |
| #4 SKILL.md activation bullets unchanged; one pointer line appended | `git diff skills/mise-en-place/SKILL.md` shows one-line addition |
| #5 Cross-links resolve in GitHub render | reviewer verifies on PR |
| #6 Validator + unittest still green | testing agent runs both |
| #7 No edits outside the three files above | `git diff --stat` shows exactly 3 changed paths |
