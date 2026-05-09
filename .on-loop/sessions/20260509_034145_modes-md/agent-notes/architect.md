# architect notes — `MODES.md`

**Session:** `20260509_034145_modes-md`
**Mode:** `explore` — divergent. Options surfaced, not prescribed.
**Scope:** add `MODES.md` at repo root; cross-link from `README.md` and `skills/mise-en-place/SKILL.md`. No production edits in this turn.

The user's framing is the constraint that does the most work: **glanceable, not a re-statement of the contract**. Everything below is downstream of that. The contract is the source of truth; MODES.md is an index/scan layer.

---

## Section 1 — Layout alternatives

Four options. Each is internally coherent; they differ in real ways (cards vs. table vs. prose; behavioral-table-embedded vs. linked; mode-first vs. scenario-first ordering).

### Option A — "Card grid" (one section per mode, fixed shape)

**One-paragraph description.** Eight uniform `### `mode`` sections, each with the same field order: tagline, when to use, the one or two principle-shifts that matter most, link into the contract anchor for depth. Reader scrolls; each card is ~6-10 lines. Behavioral-signature comparison is *linked*, not embedded — the cards already encode the per-mode shifts in prose.

**Concrete sample (two cards):**

```markdown
### `build`

**Tagline:** Default. Karpathy four at full strength.
**When:** implementing intent on a known path. Most work lives here.
**Key shifts:** none — this is the baseline the other modes shift against.
**Depth:** [contract §5b → build](skills/mise-en-place/references/contract.md#build)

---

### `firefight`

**Tagline:** Incident, hot-fix, outage. Speed and clarity over elegance.
**When:** site is down, paging fired, customer-visible breakage.
**Key shifts:**
- #1 inverted — log assumptions inline, reconcile in the postmortem.
- #3 *strengthened* — blast radius minimal even at speed. No drive-bys.
- Postcondition: postmortem stub + `HACK(firefight)` triage list.
**Depth:** [contract §5b → firefight](skills/mise-en-place/references/contract.md#firefight)
```

**Pros**
- Uniform shape — readers learn the schema once and skim every card the same way.
- Each card stands alone; great for deep-linking (`MODES.md#firefight`).
- Easy to extend when a ninth mode lands — copy the template.

**Cons**
- Eight cards is a lot of scrolling. The "glanceable" promise weakens past card 4.
- Repeating the field order eight times invites drift if someone edits one card and not the others.
- No comparative view inline — reader must click through to contract §5b for the matrix.

**Lines budget.** ~110-140 lines (8 modes × ~12 lines + frontmatter + cross-link footer).

---

### Option B — "Single comparison table" (table-first, prose-light)

**One-paragraph description.** MODES.md is dominated by one wide table: row per mode, columns for tagline, when-to-use, the headline shift, postcondition, contract anchor. Below the table, a 2-3 line preamble per mode is *omitted* — the table is the doc. A short "how to read this" intro and a pointer at the bottom to contract §5b for the principle-by-principle matrix.

**Concrete sample:**

```markdown
# Modes

Eight Mirepoix operating modes. One active at a time. The contract lives in
[contract §5b](skills/mise-en-place/references/contract.md#5b-the-eight-modes);
this page is the index.

| Mode | Tagline | When to use | Headline shift | Postcondition |
|------|---------|-------------|----------------|---------------|
| [`build`](skills/mise-en-place/references/contract.md#build) | Default. Karpathy four at full strength. | Implementing intent on a known path. | — (baseline) | — |
| [`explore`](skills/mise-en-place/references/contract.md#explore) | Divergent, generative. Output is a decision. | Design alternatives, prototype-to-decide. | #1 relaxed — generate options, don't ask. | Writeup, not a merge. |
| [`firefight`](skills/mise-en-place/references/contract.md#firefight) | Incident, hot-fix, outage. | Site is down. Pager fired. | #3 *strengthened* — minimal blast radius at speed. | Postmortem stub + HACK triage list. |
| ... | ... | ... | ... | ... |

For the principle-by-principle matrix (#1/#2/#3/#4 across modes), see
[contract §5b → behavioral signatures](skills/mise-en-place/references/contract.md#behavioral-signatures-at-a-glance).
```

**Pros**
- Maximally glanceable — one screen, one comparative view.
- Hardest layout to make accidentally drift from itself (one row per mode, columns line up).
- Strongest signal that this is an *index*, not a re-explanation.

