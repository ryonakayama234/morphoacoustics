# SMC-6 A0 DECISIONS — design record and unresolved questions

**2026-10-27 JST; owner [#219](https://github.com/ryonakayama234/morphoacoustics/issues/219). STATUS: PROPOSAL / NOT AUTHORIZATION FOR IMPLEMENTATION.**

D01 — **Do not modify SMC3 SymbolicPlan or SMC5 TaskGoal/source modules in this design phase.** Time-coordination is a research-only *sidecar*. No public MotorScore ABI.

D02 — **Two explicit modes.** COMPATIBILITY imports inherited SMC5 exact timing as mandatory `L=U`; RESEARCH_OVERRIDE must declare the deliberate exclusion of source exact timing, preserve its immutable identity and mint a separate study digest. Never silently edit SMC5's certified candidate or claim its original timing was preserved after override.

D03 — **Hard STN first.** Use finite, rational, conjunctive difference intervals. Negative-cycle detection, bounded earliest/latest windows, deterministic mathematical witness policy, and an independent oracle. Do not add soft scoring until its semantics and evidence are separately designed.

D04 — **Distinguish planning from physical dynamics.** Task ONSET/OFFSET is a plan's active interval, *not* constriction position, acceleration, muscle force, source-airflow, vocal acoustic boundary or recorded speech. Core determines physical feasibility.

D05 — **No circular naturalness proxy.** Greater overlap/shorter gaps are not assumed better speech. `relative onset fraction` is not gestural planning oscillator phase. Actual oscillator coupling, prosody and language-dependent timing form follow-up studies with measured references.

D06 — **Measure the whole feasible set, not just one schedule.** SAT and selected witness are different concepts; per-event windows and jointly feasible overlap ranges are primary observables. Fixed tolerance gates for exact math must be zero; physiological data would require measured uncertainty.

D07 — **Retain identity and consent boundaries.** Public contracts, novel creator-facing controls/Direction meaning, Studio screen changes, Core capability/physical adoption or actual voice quality must STOP→present→agree. Studio V2 panel layout is accepted/frozen and untouched.

D08 — **Independent audit.** A0 design may be discussed/accepted without running source. Future test-first preregistration, exact-head CI, independent math oracle and @codex software review precede any limited formal software adoption. Historical RED #180 unchanged. No main merge.

D09 — **Open design decisions (not disguised as implementation defaults):** constraint-equivalence/duplicate provenance policy; precise scenario replay handshake; SMC5 identity extraction without treating exact timing as editable; exact minimal bound epsilon representation; witness tie-breaker and its canonical hash; future phase-dynamics research gate. Freeze them before implementing.

## How this serves the project
Creative Script and a hypothetical MotorScore can become persistent, reusable assets; changing Character morphology should change *Core realization*, never silently rewrite body-neutral Task intent. A future Studio Motion timeline can display symbolic uncertainty; the current Studio does not acquire any new controls in A0. Distinct Core metrology and subjective listening gates preserve the project's causal claim.

## Links
- [SMC-5 #210](https://github.com/ryonakayama234/morphoacoustics/issues/210), [Draft #211](https://github.com/ryonakayama234/morphoacoustics/pull/211)
- [Foundation #199](https://github.com/ryonakayama234/morphoacoustics/issues/199)
- [Studio V2 ADR](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md)
- [Studio voice quality NO-GO #32](https://github.com/ryonakayama234/morphoacoustics-studio/issues/32)
