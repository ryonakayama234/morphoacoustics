# EL-R2-S1 Gate B — implementation-entry protocol v1 (proposal)

**2026-10-28 JST | DOCUMENTATION ONLY | PROTOCOL_REVIEW_REQUIRED | NO IMPLEMENTATION / NO MERGE / NO ADOPTION.**

This is an **additive prospective review proposal**, not an amendment to the immutable Gate A preregistration, not an independent empirical result, and not a creator's approval to code. Read after [INDEX](./INDEX.md), [SYSTEM](./SYSTEM.md), [DATA](./DATA.md), [EXPERIMENT](./EXPERIMENT.md), and [REVIEW](./REVIEW.md).

Frozen authority: [Gate A PR #158](https://github.com/ryonakayama234/morphoacoustics/pull/158) head 489111e19ffa18b21c4c4cadba8ef19f84e11bb4; oracle JSON Git blob f89ccf20cb60019c4487873a13af678e983beb6b; generating Wolfram source Git blob fa8c2112f36f2b7119d40e8125e4d979ba091eef. Existing 18 observations, analytic feasibility, tolerances, and experimental claims **must not be rewritten**. The previous Wolfram predictions were non-blinded exploratory/analytic calculations, not independently blinded empirical validation.

## 1. Target: computational estimands, not physical measurement

**Question:** Under a fixed synthetic equivalent drive ps and **absolute** resistances Zs and Zt, what are the complex pressure and volume-flow states at the entrance and terminal of a lossless, rigid, constant-area one-dimensional acoustic tube, and does a Core-based boundary solve reproduce independently frozen traveling-wave predictions?

- Exogenous inputs: geometry A,L, frequency f; air rho,c; prescribed peak phasor ps and absolute Zs,Zt. In the primary factorial **only A,L,f vary**.
- Direct computational measurands (solution coordinates): complex p0,U0 at CANAL_ENTRANCE and pL,UL at TERMINAL_SIDE. ps is a *virtual circuit-source drive*, not a physical microphone plane.
- Derived, explicitly NOT independently measured: Zc, Zin, Gamma_in, H_drive=p0/ps, H_canal=pL/p0, H_total=pL/ps, normalized geometry kL, source/load ratios rs,rt, complex pair contrasts, and mean active powers.
- Verification observables: immutable-oracle error, boundary residuals, source-loss ledger, tube-loss ledger, passivity, determinant, numerical conditioning, exact runtime/provenance, and typed refusal outcomes.
- Excluded: any anatomical ear or middle-ear impedance, ear-drum pressure, fixed free-field excitation, real source calibration, HRTF, binaural localization, perceived loudness/tingles, time-domain/WAV, contact and Studio Takes.

The interpretation is **paired mathematical counterfactuals under identical equivalent-circuit fixture parameters**, not a controlled real-ear anatomy effect. "Calibrated source" MUST mean only numerically specified synthetic source in this gate; empirical calibration is Gate C.

## 2. Planes and governing law — one owner

~~~text
SOURCE_EQUIVALENT (virtual ps, Zs)
  ps = p0 + Zs U0
        |
CANAL_ENTRANCE (total p0 [Pa], U0 [m3/s])
        |
Core UniformTube T(L,A,rho,c,f) — UNMODIFIED
  [p0,U0] = T [pL,UL]
        |
TERMINAL_SIDE (pL [Pa], UL [m3/s])
  pL = Zt UL  -> real absolute terminal Zt > 0
        |
Research-only typed observations / separate power ledgers
        |
Frozen Wolfram traveling-wave oracle / negative controls / reviewer verdict
        |
FUTURE only: science adoption -> versioned ASMR adapter -> opt-in Studio
~~~

Positive U points entrance to terminal at both planes; exp(+i omega t) *peak* phasors; SI Pa, m3/s, Pa s/m3, W. Only f>0 supports the declared harmonic mean-power formulas. Do not impose p0=ps except in the **separate** Zs=0 control; do not re-normalize Zt=R*Zc during fixed-absolute-load intervention.

Physics authority: existing Core src/morphoacoustics/acoustics/uniform_tube.py; no copied physical implementation and no changes to that file, source/gestural model, Core public API, morphoacoustics_asmr runtime, or Studio. Future implementation, separately authorized, would live in experiments/044_el_r2_s1_source_load/ on a fresh independent Draft branch and copy/reference **byte-identical** frozen oracle artifacts with their content hashes, never import code from unmerged EL-R1.

## 3. Exact design and contrasts

Unchanged primary 2 x 3 x 3 = 18 rows:
- A = {3e-5, 6e-5} m2
- L = {0.020, 0.025, 0.030} m
- f = {1000, 3000, 7000} Hz
- rho = 1.21 kg/m3; c = 343 m/s; ps = 1+0i Pa
- fixed absolute Zs = 13834333.333333334 Pa s/m3; Zt = 27668666.666666668 Pa s/m3.

For each same-(L,f) A pair, record Delta_A pL = pL(A2)-pL(A1) in complex Pa (**9 area pairs**), along with paired changes in H_drive and H_canal. For each same-(A,f) adjacent L pair, record Delta_L pL = pL(L2)-pL(L1) (**12 adjacent-length pairs**). Ratios and log-magnitude contrasts are supplemental only where source and reference port pressures are sufficiently nonzero. Never interpret phase differences without the same reference plane and phasor convention.

Primary benchmark H_B1–H_B5 and their Gate A tolerances remain controlling. H_B6–H_B8 below are proposed **new, prospective** implementation diagnostics and require reviewer agreement before code; none is silently promoted to original Gate A evidence.

## 4. Hypotheses and proposed operational acceptance

| ID | Claim / falsifier | Observable and proposed rule |
|---|---|---|
| H_B1 (frozen) | Matrix-source/load matches independent Wolfram waves | All 18 exact row IDs, p0/pL real+imag and three oracle powers checked to **original Gate A thresholds**, never loosened |
| H_B2 (frozen) | Source match cancels L-dependent *magnitude*, not phase | A=3e-5 => rs=1, rt=2, H_total=(2/3) exp(-ikL): magnitude 2/3 within frozen 1e-11; varying L must change phase as predicted |
| H_B3 (frozen) | Absolute load makes A-intervention non-null | At f=3000 Hz,L=.025m,A=6e-5, |pL|~0.4492470594476995 Pa vs baseline 2/3 Pa; other 18-row fields still oracle checked |
| H_B4 (frozen) | Two conservation boundaries, no invented tube dissipation | r_source=Pdrive-Pentrance-Psource_loss and r_tube=Pentrance-Pterminal meet original Gate A tolerances; passive powers nonnegative within specified tolerance |
| H_B5 (frozen) | Ideal-source and normalized-load are DIFFERENT fixtures | Zs=0 => p0=ps; separate total-p0 and Zt=R Zc control reproduces EL-R1 algebraic limit without using its unmerged code |
| H_B6 (new) | Source-loading and tube factors are numerically consistent; NOT two separately identified physical causes | Every nonzero-drive primary row: complex H_total - H_drive*H_canal, max of real/imag absolute error <=1e-11 dimensionless. For 9 A pairs, record both complex factors and optional log-magnitude decomposition; do not attribute all Delta_A pL to H_canal |
| H_B7 (new) | Source-matched L change is a pure delay in *terminal transfer ratio* | For 6 adjacent L pairs at A=3e-5, compare complex H_total(L2)/H_total(L1) to exp(-i 2 pi f(L2-L1)/c); complex component absolute error <=1e-11. This avoids wrapped-angle ambiguity. Report phase modulo 2pi only for display |
| H_B8 (new) | Valid zero-drive, invalid requests, excluded physical models and numerical failures remain distinct | Exact typed statuses and finite/null serialization per section 7; injected sign, unit, source-loss and absolute-load mutations must fail a named invariant (not merely run successfully) |

The H_B6/H_B7 <=1e-11 dimensionless proposals are **not** inherited from Gate A's 1e-11 Pa pressure tolerance. Approval of these new thresholds is a pre-code decision. Complex magnitude-only checks cannot substitute for real/imag component checks.

### Physical uniqueness and numerical conditioning (prospective diagnostic)

Let theta = kL, Zc=rho*c/A, rs=Zs/Zc >=0, rt=Zt/Zc >0. Obtain a,b,c_m,d from the **existing Core** transfer matrix T; normalize b_n=b/Zc and c_n=Zc*c_m. Define

~~~text
D_n = (a + rs*c_n)*rt + b_n + rs*d
pL / ps = rt / D_n
p0 / ps = (a*rt + b_n) / D_n
U0 / ps = (c_n*rt + d) / (Zc*D_n)
UL / ps = 1 / (Zc*D_n)
~~~

The **analytic, independently computed diagnostic expression** for the prescribed lossless uniform tube is

~~~text
D_analytic = (rs+rt)*cos(theta) + i*(1+rs*rt)*sin(theta)
|D_analytic|^2 = (rs+rt)^2*cos(theta)^2 + (1+rs*rt)^2*sin(theta)^2
|D_analytic| >= min(rs+rt, 1+rs*rt) > 0
~~~

Thus a finite real-passive fixture has **no true zero denominator**: apparent singularities reflect numerical representation/unsupported scale rather than a physical INFEASIBLE motor state. Compare D_n against D_analytic as an *extra diagnostic*; do not replace the Core T-based solution with a duplicated self-authored physical law merely to pass tests. For a condition warning, proposed conservative dimensionless guard:

~~~text
denom_warning := |D_n| <= 64*eps_float64*max(1, rs+rt, 1+rs*rt)
~~~

Flag this as a proposed floating-point diagnostic, **not** a proof of error or a change to frozen oracle tolerances. Genuine overflow, nonfinite outputs or failure to establish stable precision => NUMERICALLY_UNRESOLVED; absence of a warning is NOT sufficient for PASS. Verify boundary residuals separately.

The independently frozen scattering oracle is based on GammaL=(rt-1)/(rt+1) and q=exp(-i theta), not on a duplicate call to Core. Do not let the diagnostic D_analytic supplant the independent 18-row oracle.

## 5. Oracle coverage, provenance and non-circular verification

Frozen JSON declares 10 column labels, in order:
(0) area_m2; (1) length_m; (2) frequency_hz; (3) terminal_pressure_real_pa; (4) terminal_pressure_imag_pa; (5) entrance_pressure_real_pa; (6) entrance_pressure_imag_pa; (7) source_mean_power_w; (8) terminal_mean_power_w; (9) source_resistor_dissipation_w.

The independent **frozen** reference supplies complex pL and p0, plus three power values. It **does not** independently store U0, UL, Pentrance, H_drive/H_canal or numerical condition metrics; these must be verified with explicit source/terminal/tube boundary residuals and algebraic invariants and must not be mislabeled as external oracle fields. Never silently fill missing fixture columns. Compare field identity, row ordering, component precision, and exact blob hashes. Report absolute complex-component errors in Pa, active-power errors in W; never compare numbers with incompatible units.

Two power ledgers for each f>0:
Pdrive = Re(ps conj(U0))/2;
Pentrance = Re(p0 conj(U0))/2;
Pterminal = Re(pL conj(UL))/2;
Psource_loss = Zs|U0|^2/2.
Record r_source=Pdrive-Pentrance-Psource_loss and r_tube=Pentrance-Pterminal separately. Original acceptance tolerances in Gate A are authoritative.

Require source, termination and matrix boundary complex residuals separately; negative mutation tests must deliberately violate at least one residual/oracle, including flipping exp(+iwt), U sign, pressure-versus-volume-velocity units, source sign, ps=p0 at Zs>0, re-scaling absolute Zt by A, and dropping source loss. A passed test that never injected the intended mutation is **not** evidence.

Provenance: exact Core SHA, Gate A head SHA, oracle JSON and WL blob hashes, design-addendum commit SHA, implementation SHA (future), input fixture identity/content digest, Python/NumPy/runtime versions, CI head/run URL and reviewer decision. Separate PASS/FAIL/INDETERMINATE from input status and from science/product adoption. Any output labelled computed or derived must preserve SI units and [real,imag] order, not amplitudes or normalized WAV dBFS.

## 6. Ownership and interfaces (design-only)

~~~mermaid
flowchart TD
  S["Synthetic source/load fixture (experiment-owned)"] --> B["Research boundary solver (future, experiments/044)"]
  C["Core UniformTube — sole physical law owner"] --> B
  B --> O["Typed research observation / two power ledgers"]
  W["Frozen independent WL traveling-wave oracle"] --> V["Independent comparison + deliberate mutation tests"]
  O --> V
  V --> R["Scientific verdict, provenance and review"]
  R -. "separate promotion only" .-> A["morphoacoustics_asmr: catalog now, future audited adapter"]
  A -. "explicit versioned opt-in and measurement gates" .-> T["Studio Scene / immutable Take (future)"]
~~~

The research solver has no physical speaker, gesture controller, audio-rendering normalizer, sound-file playback, listener tissue material, GUI or public package import. This prevents false coupling to active speaker/body work. Gate C must explicitly measure source calibration/leakage and reference-plane/ear-canal/HRIR boundaries before linking 3D near field or real listener, otherwise double counting can occur. Empirical source calibration is not obtained from a numerical source fixture: Nørgaard et al. (2018), https://pubmed.ncbi.nlm.nih.gov/29604709/; wideband immittance terminology: Rosowski et al. (2013), https://pubmed.ncbi.nlm.nih.gov/23900187/.

## 7. Typed outcomes and zero-drive policy

One request is a single strictly named SI fixture (batch processing is an ordered collection of these records, not a shape-dependent implicit NumPy broadcast). Finite numeric real scalars may be represented by JSON integers or floats, but **boolean is not numeric**. A complex ps is exactly two finite numbers [real,imag]. No implicit unit inference, accidental bool conversion, clipping, damping, gain normalization or fallback.

| Case | Input status / observation policy |
|---|---|
| Complete supported valid positive-harmonic passive fixture | VALID; compute raw complex ports, derived ratios where defined; scientific verdict evaluated separately |
| ps=0+0i, with otherwise valid supported fixture | VALID; all raw port states and powers zero; ratios formed from zero driven pressures **undefined with a named reason** (JSON null, not zero/NaN/Inf); structural Gamma_in from the known passive termination may remain defined and must be labeled as a model property |
| Zs=0 with positive Zt | VALID ideal-source *control*; p0=ps |
| Missing units/planes, malformed complex pair, bool where numeric, nonfinite value, nonpositive L/A/rho/c, negative Zs or Zt<=0 | INVALID with specific field and reason |
| Well-formed reactive/complex Zs or Zt, f=0 or f>8000 Hz, out-of-proposed-geometry range, nonuniform/3D/contact, incompatible request to prescribe p0 AND finite-source fixture | UNSUPPORTED with physical scope reason; do not claim infeasible |
| Finite valid input within supported geometry where precision/stable finite port values cannot be established | NUMERICALLY_UNRESOLVED; retain a diagnostic, never return plausible fabricated data |
| Valid output violates frozen oracle/energy/boundary thresholds | Input remains VALID; scientific verdict FAIL; NEVER reclassify as UNSUPPORTED |

Gate A proposed research domain (not anatomical truth): 0.01<=L<=0.05 m, 1e-5<=A<=1e-4 m2, 0<f<=8000 Hz, finite positive rho/c, real Zs>=0, real Zt>0. Its pressure small-signal ratio <=1e-3 is a **prospective engineering guard**, not an established biological threshold. Before implementation the reviewer must decide whether the guard is pre-solve or post-solve; if post-solve rejects a finite mathematically solvable fixture, label that UNSUPPORTED_LINEAR_SCOPE (within UNSUPPORTED), not NUMERICALLY_UNRESOLVED. A particle-velocity/Mach diagnostic is relevant to physical small-signal fidelity but **is not yet a new hard gate** and must not be silently added to frozen Gate A.

## 8. Implementation entry / STOP decision

**Current proposed disposition: DESIGN_REVIEW_REQUIRED; NOT DESIGN_READY; NO NEW SOLVER, TEST RUN, CI RESULT OR EXTERNAL AUDIT.**

Require an explicit human/independent science-architecture review of:
1. Source/entrance/terminal pressure and volume-flow sign and equivalent-source interpretation, including no measured-real-ear claim.
2. H_B6, H_B7, H_B8 quantitative rules and exactly scoped zero-drive/refusal semantics, separately accepted as **new prospective** tests.
3. Frozen oracle column map, SHA pinning and the distinction between independent values and internally derived invariants.
4. Dimensionless conditioning / passive uniqueness proof and status taxonomy, without changing Core law or Gate A thresholds.
5. Negative test design (mutant actually injected + test must fail), exact CI evidence and future review independence.
6. Confirmation: no edit to Core production, morphoacoustics_asmr live API, Studio UI, or Gate A; no implementation without a separate authorization.

Reviewer record must state DESIGN_READY / REVISE / REJECT with rationale, reviewer identity, date, immutable design commit, unresolved issues, and whether tests H_B6-H_B8 are mandatory or diagnostic. Even DESIGN_READY alone does not constitute an instruction to implement; Gate B requires a separate work decision. After eventual numerical tests, a GO_LIMITED_NUMERICAL would certify only this synthetic model's computation, never an empirical ear or ASMR/Studio capability.
