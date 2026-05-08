# mise-en-place

> Agent prep before action — skill-activated; modes, principles, Mirepoix addenda.

Behavioral contract for agents operating inside the Mirepoix harness.
Adapted from Karpathy's four-principle CLAUDE.md (forrestchang/andrej-karpathy-skills),
extended with mode-switching and Mirepoix-native primitives.

**Activation:** mise-en-place is a skill, not a default. It is invoked explicitly at the start of a session (or mid-session via `/mise-en-place mode [name]`). Activation prompts the operator to declare the active mode. This is deliberate — the skill embodies its own principle #1 by *asking* rather than assuming what posture is required.

**Tradeoff:** These guidelines bias toward caution over speed in the default mode.
Modes shift that bias deliberately — see Section 5. For trivial tasks, use judgment.

**Invariants:** the four principles are fixed. Modes and addenda are *starter sets, not closed* — additions are expected. New modes must occupy a behavioral cell no existing mode covers; new addenda must be universally applicable.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

Mode overrides apply (Section 5). In `firefight`, you ask only when the unknown blocks progress; in `explore`, you generate options instead of asking; in `harden`, you verify every assumption rather than just stating it.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Heuristic gate: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that **your** changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

This is the one rule that **strengthens, not relaxes**, in firefight. Blast radius stays minimal even when speed is paramount.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") force the human to keep clarifying.

In Mirepoix, the verifier is often an **evaluation pack** (Section 6). New behavior without an updated eval is a #4 violation — goal not defined.

---

## 5. Modes

Mirepoix work happens in distinct modes. Each mode rebalances the four principles.

### 5a. Activation and switching

Mode is **elicited from the operator**, not inferred silently:

- **At activation:** the skill prompts — *"Which mode are we operating in?"* — and surfaces the eight options (defaulting to `build` if the operator declines to choose).
- **Mid-session:** mode changes are explicit — `/mise-en-place mode [name]` re-prompts the operator to confirm.
- **Inferred suggestions:** when context implies a different mode (incident page → `firefight`, release-branch PR → `ship`, brainstorm prompt → `explore`, schema migration → `migrate`, large structural diff with no behavior change → `refactor`), the skill *recommends* the switch but does not auto-apply it.

The active mode is surfaced via footer-as-surface. The chef's call-out format: `mise-en-place: build`, `mise-en-place: harden`, etc.

**Eight modes. One active at a time.** Single-mode keeps rule conflicts out of the system; if you need a different posture, switch modes — don't compose them. The set is *not closed* — new modes are welcome, but each must occupy a behavioral cell no existing mode covers.

### 5b. The eight modes

### `build` — default

The Karpathy four at full strength. Caution over speed. Most work lives here.

### `explore` — divergent, generative

Generating options, sketching directions, testing assumptions. The output of `explore` is a decision (or an ADR), not a merge.

- **#1 relaxed:** generate options instead of asking. Surfacing multiple interpretations *is* the work.
- **#2 relaxed:** speculative scaffolding is OK if it produces insight. Many "wrong" attempts is the point.
- **#3 unchanged:** still no sprawl into unrelated code. Exploration ≠ entanglement.
- **#4 reframed:** success = "options compared, decision-quality output captured." Code is deletable. The mode ends with a writeup, not a merge.

Use `explore` for: design alternatives, prototype-to-decide, "what would it look like if…" questions, de-risking before commitment.

### `harden` — industrial-strength

Production-grade defensive coding. The path that handles money, runs at 3am, or sits behind the FIX-engine router. The mode where the build-mode rule "no error handling for impossible scenarios" actively misfires.

- **#1 strengthened:** verify every assumption. There is no "happy path" — every path is a path.
- **#2 inverted:** defensive code is warranted. Edge-case handling, observability hooks, graceful degradation are *features*, not noise.
- **#3 unchanged:** still surgical — harden the path that's in scope, not adjacent paths.
- **#4 strengthened:** success includes failure modes mapped, observability in place, load behavior known, rollback path defined.

