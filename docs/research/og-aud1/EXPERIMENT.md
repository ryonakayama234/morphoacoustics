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

## 2026-10-20 executed global-system preflight (Experiment 043; exploratory)

[Full source, method and result](../../../experiments/043_og_aud1_preflight/README.md) · [executed numeric evidence](../../../experiments/043_og_aud1_preflight/RESULTS.md). Wolfram evaluated an explicit pressure-scaled **12×12 global port-state system** and independently compared it with scalar source-port impedance at 80/733/997/4000 Hz and both C areas. Observed **maximum relative Zin discrepancy 4.34e-16**, **scaled matrix condition at most 24.92**, **maximum signed mean-power residual 3.18e-22 W**, **maximum signed junction flow residual 9.05e-23 m³/s**. Deliberate wrong particle-velocity law deviated by relative **0.24–0.48**; changing B/C lengths with both outlets matched changed the source-port impedance only at numerical roundoff. This is a genuine evaluated exploratory artifact, **NOT a preregistered acceptance**, **NOT a 0–4k grid solver**, **NOT a 48 kHz WAV**, and **NOT an independently audited Gate B**.

| Date | Event | Evidence | Status |
| --- | --- | --- | --- |
| 2026-10-20 | Experiment 043 12-state Wolfram execution, wrong-law mutant and matched-length null | [Wolfram oracle file](../../../experiments/043_og_aud1_preflight/global_oracle.wl), [RESULTS](../../../experiments/043_og_aud1_preflight/RESULTS.md) | `PREFLIGHT_EXECUTED_EXPLORATORY`, Gate A still candidate |

## 2026-10-20 Experimental 044 (new full-grid monitor prototype; exploratory)

A [parameter-prospectively-recorded but not independently ratified protocol](../../../experiments/044_og_aud1_monitor/PROTOCOL_CANDIDATE.md) preceded new code. [Experiment 044 runnable source, oracle and evidence](../../../experiments/044_og_aud1_monitor/README.md) now produce actual **1-second / 48kHz candidate pressure monitor WAVs** and raw physically dimensioned p/U. Two independent local executions matched byte for byte, **5 unittest cases passed**, source bytes identical, and the paired pressure RMS difference was ~0.744 relative to small-C RMS; common gain 0.3848611156 reciprocal Pa. Wolfram's separately assembled 12-state matrix was evaluated at **12 new case/frequency points** including non-OG-4 off-anchor FFT bins and included as frozen values in tests. Full result [RESULTS.md](../../../experiments/044_og_aud1_monitor/RESULTS.md), new companion CI [workflow](../../../.github/workflows/og-aud1-exploratory.yml).

**Boundary:** this is real execution evidence but **NOT** a confirmatory newly validated broadband Core backend, nor source–tract feedback, radiation, Studio Take or creator-reviewed perceptual outcome. Never write `GO_LIMITED` from these checks alone.

| Date | Event | Status |
| --- | --- | --- |
| 2026-10-20 | Experimental 044 prospective candidate parameters → analytic-bin Python prototype → two byte-identical local outputs + 5 tests + off-anchor Wolfram | `EXPLORATORY_ENGINEERING_PASS; GATE_A_UNRATIFIED; GATE_B_UNCONFIRMED; STUDIO_NOT_IMPLEMENTED` |


## 2026-10-20 follow-on Experiment 045 — causal-echo falsification (EXPLORATORY)

Previous [Experiment 044](../../../experiments/044_og_aud1_monitor/RESULTS.md) is physically explicit but its >4kHz FFT brick-wall monitor projection is formally acausal. The new [Experiment 045](../../../experiments/045_og_aud1_causal_monitor/README.md) implements causal finite reflection delays under exactly the **same frozen matched-load 3-duct hypotheses**; report this as a *post hoc research improvement*, **not** an independently approved preregistered confirmatory Gate B.

H0: the matched-load source-port A/B audible difference would disappear, or the time-domain response would violate source-onset causality, p-continuity/flow or energy under a causal realization. H1: prescribed identical U(t), only C area changed, gives distinct p(A.in) with exact pre-onset zeros, junction conservation and positive passive exit energy, converges as echo count increases; its Fourier response is consistent with Wolfram's closed-form ideal input impedance.

Scientific falsification controls: wrong reflection omission and particle/volume law, illegal C area, source mismatch, finite/nonfinite rejection, insufficient echo count, reversed J flow, nonmatching outlet energy, output overwrite, per-Take normalization confound, corrupted file hash, source-plane misidentification. Current runner tests the declared bounded subset; **do not infer all listed controls passed**. Port traces and matching law are tested for the exact 48k-source record. Independent full-grid Wolfram and formally prospective acceptance Gate A/B review still open.

Observed local exploratory evidence: causal A/B RMS pressure relative difference ~0.744, reflections r=-0.2/-0.5, round-trip tau≈0.0004664723s; six local test categories passed in analogous Python implementation. Wolfram's analytic finite-series/closed-form 733Hz relative errors ~1.53e-16 and ~3.83e-16 for the two C areas; no human scientific audit. The **PCM16 audio samples match Experiment 044 hashes**, a strong candidate cross-method consistency check but not a full waveform-validity proof. See [Experiment 045 RESULTS](../../../experiments/045_og_aud1_causal_monitor/RESULTS.md). Exact committed code must pass CI; do not assert CI before it reports. Decision: **EXPLORATORY / HOLD_ADOPTION**, Studio Gate C and creator audition remain pending.
