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

### Full-matrix import regression and independent Wolfram site check (2026-10-21)

Exact prior HEAD `11aa03807aa2439ab82059635cd6cff33d79a336`: candidate dedicated pytest/mypy **PASS**, adopted SV1/OG3/OG4 **PASS**, but default `pytest` invoked as the console entry point on Python 3.12 could not import namespace `tools` from the checkout (`ModuleNotFoundError`); therefore general CI **FAIL**. Tests now use the same explicit checkout-path `runpy.run_path` pattern as the adopted CC-A2 research tests. A new exact-head full matrix must pass.

**Independent 16-tube Wolfram numerical corroboration:** Constructed a *different* outlet-to-inlet acoustic-impedance recurrence rather than reusing the existing PR #144 2×2 ABCD matrix multiplication. For 16×10mm ducts, identical shared terminal gestural log-area field and 5Hz search grid, independent evaluator produced baseline F2=2100Hz and sections (zero-based) **0: 2110 vs 2095 Hz (15Hz span); 2: 2130 vs 2075Hz (55Hz); 4: 2065 vs 2130Hz (65Hz)** at -10% and +10% rest area. This reproduces PR #144's *post-hoc ideal-model scan* with an algebraically equivalent but independently coded impedance recurrence. It is **not** a confirmatory holdout, not new physical pressure/WAV, and not a human ABX result.

Runnable independent ideal-model reference for the site-0/2/4 checks: [wolfram_site_recurrence.wl](wolfram_site_recurrence.wl) and the [result JSON](wolfram_site_recurrence_result.json). Source and result are a paired immutable evidence record in this research PR; none of its values are perceptual or prospective acceptance thresholds.


## New Gate C versioned performer experiment candidate (2026-10-22)
Hypothesis H-C1: exact CC-A2 M0 + site08 ×0.90/1.10 returns a new immutable `BodyRevision`, physically recalculates baseline and edited raw Pa with the identical fixed LF+three-task and actual 102 acoustic calls **per body**, matches adopted baseline quantized SHA and Gate B site08 edited quantized SHA, and atomically archives complete verifiable candidate evidence. Numerical sound differences need not be discernible by a listener. Old versions/aliases and out-of-scope edits must reject with no false success.
Tests: strict schema/unknown-field and bool rejection; wrong parent digest; unsupported site & ratios; NaN/Inf preview guard, playback clipping; corrupted source/solver or unexpected feasibility failure must not publish success; real two-pair physical output and independent artifact hash/WAV/NPY trace readback; old CC-A2 and broader body regressions. Dedicated `cc-b1-gate-c-versioned-limited-performer` Actions workflow. **Do not mark this Gate C CANDIDATE as adoption until exact-head CI inspected and code/security audit completed.**
Further requirements not supplied by this PR: true Studio reload/persistence, automated full trust-boundary fault injection, package distribution strategy under frozen inventory, role/capability registry, app-level cross-repo version negotiations, user creator trial, and main merge.

## Gate C candidate post-publication negative tests
For both audited ratios, CI now additionally reloads the saved `result.json` and all six physical outputs through Core's own `verify_output_archive` before acceptance. It then flips WAV bytes and confirms `ARTIFACT_HASH_MISMATCH`, plus an incomplete directory without a completion marker is refused. This does not substitute an untrusted-store security audit or future Studio restart/reload browser E2E. Stacked candidate remains DRAFT, not adopted.
