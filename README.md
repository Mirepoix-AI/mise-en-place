# mise-en-place

> Agent prep before action — Mirepoix's behavioral contract for coding agents.

`mise-en-place` is a Claude skill that activates a behavioral contract for coding agents working inside the Mirepoix harness. It adapts the four agent-behavior principles from [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (Andrej Karpathy's tweet, codified by Forrest Chang) and extends them with:

- **Eight operating modes** — `build`, `explore`, `harden`, `ship`, `firefight`, `review`, `migrate`, `refactor` — each rebalancing the four principles for a distinct kind of work.
- **An elicitation flow** — the skill *asks* the operator to declare posture rather than assuming. The activation surface embodies the contract's own principle #1 (think before coding).
- **Five Mirepoix-native addenda** — skill invocation over freeform reasoning, evaluation packs as verifiers, meta-agent decomposition before shape-shifting, ADRs that precede architectural commitments, and multi-agent review when the project declares a reviewer list.

## Repository structure

This repository is both a **Claude Code marketplace** and the **plugin** itself (a single-plugin marketplace). The layout:

| Path | Purpose |
|------|---------|
| [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) | Marketplace manifest — declares this plugin |
| [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) | Plugin manifest |
| [`skills/mise-en-place/SKILL.md`](./skills/mise-en-place/SKILL.md) | Activation surface — the skill itself |
| [`skills/mise-en-place/references/contract.md`](./skills/mise-en-place/references/contract.md) | Canonical contract — four principles, eight modes, five addenda, acceptance test |
| [`MODES.md`](./MODES.md) | Index for the eight operating modes — taglines, when-to-use, links into the contract |
| [`mise-en-place.md`](./mise-en-place.md) | Symlink to `skills/mise-en-place/references/contract.md` for browse-at-root convenience |

## Install

### Claude Code (CLI)

From any terminal on a machine with the repo cloned (or with SSH access to the private repo):

```bash
# From a local clone:
claude plugin marketplace add /path/to/mise-en-place

# Or directly from GitHub (requires SSH access to the private repo):
claude plugin marketplace add UlyssesModel/mise-en-place

# Then install the plugin:
claude plugin install mise-en-place@mirepoix
```

Restart Claude Code. The skill will appear under `/plugin` → Installed.

### Cowork (desktop)

The Cowork plugin manager accepts the bundled `.plugin` file directly. Build it with:

```bash
cd /path/to/mise-en-place
zip -r /tmp/mise-en-place.plugin .claude-plugin skills README.md LICENSE
```

Then drag `/tmp/mise-en-place.plugin` into Cowork's plugin install affordance.

## Usage

On activation, the skill prompts the operator to declare an active mode (`build`, `explore`, `harden`, `ship`, `firefight`, `review`, `migrate`, `refactor`). The rest of the session runs under that mode's overrides plus the four fixed principles plus the five starter addenda.

Trigger with `/mise-en-place`, or let the skill self-trigger at session start / on context switches. Switch modes mid-session with `/mise-en-place mode [name]`.

## Modes

Eight operating modes — see [MODES.md](./MODES.md) for the index, or [contract §5b](skills/mise-en-place/references/contract.md#5b-the-eight-modes) for the rigorous definition. One mode is active at a time; each rebalances the four principles for a distinct kind of work.

## Invariants

- The four principles are **fixed**.
- Modes and addenda are **starter sets, not closed** — additions are expected.
- New modes must occupy a behavioral cell no existing mode covers.
- New addenda must be universally applicable, foundational, and non-obvious.
- One mode active at a time. No composition.
- Mode is always knowable from the footer (`mise-en-place: [mode]`).

## Lineage

The four principles are kept verbatim from [forrestchang/andrej-karpathy-skills/CLAUDE.md](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md). Everything wrapped around them — modes, addenda, elicitation flow, the name itself — is Mirepoix-native.

## CI

Every push and pull request to `main` runs `.github/workflows/validate.yml`,
which checks JSON manifest validity, SKILL.md frontmatter integrity (including
an XML-tag ban that prevents the `fcb93f5` regression), and relative-reference
integrity across all skill files. No external dependencies — stdlib Python only.
See [`.github/scripts/README.md`](./.github/scripts/README.md) for details.

## Status

Internal artifact, work-in-progress. Iteration expected; the contract should leak before it hardens.

## License

Proprietary — Copyright (c) 2026 Kavara. All rights reserved. Internal use only. See [LICENSE](./LICENSE) for full terms and upstream attribution.

The four principles in Sections 1–4 of the bundled contract (`skills/mise-en-place/references/contract.md`) are adapted from [forrestchang/andrej-karpathy-skills/CLAUDE.md](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md), which is MIT-licensed. Everything else (modes, addenda, elicitation flow, skill wrapper) is Kavara-proprietary.
