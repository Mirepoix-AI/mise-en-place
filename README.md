# mise-en-place

> Agent prep before action — Mirepoix's behavioral contract for coding agents.

`mise-en-place` is a Claude skill that activates a behavioral contract for coding agents working inside the Mirepoix harness. It adapts the four agent-behavior principles from [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (Andrej Karpathy's tweet, codified by Forrest Chang), adds a fifth principle (Justified Action / Five Whys, Mirepoix-augmented from Amazon's Well-Architected framework per ADR-016), and extends them with:

- **Eight operating modes** — `build`, `explore`, `harden`, `ship`, `firefight`, `review`, `migrate`, `refactor` — each rebalancing the five principles for a distinct kind of work.
- **An elicitation flow** — the skill *asks* the operator to declare posture rather than assuming. The activation surface embodies the contract's own principle #1 (think before coding).
- **Five Mirepoix-native addenda** — skill invocation over freeform reasoning, evaluation packs as verifiers, meta-agent decomposition before shape-shifting, ADRs that precede architectural commitments, and multi-agent review when the project declares a reviewer list.

## The five principles

1. **Think Before Coding** — Karpathy-derived. Don't assume; surface tradeoffs; ask when uncertain.
2. **Simplicity First** — Karpathy-derived. Minimum code that solves the problem; nothing speculative.
3. **Surgical Changes** — Karpathy-derived. Touch only what you must; clean up only your own mess.
4. **Goal-Driven Execution** — Karpathy-derived. Define success criteria; loop until verified.
5. **Justified Action / Five Whys** — Mirepoix-augmented (added v0.5.0 per ADR-016). Every substantive action serves an iterative why-chain traceable to a load-bearing root premise. Five iterations is a checkpoint, not a quota or hard limit. Time is the operator's most valuable commodity; blame the system, never the operator.

## Repository structure

This repository is both a **Claude Code marketplace** and the **plugin** itself (a single-plugin marketplace). The layout:

| Path | Purpose |
|------|---------|
| [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json) | Marketplace manifest — declares this plugin |
| [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) | Plugin manifest |
| [`skills/mise-en-place/SKILL.md`](./skills/mise-en-place/SKILL.md) | Activation surface — the skill itself |
| [`skills/mise-en-place/references/contract.md`](./skills/mise-en-place/references/contract.md) | Canonical contract — five principles, eight modes, five addenda, acceptance test |
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

The Cowork plugin manager accepts the bundled `.plugin` file directly. Build the canonical bundle with:

```bash
cd /path/to/mise-en-place
python3 scripts/build_cowork_bundle.py --output /tmp/mise-en-place.plugin
python3 scripts/build_cowork_bundle.py --check /tmp/mise-en-place.plugin
```

The bundle includes both activation surfaces: `skills/` and `commands/`, plus the manifests and supporting metadata. Then drag `/tmp/mise-en-place.plugin` into Cowork's plugin install affordance.

## Usage

On activation, the skill prompts the operator to declare an active mode (`build`, `explore`, `harden`, `ship`, `firefight`, `review`, `migrate`, `refactor`). The rest of the session runs under that mode's overrides plus the five fixed principles plus the five starter addenda.

Trigger with `/mise-en-place`, or let the skill self-trigger at session start / on context switches. Switch modes mid-session with `/mise-en-place mode [name]`.

## Modes

Eight operating modes — see [MODES.md](./MODES.md) for the index, or [contract §6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) for the rigorous definition. One mode is active at a time; each rebalances the five principles for a distinct kind of work.

## Invariants

- The five principles are **fixed**.
- Modes and addenda are **starter sets, not closed** — additions are expected.
- New modes must occupy a behavioral cell no existing mode covers.
- New addenda must be universally applicable, foundational, and non-obvious.
- One mode active at a time. No composition.
- Mode is always knowable from the final status line of substantive responses (`mise-en-place: [mode]`). This response footer is not the host application's TUI status line.

## Lineage

Principles 1-4 are adapted from [forrestchang/andrej-karpathy-skills/CLAUDE.md](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md) (MIT-licensed upstream). Principle 5 is Mirepoix-augmented from Amazon's [Well-Architected Five Whys](https://wa.aws.amazon.com/) — the technique is upstream, the foundational placement and the mode-specific override structure are Mirepoix's. Everything wrapped around the principles — modes, addenda, elicitation flow, the name itself — is Mirepoix-native. See [ADR-016](https://github.com/UlyssesModel/kavara-mirepoix-internal/blob/main/adrs/ADR-016-mise-en-place-principle-5.md) for the architectural commitment that authorized the fifth principle.

## CI

Every push and pull request to `main` runs `.github/workflows/validate.yml`,
which checks JSON manifest validity and parity, SKILL.md frontmatter integrity
(including an XML-tag ban that prevents the `fcb93f5` regression), relative
references, and the canonical Principle 5 invariant. CI also runs Claude Code's
official plugin validator in strict mode and builds and inspects the Cowork
archive, including its slash-command surface. The repository validator and its
tests remain stdlib-only; the official validator is pinned in the workflow.
See [`.github/scripts/README.md`](./.github/scripts/README.md) for details.

## Status

Internal artifact, work-in-progress. Iteration expected; the contract should leak before it hardens.

## License

Proprietary — Copyright (c) 2026 Mirepoix AI. All rights reserved. Internal use only. See [LICENSE](./LICENSE) for full terms and upstream attribution.

Principles 1-4 in the bundled contract (`skills/mise-en-place/references/contract.md`) are adapted from [forrestchang/andrej-karpathy-skills/CLAUDE.md](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md), which is MIT-licensed. Principle 5 is Mirepoix-augmented from Amazon's Well-Architected framework (also openly published; Mirepoix's contribution is the foundational placement and mode-specific overrides). Everything else (modes, addenda, elicitation flow, skill wrapper) is Kavara-proprietary.
