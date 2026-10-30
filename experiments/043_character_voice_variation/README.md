# Experiment 043 — Character Voice Variation, bounded causal pilot

**RESEARCH_ONLY / NOT_ADOPTED / no Studio UI or public Core API.**

Creator capability being explored: select a physical body and change a realizable
motor schedule, then compare newly synthesized audio under one shared source and
one listening gain. This is **not** speaker identity, natural language, reliable
phonetic content, physiologically validated MotorPersona, or a higher-fidelity
voice model.

The 2×2 conditions are M0/M1 (16.0/17.6 cm axial tract) × reference/late
second-constriction onset. All four use the same existing Exp027 physical
realization, Exp023/Exp012 acoustic propagation, and Exp013 LF source.

Run from a Core source checkout in an environment with project dependencies:

    PYTHONPATH=src python experiments/043_character_voice_variation/run.py --out /tmp/exp043-fresh

The output directory must not already exist. Four WAV files share one playback
scale; four raw-pressure NPY files and a receipt provide the causal evidence.
No WAV slicing, arbitrary EQ, crossfade, or neural synthesis is used.

See [SYSTEM.md](SYSTEM.md), [DATA.md](DATA.md), [EXPERIMENT.md](EXPERIMENT.md),
and [RESULTS.md](RESULTS.md). Do not merge, promote a new Studio control, or
declare a new character-voice model until the owner accepts the relevant gate.
