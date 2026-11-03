# VF-1B2 EXPERIMENT V3 — falsifiable program and preregistration gate
Date 2026-11-02 JST. This is an implementation-ready DESIGN PLAN SUBJECT TO A1/A2/A3 SCIENCE FREEZE and owner agreement. No moving-wall code, trial outputs or voice-quality claims are made by this document. Prior #262 fixed-wall research remains its own intact evidence.

## Scientific problem and hypothesis family
The upstream OD-3 demonstrates body × timed task → distinct 1D pressure under an externally specified LF source. It cannot establish organ material → autonomous source; VF-1A/B1 shows current symmetric two-mass forcing does not support antisymmetric work. A spatial pressure-gradient-driven work-conjugate fluid law may resolve that mathematical deficiency, but **not necessarily self-excitation, biological validity or audible usefulness**.

- H0, negative ancestral control: a spatially uniform pressure and perfectly symmetric force basis produce F_L-F_U=0; reproducing this is mandatory.
- H1, static spatial force: p_g(z)=p0+a z/L produces analytic F_L-F_U=-(ell L a/3); numerical quadrature converges independently, reversed gradient reverses sign.
- H2, geometry/conservation: moving area changes V as ell L(vL+vU), integral rho A mass changes only by face mdot. An omitted swept-volume term must fail.
- H3, joint power: signed force×velocity and full fluid enthalpy boundaries plus external ambient work balance independent total storage/losses; omit/reverse/double-count wall term must fail. A numerical closure with a physically unjustified loss law is NOT G2.
- H4, passive control: with zero pressure difference between equilibrated reservoirs and no active drive, stored fluid+tissue energy does not spontaneously increase beyond independently frozen numeric floor. Reflection/finite initial transient is allowed.
- H5, morphology/intervention: changing ONLY a tissue property or h0 shape alters actual force, trajectory, threshold or is a measured null; distinct backend/observer/source changes are disallowed as substitutes.
- H6, C2 causal tract: changing ONLY a declared passive tract load alters the **physical tissue/flow state** beyond measured numerical floor, and same-time mean/acoustic power closes. A change only in rendered spectrum is NOT feedback.
- H7, autonomous regime: an externally nonperiodic steady pressure supply may create stable sustained oscillations and cessation after withdrawal, with stable modal amplitude and positive net air-to-mode energy compensating dissipation; if not, scientifically legitimate G3_NO_SELF_OSCILLATION_FOUND.
- H8, creator audio quality: subject to G2/G3 and valid observation, candidate may improve perceived phonation relative to matched LF baseline; NOT assumed, not used to tune physics, creator GO/NO-GO separate after instrument and human audition.

## Ordered work packages and evidential branching
| Package | Concrete deliverable | Entry | STOP / permitted claim |
| --- | --- | --- | --- |
| A0 repository/lineage | SHAs and code/API inventory of Core main OD-3, SFI-2/3, VF-1A/B1, VF-1B2 #259/#262, measured source and Studio V2 | this design | no code or main import; ancestry mismatches stop |
| A1 analytic law | independently derived continuum, moving-grid conservation, p_abs vs p_ext, force oracle and complete boundary/enthalpy power identity; 2 implementation-independent derivations | A0 | STOP_MODEL_LAW if terms or signs incompatible |
| A2 evidence/domain | barotropic EOS or thermodynamic alternative, reservoir characteristic conditions, low-Re #262 scope, existing higher-drive rigid external pressure-flow data with uncertainties and lawful access; range classification | A1 | G2_PHYSIOLOGY_HOLD if high-drive source cannot be qualified; mathematical C1 still possible |
| A3 prospective frozen method | signed equations, fixture and input digest, parameter ranges, numerics/CFL tolerances, independent reference, error floors, test IDs, negative mutations, release states, reviewer signoff; separate commit BEFORE new source | A2 | B2a READY_FOR_IMPLEMENTATION only with a coherent mathematical domain |
| C1 moving-wall model | isolated research module; N,dt convergence; independently computed SI mass/work report, passive/drive/refusal negative controls, raw state and failed-test artifacts | A3 | G1 math/numeric ONLY, no voice claim |
| C2 acoustic bridge | derived baseline/perturbation energy identity; shared-clock source/tract coupling; 1-way, delayed, duplicated-port negative controls | C1 + SFI ancestry audit | STOP if bridge cannot balance, no SFI public import |
| D physical autonomy | fixed-drive intervention study, two identified bodies, at least two declared passive loads, turn-off, phase/cycle work, mode energy, numerical refinement | C2 G1 | G3 limited or honest NO_SELF_OSCILLATION_FOUND |
| E sound / creator | qualified source radiation+receiver, like-for-like physical sound, source/tract/auditory measurement and masked A/B with A/A negative control | G2+G3 and separate UI/product approval | G4 release explicitly subject to creator acceptance |

