# VF-1A EXPERIMENT — prereg protocol / execution log
**At first commit: NOT RUN.** This file starts as prospective observations and thresholds, and will be *appended* after actual CI execution; historical failures remain visible.

## Experimental run order (no retuning after outcomes)
1. Freeze exact SFI-3 base source commit, apparatus, solver convention, dt, initial perturbation, pressure source and two body geometries. Record file/blob SHA hashes.
2. Independently derive algebraic discrete midpoint tissue–valve–tract power identity; test 2-mass symmetric and antisymmetric natural-mode formulas before applying fluid drive. Independent mathematical identity does not prove human vocal-fold mechanics.
3. Implement experiment-local strong-coupling residual solve with an explicit `NUMERICALLY_UNRESOLVED` path, refusing area contact. Never condition audio samples or prescribe an oscillation.
4. Run all four conditions 0/800Pa × uniform/constricted (plus a stiffness +10% intervention if stable), measure full independent port/work terms, tissue x,v, q, inlet/exit p,U; compare 24k/48k or other prereg-refinement input as same physical-time experiment.
5. Negative controls: no respiratory work should not create sustained oscillation; nonphysical mass/damping/area rejected; deliberate port power/geometry-flow mismatch rejected. Preserve failure JSON and diagnostic traces in GitHub Actions on both success and failure.
6. Measure whether the response persists in last window (no preset periodic phase). Calculate cycle counts only when robust stable crossings / spectral and time-window evidence justify it. Otherwise explicit NO_SUSTAINED... . No assertion of species-specific pitches, audible vowels or receiver.
7. Independent @codex scientific audit on exact code and evidence; correct defects without concealing initial failure; defer merge and API promotion until future agreement.

## Prospective decisions
- `G0_G1_NUMERICAL_PASS`: independent mathematical control, time-step/energy tests, source-only/tissue-only negative tests, full output hashes, strict evidence emission all succeed.
- `G1_FAIL_OR_UNRESOLVED`: any of those fail; no scientific pass.
- `SELF_OSCILLATION_FOUND` requires reproducible nondecaying periodic tissue motion driven by steady pressure, not 1–2 damped transient cycles. **Not an assumed gate outcome**.
- `G2_INDETERMINATE_PHYSIOLOGY`, `G3_RECEIVER_NOT_TESTED`, `G4_VOICE_NO_GO` always.
- No public graph module or Character Creator UI before later owner's explicit review.

## Post-registration evidence 2026-10-26 — symbolic oracle only (numeric CI pending)

- Preregistration was committed `a40222f` before source `a88c63f`. This entry was added later; it does not revise thresholds or fixture.
- **Independent Wolfram evaluation completed:** using `Uin=q-g1*v1-g2*v2`, symbolic difference between the three discrete midpoint subsystem work identities and the declared total work identity is exactly **0**. Symmetric and antisymmetric free natural modes under `m1=m2=1.2e-4kg,k1=k2=30N/m,kc=8N/m`: **79.57747154594769Hz**, **98.53906213133976Hz**; midpoint 48k antisymmetric phase **0.01289855423655888rad/step**. Source and numeric output in `experiments/036_vf1a_two_mass/wolfram/`; Python tests verify both mode numbers as an independent oracle.
- These values establish **mathematical consistency of the stated reduced system only**; they do not demonstrate transient numerical execution, physically validated phonatory tissue, source self-oscillation, or actual voiced sound.
- Research implementation `experiments/036_vf1a_two_mass/two_mass.py`, tests, run traces and scientific artifact workflow exist on stacked Draft #209. GitHub Actions is presently QUEUED. **No G0/G1 implemented-system PASS** has yet been certified; independent source reviewer request is active. Preserve this status until exact-head evidence is returned.
