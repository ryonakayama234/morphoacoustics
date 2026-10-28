# VQ-1 / G0–G1 decision sheet — proposed final design

**Date:** 2026-10-28 JST  
**Status:** DESIGN DECISION PROPOSAL / CREATOR AGREEMENT PENDING  
**Primary module:** **Core physical phonation / VF source** (not Studio, SMC or ASMR).  
**Starting code:** `morphoacoustics` `main@727b11ecf103f5c087cfcb820bdec11f883e7c03`.  
**Scope of this Draft #237:** documentation and read-only source audit; **no new solver, numerical experiment, API, audio, or main merge**.

## One-sentence decision

Do **G0-P discrete pressure/flow power-port qualification on current main** before choosing a moving tissue-force law. Separate **G1-S measured static wall-pressure qualification** and **G1-D dynamic wall-work qualification**. No invented anatomical force, negative damping, prescribed F0, wave-level beautification or silent transfer of unmerged SFI/VF research. **A physics PASS is not a creator voice PASS.**

## Why this is a character capability

In the current accepted SV1 / WG2 ancestry, a periodic flow is prescribed rather than driven by tissue material. The creator can change a fixed body and obtain an acoustic difference, but the body does not yet physically initiate/stop its own sustained phonation. The desired future intervention is

```text
Character: geometry/material    Motion: respiratory/phonatory intention
                \                        /
                 \                      /
              Core tissue force + fluid work
                             ↕
              same-step validated tract port
                             ↓
               physical sound + evidence
                             ↓
       immutable Take → existing Studio transport
```

**First deliverable is NOT that whole diagram**: it is the checkable port law and an independently measurable pressure-force *plan*. The longer-term voice identity hypothesis is deliberately conditional.

## Immutable stage boundaries

| Stage | Now proposed work | What it establishes | What it must NOT claim |
|---|---|---|---|
| **G0-P** | Fixed-duct native-tick `peek` / once-only `commit`; independent analytic scattering, signed energy, time and refusal controls | Audited acoustic port for **future** same-step coupling | Tissue, FSI, speech, arbitrary graph, sound quality |
| **G1-S** | Qualified M5 actual static measured pressure-vs-coordinate/flow, explicit geometry, uncertainty, optional independently specified force map | Static pressure/force **candidate** within model scope | Autonomous source or moving vocal fold wall stress |
| **G1-D** | Only after separate qualified dynamic reference: moving wall geometry, force, \(\dot V\), reservoir/flow/tissue/acoustic energy, concurrent timestep | Research dynamic mechanism if independently corroborated | Human physiology, natural voice or immediate Studio release |

## Explicit approach selected among force-law candidates

| Candidate for G1 | Decision |
|---|---|
| Use the current supraglottal inlet `p_in` as uniform force over the vocal folds | **REJECT**: `p_in` is an acoustic boundary, not a spatially identified glottal pressure field; may create false work |
| Use M5 35 flow/exit-pressure-coefficient values as per-tap measured pressure | **REJECT**: inverse problem is underdetermined |
| **Qualify measured M5 static wall pressure, geometry and surface force** | **SELECT G1-S**: experimentally identifiable *static* prerequisite |
| Introduce an arbitrary time lag or negative damping to create sustained oscillation | **REJECT**: physically ungrounded force/energy source |
| Carry a separately derived and validated *dynamic* pressure-to-tissue law into a coupled source | **G1-D HOLD** pending independent dynamic/reference and energy proof |
| Full 3D CFD/FSI or trained neural closure before first static reference | **DEFER**: large complexity; no need to make this the first work package |

M5 measured **static** wall pressures cannot alone validate periodic moving-wall force. If qualification is impossible, record `STOP_PHYSICAL_REFERENCE`, preserve the negative result, and reassess model or external reference *before* writing the dynamic source.

## What will be measured first

