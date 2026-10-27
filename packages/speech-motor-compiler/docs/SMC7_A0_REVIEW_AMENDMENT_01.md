# SMC-7 Gate A0 amendment 01 — Codex P2 temporal scenario and refusal receipts

**2026-10-28 JST / design correction (normative over A0 for conflicting clauses), not a Gate A freeze.**

Reviewed exact SHA aac23c41719bdf443433068e87660e0eca6a32fa; independent Codex AI design review raised **two P2**:
- [Temporal scenario P2](https://github.com/ryonakayama234/morphoacoustics/pull/230#discussion_r4389877938): same SMC5 canonical bytes can yield SMC6 UNSAT with horizon 1/10 s or SAT_UNIQUE with horizon 1 s.
- [Stage-specific digest P2](https://github.com/ryonakayama234/morphoacoustics/pull/230#discussion_r4389877954): successful SMC5 candidate and digest legitimately survive a subsequent SMC6 UNSAT.

## Normative correction to H0/H4/F09/F11/L12
1. Every direct-vs-projected SMC6 comparison MUST use the same explicitly versioned TemporalScenario: COMPATIBILITY lane, horizon, minimum duration, all extra constraints, study ID, and exact solver revision. Include both satisfiable and contradictory scenarios. There is **no** implicit scenario default; resource ceilings are distinct from original SMC5.
2. Failure receipts are STAGE-SPECIFIC. Before SMC5 compilation or after mapping refusal: no valid SMC5 candidate digest. But if SMC5 was RESOLVED and SMC6 returns UNSAT, **retain** authenticated original SMC5 plan/candidate digest and the SMC6 source digest while **forbidding** temporal witness, accepted scheduled candidate, physical execution, acoustic output and Take.
3. Compare direct/projected branches stage-by-stage. SAT may have witness/events; UNSAT cannot. Do not classify correctly diagnosed UNSAT as erroneous compilation if both frozen input arms are UNSAT.

Preserve original reviewed design and P2 comments as immutable historical evidence. Separate bounded L0 software gate from unverified L1 corpus and future L2 body/L3 audio science; do not invent Japanese reading/phonetic accuracy.

Status: DESIGN_REVISED / REVIEW_REQUIRED / NOT_PREREG_FROZEN / NO_SOURCE / NO_MAIN_MERGE.
