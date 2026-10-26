# EL-R1 — Embodied Listener Acoustic Port
**2026-10-22 JST | RESEARCH CANDIDATE | NOT ADOPTED | NO PRODUCTION CHANGE**

Primary tracker: [#152](https://github.com/ryonakayama234/morphoacoustics/issues/152).
Independent of listener research [PR #83](https://github.com/ryonakayama234/morphoacoustics/pull/83), G0 [#114](https://github.com/ryonakayama234/morphoacoustics/pull/114), G0a [#129](https://github.com/ryonakayama234/morphoacoustics/pull/129), breath [#138](https://github.com/ryonakayama234/morphoacoustics/pull/138), and oral nearfield [#53](https://github.com/ryonakayama234/morphoacoustics/issues/53).

## Reading order
1. [SYSTEM.md](./SYSTEM.md) — physical causal placement, p/U conventions and boundaries.
2. [DATA.md](./DATA.md) — fixture, versioned ports, observational identity and failure classes.
3. [EXPERIMENT.md](./EXPERIMENT.md) — preregistered hypotheses, controls, oracle and quantitative gates.
4. [AUDIT-AMENDMENT-A1.md](./AUDIT-AMENDMENT-A1.md) — post-registration audit response.\n5. [RESULTS.md](./RESULTS.md) — outcome ledger, not a plan.
6. [Experimental code](../../../experiments/043_el_r1_ear_port/) — candidate only, no Core public API.

## Scope
Only **passive listener-side** transfer between named canal entrance and terminal planes is modeled. A fixed external calibrated entrance-pressure excitation is an experimental boundary, not a Speaker body or a microphone measurement. Data are synthetic and **cannot** validate human physiology, ASMR pleasantness, or blocked-canal HRTF integration.

## Gate status
Gate A: pre-registered 2026-10-22. Gate B: not yet accepted; see RESULTS. Gates C/D separate studies. Main and Studio remain untouched.

## Sources
- Existing Core [UniformTube](../../../src/morphoacoustics/acoustics/uniform_tube.py) and [architecture](../../architecture.md).
- Ear canal input impedance and lossy 1D transmission-line study: https://pmc.ncbi.nlm.nih.gov/articles/PMC3767877/
- Acoustic ear-canal p/U and impedance terminology: https://pmc.ncbi.nlm.nih.gov/articles/PMC4906304/
- SOFA SimpleFreeFieldHRIR reference and receiver geometry: https://www.sofacoustics.org/mediawiki/index.php/SimpleFreeFieldHRIR
- Wolfram [AcousticPDEComponent](https://reference.wolfram.com/language/ref/AcousticPDEComponent.html) — independent numerical PDE validation may be a later study; current oracle is algebraic traveling waves.
