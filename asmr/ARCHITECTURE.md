# ASMR Workspace Architecture RFC v0

**2026-10-22 | architecture candidate | Issue #154 | NOT ADOPTED | not installed into Studio.**

## Ownership
~~~mermaid
flowchart TD
 C["Core morphoacoustics\nphysical body, source, p/U acoustics and observation\nproduction contract owner"] --> P["Optional morphoacoustics_asmr package\nresearch registry now; future audited ASMR adapters"]
 P -. "explicit versioned adapter/API once approved" .-> S["morphoacoustics-studio\nscript, direction, immutable takes, UI"]
 R["Separate Draft research branches/PRs\nEL-G0, EL-G0a, NV1-EAR, EL-R1"] -. "after audit / limited adoption only" .-> P
~~~

**Core** must not import `morphoacoustics_asmr`. A future optional ASMR extension **depends on Core** and cannot replace Core's physical laws, bypass gesture realization, change validated Performance Contracts, or synthesize subjective ASMR character properties inside physical state.

**Studio** (separate repo) cannot directly import experiment scripts or treat PR branch APIs as stable. A future Studio adapter must **pin** a released package version plus compatible Core contract/capabilities, specify units, time conventions and physical reference planes, and produce immutable Takes. No auto-discovery/import on installation; explicit creator/UI enablement required.

## Research and production stages
1. `asmr/` registry + installable metadata package (this PR); all studies remain `RESEARCH_ONLY`, `load_feature` refuses. Nothing is enabled.
2. Independent research PRs stay on their own branches; tests and evidence links remain in the registry. Stacked studies must be separated or land only after their parent contracts have explicitly passed.
3. Adoption RFC per candidate: scientific gate evidence, reproducibility, allowed physical boundary/units, backward compatibility, type-tested Core adapter and source-version hash. PR to import a **specific audited capability** without duplicating the Core physics.
4. Optional Studio integration: version pin and capability negotiation, schema conformance, creator audition pipeline, rollback and secure opt-in; no imports from arbitrary GitHub branches.
5. Only then may a production `morphoacoustics_asmr` API publicly load an adopted feature. Independent Studio design [PR #24](https://github.com/ryonakayama234/morphoacoustics-studio/pull/24) is currently Draft.

## Module and namespacing decision
Repository location: `asmr/` (not `/ASMR` or `src/morphoacoustics/asmr`).
Installable distribution: `morphoacoustics-asmr`.
Import namespace: `morphoacoustics_asmr`, separate from Core `morphoacoustics`.
This is **one mono-repo workspace with independently installable optional package**, not five research repos or an experimental folder smuggled into Core's published API.

## Future issues intentionally unresolved
- Dynamic source impedance and listener impedance coupling for EL-R1; 0-Hz and fixed-total-pressure interpretation must remain explicit.
- HRTF measurement/reference planes, canal entrance open/blocked measurement and load-matching, not simply multiplying filters.
- Contact/noise physical modeling vs rendering/perceptual evaluation.
- Real ASMR Studio plugin registration schema **not yet agreed**: do not add fake Python entry points or an unimplemented plugin loader.

## Sources
[Core architecture](../docs/architecture.md) | [Independent listener PR #83](https://github.com/ryonakayama234/morphoacoustics/pull/83) | [EL-R1 #153](https://github.com/ryonakayama234/morphoacoustics/pull/153) | [Studio #24](https://github.com/ryonakayama234/morphoacoustics-studio/pull/24).
