# VF-1B2 EXPERIMENT — proposed falsification protocol, pre-code decision
**Status: DESIGN CANDIDATE / NOT PROSPECTIVELY FROZEN / NO NEW PHYSICAL RESULTS.**
Implement no sound-producing source before B2a independent audit, model equation selection, reference rights and creator review. No threshold is to be changed after viewing model output.

## Scientific unknowns first
1. Can a declared 1D moving-wall pressure/flow law predict *rigid* convergent, parallel and divergent glottal p(z) and flow without post-fit?
2. Does moving-wall mass/momentum and work couple correctly to two distinct tissue positions in the same timestep, without double counting boundary volume displacement?
3. Does the interaction transfer **positive, negative or zero** net work to each vibration mode under a steady reservoir (rather than prescribed periodic source), with energy explained?
4. Does changing *only* the passive tract load change physical tissue/flow (rather than only final signal)?
5. Is a nondecaying regime and off-response ever found in the registered parameter domain? An honest NOT_FOUND is acceptable.
6. If a frequency/flow emerges, does it have physically meaningful structure? Do not claim audible quality or ear pressure.

## B2a — prerequisite derivation + evidence quality freeze (no physical code)
- Inventory and pin exact SFI-2 #81 / SFI-3 #84 / VF-1A #209 / VF-1B1 #214 sources, review debt, baseline test oracles, and 10-section fixture hash.
- Derive **continuous and discrete** two-mass tissue, moving-volume fluid mass and momentum, pressure force, acoustic port and total energy/work equations with SI and sign/orientation. Show each internal pU/Fv term cancels *once*. If no algebraically closed energy identity, **STOP**; no code to make sound.
- Preselect a fixed-wall flow reference family: a) exact equal-area/zero-flow controls; b) independent no-separation parallel-channel analytic approximation with specified validity; c) published or independently digitized convergent/divergent pressure measurements. If external geometry/uncertainty/usage rights cannot be obtained, mark REFERENCE_UNAVAILABLE and do not award quantitative external validation.
- Decide and version **one** separation-point and viscous model with independent validity ranges; allow no per-case retuning. Choose either the moving-wall momentum ROM or an explicit alternative only after gate-A reviewer signs off. This candidate is not an already approved flow constitutive formula.
- Record source SHA+artifact digests, predeclare failure classes, exact solver tolerances and run clock. Freeze a distinct versioned scientific protocol **before** running cases B2b-d. Keep this design document unchanged as historical prospective proposal.

## B2b — rigid-wall reference and negative controls
- Three geometries with frozen identical units and mean area: parallel, convergent, divergent glottal axial profiles; no tissue movement. Pressure differences 0 / 400 / 800 / 1200 Pa used as **engineering test inputs**, not physiological normal limits.
- Compare p(z), U, pressure losses, separation location and Reynolds/Mach validity against frozen analytic/independent empirical reference with SI and geometry mapping. Compare a simple viscous Bernoulli model and a 1D momentum-based candidate under *exact same* boundary/geometry, reporting errors.
- Negative controls: zero pressure difference and equilibrated initial state -> no powered flow, reversed pressure outside supported model -> explicit UNSUPPORTED (unless independently qualified), deliberate sign inversion / negative loss coefficient -> fail, separation at impossible axial coordinate -> fail. No curve fitting after viewing holdout references.
- Decision G1 rigid flow: a successful internally conservative flow solver but unavailable empirical reference is **INDETERMINATE_BIOPHYSICS**, never a verified glottal law.

## B2c — moving-wall fluid/structure/time-domain acoustic solver
- Use exact same two physical control volumes or more as independently justified, distinct pressure forces to lower/upper mass, tract inlet p/U solved **simultaneously**; repeated waveguide stepping per timestep is forbidden.
- Test 0 Pa: initial stored perturbation evolves with no externally created energy, tissue/fluid/tract/outlet energy cannot exceed initial energy subject to boundary handling.
- Test 800 Pa with 10-section uniform tract first, then same body with 10-section constricted tract. Compare x_i, v_i, rho, p(z), U, A(z), work, internal energy, global and per-system energy residual.
- Numerical refinements 24/48/96 kHz over the same fixed 0.5 s horizon and same *physical* initial conditions. Do not infer convergence from WAV hash identity. Compare a high-resolution independent observer and analytic passive subsets. Publication of normalized residuals must include denominator and absolute Joule error.
- **Proposed quantitative engineering targets to freeze at B2a, not a physiological pass:** normalized integrated global work-energy residual <= 1e-3 when nonzero work is resolvable; otherwise a separate absolute energy/measurement floor derived *before code* from independent machine/control oracle. Full physical-state convergence across dt refinements must show decreasing error or explicitly NUMERICALLY_UNRESOLVED; no fabricated common percentage criterion for unresolved near-zero quantities.
- Tamper controls: remove moving-wall volume term, flip one wall-force sign, count the same pU port twice, inject negative damping or passive outlet energy. Independent observer MUST reject all.
- Contact: any A<=A_floor fails UNSUPPORTED_CONTACT, record partial traces and no output waveform. No on-the-fly clipping to make sustained oscillation possible.

