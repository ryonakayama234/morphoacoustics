# SMC-4 Gate A — Evidence Register, Ownership & Worked Synthetic Witness

**Created:** 2026-10-24 JST  
**Status:** DESIGN EVIDENCE MAP, NOT PHONETIC APPROVAL  
**Protocol preregistration code-free SHA:** [`cc626535cc32b56f13edbb4349f39e7cf5926e6d`](https://github.com/ryonakayama234/morphoacoustics/commit/cc626535cc32b56f13edbb4349f39e7cf5926e6d)  
**Main protocol:** [SMC4_GATE_A_PROTOCOL.md](SMC4_GATE_A_PROTOCOL.md)  
**Gate:** [Issue #174](https://github.com/ryonakayama234/morphoacoustics/issues/174).

## 1. Evidence ledger: exact claim and upper bound

| ID | Level | Source | What it grounds | It does NOT establish |
| --- | --- | --- | --- | --- |
| P-SMC3 | `OBSERVED_IN_PROJECT` | [SMC-3 PR #164](https://github.com/ryonakayama234/morphoacoustics/pull/164) / [DATA](DATA.md) at research base `f36bfd5...` | Independent symbolic task IDs, many-to-many links, `Fraction` equality checks, negative-diagnostic receipts | Correct task goals, human phonology, body execution |
| P-M5 | `PROJECT_REQUIREMENT` | [M5 #11](https://github.com/ryonakayama234/morphoacoustics/issues/11) | Short bounded script → pronunciation/gestures/coordination, unchanged script and traceable provenance; no crossfaded WAV substitutes | A completed working M5 compiler |
| P-M5b | `OBSERVED_IN_PROJECT` + `SCOPE_LIMIT` | [M5b #20](https://github.com/ryonakayama234/morphoacoustics/issues/20) | Controlled sequential/overlap example motivates explicit coordination | Universal natural coarticulation or phase law |
| P-V1V2 | `PROJECT_RESEARCH_REQUIREMENT` | [V1 #31](https://github.com/ryonakayama234/morphoacoustics/issues/31), [V2 #32](https://github.com/ryonakayama234/morphoacoustics/issues/32) | Need separate static vowel and moving-acoustics calibration evidence | Closed issue means verified phonetic task inventory |
| P-V3 | `PROJECT_RESEARCH_REQUIREMENT` | [V3 #33](https://github.com/ryonakayama234/morphoacoustics/issues/33) | Task goals bind to morphology-specific motions, with separate feasibility and phonetic-retention tests | Existing supported transferable body adapter |
| P-SKILL | `HYPOTHESIS_UNVERIFIED` | [MotorSkill / MotorPersona v0](https://github.com/ryonakayama234/morphoacoustics/blob/main/docs/research/motor-skill-persona-hypotheses-v0.md) | Distinguish intended portable task, learned body binding and habitual strategy | Verified skill learning or voice individuality |
| L-AP | `REPORTED_BY_LITERATURE` | Browman & Goldstein 1992 [DOI](https://doi.org/10.1159/000261913), [PubMed](https://pubmed.ncbi.nlm.nih.gov/1488456/) | Gesture constellations may overlap and bear phonological structure | Proven universality of our TaskDefinition family |
| L-TD | `REPORTED_BY_LITERATURE` | Saltzman & Munhall 1989 [DOI](https://doi.org/10.1207/s15326969eco0104_2) | Task-based coordination and continuous articulatory movements | This repo implements Task Dynamics equations |
| L-TADA | `REPORTED_BY_LITERATURE` | [TaDA official manual](https://static1.squarespace.com/static/6463dc0cc0fa823cfe25e5fd/t/647f8ea67dc58526b1a6b0a5/1686081191000/TADA_manual_v091.pdf) | Human vocal-tract task/gestural lexicon and timing-planning precedent | Permitted unexamined code/data reuse or cross-species definitions |
| L-JPCTX | `REPORTED_BY_LITERATURE` | Shaw & Kawahara 2021 [PubMed](https://pubmed.ncbi.nlm.nih.gov/34727587/) | Surrounding consonants affect tongue-body targetlessness for Japanese devoiced [u] | Fixed universal /u/→Task rule or direct evidence about our synthetic /a i/ |
| L-VTL | `REFERENCE_SOFTWARE` | [VocalTractLab 2.4 manual](https://vocaltractlab.de/download-vocaltractlab/VTL2.4-manual.pdf) | Gesture-score and synthesis engineering reference | A copied/validated VTL dataset in SMC |
| D-SEM | `SYNTHETIC_DEFINITION` | This Gate A protocol | Type/Template/Instance semantics, diagnostic ontology and explicit sharing rules | Observed human gesture identity |
| D-PHYS | `HYPOTHESIS_UNVERIFIED` | This Gate A protocol, V3 target | Abstract functional task variables may bind to different morphologies via separate h_M | Existence of feasible h_M for any given artificial creature |

## 2. Explicit conceptual witness (NOT a Japanese phonetic mapping)

Take supplied source `"あい"`, supplied two pronunciation hypothesis objects `P1:{symbol:"/a/",span:[0,1]}` and `P2:{symbol:"/i/",span:[1,2]}`. These are **synthetic labels** chosen to demonstrate graph construction. Nothing in this evidence register verifies these as the articulatory realization of spoken Japanese.

Assume only for this artificial test that the lexicon has:
- `T_A` → goal variable `ABSTRACT_TARGET_A`, instantiated as `G_A`;
- `T_I` → `ABSTRACT_TARGET_I`, instantiated as `G_I`;
- `T_SRC` → `ABSTRACT_CONTINUOUS_SOURCE`, instantiated as one `G_SHARED` **only if** an explicit `continuous_episode_id` is supplied by the scenario.

Expected independent graph, **not code to adopt**:

```text
                  P1 (/a/)     P2 (/i/)
                    | \         / |
                    |  \       /  |
                    v   v     v   v
                   G_A   G_SHARED   G_I
                      one shared ID
```

Four `TaskAssociation` links: (P1,G_A), (P1,G_SHARED), (P2,G_SHARED), (P2,G_I); **three distinct task instances**. If the episode is broken, replace `G_SHARED` with `G_SOURCE_1` and `G_SOURCE_2`, even though their `definition_id` and parameters are equal. No acoustic or human-phonetic inference follows from either graph.

Proposed compile receipt for this example (illustrative, not wire schema):

```yaml
stage: SYMBOLIC_MAPPING
source_provenance: caller_supplied
pronunciation_profile: synthetic_not_phonetic_evidence
lexicon_revision: smc4-test-lexicon-v0
semantic_revision: smc4-semantic-test-v0
coordination_rule_revision: none
selected_templates: [T_A, T_I, T_SRC]
sharing_rule:
  id: explicit_continuous_episode
  episode_id: demo-1
  chosen_shared_instance: G_SHARED
task_instances: [G_A, G_I, G_SHARED]
mapping_status: MAPPED_SYMBOLIC
body_status: UNVERIFIED
smc3_plan_digest: computed_from_validated_plan_only
```

**Independent negative witness:** identical templates but no `episode_id` MUST give two separate source instances; a planner that deduplicates equal definition strings fails F02. Unknown task type MUST be `UNMAPPED`, not a phoneme-named fake goal.

## 3. Abstraction pitfalls / design review questions

1. *Goal semantics:* can every candidate `task_variable` be operationally evaluated by an applicable body's observation interface, or is it just a phoneme or disguised formant? If not, mark `HYPOTHESIS_UNVERIFIED` or `REVISE`.
2. *Body independence is conditional:* a functional `CONSTRICTION` goal can be meaningful for a tract-equipped body, but meaningless for a body with no such flow-path capability. Unsupported is valid and expected.
3. *Source versus representation:* the existing SMC-3 unit has one `symbol`; a caller must choose or explicitly enumerate pronunciation candidates. No hidden lexicon-generated kanji/kana reading is permitted.
4. *Overlap and event equality:* SMC-3 supports exact relative time equality, not TaDA's phase oscillators or experimentally calibrated intrinsic durations. Unsupported richer timing must remain unsupported.
5. *Provenance at two levels:* `plan_digest` covers normalized SMC-3 plan content; a new receipt must separately hash selected lexicon entries, version, evidence, and rule bindings to detect same-plan/different-reason outcomes.
6. *Physical claims:* `INFEASIBLE` needs stronger evidence than convergence failure or absent backend. Likewise task achievement ≠ phonetic preservation ≠ perceptual voice quality.
7. *Empirical language dependency:* before using real `/a/` or `/i/` targets, inspect V1/V2 exact verified outcomes and obtain independent articulatory goal data instead of naming a pre-existing section-vector `VOWEL_A`.
8. *Licensing:* author new research-only synthetic templates. Treat TaDA/VTL as theoretical references until reuse restrictions and provenance are verified, not importable lexicon contents.

## 4. Review and implementation handoff

**Do not implement executable SMC-4 mapping under Gate A.** Once this docs-only PR is reviewed:
1. Record exact protocol, final docs SHA and CI status.
2. Ask GitHub Codex `@codex review` on the final docs-only diff, focusing on contract consistency, untestable claims, ambiguous statuses, Task identity sharing and negative controls. The review may be shallow because it is not a dedicated phonetic peer reviewer.
3. If significant review conflicts arise, record a new dated amendment and rerun review; never silently alter predeclared test expectations.
4. Gate A owner decision can be `GO_DESIGN_ONLY`, `REVISE`, `MORE_DATA`, or `REJECT`. Even `GO_DESIGN_ONLY` approves *only* a later bounded research implementation PR.
5. Gate B freezes executable tests/generators and expected fixtures before writing production mapping. Target body physics, Studio performance paths, sound synthesis and public schemas remain untouched.

Current broader research status: **SCIENCE_NOT_ADOPTED / SMC-3_PR164_DRAFT / SMC-4_DOCS_ONLY / NO_MAIN_MERGE**.

## 5. First independent AI design-critique receipt and amendment

- **Frozen prior design SHA:** `44d21d1118ff8994af430e2abd4484030f60f3a2`, exactly 3 Markdown changes; 16/16 exact-SHA GitHub CI green **only for existing software regressions**.
- **Codex manual review:** completed with `has_any_findings=true`, `has_unresolved_findings=true`; four P2 issues: (i) alternate reading paths can be combined, (ii) context UNKNOWN improperly collapses into false, (iii) explicit sharing can merge disjoint target parameters, (iv) F12 admits either pass and lacks an oracle.
- **Correction:** [SMC4_GATE_A_AMENDMENT_01.md](SMC4_GATE_A_AMENDMENT_01.md) in a separate commit `4686726b2b588e8b2350462750fe095319c43202`. The initial protocol's actual words are **preserved unchanged**. Correction defines path selection/completeness, 3-valued predicates and unknown-context refusal, task-goal intersection and provenance, hard positive-overlap scalar conflict oracle, with F12a/b/c and F16–F22 prospective fixtures.
- This is **static design-review evidence**, not a synthetic-test RED, not empirically validated phonetics. New amended docs SHA and second Codex review must be checked before claiming `GO_DESIGN_ONLY`.
