# Speech Motor Compiler (SMC) — independent research package

Status: **DESIGN/RESEARCH ONLY; NOT ADOPTED; NOT MERGED TO MAIN**.
Parent research: [SMC-2 #146](https://github.com/ryonakayama234/morphoacoustics/issues/146), [design audit #148](https://github.com/ryonakayama234/morphoacoustics/issues/148). Package work: [#162](https://github.com/ryonakayama234/morphoacoustics/issues/162).

This is a self-contained, experimental **Python package** boundary for body-independent pronunciation hypotheses, motor Task IDs, many-to-many associations, and typed temporal coupling constraints. It is NOT a phonetic inventory, gesture execution engine, sound synthesizer, morphology adapter, or production API.

## Core causal boundary

Creator script → candidate pronunciation units → independent motor task graph → symbolic coordination plan → future capability validation → future physical realization in Core → future acoustics.

Studio is a browser/TypeScript app. Studio would communicate through a versioned backend service/API that imports this Python package; Studio does not import Python modules directly. No Studio integration is in this work package.

## Research invariants
- Identically identified Task IDs may be referenced by many pronunciation units; never duplicate a shared task.
- Lexical ordering does not determine physical timing. Coupling constraints are a separate graph.
- Source text and half-open Unicode codepoint spans are preserved; neither the planner nor validator guesses unavailable pronunciations.
- Symbolic capability requirements must be verified by a future body adapter; structural validation is never an executable/physical verdict.
- No physical gestures, organ parameters, pressure/F0, waveform, or playable audio are emitted by this package.
- SMC-1 and SMC-2 remain historical research branches; no implicit cherry-pick or merge.

## Contents
- `src/morphoacoustics_smc/`: experimental symbolic IR + fail-closed structural validation (code to be added only after preregistration).
- `tests/`: synthetic mathematical and rejection fixtures.
- `docs/INDEX.md`, `SYSTEM.md`, `DATA.md`, `EXPERIMENTS.md`: hypothesis and decision provenance.

## Install / validate (once code is present)
```bash
python -m pip install -e packages/speech-motor-compiler
python -m pytest packages/speech-motor-compiler/tests -q
```

All adoption decisions require separate exact-HEAD CI, independent reviewer and later real physical validation. See `docs/INDEX.md`.

## SMC-5 prototype (research-only; stacked Draft PR #211)

`morphoacoustics_smc.symbolic_bridge.compile_wire(payload: bytes)` accepts a finite versioned JSON request through the SMC-4 B-R canonical boundary and attempts to emit an **in-process, synthetic-only** `SymbolicPlan` + explicit `TaskGoal` scalar interval metadata + exact rational resolved timeline and provenance receipt. Direct snapshot entry `compile_canonical` revalidates immutable bytes/hash. No implicit Japanese reading, no waveform concatenation, no body/organ binding, no voice-quality claim, and no public stable MotorScore schema. See [SMC5_GATE_A_PROTOCOL.md](docs/SMC5_GATE_A_PROTOCOL.md), [SYSTEM](docs/SMC5_SYSTEM.md), [DATA](docs/SMC5_DATA.md), [EXPERIMENT](docs/SMC5_EXPERIMENT.md), [RESULTS](docs/SMC5_RESULTS.md), [DECISIONS](docs/SMC5_DECISIONS.md).

This candidate relies on unmerged research parent branches and remains `SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE` until exact-HEAD CI and `@codex review` are documented.
