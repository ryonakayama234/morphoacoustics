# CVI-1 × SMC — Gate A executed results / STOP ledger

2026-10-27 JST. **Software research evidence, not bodily motion or voice science adoption.** This experiment is stacked on **unmerged** SMC6 research Draft #225 at parent `0caa70f6bb8333f60fbcc2f29ea57578c998033c`. It is not present on Core main.

## Evidence order (frozen prereg → observed RED → source → CI)

- Protocol-only `c354ae7af200cb13928c4e501aa00d67462f06bc` froze hypotheses/tests A01-A09 and the no-physical-meaning STOP.
- Test-only `a922429159c161d85e049aa4bbd07b4a19d1ba4e` imported missing `binding_preflight.py`. After workflow addition `14785add867c4c6def637d8fb44edeec625933fb`, actual [workflow 40512436878](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40512436878) recorded **RED**, Python 3.13 job `122217492658`: `ModuleNotFoundError: No module named 'binding_preflight'` at pytest collection. The other two jobs were canceled, not independent observed failures.
- Source implementation `79fa1b57953388b096d9f7a386dd3a4ed594ef38` adds an experiment-local, read-only SMC5/SMC6 authenticity check and unconditional **semantic STOP when mapping evidence is absent**. It does not modify the SMC/Core engines or their public contract.
- Machine-readable JSON stdout runner `a9acbfd31dd9c99be9cc611224bbdf45829c82e0`, workflow emission at exact **code/test HEAD `05e3f6f741ec1f6e537423f9018518293420dac3`**.
- Actual [dedicated CI 40512825544](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40512825544) **SUCCESS**, all Python **3.11/3.12/3.13** jobs. Python 3.13 reported **12 pytest cases passing** and emitted full JSON data. [Root tests 40512825713](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40512825713) **SUCCESS**; [SV1 40512825569](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40512825569), [OG3 40512827752](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40512827752), [OG4 40512825583](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40512825583) also SUCCESS. They are regressions, not CVI physical evidence.

CI values refer to **exact tested code HEAD `05e3f6f`**. This RESULTS.md is a later documentation-only commit; no new exact-doc-head CI or independent review is claimed without separate verification.

## Actual authenticated synthetic fixture data (CI Python 3.13 job `122218756119`)

| Field | Observed |
| --- | --- |
| Stage A | `FORMAL_AUTHENTICATED` |
| Stage B | `UNMAPPED_SEMANTICS` |
| Stop reason | `NO_EVIDENCED_PHYSICAL_TASK_BINDING` |
| Unique SMC Tasks | **3** (P1 tract; P1 source; P2 tract) |
| SMC6 exact event timestamps | **6** |
| Physically evidenced mappings | **0 / 3**, no claim about broader text corpus |
| Physical traces, acoustic traces, Takes | all **null / NOT_TESTED** |
| Canonical request SHA256 | `e4aaadc927003c78fb665f936dfff2bca9ec004fa29f436f9b8bf10f5a76529b` |
| SMC5 candidate digest | `16233fb9753bf6ae7e421570853615dfa5403fa19b140207071a232bcba0708a` |
| SMC6 original timing digest | `48fb701e793854322bd59d744c0e030f7bd8e9ee0a33541344dbc2b29b5702db` |

Exact **symbolic** events (seconds from selected fixture; NOT measured muscular/tract onset):

| Task occurrence | Original definition / value domain / applicability | ONSET | OFFSET | Core mapped? |
| --- | --- | --- | --- | --- |
| P1 tract | `tract / open_closed / synthetic` | 0 | 3/5 | NO |
| P1 source | `source / active_inactive / synthetic` | 0 | 4/5 | NO |
| P2 tract | `tract / open_closed / synthetic` | 2/5 | 1 | NO |

All SMC candidate intervals are **synthetic dimensionless fractions [0,1]**, not physical SI tissue displacements. Tract fixture's capability strings are `contact` and `flow`: these are symbolic requirements, **not proof** of a body's contact or volume-flow actuator.

Negative tests passed: invalid bytes/nonbytes, unresolved exact timing, shared Task counted once, semantically unordered declaration permutation, incompatible additional COMPATIBILITY exact time constraint yielding UNSAT with no witness, attempted caller-provided arbitrary binding, and lexical coincidence with Core `CONSTRICT`. These are bounded software controls, not independent biophysical measurements.

## Scientific interpretation / gate

**Decision: `GATE_A_FORMAL_GO / STAGE_B_SEMANTIC_STOP`.** The originally proposed CVI-1 same-body M×H physics G0 remains **`NOT_TESTABLE_BACKEND_CAPABILITY`** on currently demonstrated interfaces. This is *not* SMC formal-algebra failure: the source lexicon intentionally has only synthetic task meanings. It is also not evidence that a real SMC-to-body mapping is physically impossible. Stage C onward was NOT RUN; no produced waveform and no Studio UI work or main merge.

**Proposed next-stage question for a new deliberate scientific choice:** can we name **one** versioned Core physically meaningful goal variable `g_i(x(t))`, SI dimensions, coordinate/location interpretation, actual actuator/capability law, independent calibration/reference measurement, and explicit failure controls; then create a separately identified SMC TaskDefinition with corresponding backed semantics? Only after this can a legitimate Core H_EXEC controller contrast be preregistered. A synthetic kinematic connector remains valid only as **software interface research**, never accepted physiological character voice.

References: [Core Issue #223](https://github.com/ryonakayama234/morphoacoustics/issues/223), [CVI design Draft #224](https://github.com/ryonakayama234/morphoacoustics/pull/224), [SMC formal Draft #225](https://github.com/ryonakayama234/morphoacoustics/pull/225), [this experiment Draft #226](https://github.com/ryonakayama234/morphoacoustics/pull/226).
