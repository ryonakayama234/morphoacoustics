# SMC-4 Gate B — preimplementation protocol

Date: 2026-10-24 JST. Status: FROZEN_BEFORE_IMPLEMENTATION. Owner issue: #179. Gate A GO_DESIGN_ONLY at 9f7a8d10ca7a524a1b47496a8c4807ce40a82165.

Normative specifications: SMC4_GATE_A_PROTOCOL.md and independent Amendments 01, 02, 03. Synthetic symbolic research only; no pronunciation accuracy, physical feasibility or audio claim; no merge to main.

Research question: Can a finite versioned lexicon transform one explicitly selected complete pronunciation path into a deterministic, fail-closed SMC-3 many-to-many task graph? Preserve source and selected-path provenance, separate mapping receipt, required additive slots and exclusive alternatives, context UNKNOWN, explicit sharing compatibility, exact rational coordination, and unsupported scope diagnostics.

Fixture IDs F01–F32 and F12a/b/c are defined by the three preregistered Gate A amendments, and are normative in full. F01 2 units/3 shared tasks/4 links; F02 no-sharing 4 tasks; F12a concurrent disjoint goals rejection; F16 alternative pronunciation paths; F18 unknown context must not become false; F20 overlapping compatible shared targets; F21 incompatible share failure; F23 required additive slots; F24 exclusive candidates; F28 unsupported multi-unit recipe; F32 missing one-unit recipe. The remaining F-cases are also mandatory test targets, not implicitly passed.

Execution order: (1) freeze this document, (2) test-first independent fixtures and preserve initial red evidence, (3) implement code in separate commit, (4) exact-HEAD CI Python 3.11/3.12/3.13 and mypy, (5) fresh manual @codex review and documented findings, (6) explicit GO_LIMITED_SYMBOLIC/REVISE/MORE_DATA/REJECT verdict. Keep original SMC-3 IR, Core and Studio untouched. Reviewer is AI code auditor, not scientific peer reviewer.
