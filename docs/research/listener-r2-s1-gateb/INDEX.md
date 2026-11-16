# EL-R2-S1 Gate B — design refinement index

**2026-10-27 JST | DESIGN_REVIEW_ONLY | no implementation authorized by this document | no scientific/product adoption.**

## Purpose and evidence level
The creator selected independent, speaker-free ASMR/listener research. This design increment sharpens the computational *measurand*, causal interventions, architecture, data/provenance and failure policy **before** any Gate B solver is written. It is NOT new ear measurements or a renewed Gate A preregistration. The end-user ambition is eventually a receiving-side, versioned optional capability for Studio Scene; the present result can only be a limited synthetic 1D circuit study.

**Immutable scientific predecessor:** [EL-R2-S1 Gate A Draft PR #158](https://github.com/ryonakayama234/morphoacoustics/pull/158), head **489111e19ffa18b21c4c4cadba8ef19f84e11bb4**, [Issue #157](https://github.com/ryonakayama234/morphoacoustics/issues/157), parent [#156](https://github.com/ryonakayama234/morphoacoustics/issues/156). Frozen oracle Git blobs: JSON **f89ccf20cb60019c4487873a13af678e983beb6b**, Wolfram source **fa8c2112f36f2b7119d40e8125e4d979ba091eef**. Never edit the frozen data, change accepted tolerances retroactively, or imply the source fixture is empirically calibrated. Gate A numerical predictions were obtained before that registration and are **not blinded**.

Architecture/ownership: [ASMR PR #155](https://github.com/ryonakayama234/morphoacoustics/pull/155) was metadata-only merged 2026-10-24; [asmr/ARCHITECTURE.md](../../../asmr/ARCHITECTURE.md), [PR #83](https://github.com/ryonakayama234/morphoacoustics/pull/83), [Issue #53](https://github.com/ryonakayama234/morphoacoustics/issues/53). Do not inherit code from unmerged EL-R1 PR #153.

## Read/search route
| Question | Source of truth |
|---|---|
| Scientific question and causal architecture | [SYSTEM.md](./SYSTEM.md) |
| Measurands, observation envelope, SI, reference planes | [DATA.md](./DATA.md) |
| Competing hypotheses, nulls, evidence ladder and prereg gates | [EXPERIMENT.md](./EXPERIMENT.md) |
| What an independent reviewer must check | [REVIEW.md](./REVIEW.md) |
| Operational pre-code tolerances, unique passive solve, exact oracle coverage and refusal matrix (prospective) | [PROTOCOL-V1.md](./PROTOCOL-V1.md) |
| Actually executed vs NOT RUN and future decision ledger | [RESULTS.md](./RESULTS.md) |
| Original 18 rows, existing numerical acceptance limits | [PR #158 frozen EXPERIMENT](https://github.com/ryonakayama234/morphoacoustics/blob/489111e19ffa18b21c4c4cadba8ef19f84e11bb4/docs/research/listener-r2-s1/EXPERIMENT.md) |

## Current status
- GATE_A_ORACLE = EXISTING_PRELIMINARY_WOLFRAM, not physical evidence.
- GATE_B_DESIGN = PROPOSED_FOR_REVIEW, this branch is documents only. 2026-10-28 prospective operational [PROTOCOL-V1](./PROTOCOL-V1.md) added; independent review and coding authorization NOT given.
- GATE_B_SOLVER / GATE_B_NEW_CI / INDEPENDENT_SCIENCE_AUDIT = NOT_RUN.
- GATE_C_MEASURED_ACOUSTICS / GATE_D_ASMR_PERCEPTION / STUDIO_FEATURE = NOT_AUTHORIZED.
- morphoacoustics_asmr currently only exports metadata; this design does not change its registry, package API, or Studio UI.

## Branch hygiene
This branch starts directly from Core main **e05e3274ad69bfb9202816049f6661a18ba39ec0** to avoid stacking unmerged research history. Only the five+ design/ledger files in this directory may change. When implementation is separately approved, use a new isolated research branch/PR tied to Gate A source hashes and this design decision; do not mutate either historical Gate A or this design review's baseline. No forced merge and no CI claim based solely on documentation.