## B2d — mechanism/phonation/intervention, conditional on B2c passing
- Registered pressure study: Psub = 0, 400, 800, 1200 Pa (constant following a declared nonperiodic startup ramp); one baseline tissue model, two signed independent initial tissue perturbations, two frozen tract-load variants. These are hypothesis-search points, **not** a calibration target for a specific expected F0.
- Observe 1 s trajectories at 48 kHz. Only for cases with repeatable late cycles, compute last-window signed per-cycle W_L/W_U, total W_plus/W_minus, D_tissue, modal/total energy change, phase p_i-v_i, area and flow spectrum, onset threshold interval and recorded uncertainty. No voiced pass from positive *cumulative* tissue work or transient 1-2 cycles.
- **Candidate sustained-regime classification:** at least 10 identifiable late cycles, late envelope growth/decay consistent with zero within the independent dt/observer uncertainty, a balanced full system ledger, no external periodic source, and repeatability under both preregistered starting perturbations. Otherwise report NO_SELF_OSCILLATION_FOUND or INDETERMINATE_TIME_HORIZON, not a tuned rescue.
- If positive, separate switch-off run: keep same body/load/solver, remove Psub after 0.5 s, observe another 0.5 s and verify subsequent free decay/cessation against 0 Pa baseline. If oscillation only persists when externally driven, label driven/resonance, NOT self-sustained phonation.
- Body contrast one factor only: change lower or upper tissue stiffness/mass/rest gap using explicitly registered *physically permissible* values, same pressure and tract. Predict **difference**, not guaranteed increase/decrease in F0. Fail/infeasible is valid observation.
- Control: original symmetric VF-1A mode pressure work stays zero (exact property of old law). A one-way flow/tract control must not be misreported as bidirectional FSI. If new nonzero antisymmetric work is below uncertainty, label unresolved.

## Gate decisions and cut lines
| Gate | Required proof | Negative / unknown |
|---|---|---|
| A (design) | full equations and independent signs/units/energy derivation; reference accessibility; exact dependency pin; independent reviewer and creator agreement | HOLD / revised design |
| G0 | exact source/fixture/trace provenance, valid SI, separate independent tests, no history rewrite | INVALID_RECEIPT |
| G1 | mass+momentum+energy closure, no manufactured energy, timestep stability/convergence, tamper controls | NUMERICALLY_UNRESOLVED |
| G2 | fixed-wall pressure/flow reference in its disclosed geometry and range; bio model scope | REFERENCE_UNAVAILABLE / BIOPHYSICS_INDETERMINATE |
| G3 | self-sustained constant-pressure dynamics and removal response, or honest absent result | NO_SELF_OSCILLATION_FOUND / INDETERMINATE |
| G4 | qualified receiver sound and creator listening/quality in separately proposed study | CREATOR_AUDIO_NO_GO; no Studio adoption |

## Evidence and scope boundaries
- Data and figures are labelled physical *computed observations* at named ports. Never call mouth-port pressure a listener's waveform or use EQ/noise to mask causal failure.
- A research pilot may succeed at G1 and fail at G3. That is an informative outcome with a preserved baseline and directs a revised model family; do not migrate failure into Studio presets.
- After each work package update SYSTEM, DATA, EXPERIMENT, append-only RESULTS and exact CI references together. No extra Studio panels, runtime import of SMC or ASMR, Core public physics ABI, new immutable Studio Take or main merge without separate approval.
- Self-oscillation G3 does not establish a naturally pleasant or intelligible voice. Post-synthesis neural beautification cannot count as a physical mechanism.
