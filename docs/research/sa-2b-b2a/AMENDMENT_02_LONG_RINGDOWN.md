# Gate A2 — prospective post-failure M0/i long-ringdown evidence extension

2026-10-25 JST. **This is POST-FAILURE, before corrected data collection, NOT retroactive acceptance of original Gate A/G6.** Original GATE_A.md and pre-test AMENDMENT_01 remain immutable.

## Actual failed source/evidence
The first B2-A 5-second impulse implementation at source SHA 1b5e5ab56a4976c891f8eada9957eb4745c5d65c, GitHub Actions PR scientific run [40111362530](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40111362530) **FAILED independent auditor G6**, despite all preceding unit tests passing. Earlier initial CI [40111124842](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40111124842) **FAILED** an ACTUAL wrong left/right junction coefficient; that engineering fault was corrected without weakening the energy oracle. These outcomes are part of the source/evidence history, never rewritten as PASS.

M0/i @200Hz measured continuum complex relative error at 5-second time-truncated impulse:
n=2: 0.0052080913277553194
n=4: 0.005218551041899371
n=8: 0.005223843463598107
The error is roughly fixed with n and therefore violates the original <=0.36 successive error-ratio gate even though each is individually below 1%.

## Independent physical diagnosis
Download raw artifact [12566945805](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40111362530/artifacts/12566945805). Reinspect **ACTUAL** 5-second M0/i impulse raw arrays without modifying solver state or using the manifest results as proof. Their nonzero last-second waveform amplitude is not numerical noise: at n=2 the 4.5–5.0s RMS lip pressure is approximately 5.1036e-6 Pa versus 0–0.5s 0.01188 Pa. M0/a and M1/a at the same 4.5–5s interval are ~1e-83 and ~1e-65 Pa for n=2. The /i/ body has a **high-Q long-lived acoustic mode**; cutting its otherwise physical passive time response at exactly 5s makes the frequency-domain DTFT measure a different, time-windowed system. This is a *data duration / spectral oracle* failure, not an entitlement to weaken a convergence threshold.

## A2 prospective new experiment (stronger evidence, unchanged physics)
Reexecute the EXACT model and shape from the existing code. All B0, junction equations and original test tolerances remain UNCHANGED. Capture actual M0/i impulse for **at least 18 complete seconds** at ALL n=2,4,8 physics clocks, archiving the FULL raw waveform without analytic window correction, fade, artificial damping, extrapolation, or changing any physical R/M. The other two bodies' documented complete five-second arrays are still accepted as originally frozen.

Independent auditor MUST, BEFORE complex-transfer PASS, verify for M0/i that:
1. Full stored impulse length = ceil(18.0 * fs_internal) (physical duration), and exact zero first N wavefront ticks.
2. Last 0.5 s RMS pressure is <= 1e-7 times first 0.5 s RMS pressure, **at every n**. If not, HOLD or prospectively add a longer horizon with honest new evidence, never artificially terminate reverberation.
3. Recompute full-horizon complex H(f) by direct time sum from the unwindowed COMPLETE raw impulse at 200,400,600,1000,2600Hz; independently compare with original continuum 16-section transfer and unchanged analog B0 using same G6 max error 0.01 at n=2 and <=0.36 successive refinement factors at every frequency (no threshold modification).
4. Store both the failed original 5-second source/run and the new prospective 18-second result in RESULT, including actual ZIP IDs and SHAs.
5. Still require all Gate A G1–G5 and G7–G9, and archive rehash. Do NOT call the original G6 five-second transfer gate a PASS.

IF new test passes: status "B2A_STATIONARY_CHARACTER_TRACT_PASSIVE_PROPAGATION_VERIFIED_UNDER_A2_LONG_RINGDOWN_GATE" (research-only). The owner may still assess review findings; core adoption remains NOT_ADOPTED.
