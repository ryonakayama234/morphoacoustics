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

## 2026-10-26 — first numerical execution and independent review (append-only)
**Evidence run:** [Actions #40306881602](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40306881602), source `09e8720669db560fc926c0ce0eac1f168dcc2a8a`: dedicated science job and general tests **SUCCESS**, scientific `vf1a-research-evidence` artifact archived. Both independent pytest and runner completed. This is a **historical pre-review-fix run**, not final G0/G1 certification under the corrected gate.

- Tract geometry only at 800Pa: RMS upstream x1 displacement difference **2.3581193009596308e-6 m** and RMS upstream valve-flow difference **7.935043542740085e-7 m³/s**. Those are waveform differences under this specified proxy, not speaker perceptual distinguishability or a guarantee of physiological larynx coupling.
- Local combined power residual, maximum per reported condition: uniform 800Pa **4.245911129300101e-15 J**, constricted 800Pa **4.1709334602576e-15 J**, +10% stiffness **4.190226587777562e-15 J**; no-drive **1.3234889800848443e-23 J**. These small numerical residuals validate coded bookkeeping **only within the declared model**.
- **Transient energy/oscillation diagnostic:** ratio of 40–60ms x1 displacement RMS (demeaned in each window) to 20–40ms: uniform 800Pa **0.3774851595402234**, constricted 800Pa **0.37888161124638886**, +10% stiffness **0.40449889878557965**, no-drive **0.5178760501910504**. This is **decaying oscillatory deviation in the frozen pilot**; it is NOT evidence of sustained self-oscillation. A 60ms window is insufficient for general long-term impossibility, but there is no license to call transient ringing a biologically active voice.
- Codex exact-head review `09e8720` raised **P2 scientific certification hazard**: the report was capable of claiming G0/G1 PASS solely from physics traces even if the independent pytest step failed while the `if:always()` runner succeeded. Original review retained on [PR #209](https://github.com/ryonakayama234/morphoacoustics/pull/209).
- Corrective implementation (after registration, no thresholds moved): CI now persists a `test_status.json` test-exit receipt; the runner requires explicit successful independent-test status before `g0_g1_research_numerics` and `verdict` can pass. Missing/failed/malformed status produces trace-only / NUMERICALLY_UNRESOLVED; independent negative control `test_scientific_gate_blocks_false_pass_from_failed_or_missing_pytest` was added. Current candidate head `232728eb`. **Exact-head scientific CI and new independent review remain required** after this change.

**Scope remains:** simplified two-mass compliant-volume device, not validated glottal aerodynamics; **G2 physiology INDETERMINATE, G3 sustained self-oscillation NOT ESTABLISHED, G4 voice NO-GO**. Do not merge SFI-3/#84 or VF-1A/#209 to main or change any Studio/public ABI.

### Next-mechanism decision (not a modification of the preregistered experiment)
Before increasing model complexity or tuning tissue parameters to produce desirable F0, isolate **net aerodynamic/acoustic work delivered into tissue vs tissue damping per cycle/window** at fixed breathing pressure. If no physical positive work pathway offsets damping, the next *independently preregistered* experiment must study a mechanically conjugate **distributed intraglottal pressure/flow-separation law** with a complete fluid/tissue/tract work identity. Mere changes to pitch/volume gain, arbitrary negative damping, time-varying prescribed area or post-EQ are not admissible substitute mechanisms. No automatic promotion into Core's organ graph or Studio.
