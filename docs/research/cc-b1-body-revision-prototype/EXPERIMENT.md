# EXPERIMENT — BodyRevision preparation prototype evidence ledger

**Status on creation: IMPLEMENTED CANDIDATE / CI AND INDEPENDENT AUDIT PENDING / NO SCIENCE OR CREATOR ADOPTION.**
No human audition, new physical waveform, human-like voice or Studio session is claimed by this branch.

## Falsifiable software hypothesis (H-PREP)
Given an authenticated immutable parent, a correctly bounded single-section rest area edit deterministically derives exactly one immutable Core prepared body with a different preparation digest, without mutating the parent or accepting forbidden geometry. Wrong/unsupported requests must never yield a replacement body.

Primary reproducible command from repo root: `python -m pytest -v tests/test_cc_b1_revision.py tests/test_preparation.py tests/test_body_presets.py`. Full mypy/pytest and existing CC-A2 dedicated CI are independent regression requirements for any adoption.

## Negative controls and observables
| Experiment / guard | Expected | Status on entry |
| --- | --- | --- |
| Exact re-execution (identical baseline and edit) | same revision ID, same prepared digest | test authored, awaiting CI |
| Change a different site | distinct revision identity, exactly one SI area diff | test authored, awaiting CI |
| Parent remains unchanged | byte/structural identity, original digest | test authored, awaiting CI |
| NaN, Inf, <=0, bool, wrong index, no-op | INVALID / no BodyRevision | test authored, awaiting CI |
| Wrong parent ID/revision/digest or tampered base content | REVISION_MISMATCH or INVALID / no BodyRevision | test authored, awaiting CI |
| Unsupported length, graph, >±10% change | UNSUPPORTED / no BodyRevision | test authored, awaiting CI |
| Historical v0/v1/CC-A2 | no contract/solver edits; regression suite must pass | pending exact-head run |
| Human discriminability / voice-likeness / generalization | separate blinded tests | NOT TESTED |

## Independent Wolfram algebra check (NOT this API's physical validation)
A simplified two-equal-section lossless duct with L=0.08m each, c=343m/s, A1=3e-4m², pressure release and A2={1.5e-4,3e-4,6e-4}m² has
`f1 = c/(2*pi*L) * ArcTan[Sqrt[A2/A1]]` →
419.9890854578, 535.9375, 651.8859145422 Hz (Wolfram evaluator independently rerun 2026-10-21).
This supports only an analytical rest-shape→resonance sensitivity sanity check; it does **not** certify the current 16-section time-varying simulator or auditory discrimination.

## Next *prospective* physics and UX Gate (not performed)
After independent Gate A ratification: freeze chosen site, source/gesture identity, raw Pa quantization, 16-tube transfer-matrix oracle, numerical tolerances and adversarial controls **before** confirmatory runs. Separate pre-registered randomized ABX with positive/null controls and blind/unblind ledger from acoustic physics Gate. Preserve exact source SHA/CI URLs, failures and abstentions. Stop on missing independent review or scientific discrepancy; never call exploratory post-hoc site selection a confirmatory discovery.

## Audit decision
Current default: **HOLD / experimental branch only**. Reviewer must check API trust boundary, deterministic canonicalization, float edge cases, frozen CC-A2 regression and quality claims. Release requires separately evidenced `GO_LIMITED` and cross-repo adapter/UI acceptance.

## Actual CI observation and corrective action (2026-10-21)
The first experimental HEAD `43e703093bc2157b4e0eded52e8747e53348b6d1` passed the **dedicated BodyRevision candidate checks**, but its general suite and SV1/OG4 gates failed: a new file under `src/morphoacoustics/preparation` violated the frozen package file-inventory invariant (`audited package source inventory changed`). This was a genuine integration regression, not an ordinary solver failure. We preserved the guard and moved the candidate to `tools/cc_b1_revision.py`. **All results on that superseded HEAD remain failed historical receipts; exact-head rerun is mandatory.**

### Dedicated typecheck correction (2026-10-21)
After isolating the research tool, the first dedicated test job passed pytest but direct `mypy tools/cc_b1_revision.py` found only `import-untyped` because its editable imported Core package has no installed `py.typed` marker. Instead of modifying published package metadata, CI now resolves local source with `MYPYPATH=src` for the research tool. The earlier failed workflow is preserved; a new exact-head pass is required.\n
### Boundary precision negative/positive control
The ±10% inclusive envelope can land one IEEE-754 ULP beyond the mathematical endpoint when the client multiplies the old area. A near-machine-epsilon check was added for endpoints only; materially out-of-range ratios remain rejected. Explicit ±10% regression cases are now included. The tolerance is an implementation convention, not a physically calibrated acceptance envelope.
