# SMC-4 Gate A — Amendment 02: Additive Task Bundles vs Exclusive Alternatives

**Date:** 2026-10-24 JST  
**Status:** SECOND POST-FREEZE DESIGN AMENDMENT / NO EXECUTABLE IMPLEMENTATION / SCIENCE_NOT_ADOPTED  
**Review origin:** GitHub Codex's second manual review of [Draft PR #175](https://github.com/ryonakayama234/morphoacoustics/pull/175) at exact SHA `947805bca9ea4615c1027db0745fab4eaddf8c95`, reporting a new P2: selection rules conflate templates that are **jointly necessary** for one pronunciation unit with mutually exclusive **alternative realizations**. Original first protocol `cc626535...` and [Amendment 01](SMC4_GATE_A_AMENDMENT_01.md) commit `4686726b...` are intentionally **preserved unchanged**.  
**Normative precedence:** This amendment *narrows and supersedes* original protocol §3.2/§4 and Amendment 01 §A2 **only as to the unit of selection**. All other clauses remain in force, including exclusive selected PronunciationPath, three-valued context, compatible shared instances, and F12 conflict-oracle.

## 1. Problem

In the original synthetic witness (see [SMC4_EVIDENCE_REGISTER.md §2](SMC4_EVIDENCE_REGISTER.md)), `P1` needs **both** `T_A` (abstract target) **and** `T_SRC` (source activity), while `P2` needs **both** `T_I` and `T_SRC`. A naïve per-unit 'choose the one winning template' drops one necessary goal; a naïve 'union every matching template' incorrectly includes mutually exclusive alternatives. The graph cannot be determined by template matching alone.

## 2. New conceptual registry entities (Gate A design only)

**`TemplateBundle`**: a versioned, context-conditioned candidate recipe selected for a **unit or declared unit-context span** on the **single selected PronunciationPath**. It declares `bundle_id`, `lexicon_revision`, applicability, evidence and a **finite set of named GoalSlots** with unique `slot_id`. Competing TemplateBundles for one target scope are *exclusive alternatives* unless a higher-level recipe explicitly declares an additive composition. **Gate B v0 does not implement higher-level bundle composition.**

**`GoalSlot`**: a named **required concurrent/additive functional role** in one TemplateBundle, e.g. `tract_target` and `source_activity`. In Gate B v0, each slot has `cardinality=EXACTLY_ONE_REQUIRED` and a nonempty finite list of alternative TaskTemplates each of which satisfies that slot's declared goal interface. **All distinct required slots are added**, but **exactly one template is selected per slot**.

**`SlotCandidate`**: a TaskTemplate reference within one GoalSlot, with independently evaluated context predicate, explicit priority where supplied, task-definition version, goal parameters, and evidence.

A single TaskTemplate definition may occur in two units' same-named slots without implying one shared *instance*. The explicit shared-episode decision and compatible-goal intersection in Amendment 01 §A3 still determine whether the resulting instances become a shared Task. `slot_id` and `bundle_id` plus candidate IDs join the mapping receipt provenance.

## 3. Deterministic selection algorithm — freeze before Gate B

1. Validate and explicitly select **exactly one complete PronunciationPath** as required by Amendment 01 §A1. No cross-path mixing.
2. For each declared mapping scope on the path, select **exactly one TemplateBundle**. Context predicates of competing bundles are tri-valued `TRUE/FALSE/UNKNOWN`: an UNKNOWN alternative that could change selection produces `INSUFFICIENT_CONTEXT`, not false. If several TRUE competing bundles exist, use only an explicit unambiguous **bundle-level priority rule** or return `AMBIGUOUS`.
3. Within the selected bundle, traverse **every REQUIRED GoalSlot** in canonical sorted slot ID order. For each slot, consider *only that slot's* eligible alternatives. Apply Amendment 01's tri-valued predicate rule **inside the slot**, with explicit slot-scoped priority for multiple TRUE candidates. If missing context could affect the choice, return `INSUFFICIENT_CONTEXT`; if multiple TRUE with no unique priority, `AMBIGUOUS`; if no eligible candidate, `UNMAPPED` and **no partial plan**.
4. **Additive composition occurs across successful distinct REQUIRED slots**, never among alternative candidates within one slot and never among mutually exclusive TemplateBundles. No optional slots in initial Gate B. A missing or failed required slot prevents any mapped plan.
5. Materialize TaskInstances for selected slot candidates. Preserve `path_id`, `bundle_id`, `slot_id`, candidate template and context provenance in the compile receipt. Do not fabricate shared identity by equal `template_id` or identical goal parameters. Apply Amendment 01 §A3 sharing compatibility only if an *explicit* cross-unit shared episode links the relevant selected slots.
6. Run defined symbolic target conflict checks (Amendment 01 §A4) and original SMC-3 timing/graph validation. Emit no partial usable plan on contradiction. Normalize input arrays deterministically; slot enumeration order cannot affect selected Task IDs or receipt.

