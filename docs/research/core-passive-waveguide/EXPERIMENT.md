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


## Amendment 01 execution + Codex finding (2026-10-25 JST; preserved after earlier pending receipts)

- The previous exact HEAD `87229c1` **failed** GHA ([full tests](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40153560727), [differential](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40153560707)) due to frozen historical source-inventory checks, **not** because negative physics evidence was discarded. See [Amendment 01](AMENDMENT_01_SOURCE_IDENTITY.md).
- Relocated the unadopted new module unchanged to opt-in companion `src/morphoacoustics_waveguide/passive_waveguide.py`, keeping old frozen files/tests/manifest bytes unchanged.
- Exact candidate HEAD `5940dbb8e38fa419b929c0d9e36a4defedaab6d1`: [tests/typecheck PASS, run 40162249790](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40162249790); [archival B2-A differential PASS, run 40162249887](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40162249887); this is **software and physics-regression** evidence, not an acoustic voice-likeness result.
- Codex exact-head rereview on `5940dbb` found a **new P2**: the standalone differential tool attached the pinned archival SHA label without independently verifying its input checkout identity or local edits. The dedicated CI checkout *had* verified revision and was clean; the standalone tool was improperly permissive.
- Prospective repair in code `519262d27ec4d01e5cdc1f8a7720d6e7d9e912ea` verifies the archival Git `HEAD`, checks for tracked edits and untracked files before importing the reference, and derives its reported `reference_exact_sha` from verified `HEAD`; tests covering correct SHA, wrong SHA, and dirty archival tree in `e6e181af292be06503b492f58d41886dbe966737`.
- **Current decision at this documentation commit**: `OPT_IN_CORE_REPO_MAIN_ELIGIBLE_IF_GATES_PASS / NO_DEFAULT_BACKEND_SWITCH`. The new exact-head CI and independent Codex review are requested; neither shall be marked PASS in advance. Even after opt-in merge, coupled source/tract, B2-B moving walls, 48k WAV integration, perceptual naturalness and Studio production adoption remain separately pending.
