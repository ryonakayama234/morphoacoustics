# CC-B1 — Experimental BodyRevision preparation / searchable index

**Status: RESEARCH PROTOTYPE ONLY / NOT PUBLIC API / NOT SCIENTIFICALLY ADOPTED / NO STUDIO RUNTIME / DO NOT MERGE TO MAIN.**

Owner: [Core #141](https://github.com/ryonakayama234/morphoacoustics/issues/141), [Studio #25](https://github.com/ryonakayama234/morphoacoustics-studio/issues/25), [Epic #12](https://github.com/ryonakayama234/morphoacoustics-studio/issues/12).

## Read in order
1. [SYSTEM.md](SYSTEM.md): Core↔Studio workflow, organ/edge future boundary, unchanged adopted solver.
2. [DATA.md](DATA.md): draft RestAreaEditIntent, immutable BodyRevision, digest, typed refusal.
3. [EXPERIMENT.md](EXPERIMENT.md): preregistered claims vs executable software tests, Wolfram and prospective sensory gates.

Code: `tools/cc_b1_revision.py`; checks: `tests/test_cc_b1_revision.py`. No root export, v0/v1 schema change, or v1 body-preset registry registration.

## Research dependency graph
- Gate A design: [Core Draft #142](https://github.com/ryonakayama234/morphoacoustics/pull/142) — NOT RATIFIED.
- Pilot: [Core Draft #143](https://github.com/ryonakayama234/morphoacoustics/pull/143) — exploratory, physical waveform evidence only.
- Spatial follow-up: [Core Draft #144](https://github.com/ryonakayama234/morphoacoustics/pull/144) — post-hoc, blinded audibility unresolved.
- Studio handoff: [Studio Draft #26](https://github.com/ryonakayama234/morphoacoustics-studio/pull/26) — design only.
- SMC-1 Core #139 and ASMR Core #133 remain independent.

This branch prototypes only a pure binder/editor. Review cannot promote it until Gate A constraints and prospective B independent physics verification are accepted. Maintain doc/diagram/data/experiment as one PR unit.

Independent reproducible theoretical spot-check: [Wolfram recurrence source](wolfram_site_recurrence.wl) and [machine-readable result](wolfram_site_recurrence_result.json). This is post-hoc ideal-model corroboration, not a new physical Gate or ABX.


## Gate C versioned limited performer candidate (2026-10-22)
**CANDIDATE IN NEW STACKED PR / NOT RELEASED.** [Limited Core performer](../../../tools/cc_b1_limited_performer.py), [v1 strict request schema](../../../contracts/cc-b1/v1/core-limited-performer-request.schema.json), [gated physical acceptance tests](../../../tests/test_cc_b1_limited_performer.py). This is an additive source-checkout adapter alongside PR #145, not yet the installed Python public API. The owner-delegated [Gate A/B limited research decision](https://github.com/ryonakayama234/morphoacoustics/blob/469bb7cf3407c7591fdc89825a6443670896cb5c/docs/research/cc-b1-tract-edit/GATE_AB_OWNER_DELEGATED_TECHNICAL_DECISION_20261022.md) permits ONLY mid-tract **site08** ±10% as a physically tested edit. Older prototype tests for other section edits are software-only; do not expose those sites as a physically validated v1 performer.

## Gate C optional verified archive consumption
Call `verify_output_archive(output_dir)` on previously generated data; never let Studio infer success from a WAV alone. It checks exact version/profile and physical-origin evidence within the limited numerical model. This is a candidate Core verifier still under `tools/`, not an installed stable library.

## Gate C / revision replay security increment (2026-10-22)
Implementation branch: [Gate C revision replay audit](https://github.com/ryonakayama234/morphoacoustics/tree/feature/cc-b1-gate-c-revision-replay-audit-20261022), stacked on candidate [PR #159](https://github.com/ryonakayama234/morphoacoustics/pull/159), tracked by [Core #160](https://github.com/ryonakayama234/morphoacoustics/issues/160).

- **SYSTEM**: trust/data-flow diagram of baseline registry → deterministic derived BodyRevision → readback verification.
- **DATA**: complete canonical receipt equality, not only file hashes, with explicit type preservation.
- **EXPERIMENT**: wrong-identity fault injections and Wolfram ideal-duct sanity check, with unexecuted Gates separately labeled.
- **Code/tests**: `tools/cc_b1_limited_performer.py` readback replay and `tests/test_cc_b1_limited_performer.py` physical-pair tamper test.
- **Status**: code authored on Draft branch; do not conflate an authored test with a passing exact-head CI receipt. Still not a durable registry, installed public ABI, Studio Take or Gate C acceptance.
