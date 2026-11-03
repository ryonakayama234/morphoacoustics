# VF-1B2 — Design decision candidate (2026-10-31)

**Status: REVIEWABLE FINAL DESIGN PROPOSAL / NOT AN APPROVED GATE-A FREEZE / NO IMPLEMENTATION / NO MAIN MERGE.**
**Primary module:** Core experimental glottal airflow–tissue–time-domain tract coupling. Existing src/morphoacoustics, src/morphoacoustics_graph, Studio, SMC, ASMR, APIs, and Takes are unchanged by this PR.

## Creative capability and non-claims
The creator eventually designs an organ/body, proposes a phonation effort in Motion, and hears the *physical result* of that body acting; the engine may honestly fail to phonate. This stage establishes **physics mechanisms**, not a playable Studio voice, intelligible Japanese, generic species organ editor, hearing-at-ear acoustics, or physiological realism of a human larynx.

## Recommendation: 1D moving-wall flow ROM + two distinguishable tissue DOFs + existing same-tick passive acoustic tract
Adopt **model family** for a bounded experiment only, not a validated separation formula or reusable public interface. 
- **Tissue:** two coupled passive spring–mass–damper coordinates (lower / upper vocal-fold medial surface); independent local wall-pressure generalized forces.
- **Glottal fluid:** minimal finite-volume moving-area mass and momentum model, pressure storage and convective inertia with physically nonnegative viscous/separation dissipation; pressure and force derived from the *same* fluid state/geometry.
- **Acoustics:** exact pinned SFI-2 passive 1D tract and SFI-3 simultaneous p/U interface, with original matched-resistive outlet flagged as a **proxy**, not ear radiation. SA-2A is an independent frequency-domain radiation reference only; SA-2B is not yet a working causal boundary.
- **Numerics:** one simultaneous implicit coupling solve per tick, state-contiguous, not lagged p or independent-step waveforms; check solver residual, conservation, and independent observer before an acoustics or phonation claim.
- **Controls:** old VF-1A symmetric two-mass model, frozen-wall viscous Bernoulli/separation reference, zero-pressure ringdown, one-way-decoupled load. Full 3D FEM/CFD deferred to disagreement diagnosis; optional port-Hamiltonian formulation is a derivation/verification framework, not a claim an existing package is approved.

### Why these boundaries
VF-1B1 #214 found zero **direct** pressure work on the antisymmetric mode under symmetric pressure-area coefficients and strong damping of the observed motion; this is limited to that old symmetric model. VF-1B2 #215 already describes the desired pressure-work experiment. The 2020 Li et al. momentum-flow ROM study reported advantages over Bernoulli for frequency/amplitude/phase in a limited benchmark. Titze (1988) and Zhang (2016) motivate vertical-phase and tract-load contributions, not guaranteed oscillation. Energy-based fluid–structure models (2021) provide a model-class precedent for power-preserving ports.

## Governing hypotheses / pre-registered falsification targets
- H0 (legacy): the symmetric VF-1A pressure-force coupling leaves its antisymmetric coordinate with exactly zero direct fluid work, all else equal. It is a necessary negative control, not a general no-voice theorem.
- H1 (mechanism): distinct moving lower/upper sections under a single self-consistent p(z,t) law can transfer **nonzero** mode-resolved fluid work where legacy H0 cannot. H1 is false in any tested condition with numerical resolution and still-zero antisymmetric work; nonzero is not proof of positive net work or sustained oscillation.
- H2 (energetics): source, fluid, tissue, acoustic tract, boundary storage/dissipation and moving-wall work close the *same* signed energy ledger. A missing wall-displacement flow term, wrong force sign, or doubled pressure work must be caught by an independent observer. Failure means stop.
- H3 (true coupling): changing only a physically defined tract load changes at least one *physical* tissue/flow trajectory beyond measured numerical uncertainty, not merely a downstream spectrum. If not, state null/indeterminate; a hidden one-way shortcut is prohibited.
- H4 (phonation, exploratory): for some predeclared passive tissue, gap and steady reservoir conditions, oscillations grow and approach a reproducible nondecaying regime without an imposed F0, area periodicity, negative material damping or source loop. Its absence is a valid negative outcome; switch-off/decay under removed reservoir work is a separate required test if positive.
- H5 (character individuality, later): two physical tissue bodies under identical task/load have measurably distinct tissue/flow outcomes **if** H2 passes. No required direction (e.g. higher stiffness implies higher F0) is assumed.

## Explicit exclusion and staged dependencies
1. Stage B2a: exact predecessor + equations + external reference availability + chosen loss/separation law + numerical thresholds must pass independent review and be frozen **before new physical source or numerical scoring**. If an equation cannot provide a closed moving-wall work identity, STOP; do not render a 'voice'.
2. B2b: rigid-wall reference and pressure/flow oracles; no tissue oscillation claims.
3. B2c: moving-wall two-mass FSI and independent energy ledger; 0-Pa, finite no-contact, 24/48/96 kHz convergence.
4. B2d: pressure/load/body interventions and onset/cessation only **after** B2c.
5. Separate SA-2B causal radiation and receiver physics + creator audio before future production capability.
6. SFI-2 #81 → SFI-3 #84 → VF-1A #209 → VF-1B1 #214 are unmerged stacked research ancestors. Their code must be inspected and pinned; a documentation PR based on main is **not** evidence that the physical code is main-compatible.
7. Studio fixed V2 slots: Character body, Motion plan, Scene role/receiver only when physically supported, Take immutable qualified observation, research.drawer numerical traces. No new UI panel or public organ graph ABI.

## Gate semantics
B2-a APPROVED DESIGN means only that design is authorized; G0 provenance/measurement and G1 physical/numerical controls are independent. G2 measures scope/biophysical reference, G3 studies self-sustained constant-pressure source. **G4 creator sound remains NO-GO**, absent physically justified radiation, listener receive point and separate listening evidence.

## Source inventory
- Core parent: https://github.com/ryonakayama234/morphoacoustics/issues/215
- VF-1A: https://github.com/ryonakayama234/morphoacoustics/pull/209
- VF-1B1: https://github.com/ryonakayama234/morphoacoustics/pull/214
- SFI-3: https://github.com/ryonakayama234/morphoacoustics/pull/84
- SA-2B planned: https://github.com/ryonakayama234/morphoacoustics/issues/173
- Studio V2: https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md
- Titze 1988 DOI: https://doi.org/10.1121/1.395910
- Zhang 2016 DOI: https://doi.org/10.1121/1.4964509
- Li et al. 2020 DOI: https://doi.org/10.1115/1.4044033
- Energy-based FSI: https://pmc.ncbi.nlm.nih.gov/articles/PMC8210679/

**Decision sought from creator:** Agree to the bounded reference-model family, research-only dependency plan and unmodified Studio boundary. This document itself does not authorize implementation.