## A1 analytical oracles and directed mutant matrix
- Uniform p(z): force difference zero, force sum consistent with pressure × changed volume.
- Linear p(z): exact F_L=ell L(p0+a/3), F_U=ell L(p0+2a/3); swap force sign/coordinate basis must fail.
- Moving sealed channel: face mdot=0, mass constant while rho changes inversely with integrated moving V. A=positive always.
- Static channel: wall work zero; if no loss and equilibrated reservoirs, no spurious drift.
- Zero-drive tissue perturbation: physical damping nonnegative, no self-powered oscillation.
- Finite mean flow: include total enthalpy inflow/outflow; removing kinetic or reference external work must be detected. A pU-only counterfeit fails.
- A/A identical model and replay: no physical difference beyond numeric repeatability; inspect raw storage hashes independently.
- Tiny perturbation near contact A_floor: capability refusal instead of hidden clipping. Reverse flow unsupported until independently bounded model selected.
- Constant-pressure source is NOT a prescribed periodic area. Periodic force injection, negative intrinsic tissue damping or post hoc spectral EQ must be rejected from source definition.

## Numerical decision policy (A3 will freeze final figures BEFORE evaluation)
Choose dt using actual smallest cell Lg/N, c, U and sought oscillation frequency; report C=(|u|+c)dt/(Lg/N). Original V2 24/48/96 kHz is a candidate *output-observation* clock, NOT sufficient evidence for stable/accurate compressible fluid timestepping. Use at least three systematically reduced physical dt values and at least two refined spatial resolutions for each accepted mechanism claim; assess empirical asymptotic error/convergence, not just success of a high-order solver. Nonlinear tolerances must be substantially below observed discretization error; reject runs when no convergent range is established.

Before running C1: set separate absolute kg/J force thresholds from analytic/manufactured oracle error and numerical precision; freeze scale-normalized mass/energy tolerances and near-zero floors from independently estimated budgets, not arbitrary percentage of huge absolute gas internal energy. Candidate upper engineering ratio for C1 energy = 1e-3 on physically exchanged energy only, additionally demanding absolute residual and convergence; this number is NOT an adopted gate until A3 derives its denominator and precision. No retuning after seeing C1/D results.

For D: freeze time windows in physical seconds and minimum cycles *from plausible physical period range before looking at output*. Estimate oscillatory amplitude after subtracting static mean, spectral peak stability, envelope slope and variability across independent window slices; corroborate period with autocorrelation or zero-crossings, and compute per-cycle signed pressure-work and dissipation. Sustained input pressure alone or positive cumulative work cannot certify a limit cycle. Vary initial perturbation at same drive and terminate drive to test autonomous onset/cessation. For load intervention: compare full tissue and glottal flow traces; isolate source/tract loads, not playback/reconstruction.

## External reference hierarchy / honesty
1. Mathematical identity and manufactured solution — supports law/solver correctness, NEVER human anatomy.
2. PR #262 low-Re rigid flow analytic control — supports only its small-pressure fixed-wall domain, NEVER moving phonator.
3. Geometry/pressure-gauge matched real rigid glottal pressure–flow measurements e.g. M5 paper DOI 10.1121/1.3514424 or independent 3D source/bench data. Current original figure-pressure access and two independent source readings are NOT qualified. Use literature suitability review before claiming G2; if unavailable report G2_HOLD and do not synthesize synthetic "measured" profile.
4. Higher-fidelity 3D FSI comparisons/published studies as external model-discrepancy evidence; published favorable conclusion is not validation of our own parameter set.
5. Acoustically and receiver-qualified physical audio plus creator perceptual test: separate G4, not a source of simulated physical truth.

## Risks and explicit fallback
- EOS/heat loss inconsistent: restrict to lossless mathematical C1 reference or stop until a physically closed law is derived.
- Intraglottal separation high-drive unmeasured: no 400/800/1200 Pa physiology claim; qualify a measurable subdomain or collect/obtain licensed independent external reference.
- Port bridge mean flow impossible in inherited SFI tract: keep C1 result, do not improvise fake acoustic correction; propose dedicated finite-mean-flow/perturbation interface as separate scoped decision.
- Flow C1 numerics too expensive at required dt: restrict temporal/spatial domain and benchmark reduced-order alternatives, not forced audio clock.
- No self-oscillation: report negative mechanism result; compare force law, positive damping, load and missing contact evidence, but do NOT add arbitrary negative damping to obtain pitch.
- Self-oscillation but poor sound: keep mechanism scientific baseline, do not mislabel as creator-quality release; independently measure transfer, source, radiation, listener before proposing constrained neural closure.
- Studio no contract approval: keep research data off current creator UI and no Take; preserve all historic assets.

## Records and decision hygiene
Keep DECISION/SYSTEM/DATA/EXPERIMENT jointly synchronized; append RESULTS and AUDIT/AMENDMENTS without editing predeclared controls. Use GitHub Actions exact source SHA, Python 3.11–3.13 when relevant, code review and separate independent reference review. Passing CI measures software and numerical properties, not scientific relevance or voice quality.
Outcome categories for each package: PASS_LIMITED, NEGATIVE_RESULT, INDETERMINATE, REFERENCE_HOLD, NUMERICALLY_UNRESOLVED, REVISE, REJECT, plus G4_CREATOR_NOT_EVALUATED. No automatic main merge.
