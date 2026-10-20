# OG-AUD1 / EXPERIMENT — Decision ledger and planned falsification

> **Gate A PROPOSAL / no preregistration freeze or new waveform as of 2026-10-20.** Core [#130](https://github.com/ryonakayama234/morphoacoustics/issues/130), Studio [#20](https://github.com/ryonakayama234/morphoacoustics-studio/issues/20). Read with [SYSTEM](./SYSTEM.md) and [DATA](./DATA.md). **No audible trial, CI, reviewer acceptance or adoption is claimed here.**

## Research question
Holding the same specified volume-flow **source time series**, 3-port typed topology, junction law, A/B geometry and matched terminal conditions, can changing **only** organ C's supported area produce independently verified, reproducibly different pressure at A.in that can be safely inspected as a bandlimited audio monitor? Do **not** treat monitoring pressure at an ideal source as physical mouth radiation.

## Hypotheses to freeze BEFORE implementation

- `H0`: claimed graph-conditioned change is a false artifact of source gain/phase differences, eight-point interpolation, wrong volume-flow/particle-velocity junction law, FFT circular boundary, illegal out-of-band extrapolation or mislabeled observation plane.
- `H1`: computed `Z_in(f)` for each lawful frozen graph matches independent global linear equations on the entire newly frozen candidate band/grid, preserves per-port continuity/conservation and passive power; a fixed physically dimensioned U(t) yields distinct deterministic raw p(A.in,t) and labeled normalized monitor clips.

| Component | Fixed | Intervention / planned observation |
|---|---|---|
| Core adopted graph base | OG-4 3 tubes, J, B/C matched, rho=1.2 kg/m³, c=343 m/s, A=.08m/.0003m², B=.09m/.0003m² | C area = **.00015 vs .0006 m²**, C length .06m fixed |
| Excitation | One identical phase/time/frequency/content-hashed physical U_A.in(t) | No re-pitch, gain or replayed WAV substitution |
| Acoustic authority | Full independently checked bandlimited 3-port calculation in SI | p_A.in(t) raw Pa; per-port p/U and power; monitor playback distinct and clearly labeled |
| Recorder | 48 kHz mono, explicit envelope, padding/FFT anti-wrap, PCM output | Source and pressure bytes, normalized WAV, content hashes, immutable manifest |
| Studio | Same Character / Direction / script context, exact versioned body choice | Fresh A/B Run→Take→listen→reload/restart and no-success-on-refusal |

## Exploratory mathematical cross-check (NOT a frozen oracle/Gate B result)

On 2026-10-20, a separate Wolfram Language calculation evaluated ideal matched B/C terminal impedance for 733 Hz with a frozen OG-4-like complex **peak source-flow phasor** `U0=(1+0.4 i)*10^-6 m³/s`. Using `Z_J=(1/Z_B+1/Z_C)^(-1)`, `Z_in=Z_A (Z_J+i Z_A tan(k L_A))/(Z_A+i Z_J tan(k L_A))`, `Z=ρc/S`, and computed outlet phasors:

| C area (m²) | Re(Z_in) (Pa·s/m³) | Im(Z_in) (Pa·s/m³) | `|U_B/U_C|` | input mean acoustic W |
|---:|---:|---:|---:|---:|
| 0.00015 | 1,603,112.27 | 559,611.88 | 2.0 | 9.298051e-7 |
| 0.00030 (anchor only) | 1,632,354.97 | 1,025,675.78 | 1.0 | 9.467659e-7 |
| 0.00060 | 1,461,638.16 | 1,632,724.23 | 0.5 | 8.477501e-7 |

At this analytic anchor `P_in - P_B - P_C` was zero to approximately 3.2e-22 W in machine arithmetic for all three configurations. This shows a **nontrivial, falsifiable impedance change**, not a validated physical 48 kHz waveform or listening quality. The calculation shares mathematical assumptions with the design and is **not** independent confirmation of future implementation. A separate global 12-state Wolfram matrix and other test oracles must be independently specified and run.

## Planned gate structure

**Gate A design review / candidate → frozen preregistration:** decide source U(t) units and physical amplitude, DC treatment, model-valid frequency cutoff and FFT grid, bandlimited output, numerical tolerances, reference-plane timing/sign, out-of-band suppression, test variants and acceptance thresholds *without seeing confirmatory results*. Record any amendments chronologically.

**Gate B Core scientific implementation (NOT YET RUN):**
- Reproduce OG-4's eight frozen phasor anchor results with the new, independent, continuous-grid computation; every new frequency is explicitly a **new scientific scope** (no use of unsupported OG-4 public response).
- Compute all 12 complex per-port p/U unknowns, signed junction flow, pressure continuity, passive mean power, condition/residual diagnostics; compare to independently assembled Wolfram global matrices over the frozen grid. Distinguish true negative law mutations from unsupported requests.
- Falsification mutants: particle versus volume velocity continuity, junction sign reversal, wrong C impedance, off-by-one ports, swapped reference plane, sample grid/window shift, source mismatch, corrupted SHA, unsupported graph/schema/frequency, numerical ill-conditioning. Require actual false-law discrimination, not just solver self-residual.
- Create same-source A/B raw Pa samples, normalized monitor WAVs and source bytes on new paths, reproducible across two exact-HEAD clean runs. Demonstrate physical difference (frequency/time) and controls; quantify numerical floor and time/window artifacts.
- Verify old OG-3/4, CC-A2, SV-1 and X2a unchanged.

**Gate C scoped Studio integration (NOT YET RUN):** two exact validated fixed body presets, fresh trusted Core runs, immutable verified take, one-shot A/B playback, body diagram/provenance, reload/restart, malicious input and no-fallback cases. Do not claim user-customizable graph topology.

**Gate D decision (NOT YET RUN):** numerical/science review, exact-HEAD software/security review and creator listening/pilot independently recorded. Decide `SUPPORTED_LIMITED`, `INCONCLUSIVE` or `REJECT` for physical ability; separately record `CREATOR_AUDITION_PILOT`. No general speech, naturalness, HRTF or human-anatomy claim.

## Evidence ledger

| Date | Event | Observable evidence | Decision |
|---|---|---|---|
| 2026-10-20 | Reconciled main Core OG-4 and Studio CC-A2 | [Core #108](https://github.com/ryonakayama234/morphoacoustics/pull/108), [Studio #19](https://github.com/ryonakayama234/morphoacoustics-studio/pull/19) | Adopted limited **antecedents**, not OG-AUD1 |
| 2026-10-20 | Initial 733 Hz theoretical matched-branch Wolfram check | Numeric table above; no file-backed oracle or independent gate yet | `EXPLORATORY_ONLY` |
| 2026-10-20 | Proposed Core/Studio linked E2E task and three sync docs | [Core #130](https://github.com/ryonakayama234/morphoacoustics/issues/130), [Studio #20](https://github.com/ryonakayama234/morphoacoustics-studio/issues/20) | `GATE_A_CANDIDATE` |

## Artifact plan (no generated artifacts yet)

Expected immutable future layout: `experiments/<new_id>_og_aud1/` with `PREREGISTRATION.md`, `run.py`, `RESULTS.md`, `oracle.wl`, `manifest.json`, `raw_U_m3_s.npy`, `raw_p_Ain_Pa.npy`, `monitor_48k_pcm16.wav`, full-port diagnostics and separate blind key. Publish exact blob hashes, commit SHA, code/env versions, two-run hashes, G2 human results and change/amendment timestamps in this ledger. **No file in this proposed list is asserted to exist.**

## 2026-10-20 supplementary exploratory preflight — NOT preregistered

The [Gate A audit](./GATE_A_REVIEW.md) records Wolfram scalar cross-checks at **80/733/997/4000 Hz** for two already OG-4-supported C areas, with fixed complex peak source-flow phasor. The source-port **|p|** phasor peaks at 997 Hz are approximately **2.192765 Pa** (C=.00015m²) and **4.211969 Pa** (C=.0006m²). These are isolated frequency-domain results, **not broadband or time-domain evidence**, and arise from the same reduced analytic model as the design. The independent global 12-state matrix, scientific thresholds and source/FFT convention remain to be settled *before* Gate B.

New falsification requirement candidate: with both distal loads matched, perturb `L_B` or `L_C` alone and require identical `Z_in(f)` (within preregistered roundoff) at the source plane; any predicted branch-length-induced resonance under those specific ideal boundary conditions falsifies the implementation. Add paired playback shared-gain vs separately normalized comparison as an explicit confound control. This addition **does not modify or freeze** the historical experimental results above.

| Date | Addition | Evidence class | Status |
| --- | --- | --- | --- |
| 2026-10-20 | Matched-load branch-length null, analytic Z positivity and 80/733/997/4000 Hz cross-check; proposed shared A/B gain | Wolfram **scalar exploratory**, no waveform nor independent 12-state solve | `GATE_A_CANDIDATE` |
