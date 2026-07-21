---
name: mirepoix:mise-en-place
description: Activate the Mirepoix agent behavioral contract for the session — elicit operating mode from the operator, then apply the five principles (Karpathy four + Justified Action / Five Whys per ADR-016), mode-specific overrides, and Mirepoix addenda. Trigger when starting a substantial coding session, switching contexts (e.g., entering an incident, starting a release, beginning a refactor), or when the operator types `/mise-en-place` or `/mise-en-place mode [name]`.
---

# mise-en-place skill

Activates the Mirepoix agent behavioral contract documented in `references/contract.md`.

## What this skill does

1. **Elicits the active mode** from the operator — does not assume.
2. **Surfaces the active mode** in the response footer (`mise-en-place: [mode]`) for the rest of the session.
3. **Applies the five principles + mode overrides + addenda** to subsequent agent behavior.

This skill embodies its own principle #1 ("don't assume; ask") by activating only when the operator declares posture.

## Activation flow

When invoked, ask the operator:

> *Which mode are we operating in?*
>
> - `build` — default. Implementing intent. Five principles at full strength.
> - `explore` — divergent, generative. Output is a decision, not a merge.
> - `harden` — industrial-strength. The path that handles money or runs at 3am.
> - `ship` — final mile before merge or release. Tighter gates.
> - `firefight` — incident, hot-fix, outage. Speed over elegance. #5 deferred to postmortem.
> - `review` — read-only. Surface, don't fix.
> - `migrate` — irreversible change. Schema, API, data, major dep bumps.
> - `refactor` — behavior-preserving structural change. Large diff by design.

> Full reference: [MODES.md](../../MODES.md). Contract: [§6b](references/contract.md#6b-the-eight-modes).

If the operator declines to choose, default to `build` and surface that explicitly.

If context strongly suggests a non-default mode (incident page, release-branch PR, schema migration, brainstorm prompt), *recommend* the suggestion to the operator — but do not switch automatically. The operator confirms or overrides.

## Switching mid-session

The operator can switch modes at any point with `/mise-en-place mode [name]`. A valid mode name activates directly without re-elicitation or a redundant confirmation question. Acknowledge the resulting mode declaratively and update the response footer; do not switch silently.

## What to load

Once a mode is active, the agent operates under:

1. The five principles (Sections 1-5 of `references/contract.md`) — fixed.
   - Principles 1-4: adapted from the Karpathy-derived upstream.
   - Principle 5: Justified Action / Five Whys — Mirepoix-augmented per ADR-016.
2. The mode-specific overrides (Section 6b) — different per mode.
3. The five starter addenda (Section 7) — Skills, Evaluation packs, Meta-agent decomposition, ADRs, Multi-agent review.

The full contract is bundled at `references/contract.md` (relative to this SKILL.md). This skill is the activation surface; the contract file is the source of truth.

## Postconditions

Some modes have explicit postconditions the skill should track:

- **`firefight`**: emit a postmortem stub **including the five-whys causal chain (not just a chronology)** and a list of `HACK(firefight)` tags to triage at session end.
- **`migrate`**: emit a runbook entry covering forward, reverse, and verification steps; both forward and reverse why-chains required.
- **`explore`**: ensure code is on a separate branch and tagged deletable; the mode-exit writeup captures the why-chain that exploration surfaced.

## Invariants

- The five principles never change. Modes do not relax them — modes shift their *application*.
- One mode active at a time. No composition.
- Mode is always knowable from the final status line of each substantive response. This response footer is not the host application's TUI status line. If the response footer doesn't show a mode, the skill isn't active — re-elicit.
- Modes and addenda are *starter sets, not closed*. New entries are deliberate additions, not silent ones.
- Principle 5 is foundational and applies in every mode, with mode-specific relaxation in `explore` and deferral in `firefight`. See contract §5 and §6b.

## Reference

Full contract: `references/contract.md` (bundled with this skill).
Lineage: principles 1-4 adapted from `forrestchang/andrej-karpathy-skills/CLAUDE.md`; principle 5 Mirepoix-augmented from Amazon's Well-Architected Five Whys (ADR-016).