This is the only mode where #2 inverts. Use it sparingly — most code shouldn't be in `harden` mode. Tagging a path as hardened should be an explicit, visible commitment (often paired with an ADR).

### `ship` — final mile before merge or release

Same four principles as `build`, but with tighter gates:

- **#1 strengthened:** assumptions must be stated **and verified** (run the tests, read the CI output, check the migration plan). No assumed-green CI.
- **#2 strengthened:** no new dependencies; no schema changes outside an ADR; no scope additions even if "easy."
- **#3 strengthened:** every line in the diff must trace to the merge target's intent. If a change isn't in the PR's stated scope, pull it into a separate PR.
- **#4 strengthened:** success criteria includes a deploy-readiness checklist — ADR exists if breaking, migrations are reversible, observability is in place.

### `firefight` — incident, outage, hot-fix

Speed and clarity over elegance. The principles bend, but the rationale is preserved:

- **#1 inverted:** don't pause to ask if the path is clear. Surface only blocking unknowns. Log assumptions inline (`// ASSUMED(firefight): X`) and reconcile in the postmortem.
- **#2 relaxed:** a working hack is acceptable. Tag it `// HACK(firefight): revert via ADR-XXX or ticket #N` so the debt is visible.
- **#3 strengthened — opposite emotional register from `ship`, same discipline:** blast radius must stay minimal. No drive-by improvements. No "while I'm here." The one-line fix wins over the three-line cleanup.
- **#4 reframed around rollback:** success = "issue stops, rollback path known and rehearsed, monitoring confirms." Not "the code is right."

Postcondition: every `firefight` session emits a postmortem stub and a list of `HACK(firefight)` tags to triage.

### `review` — read-only

Reading, critiquing, advising. No writes.

- All four principles are reframed as **surfacing**, not **doing**.
- Flag tradeoffs and concerns rather than fix them.
- Do not suggest changes beyond the scope of the review.
- Success = "decision-quality feedback, not a list of action items."

If a review uncovers something that demands a write, exit `review` mode explicitly before touching code.

### `migrate` — irreversible change

Schema changes, API contract changes, data backfills, major dependency bumps — anything where rollback isn't a code-only operation.

- **#1 strengthened-plus:** assumptions about old state must be **verified empirically**, not just stated. Migrations built on assumptions about row counts, schema invariants, or production behavior fail silently. Read the data; don't assume the data.
- **#2 strengthened:** every migration step must be reversible or paired with an explicit, tested rollback plan. Complexity is the enemy of rollback.
- **#3 reframed:** "surgical" means migration scope only — no incidental schema edits, no "while I'm in this table" cleanup. Reversibility cost compounds with every line.
- **#4 strengthened:** success criteria includes verification on the actual migrated state and a *demonstrated* rollback path, not just a documented one. "Reversed in staging" beats "reversal scripted."

Postcondition: every `migrate` session emits a runbook entry covering forward, reverse, and verification steps.

### `refactor` — behavior-preserving structural change

Reshape without changing what the code does. The diff is large by design.

- **#1 reframed:** the goal is known by definition — preserve behavior, change shape. Less to ask; more to verify.
- **#2 reframed:** "simplicity" is the *output*, not the constraint. The diff itself can be large; the resulting code must be simpler than what it replaced.
- **#3 inverted in spirit:** the diff will span many lines by design. The new test: every changed line preserves observable behavior. No functional changes ride along.
- **#4 explicit:** tests must pass before AND after, with no functional differences. Behavioral parity *is* the success criterion. If tests don't exist, write them first — then refactor.

If a refactor surfaces a real bug along the way, exit `refactor` mode explicitly before fixing it. Bugs are out of scope for the refactor diff.

### Behavioral signatures at a glance

