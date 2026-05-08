---
name: mirepoix:mise-en-place
description: Activate the Mirepoix agent behavioral contract for the session — elicit operating mode from the operator, then apply the Karpathy four principles, mode-specific overrides, and Mirepoix addenda. Trigger when starting a substantial coding session, switching contexts (e.g., entering an incident, starting a release, beginning a refactor), or when the operator types `/mise-en-place` or `/mise-en-place mode <name>`.
---

# mise-en-place skill

Activates the Mirepoix agent behavioral contract documented in `mise-en-place.md`.

## What this skill does

1. **Elicits the active mode** from the operator — does not assume.
2. **Surfaces the active mode** in the footer (`mise-en-place: <mode>`) for the rest of the session.
3. **Applies the four principles + mode overrides + addenda** to subsequent agent behavior.

This skill embodies its own principle #1 ("don't assume; ask") by activating only when the operator declares posture.

## Activation flow

When invoked, ask the operator:

> *Which mode are we operating in?*
>
> - `build` — default. Implementing intent. Karpathy four at full strength.
> - `explore` — divergent, generative. Output is a decision, not a merge.
> - `harden` — industrial-strength. The path that handles money or runs at 3am.
> - `ship` — final mile before merge or release. Tighter gates.
> - `firefight` — incident, hot-fix, outage. Speed over elegance.
> - `review` — read-only. Surface, don't fix.
> - `migrate` — irreversible change. Schema, API, data, major dep bumps.
> - `refactor` — behavior-preserving structural change. Large diff by design.

If the operator declines to choose, default to `build` and surface that explicitly.

If context strongly suggests a non-default mode (incident page, release-branch PR, schema migration, brainstorm prompt), *recommend* the suggestion to the operator — but do not switch automatically. The operator confirms or overrides.

## Switching mid-session

The operator can switch modes at any point with `/mise-en-place mode <name>`. Re-prompt to confirm the switch and update the footer. Do not switch silently — mode transitions must be visible.

## What to load

Once a mode is active, the agent operates under:

1. The four principles (Sections 1-4 of `mise-en-place.md`) — fixed.
2. The mode-specific overrides (Section 5b) — different per mode.
3. The four starter addenda (Section 6) — Skills, Evaluation packs, Meta-agent decomposition, ADRs.

The full contract is in `/Users/jekavara/Documents/Claude/Projects/Project Pi/mise-en-place.md`. This skill is the activation surface; that file is the source of truth.

## Postconditions

Some modes have explicit postconditions the skill should track:

- **`firefight`**: emit a postmortem stub and a list of `HACK(firefight)` tags to triage at session end.
- **`migrate`**: emit a runbook entry covering forward, reverse, and verification steps.
- **`spike`/`explore`**: ensure code is on a separate branch and tagged deletable.

## Invariants

- The four principles never change. Modes do not relax them — modes shift their *application*.
- One mode active at a time. No composition.
- Mode is always knowable from the footer. If the footer doesn't show a mode, the skill isn't active — re-elicit.
- Modes and addenda are *starter sets, not closed*. New entries are deliberate additions, not silent ones.

## Reference

Full contract: `mise-en-place.md` (project root).
Lineage: adapted from `forrestchang/andrej-karpathy-skills/CLAUDE.md` (the four principles), extended for Mirepoix.
