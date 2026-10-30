# Resource-respecting Gate A successor: SOLO / zero-cost route

**2026-10-30 JST / creator constraint / decision change.**
People available: one researcher/creator. External annotators: zero. Budget: zero. The creator can do narrowly scoped Japanese-reading annotations locally if supplied with a usable workflow. **No paid hiring, paid APIs or unjustified procurement expectations.**

## Governance decision
Stop using independent A/B/C and 120+880 as a mandatory resource acquisition **for software research and development**. Do not require the creator to annotate 1,000 utterances. Keep the originally preregistered #244/#247 120+880, double-blind and H1–H6 success thresholds **unchanged as an unfulfilled independent-science lane**, not an immediate action item. We do NOT rewrite H1–H4 thresholds or call one-person work independent evidence. Distinguish:
- A-SOLO (possible now): personal writing/reading examples, notation policy development, bounded errors, UI operability, candidate-generation/ranking engineering, fail-closed security and exact provenance; evidence tier SOLO_DEVELOPMENT_ONLY.
- A-PUBLIC (possible under source terms): frozen exact public external data for descriptive tests and exploratory comparisons, source rights, contamination and target-level vs whole-path limits disclosed; evidence tier EXTERNAL_PUBLISHED_REFERENCE, NOT INDEPENDENT_PRIVATE_GOLD and not silently as original #244 Gate C.
- A-INDEPENDENT (not available now): 120 pilot + 880 separate holdout with real two blind annotators + third adjudicator and full-utterance multi-gold; remain MORE_DATA, not a project-wide ban on engineering.
- H5/H6 formal/software and source-span tests can proceed independently; no L2 physical or L3 audio claims from language proposals.

## Software and solo annotation workflow
The research subtree now contains a self-contained static HTML workbench and three toy examples:
- packages/speech-motor-compiler/research/solo_workbench/index.html
- packages/speech-motor-compiler/research/solo_workbench/sample_cases.json
- packages/speech-motor-compiler/research/solo_workbench/README.md
The creator uses WSL2 Python 3 standard-library localhost static server and Windows browser; no CDN/API, no subscription, no server-side storage. Original text + context, target orthography, declared origin, status SINGLE/MULTI/UNKNOWN/CONTEXT_INSUFFICIENT, full-sentence katakana path(s), reasoning and timestamp. JSON import/export; autosave browser-local. No independent gold, no old manifest pass; no source alignment certification, TaskLexicon synthesis or Core/UI integration. No PR of private creator script; examples are original synthetic fixtures and are not a sample of human gold.

## Minimal user work
- Stage 0: import three original unannotated examples to learn the interface (not scored).
- Stage 1: create **5** personal examples and annotate before model output is viewed. This is the sufficient initial user handoff. Extra work optional: up to 20 illustrative cases with heteronyms and ordinary/OOV/ambiguity; no requirement of 120 or 880.
- Stage 2: export a private JSON and store original immutable copy; later prediction comparisons happen on a separate derived copy. No grading by repeating model output as truth. The developer can create a report from creator-permitted or redacted derived aggregate later, but should not obtain private script by default.
- Stage 3: iteratively improve language candidate and failure/error UX using solo cases. Record descriptive manual failure examples, no confidence intervals/independent science claim.

## Quality bounds and defensible experiment claims
Original 2026-10-29 frozen hypotheses retained for future qualified data and reviewed under #244. For now only language behavior on a **self-curated convenience set** and software regression can be reported; do not perform the original 100-family cluster bootstrap from a tiny sample or estimate population reading accuracy. Public Joyo and Parakeet data could provide external publisher-annotated observations with versioned rights/contamination caveats, without pretending new independent annotation. A creator's single reading may be wrong or ambiguous; preserve UNKNOWN rather than force one answer.
No human recruitment / payment requirement. No question to the user beyond one actionable small annotation assignment.

## Current verdict
**GO_SOLO_DEVELOPMENT_ENVIRONMENT (subject to exact-head CI and manual browser acceptance)**, **MORE_DATA_L1_INDEPENDENT_GOLD**, and **NOT_RUN_LINGUISTIC_H1_H4**. Software implementation of contextual C may be planned separately as an EXPERIMENTAL_SUCCESSOR after this development environment, with no unauthorized upgrade of C0 or main merge.

References: owner #244, C1 #247, Gate A Draft #253, existing SMC7_L1R_GATE_A_PROTOCOL.md; source-rights matrix, annotation manual, Joyo discrepancy audit under this folder.
