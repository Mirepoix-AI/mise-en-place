---
description: Activate the Mirepoix mise-en-place behavioral contract for the current session
---

Invoke the `mirepoix:mise-en-place` skill for this session, per the contract documented at `skills/mise-en-place/references/contract.md`.

Arguments (optional): $ARGUMENTS

If $ARGUMENTS is empty, follow the skill's default activation flow:

- Elicit the active mode from the operator. The eight modes are: `build`, `explore`, `harden`, `ship`, `firefight`, `review`, `migrate`, `refactor`.
- Default to `build` if the operator declines to choose.
- Surface the active mode for the rest of the session (footer-as-surface pattern).
- Apply the five principles (Karpathy four + Justified Action / Five Whys per ADR-016) plus the mode-specific overrides plus the Mirepoix addenda.

If $ARGUMENTS starts with `mode ` followed by one of the eight mode names, activate the skill directly in that mode without re-eliciting. Confirm the chosen mode and proceed.

If $ARGUMENTS contains anything else, treat it as operator commentary and ask whether they intended a mode switch or a different action.

Reference: `MODES.md` for the operating-mode quick reference, and `skills/mise-en-place/references/contract.md` (specifically §6b — "The eight modes") for full contract semantics.
