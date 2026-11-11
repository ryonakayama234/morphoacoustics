# EL-RP1 — INDEX / navigation and claim limits

2026-11-04 JST | Issue #281 | **D0 preregistration, NOT numerical evidence** | INDEPENDENT DRAFT / NOT ADOPTED.

## Research question
When can a pressure-only acoustic measurement be used for reference-plane-consistent, counterfactual receiver-load calculations? Explicitly distinguish data parsing, observational usability, port identifiability, numerical computation, measured generalization, rights, and production adoption.

## Read order
1. [SYSTEM](SYSTEM.md) — physical system, isolation, model ownership and coupling invariants.
2. [DATA](DATA.md) — evidence union, observable quantities, reference planes, declared physical and rights conditions.
3. [HYPOTHESES](HYPOTHESES.md) — H1–H5, analytic nonidentifiability counterexample and falsification.
4. [EXPERIMENT](EXPERIMENT.md) — **FROZEN BEFORE NEW EVALUATOR CODE**: fixtures, oracle, tolerances, negative cases, predeclared gates.
5. [RESULTS](RESULTS.md) — append-only actual observations (initially NOT RUN).
6. [FAILURE_LOG](FAILURE_LOG.md) — append-only anomalies/negative findings.
7. [DECISIONS](DECISIONS.md) — authorization, state transitions and evidence thresholds.
8. [REFERENCES](REFERENCES.md) — predecessor research and limitations.

## Ownership & evidence integrity
- Core `UniformTube` owns the existing linear 1D acoustic transfer law; RP1 is a research-only qualification boundary and a prospective adapter, never a copied production physics engine.
- `asmr/` remains a metadata-only adopted workspace; no runtime adoption and no Studio import.
- Earlier 18-point Wolfram oracle [PR #158] and 24-point independent reference [PR #275] remain on their original frozen branches. Do not silently rewrite/copy and relabel them as new human measurements.
- NF5 original measurements are NOT RP1 test truth. Do not open sealed original `Data.IR`/`Data.Delay`.
- This D0 commit must be recorded by SHA before Gate A implementation, and its files kept byte-exact for the initial gate. Corrections use a separate, dated addendum.
- A numerical PASS is not a physiological, perceptual or commercial-use PASS.
