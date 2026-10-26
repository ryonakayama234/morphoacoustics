# SMC-5 EXPERIMENT — test-first research registration

Frozen protocol: [SMC5_GATE_A_PROTOCOL.md](SMC5_GATE_A_PROTOCOL.md); issue #210. Version 2026-10-26 JST.

## Research questions
H1: one synthetic pronunciation unit can require >1 independent functional Task goals.
H2: explicit cross-unit sharing yields a *single occurrence* with multiple associations, while equal kinds without sharing remain separate.
H3: a canonically identical request yields identical graph, metadata and outcome regardless of wire serialization order.
H4: ill-typed, ambiguous, unmapped, incompatible sharing, and contradictory/unresolved timing are refused without invented executable plans.
H5: `plan_digest` is insufficient to distinguish unequal TaskGoal intervals, while `candidate_digest` does.

## Controlled variables
Fixed upstream ingress v1, SMC3 graph semantics, source Unicode and codepoint offsets, seeded synthetic TaskDefinition inventory, lexicon revisions and selected pronunciation. Intervention variables are bundle order, alternative candidate availability, context missing value, share declaration, template goal interval, and exact onset/offset constraints. Compare expected state, graph, goals and deterministic digest. Falsifiers S01–S12 are fixed in [the protocol](SMC5_GATE_A_PROTOCOL.md) and executable [tests/test_smc5_preregistered.py](../tests/test_smc5_preregistered.py).

## Evidence sequence
| Stage | Commit / evidence | Interpretation |
| --- | --- | --- |
| Protocol-only | `0cbd9171b53c16402644750018858cc8967b1377` | Frozen before tests/source |
| Initial test-only | `3d836e2b4bffc763da31790019dd50a9a18f0786` | Imports absent `symbolic_bridge` (expected RED) |
| Test-only rational-fixture amendment | `01d1e7c8fb46a1e15ab67806748ca42f1146fccf` | Normalizes int fraction before source; preserves prior test SHA |
| First source candidate | `47f67ee10c983a346e8fb3fa02d5b9d21cbb06ec` | Implementation exists, not yet independently audited |

## Reproduction
Within Core checkout using WSL2/bash or GitHub Actions, isolated package:
```bash
python -m pip install -e './packages/speech-motor-compiler[dev]'
python -m pytest packages/speech-motor-compiler/tests/test_smc5_preregistered.py -q
python -m pytest packages/speech-motor-compiler/tests -q
python -m mypy packages/speech-motor-compiler/src/morphoacoustics_smc
```
Workflow `.github/workflows/smc3-independent-package-research.yml` runs Python 3.11/3.12/3.13 plus strict mypy. Root CI and SV1 run independently by their existing workflows. Record exact-HEAD checks, not green status from an earlier source revision. Do not infer phonetic, physical, acoustic or subjective evidence from CI. Negative fixtures are first-class results; do not delete them to achieve green.
