# CC-B1 prospective NEW Core physical run: mid-tract site08
Research-only downstream of [frozen Gate A](../../docs/research/cc-b1-tract-edit/GATE_A_FREEZE_20261022.md), exact freeze commit `ca8bf64c8525a9cf59cb1332c4819763a0f9197e`.

`python experiments/cc_b1_gate_b_site08/run.py --output-dir cc-b1-gate-b-site08-output`
and `CC_B1_GATE_B_PHYSICS=1 python -m pytest -v tests/test_cc_b1_gate_b_site08.py`.

Same Exp029 16-section path, 0.5sec 48kHz, same LF source and 3-task program, site8 only ±10%, *two separate* baseline physical solver calls, 102 acoustic calls each. Frozen 5Hz independent Wolfram reference is committed in Gate A BEFORE these acoustic results. Archive 4×.npy (three conditions + fresh repeat), 3×common-gain .wav, full decision.json; do not overwrite old results. Null/refusal controls and adapted CC-A2 regression remain mandatory. If success, classify **RESEARCH_MACHINE_PASS_PENDING_INDEPENDENT_AUDIT**, never full Gate B science adoption.

Known limitations: earlier theoretical scan covered site8; waveform changes do not imply human auditory discrimination, voice quality or naturalness; no Studio UI or production revision API.

## Post-review non-semantic audit hardening

The B acceptance boundary now pins the already-audited Experiment029 task-plan
digest, validates the prepared body/provenance and terminal geometry, rejects
fallback/nonfinite pressure and nonfinite peak arrays, and refuses invalid
relative-L2 normalization. The source generator and inherited acoustic/realizer
code remain frozen; no physical model or prespecified threshold is changed.

The machine decision records Python/NumPy/platform, CI run URL when available,
artifact name (artifact *ID* is assigned only after upload), hashes of actual
NPY/WAV file bytes, and an explicit synthetic acceptance-boundary refusal
matrix. The latter is **not** a claim that the inherited solver was internally
fault-injected; that test remains NOT_TESTED and is disclosed. Independently
review the run and artifact IDs after an exact-HEAD successful CI run.
