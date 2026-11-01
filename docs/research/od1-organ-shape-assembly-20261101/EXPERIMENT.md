# OD-1 EXPERIMENT v1 — predictive/causal science and creator gates
**This is a pre-implementation design. No OD-1 code, test run, A3 freeze or voice-quality claim has been produced by this PR.**

## Hypotheses
H0 Null: r=1, source/task/solver held, exact baseline geometry and pressure are reproduced without a novel body.
H1 Shape: for all 16 cells ln(Anew/Abase)=ln(r)w_i; analytic V and dV/dθ and reciprocal characteristic-impedance law independently match. Wrong orientation/neighbor weight/sum-preserving mutation fails.
H2 Motor: three-task motor source, LF F0, time/seed and solver remain unchanged; the rest edit propagates into timed tract shape, not an audio correction.
H3 Model acoustics: for matched physical source/terminal/observation, two independent complex acoustic transfer formulations predict observable changes; Core's raw pressure differs for nonnull shapes above a declared numerical floor, or scientifically reports a resolved null.
H4 Shape position: c=4 vs c=8 at same r may give different loaded transfer responses; no positive effect is assumed and posthoc-known site properties are disclosed.
H5 Persistence: every accepted BodyRevision is exactly resolved, source/body/task trace agrees, fresh raw→WAV bytes with one shared gain and old Take identity survive restart/reload; fabricated receipt refused.
H6 Listening: audible distinction, timbre quality, buzziness, consistent character identity and creator usability are **separate** from H0–H5. A machine pass alone never promotes voice-discovery.

## Prospective conditions
Existing CC-A2 M0/r1 16×0.010m /a/ rest geometry, fixed source LF 100Hz, three-task /a/→/i/-like trajectory, 48 kHz ×24000 raw SI Pa at actual declared Core output, current fixed backend and load. New six (c,r) cases: c=4/8 ×r=.90/1.00/1.10; 1.00 cases are semantic null controls. Also run legacy site08 single-cell as separate regression (do not overwrite its meaning), CC-A2/SV-1/OG3/OG4 and Performance contract regressions.

## Ordered work before implementation
A0 Audit exact inherited code/SHAs: main, PR ancestry and cross-repo pin; actual Exp009/027/029 source/observable, time clock, 102-acoustic-call expectation where applicable, calibrated geometry, output unit and real load; archive baseline hashes.
A1 Independently re-derive shape/log area/volume/dV/dθ/impedance formulas, create a shape observer not importing candidate method; identify conditioning and geometry orientation.
A2 Independently derive acoustic forward transfer with exact inherited source/load/output plane. Run TWO model-matched oracle implementations: global ABCD product and backwards recurrence/scattering. Existing ideal pressure-release Z_in is merely a secondary cross-check, never the primary output oracle. If matched oracle impossible, HOLD G2 instead of inventing accuracy.
A3 Freeze exact HEAD/input hashes, implementation-independent oracle predictions, error-floor protocol, numerical tolerance, negative mutants, chosen sample indices, blinded randomization/positive control if doing listening **before new candidate code or trial**. Current numeric thresholds below are review proposals, not a completed A3 decision.
B Run experiment-local Core six cases and independent observer; preserve errors and STOP states, original raw float64 Pa and common-gain derived PCM previews.
C After B limited success, assess a bounded Core versioned shape-family/revision adapter. No existing public API or v0/v1 contract mutation.
D After new explicit creator approval for Studio V2 UI, connect approved capability inside existing character.canvas/selection.inspector and take.transport; genuine fresh physical renders, validation, reload/tamper negatives.
E Controlled creator audition and separated G4 quality judgement. Human ear is not a substitute for G1 physical truth.

