# EL-NF5 — research INDEX / D0 design freeze

**2026-11-01 JST | Issue #263 | DESIGN_ONLY / RESEARCH_ONLY / D0_INTENT / NOT_ADOPTED / NOT_RUN / DO_NOT_MERGE.**

Owner approved **documentation, planning and Draft PR only**. No experimental implementation or measurements, no runtime changes, no source/gesture/receiver adoption, no Studio integration.

## Start here: authoritative reading order

1. [SYSTEM](SYSTEM.md) — physical measurand, cue factorization, reconstruction, architecture.
2. [DATA](DATA.md) — historical measured exposures, data provenance and claim limits.
3. [G0_DATA_QUALIFICATION](G0_DATA_QUALIFICATION.md) — source/microphone/reference-plane/rights checks and hard stop.
4. [PREREGISTRATION](PREREGISTRATION.md) — D0 hypotheses, negative controls, splits, estimands, numerical gates and selection protocol.
5. [EXPERIMENT](EXPERIMENT.md) — *future* research-only execution plan and independent audit protocol.
6. [COMPONENT_FREEZE_POLICY](COMPONENT_FREEZE_POLICY.md) — prospective partial-freeze prerequisites, preservation and promotion.
7. [RESULTS](RESULTS.md) — append-only; at D0, **NO RESULTS / NOT_RUN**.
8. [DECISIONS](DECISIONS.md) — explicit gate and authority decisions.

This directory is the **design source of truth** for NF5. No executable code or adopted API is part of this PR. A Git commit SHA containing these documents is the immutable D0 baseline once identified in the Draft PR.

## Research aim

On an *already-measured, stationary* head/listener, test whether arrival, interaural level and timing, common spectral magnitude, ear-specific detail and residual phase can be **modeled separately yet reconstructed as physically coherent bilateral measured-relative HRIR**, at spatially unseen positions with empirically bounded support. Strongest eligible development-selected baseline **and B0 nearest measured HRIR** remain mandatory.

The output is not absolute ear-drum Pa, generic human HRTF, near-contact sound, moving listener, acoustic source simulator or ASMR perceptual quality. One HATS result is not across-human generalization.

## Chronology / boundaries

- Parent source → field → receiver → observation separation: [Issue #53](https://github.com/ryonakayama234/morphoacoustics/issues/53).
- Embodied listener hypothesis guardrails: [PR #83](https://github.com/ryonakayama234/morphoacoustics/pull/83).
- Optional ASMR research registry and owner constraints: [PR #155](https://github.com/ryonakayama234/morphoacoustics/pull/155), `asmr/ARCHITECTURE.md`.
- Historic receiver evidence: [NF1 #252](https://github.com/ryonakayama234/morphoacoustics/pull/252), [NF2 #255](https://github.com/ryonakayama234/morphoacoustics/pull/255), [NF3 #257](https://github.com/ryonakayama234/morphoacoustics/pull/257), [NF4 #261](https://github.com/ryonakayama234/morphoacoustics/pull/261).
- [Issue #263](https://github.com/ryonakayama234/morphoacoustics/issues/263): authorized design-only tracking.

NF4 is **negative G3 / NOT_ADOPTED**, not a software failure; it must remain frozen as negative evidence, and its exposed SCUT final truth cannot be advertised as a fresh NF5 blind test.

## Gate map (not a claim that any gate passed)

D0 approved documentation → G0 original-data/intake, license and blind-evidence feasibility → G1 synthetic mathematical reconstructions → G2 failure/independent arithmetic → G3a historical-data model development → G3b **new independent original measured blinded confirmation** → optional G4 perception → G5 independent acoustics/code review → *separate* owner decision for any limited freeze or adopted API.

**Current state:** D0 documentation only. G0–G5 NOT_RUN. G3b remains BLOCKED until a truly independent qualified source is secured; no assumed future access. No Core `src/`, `asmr/`, experiments, workflows, Studio, SMC or main changes.
