# VF-1B2a EXPERIMENT v2 — prospective tests, gates and work order
**This is a pre-implementation DESIGN PROTOCOL. No B2a source, moving-wall results or external biology claim has been produced by this revision. Numerical thresholds marked CANDIDATE must be registered prior to corresponding code/run.**

## Decision-grade questions and nulls (separate falsification)
- H0 legacy: identical spatial pressure load makes symmetric legacy VF-1A mode coupling zero in the antisymmetric direct-force coordinate; its damping causes decay in that mode. Analytic null, not a general no-voice theorem.
- H1 wall-force mechanism: for p_g(z)=p0+a z/Lg, nonzero a yields F_L-F_U = -ell Lg a/3 in the selected shape basis, and a=0 gives zero difference. Check independent quadrature and negative sign-mutants. H1 does NOT require persistent oscillation.
- H2 conservative moving volume: with moving walls, discrete ∆m matches face mass flux and ∆E matches full endface *total enthalpy*, ambient-reference work, signed wall work and declared sinks, with separately calculated observer. Refuse missing swept volume, doubled wall work and pU-only counterfeit.
- H3 causal flow/geometry: changing only moving-wall shape or a material property changes the predicted pressure/force or is measured null; distinguish from changing numerical discretization.
- H4 source feedback C2: only when mean/acoustic bridge is qualified, changing a passive tract load changes some **physical** tissue/flow state beyond numerical uncertainty, not solely final spectrum.
- H5 autonomous oscillation: under fixed or nonperiodic reservoir drive, without prescribed periodic A/F0, nondecaying stable oscillation if present is reproduced across step refinements, survives initial-condition control, ends after drive removal. Not finding a regime is an admissible negative result.

## Execution order and evidence dependencies
| Stage | Action | Independent comparisons | Authorized claim |
|---|---|---|---|
| A0 source inventory | Pin PR #81/#84/#209/#214/#262 exact code, ancestry and oracle hashes, review state, 10-section vs 16-section fixture separation | Git SHA + tests; reject mistaken main imports | provenance only |
| A1 derivation | Derive full continuum volume/flux+work identities and absolute/reference EOS; verify dimensionality, signs | second independently constructed control-volume/power derivation + exact linear-gradient force analytic | mathematical candidate |
| A2 model selection | Freeze chosen EOS, reservoir inflow/outflow characteristic conditions, spatial/temporal method and validity range; identify missing separation data | independent available measured/CFD rigid profiles and geometry mapping; if absent explicit HOLD | qualified *mathematical* domain only |
| A3 preregistration | Freeze SI fixtures, numerical tolerance, uncertainty, negative mutants and STOP rules before source | reviewer audits signed formula and reference relevance | B2a READY_FOR_IMPLEMENTATION or HOLD |
| B (rigid control) | Keep PR #262 v1 intact; optionally add separate high-drive model benchmark in a new experiment, never extrapolate Stokes | analytical/geometry-matched external reference | G1 limited; G2 only if independent reference permits |
| C1 moving-wall FV | Implement 2DOF tissue + compressible channel with finite reservoir boundaries, no contact and no tract | analytic wall-force, moving-volume mass test, 0-drive, manufactured/limit solutions, full energy observer | numeric moving-wall FSI only |
| C2 acoustic bridge | Derive/test baseline+perturbation energy conversion and strong p'/u' port with pinned SFI-2/3 | independent perturbation linearization, power/residual and deliberate one-way/lagged mutants | conditional physical source–tract coupling |
| D intervention | Only after C1/C2 scope passes, vary pressure/body/tract load and initial perturbation, perform shut-off | pressure/velocity phase, per-cycle tissue work, amplitude envelope, temporal/spatial refinement | G3 bounded mechanism candidate |
| E audio | Separate radiation/receiver, listenable baseline and masked listening | fixed matched task/body/gain, A/A, A/B, blind naturalness/intelligibility and provenance | G4 creative decision only |

## Engineering falsifications and acceptance
1. **Exact force identity**: uniform p_g -> F_L=F_U=ell Lg p0; linear gradient -> analytic F_L=ell Lg(p0+a/3), F_U=ell Lg(p0+2a/3). Convergent quadrature errors decrease with spatial refinement. Wrong sign or swapped upper/lower shape fails.
2. **Geometric mass test**: integrated area changes by ell Lg(vL+vU); at sealed ends, fluid mass stays constant and density adapts. If a volume term is omitted, independent mass observer detects it. Exercise moving geometry with no periodic source.
3. **Energy boundary test**: finite nonzero mean flow with prescribed endface states detects pressure-only pU accounting. Subtracting a constant ambient reference and adjusting all accompanying boundary/work terms must yield unchanged physical predictions. Double counted acoustic port, omitted enthalpy/kinetic flux, reversed wall-force, passive negative loss must fail.
4. **Passive and zero drive**: no external driving energy with equilibrated reservoirs and passive components means no artificial increase of total stored energy; initial perturbation rings down or remains neutrally stable if lossless. Preserve nonzero equilibrium ambient pressure consistently.
5. **Numerics**: prospective dt grid 1/24000,1/48000,1/96000 s at same physical duration when stable; spatial N=8/16/32 cells as initial study grid. Report convergence order/actual error and reject unresolved cases. A proposed global relative energy residual <=1e-3 is *only* an engineering candidate from PR #259, contingent on explicit signed-work denominator plus independently derived absolute floor at A3. No target is retroactively adjusted.
6. **Domain refusal**: A<=A_floor, rho<=0, unqualified reversal, invalid gamma/pressure/loss coefficient, solver nonconvergence and unsupported mean/acoustic port refuse with preserved traces. No success WAV or fake positive flow.
7. **Mechanism test**: for D, define before run minimum late-window cycles, steady-envelope slope/variance, source turn-off decay, sensitivity to initial conditions and load, and net per-cycle energy consistency; positive cumulative work alone fails. Choice of 400/800/1200 Pa from prior proposal is a *test domain* only if independent loss/reference scope authorizes it, never a presumed physiological calibration.
8. **Quality test**: no G4 before independently qualified output and listener location; no subjective human tuning during G0/G1. Once listenable, Creator's masked naturalness and usability must not be overridden by numerical PASS.

## Test harness and anti-self-certification
Use separate symbolic/analytical force oracle and a separately implemented SI mass/energy observer, not the solver's internal receipt. Use deliberate corrupted state/record mutations (interior p(z), sum-preserving flux loss changes, force sign, missing wall term, duplicate pU, negative damping) where each must fail. Evidence has immutable fixture/version/test/source hashes. Keep failed tests and later corrections. Use exact-head Python 3.11/3.12/3.13 CI, normal Core/OG3/OG4 regressions and external Codex review where available; a code review cannot substitute for external biophysical validation.

## No-claim conditions
If external measured high-drive p(z) data, boundary reference, or separation loss laws cannot be qualified: **G2 HOLD** and high-drive biology/phonation interpretation held; proceed only with explicitly mathematical low-domain tests if no misleading extrapolation. If total energy/mean–acoustic port cannot be reconciled, **C2 STOP**, not "numerically fixed" by added clipping/EQ/feedback. If numerical self-oscillation is absent, record NO_SELF_OSCILLATION_FOUND rather than tuning negative damping.

## Record management
Update SYSTEM/DATA/EXPERIMENT and decision together at every conceptual change; RESULT records separate prospective from observed claims. This v2 is not a preregistration freeze and does not supersede the historical fixed-wall PR #262 G0/G1 cutoffs or evidence. The creator's acceptance of this design and a later exact A3 scientific protocol freeze are separate decisions.
