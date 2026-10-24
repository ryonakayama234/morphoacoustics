# SA-2B B1 — lossless 1D duct + physical mouth boundary (research only)
Status: GATE_A_PREREGISTERED / NOT_RUN / NOT_ADOPTED, 2026-10-24.
Issue: https://github.com/ryonakayama234/morphoacoustics/issues/177
Predecessor: B0 Draft #176 https://github.com/ryonakayama234/morphoacoustics/pull/176 ; verified executed B0 source 5b3a981f6966a76169b0eb3f5a8d6ab9ebc95120.
This is a stacked research branch on the unmerged B0 branch. DO NOT merge B1 into main directly while B0 is unadopted.

- [SYSTEM.md](SYSTEM.md): dynamics, conservation, coupling, architecture, Core/Studio boundary.
- [DATA.md](DATA.md): states, SI quantities and output/evidence fields.
- [EXPERIMENT.md](EXPERIMENT.md): hypotheses, tests, expected failures and prospective gate.
- [GATE_A.md](GATE_A.md): pre-implementation frozen tolerances; future results MUST be written to a separate retrospective RESULTS file.

Scope: one fixed uniform lossless tube, not genuine variable-area M0 body; M0 lip *area* sets B0 load but uniform tube sections are calibration-only. No waveform synthesized, human voice, glottal self-oscillation, nearfield microphone, SMC, ASMR, or Studio adoption. B2 follows after independent B1 evidence.