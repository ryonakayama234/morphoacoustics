# CORE-WG-1 — Hypothesis / protocol / evidence ledger

## Prior verified facts (NOT new results)
- Research B2-A [PR #184](https://github.com/ryonakayama234/morphoacoustics/pull/184), tested SHA `49d56f581036286e534e14835bede895a06327d6`, reports 16-section finite-speed passive scattering on prepared M0/M1, independent continuum and energy auditor, and successful CI [run 40146911007](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40146911007). External review found no major issues at this SHA. This is *only* evidence for the research branch.
- Experiment 025 / Studio Voice Atlas [issue #28](https://github.com/ryonakayama234/morphoacoustics-studio/issues/28): phonetic/forced-choice distinction or waveform difference is not the same as voice-likeness or character identity; listening remains a separate gate.

## Preimplementation registration
- `GATE_A.md` frozen at commit `54ef8a087236924599caa78a31cf1f9c2d283b61` before new Core code.
- Hypothesis H1-H3: preserve B2-A physical causality/passivity with a typed stateful Core port, without touching old paths.
- Independent controls: signed junction continuity/power; equal-area/length transit; B0 exact low-frequency RL equations; zero-input/signed drive; 4 terminations; invalid input state retention.
- Acceptance limits, static-only exclusions and future gates: [GATE_A.md](GATE_A.md).

## Actual new implementation (pending independent adjudication)
- Candidate module: `src/morphoacoustics/acoustics/passive_waveguide.py`.
- Scientific automated tests: `tests/test_passive_waveguide.py`.
- New Core code commit: `44108fbba2af7b2042400519ca19540dda4d25d0`.
- Focused tests commit: `c3887233b710019d9a3e851692c58d7ec106b5a9`.

## Evidence table

| Verification | Outcome | Authority |
|---|---|---|
| Old B2-A experimental CI and independent auditor | PASS on *old research source* | PR #184 / exact SHA above |
| New CORE-WG-1 tests on exact branch HEAD | **PENDING** | GitHub Actions receipt to insert after run |
| New CORE-WG-1 mypy / full regression | **PENDING** | exact HEAD CI |
| Differential raw wave/B0 traces versus B2-A archival source | **NOT RUN** | additional comparator required before adoption |
| Third-party Codex review of this new Core port | **NOT REQUESTED YET** | review after exact code and CI |
| Real source↔tract closed-loop + 48k physical bridge | **NOT IMPLEMENTED** | separate Gate CORE-WG-2 |
| Studio Take / blind voice-likeness / identity | **NOT TESTED** | Studio Voice Atlas separate |

## Decision
`RESEARCH_CANDIDATE / SCIENCE_ADOPTION_PENDING / NO_MAIN_MERGE`. The module presently has neither full independent result nor a validated audible creator loop. Do not relabel module-level tests as evidence of speaker identity, naturalness, or B2-B moving-wall physics. Record negative evidence and reviewer issues here rather than rewriting the preregistration.
