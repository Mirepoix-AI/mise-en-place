# Sub-phase — Addendum #5: Multi-agent review

**Resolves:** Codifies the multi-agent review face-off pattern as a behavioral commitment in the mise-en-place contract. Promotes the pattern from downstream Kavara experiment to contract addendum.

**Empirical evidence:** Two PR-level face-offs in `UlyssesModel/kavara-mirepoix-internal` (PR #11 codex-teammate, PR #12 codex-events / Issue #10) — both caught real architectural issues a single reviewer had approved past.

**Phase:** mise-en-place v0.4.0. Mode: `build`.

## Context

The mise-en-place contract currently has four starter addenda — slash-tree skill discipline, evaluation packs, meta-agent decomposition, ADRs precede commitments. The promotion criteria from existing addenda (universally applicable, foundational, non-obvious) was an intentional gate: addenda are not casual additions.

Recent Kavara work introduced a fifth pattern that meets the same criteria — multi-agent review. The pattern dispatches review and ship-gate work to multiple agents in parallel when the project being operated on declares a reviewer list. Empirically validated across two face-offs:

- **PR #11 (codex-teammate spec)** — Codex caught vocabulary inconsistencies and deliverables-convention compliance gaps that Claude APPROVE'd past.
- **PR #12 (codex-events / Issue #10)** — Codex caught a verdict-vocabulary mix (source vs gate-normalized), an ADR-005 audit-envelope violation, a state-machine completeness bug (3-of-5 rescue states), and three missing fields. Claude APPROVE'd without raising any of these.

Two-for-two on real architectural issues caught by the second reviewer. The pattern has earned promotion to the contract.

## Goal

Add addendum #5 — multi-agent review on declared convention — to the behavioral contract. Update the supporting documentation (MODES.md cross-references for `review` and `ship`, CHANGELOG, version manifests) so the addendum is correctly surfaced when the skill activates.

The addendum codifies the *dispatch and reconciliation shape*. The *reviewer-identifier vocabulary* stays project-defined (typically declared in the project's `CLAUDE.md`).

## Functional requirements

**FR-1.** Add addendum #5 to `skills/mise-en-place/references/contract.md` under the existing addenda section. Match the structural pattern of addenda #1–4: short principle-stating description, not a multi-paragraph explanation. Include:

- The name: "Multi-agent review"
- The principle: high-stakes review and gate work dispatches to multiple agents in parallel when the project declares a reviewer list
- The reconciliation rule: unanimous APPROVE — any REQUEST_CHANGES blocks delivery until resolved and re-reviewed or explicitly waived by a human; retry exhaustion must not silently continue the phase
- The activation convention: project-level `CLAUDE.md` declares the reviewer list (typically via a `## Multi-agent review` section)
- An empirical-evidence pointer to `UlyssesModel/kavara-mirepoix-internal#11` and `#12`

**FR-2.** Add brief cross-references in `MODES.md` for `review` and `ship` modes noting the addendum's behavior when active. These are *cross-references*, not structural changes to the mode definitions — the modes themselves are unchanged.

**FR-3.** Add an entry to `CHANGELOG.md` for version `0.4.0`. Follow the existing Keep a Changelog format used in earlier entries (0.1.0, 0.2.0, 0.3.0). Include the empirical-evidence references and the promotion-criteria justification (briefly — the contract text doesn't need it; the CHANGELOG does).

**FR-4.** Bump the plugin version in:
- `.claude-plugin/plugin.json`: `0.3.0` → `0.4.0`
- `.claude-plugin/marketplace.json`: `0.3.0` → `0.4.0`

MINOR bump per SemVer — behavior addition, no breaking change.

**FR-5.** If `SKILL.md`'s activation prompt enumerates the addenda explicitly, update the enumeration to include addendum #5. If it doesn't, no change.

**FR-6.** Ensure the CI validator from PR #1 still passes — no XML-like tags in frontmatter descriptions, all backtick-quoted `.md` references inside `SKILL.md` resolve to existing files on disk.

## Constraints

- **Promote the pattern's shape only, not its implementation.** mise-en-place is a behavioral contract; it specifies what agents should do, not how they do it. The addendum says "dispatch to multiple reviewers in parallel and require unanimity"; it does *not* prescribe code, plugin internals, or specific reviewer identifiers.
- **No upstream changes.** The addendum stays Kavara-side. on-loop is not modified. Joe's upstream is not contributed to.
- **No reviewer-identifier hardcoding.** The contract accepts arbitrary reviewer identifiers (`claude`, `codex`, future agents like `gemini` or `local-qwen`); the dispatch layer downstream looks them up. The addendum does not enumerate "supported" reviewers.
- **Backward-compatible.** Projects whose `CLAUDE.md` does not declare the multi-agent review convention see no behavior change. The addendum is opt-in via the declared convention.
- **Maintain `[name]` / `[mode]` placeholder convention** in any frontmatter descriptions per the CI validator from PR #1.
- **Match the existing voice.** Addenda #1–4 are short and structural — single line or single short paragraph each. Addendum #5 should match. If your draft exceeds three sentences for the principle-stating text, you're over-explaining.

## Success criteria

1. `contract.md` has a fifth addendum following the structural pattern of addenda #1–4, with requested changes remaining blocking unless a human explicitly records a waiver.
2. `MODES.md` has brief cross-references for `review` and `ship` to the new addendum.
3. `CHANGELOG.md` has a `0.4.0` entry with the empirical-evidence pointers and promotion-criteria justification.
4. Both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` report version `0.4.0`.
5. CI validator passes (no XML tags in descriptions, all `.md` references resolve).
6. `SKILL.md` continues to render correctly with the new contract.
7. The README, if it lists addenda, is updated to include #5; otherwise no change.

## Non-goals

- Implementing the dispatch and reconciliation logic — that is downstream tooling concern (on-loop, future Kavara extensions), not the contract's job. The contract is the *behavioral commitment*; the implementation is wherever runs the agents.
- Specifying the exact `CLAUDE.md` syntax in the contract. Recommend a `## Multi-agent review` section as illustrative, but the project being operated on owns the syntax — the contract is agnostic.
- Modifying any of the eight modes structurally — the addendum operates on top of modes, not as a mode.
- Contributing upstream to `joestein/on-loop` — explicitly rejected per the Kavara-side strategic decision to keep the face-off pattern Kavara-private.
- Adding code to mise-en-place — this is a markdown-only sub-phase.

## Deliverables

- `skills/mise-en-place/references/contract.md` — modified (addendum #5 added)
- `MODES.md` — modified (`review` and `ship` cross-references)
- `CHANGELOG.md` — modified (`0.4.0` entry)
- `.claude-plugin/plugin.json` — modified (version bump `0.3.0` → `0.4.0`)
- `.claude-plugin/marketplace.json` — modified (version bump `0.3.0` → `0.4.0`)
- `specs/multi-agent-review-addendum.md` — this spec, committed alongside

`SKILL.md` and `README.md` updated *only if* either currently enumerates the addenda. Otherwise no change.

## Key references

- `skills/mise-en-place/references/contract.md` — current contract with four starter addenda. Architect should read this before drafting the addendum text to match voice and length.
- `MODES.md` — current eight-mode quick-reference.
- `CHANGELOG.md` — Keep a Changelog format, SemVer convention; existing entries for 0.1.0, 0.2.0, 0.3.0 show the house style.
- `.github/workflows/validate.yml` + `.github/scripts/validate_plugin.py` — CI validator from PR #1.
- Empirical evidence:
  - `UlyssesModel/kavara-mirepoix-internal#11` (codex-teammate spec, first multi-agent face-off)
  - `UlyssesModel/kavara-mirepoix-internal#12` (codex-events / Issue #10, second face-off — Codex caught 4 real issues + 3 missing fields)

## Notes for the architect during PLAN

- **Read `contract.md` before drafting.** The four existing addenda are short and structural; addendum #5 should match that voice and length. If your draft is two paragraphs explaining context, that's over-explanation — the contract text should be principle-stating, not justification-providing. The CHANGELOG is where the justification lives.
- **The reconciliation rule (unanimity) is the load-bearing architectural commitment.** Make sure the contract text is unambiguous: REQUEST_CHANGES blocks delivery until resolved and re-reviewed or explicitly waived by a human. Retry exhaustion is not approval and must never cause silent continuation. This is the property that produced PR #12's wins.
- **The empirical-evidence references belong in the contract**, not just the CHANGELOG. Future readers should see the empirical justification in the contract itself — "this pattern is in the contract because PR #11 and #12 demonstrated it." Without that reference, future operators may treat the addendum as theoretical.
- **The addendum is project-agnostic.** Reviewer identifiers are arbitrary strings the contract doesn't enumerate. Don't write "claude and codex"; write "the reviewer identifiers declared by the project."
- **Promotion criteria justification doesn't need to be in the addendum text** — that's the CHANGELOG's job. But verify each of the three criteria holds: *universally applicable* (any review work benefits), *foundational* (review is part of every coding workflow), *non-obvious* (not default agent behavior).
