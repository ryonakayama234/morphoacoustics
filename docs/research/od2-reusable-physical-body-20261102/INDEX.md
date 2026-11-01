# OD-2 — Reusable Physical Body / design package (2026-11-02)

**DESIGN FOR CREATOR REVIEW; NOT A RELEASE, NOT A CODE IMPLEMENTATION, NOT AN A3 PREREG FROZEN SCIENTIFIC TRIAL, NOT STUDIO UI PERMISSION.**

**Primary module**: Core Organ Modeling & Physical Assembly; later Studio Character.canvas / Selection.inspector / Take.transport only under existing approved slots and a separate UI authorization.

## File responsibilities
- [DECISION.md](DECISION.md): creative objective, deep GitHub prior-art audit, selected option vs alternatives, precise technical scope and adoption ladder.
- [SYSTEM.md](SYSTEM.md): diagrams for authoritative Core physics + approved Studio panel roles, mathematical shape law and actual acoustic observation.
- [DATA.md](DATA.md): proposed typed input/body/physical/result records, identity, one registry, failure taxonomy and historic Take preservation.
- [EXPERIMENT.md](EXPERIMENT.md): H0–H8 hypotheses, units and measurands, independent oracles, mutation controls, numeric bounds, stop rules and creator gates.
- RESULTS.md: **NOT CREATED because OD-2 has not been executed.** Create only with real results when a later authorized experiment runs, and preserve negative findings.

## Repos and authoritative prior decisions
- Core main at design audit: 4d7730a5552eca1d1758e1b2f137bd5acf64950f.
- Studio main at design audit: 6bc0d715e0a66b1e770091ffdcb44cdf1a4bfca9.
- OD-1 shape model and archived outcomes: Core merged #267/#268, docs/research/od1-organ-shape-assembly-20261101/RESULTS.md.
- Existing Core revision stack: #160; unmerged Drafts #145/#159/#163/#165/#166.
- Existing private Studio CC-B1 site08 edit: merged Studio #27, pinned to unmerged Core #166 exact SHA; **do not reimplement it**.
- Studio Workspace V2 fixed slot ADR: merged Studio #34, draft preview #33. Studio #31 quality NO-GO remains.
- Core body preparation authority: src/morphoacoustics/integration/body_presets.py; passive graph only: src/morphoacoustics_graph/ (OG-3/OG-4).

## One-sentence decision
Do NOT introduce another BodyRevision engine: create a bounded, versioned five-cell shape-family capability that reconciles the existing Core exact body registry/receipt, binds to the inherited prepared physical 1D body and, *only after separately authorized Studio UI work*, produces verified immutable physical Takes in the fixed Workspace V2 slots.

## Boundary of this draft
This documentation PR does not modify Python source, physical solvers, tests, GitHub workflows, vendor contracts, old revision history, UI code, SMC, ASMR or physics quality. It does not automatically approve future code, production API, main merge or the acknowledged speaker-quality defect.

Related design tracker: https://github.com/ryonakayama234/morphoacoustics/issues/271
