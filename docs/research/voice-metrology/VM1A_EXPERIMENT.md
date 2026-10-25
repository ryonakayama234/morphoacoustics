# VM-1A experiment ledger

**2026-10-25 proposal / not yet executed at preregistration commit.** Gate A: [VM1A_GATE_A](VM1A_GATE_A.md); system: [VM1A_SYSTEM](VM1A_SYSTEM.md); data: [VM1A_DATA](VM1A_DATA.md). Issue [Core #196](https://github.com/ryonakayama234/morphoacoustics/issues/196).

| Experiment | Intervention | Controls | Falsification |
|---|---|---|---|
| E0 analytic null | uniform area, matched termination, 1 tick volume pulse | exact delay 32 native ticks, Zc and one-way transfer | delay, p/U, complex phase mismatch |
| E1 frozen body | 16-section /a/ M0 0.16m vs M1 0.176m; identical areas | exact frozen JSON blob and source volume | invalid identity or no reproducible physical response |
| E2 terminal ablation | B0 vs perfectly matched with body held | no wall correction, no gain, one source pulse | nonphysical energy creation or untracked port changes |
| E3 linearity | 1x vs 2x injected pulse, same body/B0 | zero-state reset only between whole runs | unequal complex transfer / non-proportional pressure |
| E4 negative | zero pulse, wrong geometry digest, bad trace input | strict refusal | false silent PASS or spoofed body identity |

Expected outputs: frequency-grid complex transfer points around 100 and 600 Hz, source impedance, mouth flow transfer, per-run energy and validation. No predicted numerical M0/M1 selectivity is pre-declared; avoid retrospective thresholds. `NO_GO_PENDING_PHYSICAL_REFERENCE` is a scope status, not an observation made before experiment.

**Actual machine runs, commit IDs, CI links, and independent reviews are deliberately NOT filled in at preregistration time.** They must be appended only when genuinely executed, with any protocol changes recorded as amendments, not quietly rewritten.

Next: compare to independent segmented/B0 frequency oracle, then ringdown and linewidth and finally investigate physical tissue/wall attenuation or source coupling if warranted. Studio's default UI and frozen Take audio remain unchanged.

## Actual instrument runs — 2026-10-25 UTC (not biological or voice validation)

**Executed branch head:** `95bb69d77dca6116ba16dd57a57c3b8082110233`.
[VM1A science workflow run 40204339104](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40204339104) **PASS** with seven focused tests, authentic frozen Experiment028 body arrays, two terminations, and 2x physical amplitude checks on M0 and M1 B0. The run published `vm1a-research-transfer-json` with all complex transfer points, native ports, hashes, energy and integration metadata. This is a diagnostic artifact, not a Take.

| Body | Termination | Native physics clock | Actual nearest frequencies | `20log10(|H_pU(600)|/|H_pU(100)|)` |
|---|---|---:|---|---:|
| M0 | ideal matched | 68,600 Hz | 100.000 / 600.000 Hz | +2.99453 dB |
| M0 | B0 passive RL | 68,600 Hz | 100.000 / 600.000 Hz | +34.69097 dB |
| M1 | ideal matched | 62,363.636 Hz | 99.995 / 599.971 Hz | +3.69106 dB |
| M1 | B0 passive RL | 62,363.636 Hz | 99.995 / 599.971 Hz | +55.18207 dB |

Measurement: finite 0.30 s impulse-response DFT with no WAV export, normalized by a native-clock source flow input. This method is **different** from the historically measured finite-window, periodically driven VM-0 monitor. VM-0 source-to-mouth selection contrasts were M0 +34.665 dB and M1 +54.748 dB. Similar orders of magnitude are strong *mechanistic consistency* evidence but are not an exactly matched replay, a fitted formant, or an independent B0 physical-law validation.

**Current interpretation:** For BOTH frozen anatomies, the choice of termination materially changes relative 600/100 Hz transmission. M1's B0-bound static acoustic model reproduces a selective contrast close to its historical periodic observation. This narrows the likely causal path to the *modeled tract + boundary response* rather than a final PCM-only defect. The scientific question **whether the adopted B0 impedance and wall-free acoustic tube reproduce a real radiating vocal tract remains OPEN**.

**Controls:** matched uniform analytic delay/impedance/complex phase passed; missing/modified frozen body rejected; silence, scalar 2x linearity, B0-vs-matched and nonfinite inputs tested. The initial test-only failure (128 ticks did not resolve 100 Hz) was corrected by increasing the measurement control to 512 ticks, not by removing DC rejection. First failed workflow [40204115365](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40204115365) is retained. Initial independent Codex review of head `1cfd8cf` found this same P1 record-length defect; fixed in `3702686f`. Exact-final-head review and post-merge CI remain separate acceptance gates.

**Disposition:** `SUPPORTED_DIAGNOSTIC_SENSITIVITY`; `INDETERMINATE_ABSOLUTE_B0_PHYSICS`; `VOICE_NO_GO_UNCHANGED`; `CREATOR_AUDITION_NOT_REQUESTED`. Do not fit Q from this transfer pair, present these as natural formants, or treat the matched outlet as a plausible human mouth.
