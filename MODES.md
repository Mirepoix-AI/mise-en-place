# Modes

Mirepoix runs in eight operating modes. One is active at a time; each rebalances the **five Mirepoix principles** for a distinct kind of work. This page is the index — the rigorous definitions live in [contract §6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes), which is the source of truth. If a tagline here disagrees with the contract, the contract wins.

| Mode | Tagline | When | Contract |
|------|---------|------|----------|
| [`build`](#build) | Default. Five principles at full strength. | Implementing intent on a known path. | [§6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) |
| [`explore`](#explore) | Divergent, generative. Output is a decision. | Design alternatives, prototype-to-decide. | [§6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) |
| [`harden`](#harden) | Industrial-strength. Defensive code is a feature. | Money paths, 3am paths, FIX-engine paths. | [§6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) |
| [`ship`](#ship) | Final mile. Tighter gates than `build`. | Merge or release with deploy-readiness checks. | [§6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) |
| [`firefight`](#firefight) | Incident, hot-fix, outage. Speed over elegance. | Site is down, pager fired, customer-visible breakage. | [§6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) |
| [`review`](#review) | Read-only. Surface, don't fix. | Critiquing or advising on code you won't write. | [§6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) |
| [`migrate`](#migrate) | Irreversible change. Verify state empirically. | Schema, API contract, data backfill, major dep bump. | [§6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) |
| [`refactor`](#refactor) | Behavior-preserving structural change. Large diff by design. | Reshape without changing what the code does. | [§6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes) |

The five principles:

1. **Think Before Coding** (Karpathy)
2. **Simplicity First** (Karpathy)
3. **Surgical Changes** (Karpathy)
4. **Goal-Driven Execution** (Karpathy)
5. **Justified Action / Five Whys** (Mirepoix-augmented from Amazon's Well-Architected; added v0.5.0 per ADR-016)

For the principle-by-principle matrix (#1/#2/#3/#4/#5 across the eight modes), see [contract §6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes).

## Load-bearing oddities

Worth memorizing — these are the non-obvious points the contract calls out explicitly:

- **`harden` is the only mode where #2 inverts** in the build-style sense. Defensive code is *features*, not bloat.
- **Both `ship` and `firefight` strengthen #3.** Opposite emotional registers — calm vs. panic — same blast-radius discipline.
- **`migrate` is the only mode that requires empirical assumption verification.** "I assume the table has X rows" is not a stated assumption — it's an unfalsified one. Read the data first.
- **`refactor` is the only mode where the diff size rule inverts.** A large refactor diff is correct; a small refactor diff is suspicious (probably a bug fix in disguise).
- **`firefight` is the only mode where #5 defers entirely.** Mid-incident causal analysis is a known anti-pattern; the principle pauses for the duration of the act-rollback-verify cycle and resumes in the postmortem with full force.

---

### `build`

Default. The five principles at full strength; the other modes are defined as deltas from this one. Most work lives here. Every action gets a why-chain (#5 full).
[Full contract →](skills/mise-en-place/references/contract.md#6b-the-eight-modes)

### `explore`

#1 and #2 relax: generate options instead of asking; speculative scaffolding is OK if it produces insight. #3 holds — exploration is not entanglement. #5 relaxes: instinct-driven exploration is allowed; the why-chain may not be complete yet — defer to mode-exit writeup.
Postcondition: a writeup or ADR. The code is deletable by design.
[Full contract →](skills/mise-en-place/references/contract.md#6b-the-eight-modes)

### `harden`

#2 inverts: defensive code, edge-case handling, observability hooks, and graceful degradation are *features*, not noise. #1 and #4 strengthen — every path is a path; success includes failure modes mapped and rollback defined. #5 strengthens — every failure mode mapped must include a why-this-could-happen chain. Use sparingly; tagging a path as hardened is an explicit, visible commitment.
[Full contract →](skills/mise-en-place/references/contract.md#6b-the-eight-modes)

### `ship`

All five principles strengthen. Assumptions stated *and* verified, no new dependencies, every line traces to the merge target's intent, deploy-readiness checklist met. #5 strengthens to "why-this-ships-now chain" — the why must terminate in a load-bearing premise, not "...because we said we would." No assumed-green CI.

The ship gate also runs under multi-agent review when the project declares a reviewer list; any REQUEST_CHANGES blocks delivery until resolved and re-reviewed or explicitly waived by a human. Retry exhaustion is not approval — see [contract §7 / Multi-agent review](skills/mise-en-place/references/contract.md#7-mirepoix-addenda).
[Full contract →](skills/mise-en-place/references/contract.md#6b-the-eight-modes)

### `firefight`

#1 inverts: log assumptions inline (`// ASSUMED(firefight): X`), reconcile in the postmortem. #2 relaxes — a working hack is acceptable, tagged `// HACK(firefight): ...`. #3 *strengthens* — blast radius minimal even at speed; no drive-by improvements. **#5 defers entirely** — do NOT run five-whys during the incident; resume in the postmortem.
Postcondition: postmortem stub including the five-whys causal chain (not just chronology), plus a list of `HACK(firefight)` tags to triage.
[Full contract →](skills/mise-en-place/references/contract.md#6b-the-eight-modes)

### `review`

All five principles reframed as **surfacing**, not **doing**. Flag tradeoffs and concerns rather than fix them; don't suggest changes beyond the review's scope. Success is decision-quality feedback, not an action-item list. #5 applies to findings — every flagged finding traces to at least one iteration of why; "this looks wrong" is insufficient. If a review uncovers something that demands a write, exit `review` mode explicitly first.

When the project declares a reviewer list, review work dispatches to those reviewers in parallel and requires unanimous APPROVE; requested changes remain blocking unless a human explicitly records a waiver — see [contract §7 / Multi-agent review](skills/mise-en-place/references/contract.md#7-mirepoix-addenda).
[Full contract →](skills/mise-en-place/references/contract.md#6b-the-eight-modes)

### `migrate`

#1 strengthens-plus: assumptions about old state must be **verified empirically** — read the data, don't assume it. #2 strengthens around reversibility; #3 means migration scope only (no incidental schema cleanup); #4 requires a *demonstrated* rollback path, not a documented one. #5 strengthens bidirectionally — both "why does this migration succeed?" and "why does the rollback work?" must terminate in load-bearing premises.
Postcondition: a runbook entry covering forward, reverse, and verification steps.
[Full contract →](skills/mise-en-place/references/contract.md#6b-the-eight-modes)

### `refactor`

#3 inverts in spirit: the diff is large by design. The new test is that every changed line preserves observable behavior — no functional changes ride along. Tests must pass before AND after. #5 applies to the refactor's existence — "why this refactor now?" must terminate in a load-bearing premise (architecture debt, scaling pressure, vocabulary alignment per ADR-014). Refactor-for-aesthetics is among the most expensive ways to spend time. If a refactor surfaces a real bug, exit `refactor` mode explicitly before fixing it.
[Full contract →](skills/mise-en-place/references/contract.md#6b-the-eight-modes)

---

> Source of truth: [contract §6b](skills/mise-en-place/references/contract.md#6b-the-eight-modes)
