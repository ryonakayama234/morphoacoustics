# Experiment 045 — executed local prototype evidence (2026-10-20)

**Exploratory only. The following numbers were observed with a locally tested equivalent causal series implementation; this branch's exact committed runner/CI is separately verifiable. No independent human scientific Gate A ratification or confirmatory Gate B.**

| Quantity | Small C=.00015 m² | Large C=.00060 m² |
|---|---:|---:|
| Reflection r | -0.2 | -0.5 |
| Round-trip delay (both) | 0.000466472303207 s | same |
| Conservative omitted-tail pressure upper bound | 2.28e-34 Pa | 1.15e-14 Pa |
| Inlet-vs-outlet integrated energy imbalance (relative) | 7.8e-16 | 1.3e-14 |
| Junction signed flow residual max | 3.71e-22 m³/s | 3.18e-22 m³/s |
| Pressure before source onset | exactly zero | exactly zero |
| PCM16 WAV SHA-256 | d7b4d7a428f5c6f158c00833ebfbf67d67d2b632b991669c3aab07f000626ce6 | 1a117eecd80370a9faa3165c36f88e0278b6fca823787eba36843d45bfd38563 |

Input source NPY SHA-256: 52bbebf4fec46861b252d0abf81a239f1396e5ec499527bd5168a299f9eafddd, matching the prior Experiment 044 source input. Relative physical pressure RMS difference: **0.7440267506929074** (not a perception score). The two PCM16 byte hashes also match Experiment 044 even though independent raw floating-point pressure implementations differ by rounding.

### Wolfram check

Standalone Wolfram closed-form ideal source impedance versus causal 60-reflection series at 733Hz yielded:
- C=.00015: 1603112.2733702508 + 559611.8806294522 I Pa·s/m³; relative discrepancy 1.53e-16.
- C=.00060: 1461638.155840067 + 1632724.2267963341 I Pa·s/m³; discrepancy 3.83e-16.

Independent **algebraic** check is not empirical validation. The six local regression *categories* succeeded for analogous test code: closed-form oracle, all-port continuity/energy, causality/tail, invalid no-reflection mutant, two-run PCM determinism, refusal/immutability. Exact committed files must pass PR CI, and separate numerical/security reviewers before any scope promotion.

**Decision: EXPLORE_MORE / HOLD_ADOPTION.** Next Gate A ratification must prospectively freeze numerical thresholds/oracle coverage and trust boundaries; do not retroactively call this experiment confirmatory. After Gate B, implement a new exact-pinned Studio adapter with perform→listen→persist→reload/restart. No success Take from this experimental runner.