## Measurands and engineering rules
Geometry per cell A_rest [m²], length [m], V [m³], dV/dθ [m³], timecourse A(t) [m²]; source actual flow/pressure at declared plane; complex loaded transfer H(f) and magnitude/phase; rest and terminal resonance conditions; native pressure Pa, RMS [Pa], raw relative L2 from baseline; independent artifact SHA/source/gesture identity; runtime and failures. Do not report calibrated SPL from peak-normalized WAV or ear pressure from mouth-port proxy.
Design sample grid: 100–3500Hz at 25Hz for complex response, explicit 100Hz harmonics, refine root peak checks to ≤0.25Hz resolution. Do not compare ideal input Z_in peaks to resistively loaded output as if identical.
Candidate geometry numeric gate: absolute residual |ln(Anew/Abase)-θw| ≤1e-12; relative volume oracle residual ≤1e-12 for positive reference. These are engineering **proposals pending A3 independent floating-point audit**.
A3 must fix frequency magnitude/phase acceptable error, response floors and null pressure floor using independent same-model baseline calculations **before** examining new edited responses. Report frequency-by-frequency residual and any singular-response exclusions predeclared; if no reliable floor, G2 INDETERMINATE. Raw L2>1e-8 from old exploratory pilot is NOT automatically a trustworthy perceptual or new-family threshold. Never inspect a favorable result and then move cutoffs.

## Mutants (required failing cases)
Wrong center, source/receiver reversed, swapped area vs radius, wrong five weights, zero/negative/nonfinite area, boolean/range/unknown family, changed source or gesture, per-file listening gain, changed time clock, frame/peak distortion, missing old-body digest, forged new body ID, preserved aggregate volume but altered two cells, stale registry replay, truncated file, changed backend, overpromoted ideal pressure-release to actual output, unsupported graph port, inadvertent fallback. Per-cell independent observer must detect aggregate-preserving corruptions.

## Listening (separate creator gate)
Prior informal site0 unidentifiable and site4 slightly different reports are exploratory. Suggested prospective single-creator controlled screen: preregister primary new five-cell c=4,r=1.10 against baseline; secondary c=8,r=1.10. For the primary, randomize 24 blind ABX trials; 19/24 correct is an explicit exploratory above-chance within-listener screening decision, not a population claim. Include separate A/A same–same negatives and a verifiably audible positive-control pair; failed controls => INDETERMINATE. Fix one pooled WAV gain; lock answer key until responses; record unsure and listening device. Record vocal likeness, audible artifacts and creator usefulness separately. Do not claim arbitrary Japanese, stable speaker identity or naturalness from ABX.

## Stop / decision
G0 proven source + ancestry/revisions; G1 independent shape+mutants; G2 model-matched transfer/physical pressure; G3 new approved Core/Studio loop; G4 audible/voice quality. Report GO_LIMITED / REVISE / MORE_DATA / REJECT per capability with actual evidence and remaining risks. STOP on painted audio, wrong port/load, impossible motor silently rendered, unqualified source–tract physics, changed legacy Take identity or unauthorized Studio panel changes. A negative physical/acoustic result is retained without EQ/F0 tweaks.


## Gate B initial actual CI evidence and coverage boundary
See RESULTS.md for measured exact-head six-case machine output and archived native Pa/WAV. A0–A3 physical/equation/oracle thresholds were committed **before** new experiment files, at Core commit b3f0efd2dc88f5695eee14c51c2579a6fc1ca85a (A0_A3_FREEZE_20261101.md). Reference geometry, model-matched complex H, two oracle computations, 4 temporal log-area invariance probes, source/plan identity, old M0 quantized waveform and each condition's 102 acoustic calls are checked by actual run.py. The old Core CC-A2 regression runs in the same scientific workflow.

Negative test categories implemented: illegal numeric edit (including bool, NaN/Inf, center, ratio), one-cell/aggregate volume preserving geometry corruption as independent-oracle discriminator, false output acoustic observer, wrong/source/preregistration blob pin and WAV gain/clipping corruption. G3 independent body registry/tampered historical Take/restart, source/actuator fault injection, Studio browser E2E, controlled human ABX, voice-naturalness and moving-wall C1/C2 remain NOT_TESTED by this new five-cell experiment. Do not report any of these as a pass merely because runner/CI succeeded.
