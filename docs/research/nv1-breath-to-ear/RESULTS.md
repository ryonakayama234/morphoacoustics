# NV1-EAR / Core — RESULTS ledger

2026-10-21 — **DESIGN ONLY; NO IMPLEMENTATION, NO NV1 WAV, NO SCIENTIFIC OR HUMAN LISTENING RESULTS.**

- Analytic calculation only, independently checked in Wolfram Language: P0 Q=0.2757716447 L/s, P2 Q=0.390 L/s, A2 Q=0.5515432893 L/s, Z0=0. Detailed parameters and tolerances in PREREGISTRATION.
- Existing [EL-G0a #129](https://github.com/ryonakayama234/morphoacoustics/pull/129) provides measured-receiver *research infrastructure* and six earlier source-test clips, **not NV1 bodily exhalation evidence**.
- Known blocker: measured SOFA `ReceiverPosition` ambiguity/reference-plane and absolute B level unverified. Human headphone review and independent audit pending [#128](https://github.com/ryonakayama234/morphoacoustics/issues/128).
- Next record must include real command, exact commit, dataset and result artifact digests, numeric and listening outcomes, controls and decision. Do not convert this design ledger into a pass report without execution evidence.

## W0/W1 first execution: physically conditioned aperiodic source — 2026-10-21

**Status:** source-only **IMPLEMENTED / W0+W1 local and dedicated CI numerical gate passed / AUDIO GENERATED / NOT_ADOPTED**. No measured B/SOFA, Studio execution, complete organism, human blinded listening sign-off, independent acoustic/physics review, or scientific realism approval.

**Code:** experiment-local `experiments/042_nv1_breath_ear/{source.py,run.py,README.md}`; `tests/test_experiment_042_nv1_breath_ear.py`; dedicated `.github/workflows/nv1-ear-source.yml`. Exact source follows prereg A0 seeded `Q -> q_ac` hypothesis; pressure and aperture inputs are **experimental actuation**, not anatomically measured performance gestures.

**Environment/command (local):** Python with numpy 2.3.5, scipy 1.17.0, soundfile 0.13.1; `python -m pytest tests/test_experiment_042_nv1_breath_ear.py -q` -> **15 passed**; `python experiments/042_nv1_breath_ear/run.py --output /mnt/data/nv1_w1/listening` -> four physical-condition fresh 48k 24-bit L/R WAV, NPZ SI traces, sha256 receipt. Local execution directory was **not a verified Git checkout**; local evidence recorded `core_commit_sha:null`/`git_dirty:null`. GitHub Actions provides the clean linked code revision.

**Independent GitHub CI:** [workflow SUCCESS](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39538659810) on commit `29ebff8cdbe7ec84e930cd221acf1644ea796bee` (2026-10-21), including 15 W0/W1 cases, new waveform generation, PCM_24 stereo check, clean Git worktree assertion and upload. Actual [30-day artifact](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39538659810/artifacts/12318735201), artifact ID `12318735201`, expires 2026-11-20. CI printed P0 `q_ac` digest identical to the local independently executed value below: `6ab131b7e7214d030f3c28b94d68b7c5ef53bcdfb2abc12add44b504b7bdb07e`.

**Physical and source metrics** (these are *model outputs*, not empirical human respiratory measurements):

| condition | Wolfram Q_peak L/s | q_ac energy >=2kHz | 5k/1k spectral-band ratio dB | ideal acoustic-to-pneumatic power ratio | L/R WAV peak after fixed 70x playback |
|---|---:|---:|---:|---:|---:|
| P0 (120 Pa;30mm²) | 0.27577164 | 0.429416 | -8.46337 | 6.0875e-8 | 0.233637 |
| P2 (240 Pa;30mm²) | 0.39000000 | 0.512497 | -6.67457 | 7.9520e-8 | 0.435204 |
| A2 (120 Pa;60mm²) | 0.55154329 | 0.339179 | -10.28618 | 7.0179e-8 | 0.353577 |
| Z0 (0 Pa;30mm²) | 0 | 0 | 0 (silent, undefined ratio convention) | 0 | 0 |

Noise seed fixed at 133041. The same presentation gain 70 is disclosed across all nonzero cases and **must not** be confused with calibrated SPL. Raw pre-presentation A modeled Pa traces are stored in NPZ. Output safety budget (<1% equivalent acoustic/source power ratio), finite samples, no overrange >0.95, refused invalid/unsupported pressure or aperture, exactly silent Z0 and exclusive creation verified locally. **Future human perception and calibration have not been tested.**

**Gain-only null:** relative best-fit waveform residual `||q_variant - k_best*q_P0||/||q_variant||` is P2=0.1523677 and A2=0.1441858; both are above the 0.01 implementation-gate threshold. The non-gain spectral shift is structurally *guaranteed by the explicitly chosen model filter*, hence NOT independent evidence that natural human exhalation behaves this way. Formal significance across random seeds, reference human recordings, human listening, and perceptual superiority remain untested.

**Sample source and WAV hashes:**
- P0 `q_ac` SHA256 `6ab131b7e7214d030f3c28b94d68b7c5ef53bcdfb2abc12add44b504b7bdb07e`; PCM24 WAV SHA256 `8037b0a87211cd0b4a3d6758de703e79ab1a4da5ef12fdda48f3243f8b50b585`.
- P2 `q_ac` SHA256 `90eb582963fab42873412c344e3e7c20571f6702658c2061f4ca6ea8fc735ff9`; PCM24 WAV SHA256 `07a7f7995b91d16cd57005293919efca8832ce45295c5e8ec9a25da6e77f0ede`.
- A2 `q_ac` SHA256 `c54652749e428993a3f9fabf689621f8b22c98cf4e1362d0294ec258a0f332d0`; PCM24 WAV SHA256 `82b411f76095ddef2367583afefd6b230bb86c91412e4ec0201c98dc7cd9244e`.
- Z0 `q_ac` SHA256 `0b150fd32588b1daca5569992ebe559c0102c837306b1af4c44d35128ec58366`; PCM24 WAV SHA256 `41089f12c99542ecc16d5e48cef5455f1d9466ed4b2234b8b2a1870a7fd387bf`.

**Known risks / unmet gates:** no full gestural-realizer/physiological breathing dynamics; pressure directly scheduled, no vocal fold or shape-varying speech tract, substitute circular aperture; stochastic closure filter and Re gate are uncalibrated; reproduction may depend on pinned numerical versions; W1 duplicates a bounded analytic ideal-A receiver routine and W2 must reconcile phase and delay conventions against EL-G0a; no real measured HRTF B or matched-ear A/B calibration; no independently verified ASMR quality. Do not merge or promote until a distinct decision.