**No new SMC-3 v0 enum or wire schema is adopted in Gate A.** `TemplateBundle`, `GoalSlot`, and selection outcomes belong to a prospective separate research-only lexical compilation layer.

## 4. Normative worked example (replaces implicit single-template selection)

With one selected pronunciation path containing P1=`/a/` and P2=`/i/` (SYNTHETIC LABELS, NOT REAL JAPANESE TASK FACTS):

```text
Bundle for P1: B_A
  REQUIRED slot tract_target    -> candidates [T_A]   -> G_A
  REQUIRED slot source_activity -> candidates [T_SRC] -> G_SOURCE(P1)

Bundle for P2: B_I
  REQUIRED slot tract_target    -> candidates [T_I]   -> G_I
  REQUIRED slot source_activity -> candidates [T_SRC] -> G_SOURCE(P2)
```

**If, and only if**, an explicit `continuous_episode_id` links the two `source_activity` slots *and* their definitions, parameter goals and time applicability pass Amendment 01 §A3 compatibility, their `G_SOURCE` instances merge into **one `G_SHARED`**. Output: 3 distinct Task IDs, exactly 4 TaskAssociation edges. If no sharing decision, output 4 distinct Task IDs and 4 edges. If same share episode but targets disjoint, return `TASK_SHARE_CONFLICT` and no plan. An additive slot is NOT a pronunciation-path alternative.

## 5. New fixed prospective adversarial oracles

- **F23 (required additive slots):** selected P1 bundle has `tract_target:[T_A]`, `source_activity:[T_SRC]`, both required. Deterministic output: *two distinct tasks and two association links for P1*. A compiler selecting only one matching template fails.
- **F24 (alternatives within one slot):** P1 bundle has one `tract_target` slot with two mutually exclusive, context-TRUE templates T_A1/T_A2. Without explicit slot priority, output `AMBIGUOUS` and **no plan**, not two additive tasks. With explicit unique priority, exactly one Task and matching evidence selected.
- **F25 (mixed additive/alternatives):** P1 requires two slots: `tract_target` with one TRUE and one FALSE candidate, `source_activity` with one TRUE candidate. Select one from each slot => *two tasks*. Changing input candidate/slot tuple order does not change canonical plan or receipt; no phantom third task.
- **F26 (missing required slot):** P1 has valid `tract_target` candidate but no eligible `source_activity` candidate. Return `UNMAPPED` with required slot ID in diagnostic, **zero emitted mapped/executable plans**; never a partial task graph.
- **F27 (bundle alternatives):** two TRUE mutually exclusive TemplateBundles B1/B2 both eligible for the same selected path and scope, each containing a complete and different slot set. With no explicit unique bundle priority return `AMBIGUOUS`, not union of their slots. If B2 is context-UNKNOWN and could alter selection, return `INSUFFICIENT_CONTEXT` (even if B1 is generic TRUE).

**F01 restatement under this amendment:** Two bundles each have **two required slots**; compatible `source_activity` selected slots are *explicitly* shared using Amendment 01 §A3, producing G_A, G_I, G_SHARED (3 tasks; 4 links) — not because of automatic task-kind deduplication. F02 remains the no-share counterexample. F18/F19 context unknown rules apply **per bundle and per slot**, not an arbitrary union of all matching templates.

## 6. Review, versioning and disposition

- This is a **prospective design correction based on an independently executed AI review**. No SMC-4 new mapping code, test suite, Japanese phonetic target or acoustic synthesizer exists.
- Initial Gate A frozen protocol `cc626535...`, first-reviewed SHA `44d21d...` and Amendment 01 are retained as immutable historical evidence, **not quietly rewritten**.
- Run the existing CI on the final amended docs SHA; make a *new* manual Codex `@codex review` request at that SHA. Do not resolve the P2 design finding until its replacement oracle and selection-group semantics receive a clear disposition.
- All four original P2 threads are retained with explicit responses; a no-findings response from a code-review bot is **limited AI design evidence**, not a human phonetic or physiology review.
- **No Gate A `GO_DESIGN_ONLY` yet; Draft PR #175 remains unmerged; SMC-3 #164 remains Draft; no `main` merge.**
