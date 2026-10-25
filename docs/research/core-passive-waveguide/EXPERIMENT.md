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
| Differential raw wave/B0 traces versus B2-A archival source | **IMPLEMENTED / CI QUEUED** | [pinned-source workflow](../../../.github/workflows/core-wg1-differential.yml), see run 40153389314 |
| Third-party Codex review of this new Core port | **ROUND 1: 4 P2; remediation committed; ROUND 2 REQUESTED** | PR #187 review threads |
| Real source↔tract closed-loop + 48k physical bridge | **NOT IMPLEMENTED** | separate Gate CORE-WG-2 |
| Studio Take / blind voice-likeness / identity | **NOT TESTED** | Studio Voice Atlas separate |

## Decision
`RESEARCH_CANDIDATE / SCIENCE_ADOPTION_PENDING / NO_MAIN_MERGE`. The module presently has neither full independent result nor a validated audible creator loop. Do not relabel module-level tests as evidence of speaker identity, naturalness, or B2-B moving-wall physics. Record negative evidence and reviewer issues here rather than rewriting the preregistration.

## Independent audit round 1 and remediation (2026-10-25 JST)

Codex review of exact initial PR HEAD `5c46b7fe84a84bc80612db2c64bdd9f08870f9db` reported **four P2 issues**, none treated as a physics pass:
1. Finite but enormous inlet flow could overflow and corrupt persistent waves/B0 state before failure; corrected with **copy-on-write tick state and commit-after-full-validation**, [code fix `c91c595`](https://github.com/ryonakayama234/morphoacoustics/commit/c91c595e6621fbef613f5a0d6236060fe4ed8b1c).
2. Finite primitive geometry/air values could generate infinite/zero derived Z/clock/B0 coefficients; added derived physical validation in the same commit.
3. `zl+zr` could overflow on finite extreme impedance, giving silently unphysical scattering; scale both impedances before computing r. Same fix commit.
4. Independent differential trace equivalence against audited B2-A source was absent; implemented `tools/core_wg1_differential.py` ([source `01664281`](https://github.com/ryonakayama234/morphoacoustics/commit/01664281d0d906eb51c0925b25c3695839c3a324)) and [dedicated pinned checkout CI workflow](../../../.github/workflows/core-wg1-differential.yml) ([`46b5da9`](https://github.com/ryonakayama234/morphoacoustics/commit/46b5da999d0048c8c46b7638223ada4604151ec2)). Regression cases for the first three issues committed at `743e0618b4dcd2f07aeed264ef738723679ead14`.

The differential audit MUST compare original research `49d56f581036286e534e14835bede895a06327d6` (GitHub immutable checkout verification) to new Core state for actual M0/M1 prepared registry, cell counts 2/4/8, all four terminations, zero/nonzero seeded forward/backward wave states and B0 inertial flow; verify **every tick**, not only a terminal scalar. This is a software-equivalence gate; the original B2-A independently measured continuum/energy oracle remains separately credited. Do not claim independent physical theory from identical equations.

**Current execution receipts:** [new Core suite CI 40153389318](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40153389318) = QUEUED at last check; [differential CI 40153389314](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40153389314) = QUEUED at last check. New exact-HEAD CI, archival comparison, and second Codex review have **NOT YET PASSED**. Do not merge on the basis of queued or merely designed tests.

## Codex round 2 — test fixture falsification (2026-10-25 JST)

Review of `46b5da999d0048c8c46b7638223ada4604151ec2` independently executed focused pytest. **17 tests passed, one failed**: the newly invented `1e-300 m` test geometry yielded a finite (though extremely large) clock, so expecting `ValueError` was false. This is a test hypothesis error, not evidence of an observed loss of passivity. Exact negative fixture changed prospectively to `1e-309 m` in [`7665b69`](https://github.com/ryonakayama234/morphoacoustics/commit/7665b6981b75ae97775c001c967a1f1101cbef28), where `c*2/L` mathematically exceeds binary64's finite range. Preserve the original failed fixture in this record. Full exact-SHA GHA and differential audit remain pending; still NO_MAIN_MERGE.
