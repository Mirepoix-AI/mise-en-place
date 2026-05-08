# mise-en-place

> Agent prep before action — Mirepoix's behavioral contract for coding agents.

`mise-en-place` is a Claude skill that activates a behavioral contract for coding agents working inside the Mirepoix harness. It adapts the four agent-behavior principles from [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (Andrej Karpathy's tweet, codified by Forrest Chang) and extends them with:

- **Eight operating modes** — `build`, `explore`, `harden`, `ship`, `firefight`, `review`, `migrate`, `refactor` — each rebalancing the four principles for a distinct kind of work.
- **An elicitation flow** — the skill *asks* the operator to declare posture rather than assuming. The activation surface embodies the contract's own principle #1 (think before coding).
- **Four Mirepoix-native addenda** — skill invocation over freeform reasoning, evaluation packs as verifiers, meta-agent decomposition before shape-shifting, ADRs that precede architectural commitments.

## Files

| Path | Purpose |
|------|---------|
| [`mise-en-place.md`](./mise-en-place.md) | Canonical contract. Four principles, eight modes (with behavioral signature table), four addenda, acceptance test. |
| [`skills/mise-en-place/SKILL.md`](./skills/mise-en-place/SKILL.md) | Activation surface. Frontmatter + activation flow + invariants. Drop into a Claude Code or Mirepoix skills directory. |

## Usage

Place `skills/mise-en-place/` into your skills directory. The skill self-describes via its frontmatter and triggers on session start, context switch, or explicit `/mise-en-place` invocation. On activation, the skill prompts the operator to declare an active mode; the rest of the session runs under that mode's overrides plus the four fixed principles plus the four starter addenda.

## Invariants

- The four principles are **fixed**.
- Modes and addenda are **starter sets, not closed** — additions are expected.
- New modes must occupy a behavioral cell no existing mode covers.
- New addenda must be universally applicable, foundational, and non-obvious.
- One mode active at a time. No composition.
- Mode is always knowable from the footer (`mise-en-place: <mode>`).

## Lineage

The four principles are kept verbatim from [forrestchang/andrej-karpathy-skills/CLAUDE.md](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md). Everything wrapped around them — modes, addenda, elicitation flow, the name itself — is Mirepoix-native.

## Status

Internal artifact, work-in-progress. Iteration expected; the contract should leak before it hardens.

## License

TBD.
