# CVI-1 × SMC — Gate A protocol: authentic SMC-to-Core preflight

**Status:** research-only, independently stopped integration evidence. Parent CVI design Core #223 / Draft #224; SMC formal research Draft #225. New experiment 040 is **stacked on unmerged SMC-6 source at `0caa70f6bb8333f60fbcc2f29ea57578c998033c`**, which itself stacks SMC-5/4 research. It is NOT Core main, a product ABI, a real articulatory plan or a merged feature.

**Research question:** Can the first bounded SMC synthetic selected-pronunciation fixture produce an authentic, immutable task-and-exact-time receipt *and* demonstrate an independently substantiated SMC TaskDefinition -> Core physical task target binding? Separate these questions; do not fake a usable Core Gesture merely because Task goal labels sound similar.

## Frozen before any implementation: audit inputs
- Existing unmodified SMC test fixture: `packages/speech-motor-compiler/tests/test_smc5_preregistered.py::valid` / `encoded` derived from historical SMC4-BR fixture. Source text `甲乙`, externally chosen artificial symbols, exactly three tasks (two `FUNCTIONAL_TRACT`, one `SOURCE`), SMC exact event anchors.
- Existing physical-domain counterpoint: Core `src/morphoacoustics/domain/gesture.py` has named tasks `CONSTRICT`, `OPEN`, `PHONATE`, `PRESSURIZE`, and typed timestamps/location/parameters. This *representation alone* is not a measured SMC TaskGoal semantic map or lawful body-dependent execution.
- SMC5 `TaskGoal` does not expose full TaskDefinition variable/value_domain/applicability_domain; these must be retrieved from authenticated canonical request, never inferred from goal_kind.
- Temporal lane restricted to SMC6 `COMPATIBILITY`, original exact timing. `RESEARCH_OVERRIDE` is explicitly out of scope.

## Prospective tests, listed before source
A01 valid canonical fixture -> `FORMAL_AUTHENTICATED` stage A, exactly three unique Task IDs and six exact event endpoints with correct canonical/candidate/timing digests. No Core Gesture or audio.
A02 independently read definition IDs and three extra TaskDefinition fields. Exact `tract` definition has variable=`tract`, value_domain=`open_closed`, applicability_domain=`synthetic`, capabilities=`flow, contact`; `source` uses synthetic active_inactive. **Neither is physical evidence.**
A03 Stage B **STOP** with `UNMAPPED_SEMANTICS` for the fixture, because there is no independently qualified dimensioned Core target, position/location rule and capability mapping. No Core Gesture/solver/waveform/take emitted.
A04 source corruption / changed or malformed canonical request, unresolved SMC -> fail-closed, no usable downstream schedule or mapped task.
A05 shared Task across P1/P2 -> one task, one authentic event pair, not duplicate physical actions.
A06 semantically unordered JSON declaration permutation -> unchanged canonical candidate and timing digests (SMC5/6 contract); no arbitrary anatomy inferred.
A07 COMPATIBILITY extra contradictory hard time constraint -> UNSAT; no timing witness or physics.
A08 direct invented mapping evidence or `CONSTRICT` lexical coincidence cannot turn missing independent physical mapping into a pass.
A09 test scanner verifies Gate A code cannot import physics execution or emit WAV/pressure/Take, and branches/statuses preserve explicit scope.

## Outcome metrics
- count unique TaskGoals and temporal endpoints, shared IDs, recovered definition fields;
- SHA-256 source/candidate/timing receipts and event interval exactness (`fractions.Fraction`, seconds);
- semantic binding coverage `N_supported / N_required` for a **declared physical target capability** (NOT linguistic coverage). Here expected `0/3` physically supported; do not report a software bug because the synthetic fixture is intentionally not a body contract;
- actual negative controls: rejection code, no mapped Core Gesture/physical trace/port observation.

## STOP and next-stage boundary
- **A must pass:** valid SMC source and exact timing; failure indicates software compatibility/refusal and requires CI/debugging.
- **B deliberately may stop:** source describes only synthetic TaskDefinitions. Record `UNMAPPED_SEMANTICS` with the **actual TaskDefinition fields** and no physical conversion. Do not choose an arbitrary length/pressure, treat unitless fractions as actual tongue displacement, or invent a Core gesture to score a fake pass.
- A future *different* Gate B will need an independently documented physical variable / units / location interpretation / measurement reference, versioned TaskDefinition and a verified Core realizer. H_EXEC 2x2 remains separately blocked if no physical dynamical controller.
- No new Studio UI, no MotorPersona, no free-text reading proof, no acoustic signal or main merge.

## Evidence order
1. This protocol commit (freeze tests and expected refusal).
2. Test-only commit (expected collection RED until code exists); preserve actual CI evidence if observed.
3. Minimal research adapter + tests and exact-HEAD GitHub Actions.
4. RESULTS.md append-only with source SHA, actual CI/negative cases and truthful STOP interpretation.

Owner: Core #223; parent design #224, SMC research #225. Independent review and product decisions remain distinct from software CI.