**Cons**
- Wide tables wrap awkwardly on narrow viewports (GitHub mobile, terminal `glow`).
- "Headline shift" forces a one-shift-per-mode editorial choice; some modes (`ship`, `migrate`) shift on multiple axes meaningfully.
- No deep-linkable per-mode anchor *inside* MODES.md — you'd link straight to contract.md, which weakens MODES.md's role as the citable index.

**Lines budget.** ~40-60 lines. Smallest of the four.

---

### Option C — "Scenario-led prose" (when-to-use first, mode names as the punchline)

**One-paragraph description.** Reorders the page around the *operator's question*: "what am I doing today?" Each section opens with a scenario ("You're paged at 2am" / "You're starting a refactor"), names the mode that fits, and gives 2-3 lines on the posture shift. Mode names appear as headers but the scenarios are the navigational backbone. Behavioral-signature table linked, not embedded.

**Concrete sample (two scenarios):**

```markdown
## "I'm paged. Production is on fire."

→ **`firefight`** mode.

Speed over elegance. Log assumptions inline (`// ASSUMED(firefight): X`),
reconcile in the postmortem. Blast radius stays minimal — no drive-by
improvements, even when the file is right there. Session ends with a
postmortem stub.
[Full contract](skills/mise-en-place/references/contract.md#firefight).

## "I'm sketching design alternatives. Nothing has to merge."

→ **`explore`** mode.

Generate options instead of asking. Speculative scaffolding is OK if it
produces insight. The output is a writeup or an ADR — the code is
deletable by design.
[Full contract](skills/mise-en-place/references/contract.md#explore).
```

**Pros**
- Maps to how operators actually decide which mode to invoke ("what am I doing?" → mode).
- Reads naturally aloud and in onboarding — a new contributor learns the menu by reading scenarios, not by memorizing labels.
- Less brittle to mode renames; the scenario is the stable thing.

**Cons**
- Worst at the "I know I want `migrate`, take me there" reverse lookup. Anchor stability suffers (`#scenario-im-migrating-a-schema` is ugly; `#migrate` is what citers will type).
- Loses the "eight peers in one set" framing — modes feel like answers to disjoint questions rather than facets of one contract.
- More prose to write, more prose to drift from the contract.

**Lines budget.** ~120-160 lines.

---

### Option D — "Hybrid: table + cards" (top matrix, then per-mode mini-cards)

**One-paragraph description.** Lead with a tight comparison table (mode, tagline, when, link) — the glance layer. Below it, eight *very short* cards (3-5 lines each) covering the headline shift and postcondition. Cards exist primarily to host stable per-mode anchors (`#build`, `#firefight`, etc.) for external citers, and to give the headline shift breathing room outside a table cell. Behavioral-signature principle matrix linked, not duplicated.

**Concrete sample:**

```markdown
# Modes

| Mode | Tagline | When | |
|------|---------|------|---|
| [`build`](#build) | Default. Karpathy four at full strength. | Implementing intent. | [contract](skills/mise-en-place/references/contract.md#build) |
| [`firefight`](#firefight) | Incident, hot-fix, outage. | Production is broken. | [contract](skills/mise-en-place/references/contract.md#firefight) |
| ... | ... | ... | ... |

For the principle-by-principle matrix, see
[contract §5b → behavioral signatures](skills/mise-en-place/references/contract.md#behavioral-signatures-at-a-glance).

---

### `build`
Default. The other modes are defined as deltas from this one.
[Full contract →](skills/mise-en-place/references/contract.md#build)

### `firefight`
Speed over elegance, but #3 *strengthens* — minimal blast radius even at speed.
Postcondition: postmortem stub + `HACK(firefight)` triage list.
[Full contract →](skills/mise-en-place/references/contract.md#firefight)
```

**Pros**
- Glance-first (table) + deep-linkable anchors (cards) = best of A and B.
- Cards are short enough to resist drift — there's not much to keep in sync.
- Table doubles as a TOC; cards double as anchor targets. Each piece earns its keep.

**Cons**
- Two structures to maintain; risk of the table and the cards saying different things if edited carelessly.
- Slightly redundant — careful reader sees the same mode named twice on one page.
- Highest "construction overhead" of the four options (still small in absolute terms).

**Lines budget.** ~90-120 lines.

---

## Section 2 — Cross-link decisions (independent of layout choice)

These can be picked separately from the layout above; any layout works with any cross-link choice.

### README.md insertion point — three candidates

1. **New top-level section "Modes" between "Usage" and "Invariants"** (around line 58 of current README).
   *Why:* Usage already says "the skill prompts the operator to declare an active mode (...)" and lists the eight names. The next thing a curious reader wants is "where do I learn what those mean?" — a Modes section there is the natural answer. Anchors line up: Usage → Modes → Invariants reads as a progression from "how to invoke" → "what the choices mean" → "what's fixed."

2. **One-line pointer inside the existing "Usage" paragraph.**
   *Why:* Lowest-disruption option. Just append "See [MODES.md](./MODES.md) for what each mode means." to the existing paragraph. No new section, no restructuring. Cost: easy to miss; the link sits inside prose rather than as a header in the TOC.

3. **Add a row to the "Repository structure" table.**
   *Why:* MODES.md is structurally a sibling to SKILL.md and contract.md — it deserves a row in that table regardless of which other option wins. This is *complementary* to options 1 and 2, not exclusive.

**Recommendation:** do (1) **and** (3) together. (1) makes it discoverable in the reading flow; (3) makes it discoverable in the structural index. Cost is one section header + one table row.

### SKILL.md cross-link — two candidates

The current Activation flow lists eight modes inline as bullets (lines 22-31). Options:

1. **Replace the bullets with a single line: "See [MODES.md](../../MODES.md) for the menu."**
   *Pro:* one source of truth for mode summaries — no drift between SKILL.md bullets and MODES.md cards. *Con:* the activation prompt the agent shows the operator now requires the operator to flip files mid-prompt, which weakens the elicitation UX. The bullets are *the prompt the agent reads aloud*; demoting them makes the prompt less self-contained.

2. **Keep the bullets (they're terse) and append a single pointer line:** `> Full reference: [MODES.md](../../MODES.md). Contract: [contract §5b](references/contract.md#5b-the-eight-modes).`
   *Pro:* activation stays self-contained; MODES.md becomes the next-step for "tell me more." *Con:* mild duplication — the SKILL.md bullets and MODES.md taglines must agree. In practice they should be near-identical anyway.

**Recommendation:** (2). The bullets in SKILL.md are part of the *spoken activation prompt*, not a reference. They serve a different function than MODES.md and shouldn't be replaced by a link.

### Anchor strategy — yes

Every mode should have a stable bare anchor (`#build`, `#explore`, `#harden`, `#ship`, `#firefight`, `#review`, `#migrate`, `#refactor`) in MODES.md. Reasons:

- External citers (ADRs, postmortems, internal docs) will want to deep-link to "the firefight definition" — and MODES.md is a more stable target than a deep section of contract.md.
- Single-word anchors are typeable from memory.
- Markdown auto-generates these from `### `mode`` headers — zero extra cost in layouts A, C, D. Layout B (pure table) gets anchors *only* if the cards-after-table option is added.

This consideration is mild evidence for layouts A or D over pure-B.

---

## Section 3 — Behavioral-signature table

The contract §5b ends with a 4-column-by-8-row matrix of how each principle shifts per mode, plus four "load-bearing oddities" bullets. Three options for MODES.md:

1. **Repeat verbatim.**
   *Pro:* MODES.md becomes self-sufficient — no click-out for the comparative view. *Con:* drift risk is real; the contract is explicitly the source of truth, and a duplicated table will eventually disagree with it after one careless edit. Violates the "glanceable, not a re-statement" framing.

2. **Render differently** (e.g., transpose: one row per principle, columns per mode; or collapse the 4 columns into a single "headline shift" column already covered by the cards/table in Section 1).
   *Pro:* divergent shape signals "this is the index view, contract has the rigorous view" — no drift because there's nothing to drift *into*. *Con:* operators reading both files now need to mentally re-pivot; small cognitive tax.

3. **Link to it, don't repeat.**
   *Pro:* zero drift, smallest doc, sharpest "this is an index, contract is the truth" framing. *Con:* the comparative principle-by-principle view is one click away, not on-page.

**Recommendation:** (3) — link to it. The contract §5b matrix is dense and rigorous; that's its job. MODES.md's job is the scan layer. Forcing the matrix to live in two places creates a maintenance burden that the user's "glanceable, not a re-statement" framing explicitly rules out. The "load-bearing oddities" bullets (`harden` is the only mode where #2 inverts, etc.) are arguably worth quoting directly in MODES.md *because* they're memorable scan-layer payoff — but that's a separable call from the matrix itself.

A reasonable middle: link the matrix, but inline the four oddities bullets (~6 lines). Best of both — comparative depth stays in contract; the most-cited insights stay in scan-layer reach.

---

## Section 4 — Recommendation (explore-mode style — non-prescriptive)

If I had to ship today, I'd ship **Layout D (hybrid table + cards)** with **README cross-links at insertion points (1) + (3) combined**, **SKILL.md handled via option (2) — bullets retained, MODES.md pointer appended**, and **behavioral-signature handling option (3) — link to contract §5b, but inline the four "load-bearing oddities" bullets**.

Reasoning, briefly:

- Layout D wins because it satisfies both reading goals: (a) the wide table answers "show me all eight at once" in 8 lines; (b) the per-mode cards give stable `#mode` anchors for external citers — and they stay short enough to resist drift. It pays a small redundancy tax, and that tax is the price of being both glanceable and citable.
- Cross-link (1)+(3) is additive, not exclusive — costs one section header and one table row in README, and MODES.md becomes findable from both the reading flow and the structural index.
- SKILL.md bullets stay because they're part of the *spoken* activation prompt, not a reference list.
- Linking the §5b matrix preserves the source-of-truth invariant; quoting the four oddities is a small win because they're the most memorable insights in the whole contract.

**But I'd happily ship Layout B if the operator prefers smallest-possible-doc.** B is sharper as a pure index; the cost is no per-mode anchors. If MODES.md will be deep-linked frequently, prefer A or D. If it will mostly be linked-to as a whole, B is fine.

The operator should pick. I have no strong evidence about deep-link frequency.

---

## Section 5 — Open questions / risks for downstream agents

For the implementer (build/ship agent):

1. **Anchor format.** GitHub auto-generates `#build` from `### `build``. Verify by previewing — backticks in headers occasionally produce surprising slugs (`#build-1` if the heading was templated wrong, `#build-default` if a tagline trails the mode name on the same line). The implementer should test the anchors after writing.

2. **Contract.md anchors.** Cross-links into contract.md (e.g., `contract.md#firefight`) only work if contract.md exposes those anchors. Contract.md uses `### `firefight` — incident, outage, hot-fix` as a header; GitHub will slug that to `#firefight--incident-outage-hot-fix` or similar. The implementer should either (a) shorten contract.md headers to bare mode names — but that's an out-of-scope edit per principle #3 — or (b) link to `contract.md#5b-the-eight-modes` and let the reader scroll, or (c) use exact-slug deep links and verify them.
   **Recommendation:** option (b) — link to the section anchor, not per-mode anchors inside contract.md. Avoids editing contract.md from a MODES.md-scoped session.

3. **mise-en-place.md root symlink.** The repo has a `mise-en-place.md` symlink to the contract at root for browse convenience (per README). MODES.md will sit alongside it. Consider whether MODES.md should link to `./mise-en-place.md#5b-...` (the symlink) or the real path `./skills/mise-en-place/references/contract.md#5b-...`. The symlink is friendlier for casual readers; the real path is unambiguous. Pick one and use it consistently.

4. **CI validation.** `.github/workflows/validate.yml` (per README) checks "relative-reference integrity across all skill files." MODES.md is not a skill file (it's at root), so it likely isn't covered by the existing checks — but cross-links *into* skill files (SKILL.md → MODES.md) might trip the validator if it walks SKILL.md links. Worth a dry-run before merge.

5. **Postcondition mentions.** Three of the eight modes have explicit postconditions (`firefight`, `migrate`, `explore`/`spike`). The samples above include them in the `firefight` card; the implementer should be consistent across all eight cards — either every card has a postcondition line (most read "—") or only the three that do, with no awkward empty placeholders.

6. **License/attribution.** MODES.md is downstream of the proprietary contract; no special attribution needed (the four principles are upstream, but mode names and mode definitions are Kavara-proprietary per LICENSE). One footer line `> Source of truth: [contract §5b](...)` is sufficient.

For the review agent:

7. **Drift check.** Whichever layout ships, the reviewer should diff MODES.md taglines against SKILL.md bullets and against contract §5b's first lines per mode. The three should agree to within obvious paraphrasing. If they don't, MODES.md is the one to align (it's downstream of both).

8. **Glance test.** Time-to-comprehension is the implicit acceptance criterion. A reasonable check: a reader unfamiliar with the project should be able to answer "which mode do I use for a hot-fix?" in under 30 seconds from MODES.md alone. If they can't, the layout failed regardless of which one was picked.
