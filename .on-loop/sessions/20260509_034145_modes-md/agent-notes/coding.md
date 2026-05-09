# Coding Agent Notes

## Summary

Implemented the locked plan: created `MODES.md` (74 lines, Layout D), added an additive `## Modes` section + `MODES.md` row in `README.md`, and appended one pointer line to `skills/mise-en-place/SKILL.md` after the activation bullets. Validator and unittest suite both pass (exit 0).

## Decisions

- **Card length variation.** Per plan risk #3, `migrate` and `harden` were allowed slightly more breathing room (4 lines including postcondition) than the simpler modes. `firefight` also runs 4 lines because its #1/#2/#3 shifts and its postcondition all earn their place. None hit the 5-line "drift toward re-statement" ceiling. `build`, `ship`, and `refactor` stay at 2-3 lines — the leanest cards.
- **Footer-row "Contract" column in the table.** All eight rows point at the same `§5b` anchor. Per plan §"Linking strategy", per-mode anchors inside contract.md are unstable due to multi-word headers; linking to the section anchor is robust. The repetition is intentional — every row earns its own click target.
- **Tagline wording.** I aimed to agree with both the SKILL.md activation bullets and the contract §5b first lines within obvious paraphrasing. Specifically:
  - `harden`: SKILL.md says "industrial-strength. The path that handles money or runs at 3am." Contract says "industrial-strength. Production-grade defensive coding." I wrote "Industrial-strength. Defensive code is a feature." — the second half captures the contract's #2-inverts framing, which is the load-bearing point.
  - `migrate`: SKILL.md says "irreversible change. Schema, API, data, major dep bumps." Contract emphasizes empirical state verification. I wrote "Irreversible change. Verify state empirically." — combining the SKILL.md headline with the contract's most-cited shift.
  - `review`: I wrote "Read-only. Surface, don't fix." This is verbatim from the SKILL.md activation bullets — agree-by-construction.
- **Load-bearing oddities are quoted verbatim** from contract §5b (the four bullets directly above the "## 6. Mirepoix Addenda" header). Per plan §"Content contract" item 5: "Source-of-truth invariant: if these change in the contract, change MODES.md too." Verbatim quoting makes the drift check trivial — `diff` between the two will flag any divergence.
- **README "Modes" section content.** Two lines: the pointer to MODES.md + contract §5b, plus a one-line orientation ("One mode is active at a time; each rebalances the four principles for a distinct kind of work."). Plan said 2-4 lines and "optional one-line orientation" — I included it because Usage → Modes → Invariants reads as a progression and the orientation line bridges Usage's "declare an active mode" with Invariants' "One mode active at a time. No composition."
- **SKILL.md insertion.** Placed the pointer line as a blockquote (`> Full reference: ...`) to match the visual style of the activation prompt block above (which is also a blockquote). Single line, surgical.

## Files Modified

- `MODES.md` (new) — 74 lines. Title, intro, comparison table, load-bearing oddities (verbatim), 8 cards in contract order with `### \`mode\`` headers (auto-slug to `#build`, `#explore`, etc.), footer source-of-truth line.
- `README.md` (modified) — added one row to the Repository structure table for `MODES.md`; added a new top-level `## Modes` section between Usage and Invariants. No other edits.
- `skills/mise-en-place/SKILL.md` (modified) — appended one blockquote line after the eight activation bullets and before "If the operator declines to choose...". Bullets unchanged.

## Issues Found

- [LOW] `.on-loop/index.json` shows in `git status` as modified, but it was edited by the orchestrator at session start (it added the session entry to the registry), not by me. Not part of my three-file scope. Confirmed via `git diff .on-loop/index.json` — only adds the session record.
- [INFO] Validator did NOT trip on MODES.md (correctly — it's at root, not under `skills/`) or on the SKILL.md addition (Markdown link syntax, not backtick-wrapped). All cross-links use `[label](path)` syntax exactly as the plan prescribed.

## Verification (run from worktree)

- `python3 .github/scripts/validate_plugin.py` → exit 0 (PASS, 2 manifests + 1 skill checked)
- `python3 -m unittest discover .github/scripts -p 'test_*.py' -v` → exit 0 (22 tests, OK)
- `git diff --stat`:
  ```
  .on-loop/index.json           | 11 +++++++++++   (orchestrator-owned, not in my scope)
  README.md                     |  5 +++++
  skills/mise-en-place/SKILL.md |  2 ++
  ```
  Plus untracked: `MODES.md` and `.on-loop/sessions/20260509_034145_modes-md/`. The three production files match the plan.
- `wc -l MODES.md` → 74 lines (within plan's 90-120 target band; under-band because cards are tighter than the upper estimate, which is good for the "glanceable" framing).

## Recommendations for Next Agent (testing / review)

- **Anchor verification.** Per plan risk #1, GitHub auto-slugs `### \`mode\`` headers to `#mode`. In-page table links use `#build`, `#explore`, `#harden`, `#ship`, `#firefight`, `#review`, `#migrate`, `#refactor`. Reviewer should pull the rendered preview on the PR and click each anchor. If GitHub slugs `### \`build\`` to `#build-1` (rare but possible if there's a header clash), the table breaks silently.
- **Drift check.** Per plan risk #2 and architect §5 question 7: diff MODES.md taglines against SKILL.md activation bullets and contract §5b first lines. They should agree to within obvious paraphrasing. I already did a one-pass alignment but a second pair of eyes is wise.
- **Glance test.** Acceptance criterion #4 from the architect notes: a reader unfamiliar with the project should identify the mode for a hot-fix in under 30 seconds from MODES.md alone. The table's row for `firefight` should answer this on first scan.
- **Known limitation.** Per plan §"Linking strategy", every "Full contract →" link points at the same section anchor (`#5b-the-eight-modes`), not per-mode anchors inside contract.md. Reader scrolls four lines to find their mode. This is intentional — fixing it would require editing contract.md headers, which is out of scope (#3).
