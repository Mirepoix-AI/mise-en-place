# Reviewer Agent Notes

## Summary

Final-gate review of the MODES.md change. The implementation honors all four operator-locked decisions (Layout D; README "Modes" section + structure-row; SKILL.md keep-bullets-plus-pointer; §5b link-and-inline-oddities). Surgical scope holds (3 production files). Cross-links resolve. Load-bearing oddities are verbatim from contract §5b. The two flagged tagline emphasis-shifts (`harden`, `migrate`) are intentional editorial choices that prioritize the most-cited principle-shift over the use-case framing; the use-case framing is preserved in the table's "When" column and in the card body, so there is no semantic gap. Total length 74 lines — under the 90-120 plan band, which serves the "glanceable, not a re-statement" framing rather than violating it.

No BLOCKERs. Two NITs and one NICE-TO-HAVE.

## Findings

### [NIT] Footer source-of-truth line could acknowledge the inline oddities
**File:** `MODES.md:74`
**Detail:** The footer reads `> Source of truth: [contract §5b](...)`. Because the "Load-bearing oddities" block (lines 18-25) is verbatim-quoted from the contract, a careless future edit to the contract's bullets will silently desync MODES.md. The plan says "Source-of-truth invariant: if these change in the contract, change MODES.md too" — but that invariant lives only in the plan, not in the file itself.
**Suggested fix (non-blocking):** A future edit could add a one-line comment near the oddities block, e.g. `<!-- Verbatim from contract §5b. Re-sync if the contract bullets change. -->`. Not worth a code retry on its own; flag for the next docs touch.

### [NIT] Two cards omit a postcondition line where the contract has one
**File:** `MODES.md:40-43` (`harden`), `MODES.md:67-70` (`refactor`)
**Detail:** Architect §5 question 5 flagged the consistency choice: "either every card has a postcondition line (most read '—') or only the three that do." The implementation lands on "only the three that do" — `explore`, `firefight`, `migrate`. That is internally consistent. However, `harden` (ADR pairing per contract line 129) and `refactor` ("tests must pass before AND after") arguably have implicit postconditions worth surfacing. The coding agent's choice is defensible — the cards are tighter without forced placeholders — and the testing agent confirmed no card exceeds the 5-line ceiling.
**Suggested fix (non-blocking):** None. The current shape is coherent. Mentioned only because the architect explicitly raised it as a consistency call worth checking.

### [NICE-TO-HAVE] In-page table "Contract" column is eight identical links
**File:** `MODES.md:7-14` (column 4)
**Detail:** Every row's "Contract" column is `[§5b](skills/mise-en-place/references/contract.md#5b-the-eight-modes)` — the same target eight times. This is a deliberate consequence of the operator-locked decision to link to the section anchor (per-mode anchors in contract.md are unstable due to multi-word headers; editing contract.md is out of scope). The repetition is not a defect, but the column carries little signal because every cell is identical. A pure-Layout-D reading would point each row at a per-mode anchor; the operator's surgical-scope constraint forecloses that.
**Suggested fix (out of scope this session):** If a future session touches contract.md headers, shorten the eight `### `mode` — ...` headers to bare `### `mode``. That would unblock per-mode anchors and let MODES.md table column 4 carry per-row signal. Explicitly out of scope here.

## Review Checklist Results

### Spec/plan compliance: PASS
- Layout D — table + 8 anchored cards: confirmed (table at lines 5-14, cards at 29-70).
- README "Modes" section between Usage and Invariants: confirmed (README diff inserts after Usage, before Invariants).
- README repo-structure table row for MODES.md: confirmed (added between contract row and symlink row, correct logical order).
- SKILL.md activation bullets unchanged + single pointer line appended: confirmed (diff is +2 lines: blockquote pointer + blank line).
- §5b: linked, not repeated; four oddities inlined verbatim: confirmed.

### Glanceable, not a re-statement: PASS
- Total length: 74 lines (under the 90-120 plan band — leaner is better here).
- Card sizes: max is 4 non-blank body lines (`migrate`, `firefight`); minimum is 1 (`build`). All under the 5-line "drift toward re-statement" ceiling.
- Comparison table is on the first screen (begins line 5). Hot-fix lookup time well under 30 seconds (`firefight` row reads "Incident, hot-fix, outage").

### Surgical: PASS
- `git diff --stat` shows exactly 3 production files changed (or new):
  - `MODES.md` — new (74 lines)
  - `README.md` — +5 insertions (one table row, one section)
  - `skills/mise-en-place/SKILL.md` — +2 insertions (one blockquote pointer + blank line)
- `.on-loop/index.json` is orchestrator-owned; not counted against scope.
- No formatting cleanup elsewhere, no header reordering, no contract.md edits.

### Cross-link correctness: PASS
- Every card header (`### `mode``) auto-slugs to `#mode` per GitHub Markdown rules. Testing agent verified all 8.
- Every relative path (`./MODES.md`, `../../MODES.md`, `skills/mise-en-place/references/contract.md`, `references/contract.md`) resolves to a real file.
- Section anchor `#5b-the-eight-modes` matches contract.md header `### 5b. The eight modes` (slugged: `5b-the-eight-modes`).
- No new link uses the root-level `mise-en-place.md` symlink. Only the pre-existing README repo-structure table row mentions it (out of scope; correct).

