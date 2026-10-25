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
