# SMC-6 A0 EXPERIMENT — hypotheses, adversarial cases and stage separation

**DESIGN ITERATION, NOT YET FROZEN PREREGISTRATION; NO TESTS/EXECUTION.** Owner #219. A later frozen Gate A protocol and distinct test-first RED commit are necessary before any implementation.

## Hypothesis map
| H | Hypothesis | Explicit falsifier | What passing would **not** prove |
| --- | --- | --- | --- |
| H0: inheritance | Exact SMC5 equalities, represented as `L=U`, yield exactly the same event table in compatibility lane | any widened feasible window or changed original digest/event time | general timing planning, phonetics |
| H1: bounded expressivity | finite rational STN expresses a non-singleton set of feasible schedules including strictly positive overlaps | exact fixture cannot represent 80..120ms overlap range or solver fabricates a unique natural schedule | realism of overlaps |
| H2: soundness | every returned witness satisfies all hard constraints exactly; contradicted network emits no witness | even one nonzero bound residual, contradicted case "RESOLVED", or unverifiable UNSAT | physical execution |
| H3: honest uncertainty | bounded but nonunique event times remain explicitly nonunique, with correct event windows and overlap extrema | report labels arbitrary witness as uniquely determined or combines independent event envelopes to compute incorrect joint overlap bounds | Bayesian/empirical uncertainty |
| H4: identity preservation | explicit Task sharing and ordering-invariant serialization keep exact object identity; semantic perturbation changes scenario identity | shared task duplicated, original digest overwritten, permutation changes result in defined invariant class | universal cross-body motor meaning |
| H5: controlled intervention | altering one hard interval with otherwise frozen identity gives predicted set/witness/sensitivity changes | unrelated input changes, wrong direction, or unreproducible metric | human speech-rate strategy |
| H6: trust boundary | arbitrary forged/invalid untrusted inputs fail closed and forbidden physical fields never appear | hand-forged SMC5 receipt trusted, illegal Task endpoint accepted, floating/NaN times accepted | production ABI/capability |

The true coupled-oscillator hypothesis `H_PHASE` is **deferred**, not merely renamed `(s_j-s_i)/d_i`. Prosodic effects, linguistic boundary effects, local realtime corrective feedback and natural Japanese pronunciation remain research questions, not evidence in this pilot.

## Preregistered **candidate** synthetic fixtures (to freeze later)
All exact fractions, finite `T=3/5s`, `min_d=1/100s`, body absent. Scenario P: `s1=0,e1=3/10`; `s2-s1∈[9/50,11/50]`; `e2-s2=19/100`.
| ID | Manipulation | Expected reference |
| --- | --- | --- |
| T01 | bounded P base | SAT, `s2∈[9/50,11/50]`, `e2∈[37/100,41/100]`, `O12∈[2/25,3/25]` |
| T02 | P + pin s2=9/50 | SAT, one witness overlap 3/25; pinned s2 unique |
| T03 | P + pin s2=11/50 | SAT, overlap 2/25 |
| T04 | separate sequential s2=3/10 | SAT, zero overlap, scenario digest distinct |
| T05 | P + s2>=7/20 | UNSAT; negative cycle; no witness |
| T06 | P + duration e2-s2=0 | UNSAT due positive minimum duration; no witness |
| T07 | valid SMC5 exact-event fixture compatibility lane | exact SMC5 timing equality, all event widths 0; unchanged inherited candidate digest |
| T08 | SMC5 exact-event input + range added WITHOUT override | exact timing remains hard; any timing variability is an invalid claim |
| T09 | explicitly declared research override of P's exact timing | new study digest and conspicuous original-exact-time omission provenance |
| T10 | permute declared unordered constraints, keep event/phonetic order | byte-identity of normalized study and identical result |
| T11 | explicit shared G2 across two units, independent G1/G3 | only one G2 ONSET/OFFSET pair; overlap rows per unique Task ID |
| T12 | duplicate/conflicting IDs, dangling task/event references, unsupported disjunction | typed rejection and no candidate/witness |
| T13 | unanchored time or absent finite horizon, invalid rational/float/NaN | refuse bounded result or report indeterminate, never choose arbitrary zero |
| T14 | add irrelevant consistent constraint / change one valid bound | metamorphic feasible set nonexpansion under added hard constraint; consistent sensitivity receipt |
| T15 | independent oracle disagreement on random small exact networks | REVISE/MORE_DATA, not pass; preserve counterexample |

## Control logic and experiment designs
**Comparison A — representational:** exact-equality-only (SMC5 legacy) versus extended bounded-hard semantics. Freeze Task IDs/TaskGoals/lexicon, intervene only timing declarations. Measure representable feasible-set width and refusals; do not compare perceived voice.

**Comparison B — schedule vs feasible set:** same P, examine earliest-vs-latest schedule and min/max overlap over *joint* feasible set. Confirm an arbitrary witness is not identified as a phonetic optimum.

**Comparison C — robustness/metamorphic:** declaration ordering, graph renaming under proven bijection, shared Task many-to-many source changes (must change provenance, not multiply occurrences), contradiction injection and relative interval tightening.

**Comparison D — future, not Gate A0:** external annotated articulatory corpus with speaker/trial conditions, compare which scheduling model predicts measured onsets; only if it has a valid measurement uncertainty/segmentation model. Later body-conditioned execution, waveform and listener assessment are independent gates.

## Methodological guardrails
1. **Freeze before code:** independent expected outputs and rational fixtures; version the protocol and demonstrate a real test-only RED run before writing solver code.
2. **Independent reference:** enumerate compact P cases symbolically / use independent shortest-path equations, not the compiler helper.
3. **No post-hoc targets:** exact algebraic checks use equality; broader stochastic/model-fit thresholds only after reference dataset and statistical power rationale.
4. **Provenance:** exact repo+base+head SHA, prereg tests commit, code commit, oracle commit, workflow URL, reviewer SHA, outcomes, and all failures retained in append-only RESULTS.
5. **Review:** Python isolated version matrix, strict mypy, Core regressions, independent GitHub @codex review; AI review is software audit only.
6. **Decision:** A0 design acceptance ≠ approval of implemented public contract; B formal limited software pass ≠ biological/acoustic/creative adoption.

## Open decisions before freezing Gate A
- Reference clock and finite horizon fixed globally or per scenario? For pilot: per-scenario explicit `T` and relative origin.
- What to do with valid SAT yet nonunique scenario? Prefer `SAT_NONUNIQUE` + optional witness, never `PHONETIC_RESOLVED`.
- Policy for duplicate equivalent constraints with distinct evidence IDs (reject vs preserve separate evidence)? Explicitly decide before protocol freeze.
- Which exact SMC5 fixture(s) exercise compatibility lane? Pin by source/candidate digest; do not fabricate a SMC5 result.
- Whether and how to propose separate `TaskIdentitySnapshot` formal API later: deferred until bounded results.

## Review literature
- Dechter, Meiri & Pearl (1991), DOI 10.1016/0004-3702(91)90006-6
- Saltzman et al. (2008), *A task-dynamic toolkit for modeling the effects of prosodic structure on articulation*
- *A procedure for estimating gestural scores from speech acoustics* (PMC3528686)
- Krause & Kawamoto (2020), DOI 10.1111/lnc3.12373