1. G0 discrete inlet: \(p_n=2b_n+(\rho c/A)U_n\) [Pa] with explicitly pre-shift \(b_n\) [Pa]; \(\Delta t=L/(cn_{\rm cells})\) [s].
2. G0 per-tick work: \(W_{\rm source}=\Delta t\,p_n U_n\) [J], comparison to independently reconstructed stored-energy change plus named outlet dissipation; detect wrong sign, wrong tick and wrong Z.
3. G0 referential state: same session snapshot must not advance on `peek`; one chosen flow commits exactly once; stale/duplicate/invalid must not alter live state.
4. G1-S actual observed \(\Delta p_i(z)\) [Pa] at qualified M5 positions and matched \(Q\) [m³/s], geometry and uncertainty. Reconstructed published pressure formulas are a *comparator*, not an independent observed pressure profile.
5. G1-D later tissue mode amplitude/phase, wall \(F_i v_i\), reservoir \(P_{\rm sub}q\), tract \(p_{\rm in}U_{\rm in}\), complete work and energy, plus no-drive/model-negative controls. Never infer sustained cycles solely from positive cumulative work or spectral peaks.

Detailed test matrix, independent oracle, proposed G0 engineering numerical targets and refusal cases are in [EXPERIMENT.md](./EXPERIMENT.md). This document is not executable test preregistration approval by itself.

## Studio closed-slot compliance

- `character.canvas` + `selection.inspector`: eventual body/material parameters, only after new physical capability and explicit UI change approval.
- `motion.canvas`: respiratory/phonatory task intention, no duplicate text compiler; separately import gated SMC.
- `scene.canvas`: Speaker/Listener and receiver, separately qualify sound propagation; ASMR independent.
- `research.drawer`: signed port and force evidence, **not an extra panel**.
- `take.transport`: immutable actual sound take only after acoustic and creator gates. No legacy history rewrite.

**NO edits** to Studio `App.tsx`, preview, layout, `PANEL_REGISTRY.json`, `src/morphoacoustics`, `src/morphoacoustics_graph`, installed schemas, external SMC or ASMR in this design PR.

## Implementation authorization requested after this design agreement

**Approve only one narrow next work package:** G0-P **source-free/voice-free test-first port adapter**, on a new Core `main`-based research branch, with its own prospective protocol committed before source/tests. Existing `PassiveWaveguideSession` numerical physics is immutable; a private research adapter is allowed, not a new production ABI. No dynamic tissue work until G1-S and G1-D pass their separately established references.

**G0 exit:** limited GO only with nontrivial port/reference tests, nonzero wave state, current-body geometry clock, exact-step work, negative mutations, stale/double-commit rejection, exact-head CI/review and synchronized diagrams/records. Failure is STOP/REVISE with raw data retained.

**G1 exit:** static source qualification, not dynamic GO; dynamic law explicitly HOLD while independent wall force and moving-wall work remain unsupported. Commit/merge decisions are separate from numerical evidence. Creator remains final judge of creative/audible benefit after later proper audition.

## Source provenance and limitations

- Main passive waveguide: `src/morphoacoustics_waveguide/passive_waveguide.py`; G0 relation is **read directly from code**, not independently experimentally validated here.
- Unmerged dependency chain: SFI-2 #81 → SFI-3 #84 → VF-1A #209 → VF-1B1 #214; VF symmetric test measured decay and no direct antisymmetric pressure work.
- Voice metrology: `docs/research/voice-metrology/CASE_001.md`. The 600 Hz M1 harmonic dominance is a separate CI mouth-port diagnostic, **not** a diagnosis of the creator's local UUIDs or a physical proof of a faulty harmonic.
- Titze (2008): https://doi.org/10.1121/1.2832337 — tract/reactance influence on source, not validation of our acoustic port implementation.
- Fulcher, Scherer & Powell (2011): https://doi.org/10.1121/1.3514424 — measured **static** M5 wall pressure, not a measured moving-fold force.
- Core #220 / #222 have candidate M5 case/35 scalar table references. The full tap-profile digitization and matched wet-surface geometry are not yet a qualified immutable Core input.

**Scientific verdict as of this proposal: `G0_PARTIAL_SOURCE_AUDIT`; `G1_S_REFERENCE_UNQUALIFIED`; `G1_D_HOLD`; `NO_NEW_PHONATION_RESULT`; `NO_CREATOR_VOICE_GO`.**

See sibling [SYSTEM.md](./SYSTEM.md), [DATA.md](./DATA.md), [EXPERIMENT.md](./EXPERIMENT.md). Their D1 appendices together with this sheet constitute the prospective decision design; all future code changes must update the three evidence views together.