### Tagline drift: PASS (with two acknowledged emphasis shifts)
- `harden`: MODES.md tagline "Industrial-strength. Defensive code is a feature." leads with the principle-shift; SKILL.md and contract lead with the use-case ("money paths, 3am paths"). The use-case framing appears in MODES.md's "When" column ("Money paths, 3am paths, FIX-engine paths") and card body. Acceptable paraphrasing — no semantic gap.
- `migrate`: MODES.md tagline "Irreversible change. Verify state empirically." leads with the #1-strengthened-plus shift; SKILL.md leads with examples. Examples appear in MODES.md's "When" column ("Schema, API contract, data backfill, major dep bump"). Acceptable.
- `explore`: drops the "not a merge" half-phrase from the tagline; covered in card body. Negligible.
- All other modes: agree across SKILL.md / contract / MODES.md to within obvious paraphrasing.
- Reasonable people can disagree on whether the tagline should match SKILL.md or lead with the principle-shift. The cards' role is to host the most-cited insight, and "defensive code is a feature" / "verify state empirically" *are* the most-cited insights. Defensible editorial call.

### Load-bearing oddities verbatim: PASS
- Contract §5b lines 199-202 match MODES.md lines 22-25 verbatim, including emphasis markers and punctuation. Bullet order preserved.
- The section header in MODES.md ("Load-bearing oddities") and lead-in ("Worth memorizing — these are the non-obvious points the contract calls out explicitly:") are MODES.md additions, not from contract; that is correct since the contract presents these bullets without that framing.

### Anchor-in-table to card linkage: PASS
- Table column 1 anchors: `#build`, `#explore`, `#harden`, `#ship`, `#firefight`, `#review`, `#migrate`, `#refactor`. All eight resolve to the corresponding `### `mode`` card headers in the same file. Testing agent verified programmatically; review confirms by inspection.

### Operator's pre-empted concern (anything left ambiguous or quietly drifted from the operator's pick): PASS
- Layout D: confirmed (not silently reverted to A/B/C).
- README cross-link: both option (1) section + option (3) row, exactly as the plan locked. Not silently reduced to one.
- SKILL.md cross-link: bullets retained (option 2), not replaced with a link (option 1).
- §5b handling: linked + four oddities inlined (option 3-with-oddities), not repeated wholesale (option 1) and not transposed (option 2).
- Linking strategy (real path, not symlink; section anchor, not per-mode contract anchors): both honored across all three files.
- No quiet drift detected.

## Files Reviewed

- `MODES.md` — new, 74 lines, Layout D structure verified.
- `README.md` — diff inspected (+5 insertions, additive only).
- `skills/mise-en-place/SKILL.md` — diff inspected (+2 insertions, additive only).
- `skills/mise-en-place/references/contract.md` — read §5b at lines 199-202 to verify verbatim oddities quote.
- `.on-loop/sessions/20260509_034145_modes-md/plan.md` — read in full for compliance check.
- `.on-loop/sessions/20260509_034145_modes-md/agent-notes/architect.md` — read in full to understand alternatives traded off.
- `.on-loop/sessions/20260509_034145_modes-md/agent-notes/coding.md` — read for implementation decisions.
- `.on-loop/sessions/20260509_034145_modes-md/agent-notes/testing.md` — read for verification results.
- `.on-loop/sessions/20260509_034145_modes-md/agent-notes/security.md` — read for audit results.
- `.on-loop/sessions/20260509_034145_modes-md/agent-notes/documentation.md` — read for sanity findings.
- `.on-loop/sessions/20260509_034145_modes-md/agent-notes/build.md` — read for CI verification.

## Commendations

- **Verbatim oddities quote.** The coding agent took the right call — quote the four bullets literally rather than paraphrase. That makes the source-of-truth invariant trivial to enforce with `diff`.
- **Length discipline.** 74 lines is under the plan's 90-120 band. The cards stay tight; no card balloons toward re-statement. The "glanceable" framing is honored at the structural level.
- **Tagline emphasis-shift was a deliberate editorial choice, documented.** The coding agent flagged the `harden` and `migrate` shifts in their notes with reasoning. That is the right behavior — surface the trade, don't hide it.
- **Surgical compliance.** Three production files, zero drive-by edits, even though README and SKILL.md were both touched (high-temptation files for cleanup). Validator and unittest both green without modification.
- **Linking strategy executed cleanly.** Real path used consistently, never the root symlink. Section anchor used uniformly across all "Full contract →" links — the consequence (eight identical column-4 cells) is a known cost of an out-of-scope-fixable problem, correctly accepted rather than papered over.

## Recommendations for Next Agent (commit + PR)

- **Commit message:** Reflect that this is a docs-only change introducing the mode index. Surface the three-file scope explicitly.
- **PR description:** Should mention that the layout was operator-locked (Layout D from four alternatives), and that load-bearing oddities are verbatim from contract §5b (so contract changes must propagate).
- **PR rendered preview:** Worth a human eyeball on the eight in-page anchors in the GitHub-rendered MODES.md to confirm GitHub's slugging matches expectations. Programmatic verification passed; human spot-check is cheap insurance.
- **Future-touch followup (out of scope this session):** If contract.md headers are ever shortened to bare mode names (`### `firefight`` rather than `### `firefight` — incident, outage, hot-fix`), the MODES.md "Contract" column can be updated to per-mode anchors, gaining per-row signal. Explicitly not a fix for this PR.

## Verdict: APPROVE
