# EL-R1 EXPERIMENT — frozen preregistration
**Registered 2026-10-22 before implementation | Issue #152 | Gate A.**

## Hypotheses
H1: A lossless passive 1D listener-side tube with R>0 generates geometry- and termination-dependent **complex** terminal pressure with a well-defined entrance p/U port.
H2: Two independent derivations (Core transfer matrix vs Wolfram traveling waves) agree at declared fixtures within numerical tolerance.
H3: Energetic passivity and losslessness hold: |Γ0|<1; P0=PL>=0 to tolerance, including reflection despite occasional |pL/p0|>1.
H4: Wrong sign/time-convention, pressure/velocity swap, load ratio mutation, discarded phase, and invalid bounds are independently detectable.

## Frozen fixtures, interventions and negatives
rho=1.21 kg/m³; c=343 m/s; area=3e-5 m²; total entrance pressure p0=1+0i Pa; f=[0,1000,3000,7000] Hz. Full factorial L in [0.02,0.025,0.03] m, R in [0.5,1.0,2.0]. Primary printed table compares f=3000 Hz (9 fixtures). Reference is an analytical traveling-wave calculation, not an empirical measurement. Mutations: changed L at fixed R, changed R at fixed L, matched R=1, complex drive linear scaling, f=0, zero-pressure drive, invalid/unsupported bounds and planes.

## Numerical acceptance predeclared
- Wolfram frozen oracle complex H and Γ0: max componentwise absolute error <= 1e-11.
- determinant residual |det T-1| <= 1e-12 for all sampled fixtures.
- power conservation |P0-PL| <= 1e-10 * max(1e-12, |P0|, |PL|).
- real active powers >= -1e-12 W; |Γ0|<1+1e-12 for strict positive R.
- matched R=1: H=exp(-ikL), Γ0=0 within 1e-11.
- Intervention: f=3000, R=2, L=.02 vs .025 vs .03 produce distinguishable **complex** H (>1e-3 absolute pairwise).
- Negative controls must throw explicit INVALID or UNSUPPORTED; numerically unresolved never hidden with clipping/damping.
- CLI can emit JSON with SI, version, planes, fixture digest and phasor conventions. CI executes pytest on PR; full repo CI must not regress.

## Audit separation
Independent Wolfram kernel output (not merely Python recomputing its own equation); reproducible oracle script and frozen records stored together. Any fixture/tolerance change after Gate A requires a numbered amendment; failed outcomes are recorded, not rewritten. Gate B verdict is not human-ear validity or ASMR naturalness.

## Gate C/D (not authorized under Gate A/B)
Sampled time-domain/48kHz listening requires causality/stability proof, sample-rate phase and delay auditing and explicit physical source calibration. Any measured SOFA dataset must disclose actual receiver reference plane before composition: a blocked-ear-canal HRTF must not receive a second ear-canal filter. Independent empirical evaluation and peer audit later.

## References
https://pmc.ncbi.nlm.nih.gov/articles/PMC3767877/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC4906304/ ; https://www.sofacoustics.org/mediawiki/index.php/SimpleFreeFieldHRIR ; https://reference.wolfram.com/language/ref/AcousticPDEComponent.html ; Core UniformTube implementation.