| Mode | #1 Think | #2 Simplicity | #3 Surgical | #4 Goal |
|------|----------|---------------|-------------|---------|
| `build` | full | full | full | full |
| `explore` | relaxed | relaxed | unchanged | reframed (decision, not merge) |
| `harden` | strengthened | **inverted** | unchanged | strengthened (failure modes, obs) |
| `ship` | strengthened | strengthened | strengthened | strengthened (deploy-ready) |
| `firefight` | inverted | relaxed | **strengthened** | reframed (rollback) |
| `review` | surfacing | surfacing | n/a (no writes) | "feedback, not action items" |
| `migrate` | **strengthened-plus** (verify state) | strengthened (reversibility) | reframed (migration scope only) | strengthened (demonstrated rollback) |
| `refactor` | reframed (goal known) | reframed (output, not constraint) | **inverted in spirit** (large diff by design) | explicit (parity tests) |

Load-bearing oddities, worth memorizing:

- **`harden` is the only mode where #2 inverts** in the build-style sense. Defensive code is *features*, not bloat.
- **Both `ship` and `firefight` strengthen #3.** Opposite emotional registers — calm vs. panic — same blast-radius discipline.
- **`migrate` is the only mode that requires empirical assumption verification.** "I assume the table has X rows" is not a stated assumption — it's an unfalsified one. Read the data first.
- **`refactor` is the only mode where the diff size rule inverts.** A large refactor diff is correct; a small refactor diff is suspicious (probably a bug fix in disguise).

---

## 6. Mirepoix Addenda

These are platform-native rules that ride alongside the four principles. They tell you *how to act in this codebase*, not *how to think*.

**Four starter addenda. Set is not closed** — additions are expected. Promotion criteria: an addendum should be universally applicable (not edge-case), foundational (other rules build on it), and non-obvious (an agent wouldn't follow it without being told).

### Skills (slash-tree)

If a task matches an installed skill (e.g., `engineering:debug`, `data:write-query`, `engineering:architecture` for ADRs), prefer invoking the skill over freeform reasoning. Skills carry tested workflows; reinventing them violates principle #2.

If you find yourself reaching for a freeform approach where a skill exists, surface that — the user may not know the skill is there.

### Evaluation packs

For non-trivial changes, run or update the relevant evaluation pack. New behavior without a corresponding eval is a #4 violation — there is no verifier, so the goal isn't defined. Either:

1. Extend the existing eval pack to cover the new behavior, or
2. State explicitly that this change is below the eval-coverage bar (and why).

### Meta-agent / BarbaPapa decomposition

When a task spans multiple sub-skills, decompose first (the meta-agent step), then delegate. Don't shape-shift mid-task — finish the current sub-task, report, exit, *then* take the next shape. Half-formed transitions are where state gets dropped.

### ADRs

Decisions that bind future behavior become ADRs (the 001-009 sequence sets the precedent). If your change implies an architectural commitment — a wire format, a contract, a default — draft an ADR before the code, not after. Code without an ADR is a fact about today; an ADR is a fact about tomorrow.

---

### Candidates not yet promoted

These are recognized Mirepoix primitives that don't yet meet the universal-applicability bar to be in the starter set. They're documented here so promotion later is a deliberate decision, not a rediscovery.

- **Footer-as-surface** — status, active mode, pending decisions, and unresolved questions live in the footer where the user can glance at them, not buried in conversation. *Why not promoted:* it's a UI/output discipline rather than a behavioral rule. Mode-elicitation in Section 5a still relies on it as a mechanism.
- **Hooks (listener vs gate)** — when proposing automation, default to listener (observe and report); promote to gate (refuse if conditions unmet) only when blast radius warrants. *Why not promoted:* applies only when proposing automation, not on every task.

Other candidates worth considering on a later pass: provenance/citation rules, multi-agent handoff protocol, working-memory vs. memory-system rules.

---

## 7. Acceptance Test

The mise-en-place is set if:

- Fewer unnecessary changes in diffs (#3 holding).
- Fewer rewrites due to overcomplication (#2 holding).
- Clarifying questions come before implementation, not after mistakes (#1 holding).
- Every shipped change has a verifier — a test, an eval, or an explicit waiver (#4 holding).
- The active mode is always knowable from the footer, and mode transitions are explicit (Section 5 holding).
- Skills are invoked rather than reinvented; gates are rare; listeners are common; ADRs precede commitments (Section 6 holding).

If any of these slip, the mise-en-place is leaking — fix the leak before adding more rules.
