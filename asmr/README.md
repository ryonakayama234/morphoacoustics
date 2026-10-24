# ASMR Research Workspace — one starting point

**Status: WORKSPACE PROPOSAL / NO ASMR SOLVER ADOPTED / NO STUDIO PLUGIN ENABLED.**

This directory is the single **navigation and optional-package** entry point for ASMR-targeted research in Morphoacoustics. It is intentionally lowercase (`asmr/`) for Linux/WSL2 and Python portability. It is not a repository fork and **does not duplicate Core acoustics**.

- [Research registry](./src/morphoacoustics_asmr/research_registry.json) — version-pinned, manually reviewed snapshot of ASMR research including EL-R2-S1 #158.
- [Architecture](./ARCHITECTURE.md) — exact Core/ASMR/Studio ownership and adoption gates.
- [Python package](./pyproject.toml) — a separately installable **metadata-only** `morphoacoustics_asmr` entry point.
- [Tracker #154](https://github.com/ryonakayama234/morphoacoustics/issues/154) — future migration/adoption governance.
- [EL-R1 science audit #152](https://github.com/ryonakayama234/morphoacoustics/issues/152) and [Draft PR #153](https://github.com/ryonakayama234/morphoacoustics/pull/153).

## Install and use the *metadata-only* package
~~~bash
# WSL2/Linux from Core repository root:
python -m pip install -e ./asmr
python -c "from morphoacoustics_asmr import list_research; print([x.id for x in list_research()])"
~~~
This makes **only the metadata registry importable**, *not* audio rendering, listening, physical contact, breath generation, SOFA rendering, or Studio integration. Attempts to resolve an unavailable capability explicitly raise `ResearchUnavailable`.

## Why files are NOT bulk-moved yet
The indexed ASMR-oriented Core PRs are draft/unmerged. G0a and NV1 are stacked on earlier listener research branches. Moving these experiments from their branches into `asmr/` without independent scope and review would break relative paths, imports, fixtures, CI workflows, and provenance and could silently make research look adopted. The registry links to actual source branches/PRs for now. This registry is an explicit **package-version snapshot**, not an exhaustive live GitHub feed. Newly relevant ASMR research PRs require a reviewed metadata/test update; being indexed never implies adoption. Once audited and approved, a **dedicated adoption PR** may reorganize a study under `asmr/research/<id>/` while preserving references and source hashes.

Only `src/morphoacoustics` Core owns the physical laws, morphology, realizations and invariant contracts. ASMR orchestration and optional creator-facing behavior may live in this independent package, but the physical components themselves are reusable across speech/ASMR/nonvocal contexts.
