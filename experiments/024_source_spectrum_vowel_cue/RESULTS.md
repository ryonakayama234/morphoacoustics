# Experiment 024 results

Issue: #55

Decision: **SOURCE_SPECTRUM_OBJECTIVE_GATE_FAILED**.

No human listening result is collected from this experiment.

Objective measurements:
- tract oracle: PASS, 0.0 Hz error on checked peaks;
- source magnitude oracle: PASS;
- /i/ rendered P2/P1: S0 -28.7989 dB, S1 +2.7233 dB;
- /i/ improvement: **+31.5222 dB**, above the +10 dB requirement;
- finite outputs: PASS;
- startup metric: PASS;
- level normalization: PASS;
- S1 cycle-boundary jump/RMS: **0.5790**, above the <0.01 limit;
- absolute rendered-oracle error: /a/ 2.0047 dB, /i/ 1.0939 dB, /u/ 0.1400 dB; the frozen 2 dB /a/ check therefore also failed.

The public listening set is not used because the objective Gate failed.

The useful result is that changing only the excitation spectrum changed the /i/ P2/P1 cue by +31.5 dB while tract geometry stayed fixed. This supports continued source-only diagnosis but is not a perceptual result.

Do not relax Experiment 024 thresholds. A separate revision should use a smoother periodic diagnostic source while retaining at least +10 dB predicted /i/ cue improvement and the same artifact limit.

Provenance: GitHub Actions run 37549679294; full artifact 11452595232; public listening artifact 11452550430.

## Post-merge reproducibility repair (PR #57 review)

The Wolfram generator was repaired to use real newlines, export the consumer's
`predicted_listening_pressure_p2_over_p1_db` key and all existing tolerance
fields, and numerically evaluate exact logarithmic expressions before JSON export.
A Wolfram kernel executed the repaired generator and re-imported its JSON;
every value matches the committed oracle. No predicted value was changed.

`s0_baseline.json` freezes the source and rendered harmonic ratios recomputed
from the canonical Experiment 023 source commit `4b9eacee8076b9cf285d24f79b6d6daa26d71449`
(originally experiment directory 015). The current S0 reproduces all six ratios
with zero measured error. The new 1e-6 dB tolerance is a numerical reproduction
check, not a perceptual or model-accuracy threshold. It was added after the
original experiment and is not described as an original preregistered gate.

Future runs require that control reproduction and finite S0/S1 /i/ ratios
before the objective gate can pass. Non-finite ratios cannot count as infinite
improvement. Re-running Experiment 024 preserves all existing measurements,
including +31.5222 dB /i/ improvement, and the objective-gate failure.
