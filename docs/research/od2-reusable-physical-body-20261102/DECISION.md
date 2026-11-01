# OD-2 DECISION — Versioned reusable physical body, design decision candidate (2026-11-02)

**STATUS: DESIGN COMPLETE FOR CREATOR REVIEW / NO CODE / NO A3 SCIENTIFIC PREREG FREEZE / NO CORE API ADOPTION / NO STUDIO UI APPROVAL / NO MAIN MERGE.** Parent #271. This document selects a bounded technical architecture for a future implementation, not the implementation itself.

## Creative purpose and unit of capability
A Character creator selects an organ, changes a *physical rest-shape*, retains the old Character/body/Takes, and can later replay the same valid task on either immutable body revision. The core novelty is reusable morphology as a creative asset; it is NOT an audio filter, 16 anatomy nodes, a 3D tissue model, or a proof of an attractive voice.

**Primary module:** Core Organ Modeling & Physical Assembly, initially the 16-cell serial 1D vocal-tract body. Studio Character/Inspector/Take is a later separate contract/UX gate.

## Repository audit and correction
- Core main at design start: 4d7730a5552eca1d1758e1b2f137bd5acf64950f. OD-1 PRs #267/#268 merged. The 5-cell rest-shape experiment exists only in experiments/od1_local_shape; its scientific conclusion is limited to inherited 1D physics.
- Existing Core main src/morphoacoustics/integration/body_presets.py already defines BodyPreset, BodyPresetRegistry, exact revision binding, and preparation_digest. Reuse; do not create a contradictory independent catalog.
- Existing site08 single-cell preparation/performance/replay/registry research: Core #160 and stacked unmerged Drafts #145 -> #159 -> #163 -> #165 -> #166. #166 provides an opt-in private receipt registry and restart replay. Studio PR #27 is **MERGED** and pins #166 SHA ef23738e1e6e3c631de5e36912bf5b601c7a17b3. Do NOT implement the same functionality twice or silently treat unmerged stacked code as main.
- Studio main 6bc0d715e0a66b1e770091ffdcb44cdf1a4bfca9 has approved Workspace V2 layout ADR via merged PR #34; preview PR #33 is **DRAFT and unmerged**. STOP-AND-PROPOSE before any new Studio UI code. Legacy CC-B1 site08 stays independently meaningful.
- src/morphoacoustics_graph is OG-3/OG-4 passive fixed typed acoustic.p_u graph; it is not a general active organ/FSI execution backend. Do not make 16 acoustic sections appear as 16 independent organ nodes.
- The legacy live performer audits a frozen production-source inventory. Any later change under src/morphoacoustics requires an explicit inventory migration, old known-good execution, and regression; a mere new import can break the pinned pipeline.

## Explicit alternatives
| Option | Gain | Failure mode | Decision |
|---|---|---|---|
| A. New standalone OD-2 registry + new Core body stack | quick experimental isolation | duplicates Core #160 / #166 and splits identity authority | REJECT |
| B. Expand Studio #27 site08 UI only | immediate control | stale pinned experimental Core; no reusable 5-cell Core capability | REJECT |
| C. Directly merge all stacked #145–#166, then patch 5-cell | code reuse | old PR ancestry, frozen trust boundary and deployment may not fit main | DO NOT ASSUME; audit, extract minimal reviewed components if needed |
| **D. One bounded shape-family adapter and one Core authoritative revision/readback path, reconciled with existing BodyPresetRegistry and older Gate C** | versioned physical reuse, minimal moving parts, preserves source-of-truth | needs careful identity/compatibility and exact executable gate | **SELECT** |
| E. General graph/3D material/FEM/FSI now | maximum apparent edit scope | unsupported physics and authoring semantics; invalid evidence | DEFER |

## Exact bounded family chosen
Base = audited CC-A2 M0 rest tract, 16 0.010 m sections (glottis→mouth). New family identifier = tract1d.local-log-area-5.v1, zero-based center c in {4,8}, ratio r in {0.90,1.00,1.10}, five weights (.25,.5,1,.5,.25) at c-2 ... c+2. A_i(new)=A_i(base)*r^(w_i); length, air properties, source, GestureScore and acoustic observation held fixed. All new edits must be generated through Core before their numerical geometry is available to Studio.

r=1.00 is an identity/null control referring back to the same baseline revision, not a minted 'new' body. Legacy site08 single-cell family and existing IDs remain distinct, even if numbers look similar. Exactly four new nonnull geometry configurations are supported for the initial family; two semantic null executions complete the six-case scientific matrix. No continuous slider or arbitrary site is authorized by this design.

## Model fidelity and meaning
OD-2 defines a versioned *shape asset* and its physical preparation/transport contract. It introduces no organ material constitutive law, tissue contact, glottal FSI, self-oscillating source, side-branch solution, scene receiver, vowel intelligibility or calibrated absolute SPL. Inherited prescribed LF100Hz / three-task and observer are acknowledged as limited, and Core WG2 quality NO-GO remains unchanged.

## Adoption ladder and required independent decisions
1. **DESIGN REVIEW** (this PR): creator approves objective, fixed Studio slots, chosen family, status semantics, falsifiers, and no duplicated registry.
2. **G0/G1**: existing proof/lineage and analytical shape/revision verifications. Numerical thresholds locked before new OD-2 code and outputs in separate exact-head A3 prereg commit.
3. **G2**: genuine physics execution using inherited model; no waveform synthesis at Studio. Independent same-model oracle, null/negative comparisons, and frozen OD-1 regression.
4. **G3**: one Core bounded versioned importable API or documented local CLI ABI after trust-boundary review; exact durable registration, readback/restart and archived identity. No public claims until demonstrated.
5. **G4**: approved Studio V2 integration in existing slots, with immutable physical Take and A/B user journey. No new mode or fourth panel.
6. **G5**: optional controlled perceptual discrimination/voice-likeness and creator adoption; distinct from G0–G4; 'more characters' is not inferred from waveform norms.

Each gate returns GO_LIMITED, REVISE, MORE_DATA, REJECT or NOT_TESTABLE (where solver capability absent), with exact SHA and full negative ledger. A physical pass cannot force a product pass.

## Work package and Git approach
Main remains untouched until review. Base the future development branch on current main, reconcile old #166 code through focused review/cherry-pick/reimplementation only if indispensable; never auto-merge the stacked ancestry. Freeze one authoritative body identity route, preserve old site08 and all X2a/CC-A2/OG3/OG4/SV1 contracts, compare both code-level and creator-output regressions. Keep SYSTEM/DATA/EXPERIMENT/RESULTS synchronized per work increment and failures append-only.

## External scientific framing, not project validation
VocalTractLab's geometry→area function→acoustic propagation is precedent, not an oracle validating this implementation (https://www.vocaltractlab.de/index.php?page=background). Takemoto et al. 2023 discusses limited 1D wave-propagation regimes (https://doi.org/10.1250/ast.44.9). NIST's metamorphic verification framework motivates invariants and controlled input transformations (https://www.nist.gov/publications/metamorphic-testing-continuum-verification-and-validation-simulation-models). None of these papers certifies MORPHO body identity or voice quality.
