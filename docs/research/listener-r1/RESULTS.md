# EL-R1 RESULTS — execution ledger

**Gate A sealed:** 2026-10-22 JST, in separate documentation-only commit [db2f871](https://github.com/ryonakayama234/morphoacoustics/commit/db2f8719653b5effcfd6a4528e43a7baad0abe39). Protocol defined before code. No preregistered acceptance thresholds changed.

## Gate B experimental findings, 2026-10-22
- **Independent Wolfram evaluation executed**: det(T)=1 symbolically, traveling-wave H minus Core-style ABCD-derived H = 0 symbolically. Also computed the 3 lengths × 3 loads × 4 frequencies = 36 synthetic records with phase, reflection and power. The frozen [nine 3000-Hz oracle records](../../../experiments/043_el_r1_ear_port/wolfram_oracle.json) are replay-tested using a distinct Core matrix derivation.
- Synthetic drive total pressure p0=1+0i Pa, rho=1.21 kg/m³, c=343m/s, A=3e-5 m², f=3000Hz, R=2: H=1.1223637436-1.1001356446i (L=.020m), H=0.7019911285-1.7593098368i (L=.025m), H=-0.3055523239-1.9584038046i (L=.030m). Complex phase and geometry intervene materially. Higher terminal pressure amplitude than entrance is not power gain; both endpoint power balances are separately checked.
- Local execution: PYTHONPATH of a local **reconstruction of the Core uniform tube primitive from current main** with NumPy 2.3.5 and pytest 9.0.2: **42 tests passed** (including 9 Wolfram fixed-vector tests, 9 parameterized 4-frequency passivity tests, 4 matched checks, 16 refusals, morphology differences, complex pressure scaling, zero excitation and JSON determinism). Exact tested experiment/test/oracle file blob SHA match GitHub branch. This is a local preflight, **not** independent CI of the full repository.
- Executable CLI outputs SI, complex phasors, both planes, provenance and fixture digest; waveform synthesis, subjective assessment and physiological realism not tested.
- GitHub Actions: **PENDING external runner execution at time of Gate B evidence record**; do not claim CI success until run is observed. Gate B remains provisional until CI + independent review.

## Gate B acceptance ledger
| Criterion | Observation | State |
| --- | --- | --- |
| Pre-registered controls and thresholds | Frozen in Gate A commit | PRE-REGISTERED |
| Symbolic Wolfram independent physics derivation | determinant=1; H scattering=H matrix | PASS |
| Frozen complex H/Γ/power vectors | 9 fixtures, local pytest all match | LOCAL PASS |
| Power, passivity, matched and morphology controls | 42 local tests collectively pass | LOCAL PASS |
| Negative inputs and explicit refusal | 16 local cases | LOCAL PASS |
| GitHub CI same branch, 3.11/3.12 | Pending | NOT YET VERIFIED |
| Human ear anatomical/mechanical measurement | Not undertaken | NOT VALIDATED |
| Time-domain stable impulse/WAV human listening | Gate C | NOT RUN |
| Independent scientific audit / limited adoption | Gate D | NOT ADOPTED |

## Provenance and scope boundaries
- Core source code in main unchanged; Studio unchanged; research branch from main SHA 6869cfec04041393eae44485ce2fc91f002114f5.
- No HRTF concatenation without ear reference-plane metadata; neither blocked-canal SOFA nor microphone field is passed through this system.
- The apparent finite-pressure resonance is an ideal analytic boundary response. No measured human eardrum load, tissue loss, pinna deformation or perceived ASMR effect can be inferred.
