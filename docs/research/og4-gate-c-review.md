# OG-4 Gate C review and limited integration scope

**Review date:** 2026-10-16 JST. **PR:** [#108](https://github.com/ryonakayama234/morphoacoustics/pull/108).
**Reviewed starting HEAD:** `43fb39bebaec7a818f64d1b5afc8f3d0ad4a4583`.
The final Gate C receipt in that PR must bind the corrected exact HEAD, successful
CI runs and inspected raw artifact. Until that receipt, the decision is
`INCONCLUSIVE / CORRECTED_HEAD_VERIFICATION_PENDING`; this document alone does
not adopt or merge the implementation. The permitted passing decision is
`GO_LIMITED_CORE_FIXED_3PORT`, within the scope below.

## Critical pass 1: physics and numerics

The fixed 12-complex-state equations correctly use peak phasors `exp(+i omega t)`,
`Z=rho*c/area`, identical junction pressure and signed **volume flow** conservation
`U_A.out=U_B.in+U_C.in`. Terminal matched impedance comes from its own tube;
the fixed C load stays 1372000 Pa s/m³ when C area changes. Six oriented powers
are `.5 Re(p conj(U))`. The fixed matrix and normalizations match Amendment A1.
No runtime experiment import, damping, clipping or least-squares rescue was found.

A newly executed Wolfram computation in this review independently constructed
positive-admittance scattering and the finite tube equations. Weighted energy and
reciprocity residual matrices are exactly zero; the declared 2143.75 Hz singular
fixture has rank 11 and nullity 1. As an additional finite-length check, ratio 2,
closed C, 733 Hz gives `p_A.in=-0.06681441784882724934 + 1.23390186464997856219i`
Pa and `p_C.out=0.65065052081557297797 - 0.89276969890497246002i` Pa.
These are mathematical checks of the ideal model, not biological measurements.

**Acceptance gap corrected:** the original singular test only checked a condition
number; it never exercised numerical refusal. New fault-injection tests call the
actual response path with one valid earlier frequency and then a singular system,
solve exception, nonfinite state, excessive backward residual or physical defect.
Each must raise the specified `NUMERICALLY_UNRESOLVED` at index 1, without hashing
or returning a partial observation. The singular input is test-only; the public
frequency/geometry capability remains unchanged.

Local scattering acceptance now solves a separate 4-unknown pressure/flow system
for all three incident bases, compares all 27 coefficients against the unchanged
Wolfram rational matrices, checks mixed complex incidence, and measures the wrong
particle-velocity law's power defect (8/9 at C area ratio 2; zero at equal area).
The previous energy check on an internally constructed formula alone did not
provide that coefficient-to-oracle comparison.

## Critical pass 2: code, API and evidence

| Finding | Severity | Reproducer and correction |
| --- | --- | --- |
| Structural error precedence differed from the frozen API | P2 | Duplicate organ and junction IDs reported `/organs` instead of `/junctions`; duplicate loads plus boolean source scale reported `/source/scale` instead of `/loads`. Collect independent field/relation failures before choosing the smallest pointer, suppressing dependent cascades. |
| Malformed snapshot envelope could be classified as unsupported | P2 | Unknown backend plus list-valued blueprint returned `UNSUPPORTED`; validate all envelope types/keys/hash spellings first and return `INVALID:SNAPSHOT_STRUCTURE:/blueprint`. |
| Error paths were not valid JSON Pointers for unknown keys | P2 | `a/b~c` was emitted literally; escape tokens as `a~1b~0c` in blueprint and snapshot envelopes. |
| Forged prepared JSON could leak RecursionError | P2 | A deeply nested forged `_blueprint_json` bypassed the typed binding failure; contain parser recursion errors as `PREPARED_BINDING_MISMATCH`. |
| Numerical and scattering acceptance paths were incomplete | P2 | Add the actual refusal/atomicity controls and independently solved coefficient comparison described above. |
| Archived observation hashes could not be recomputed from the artifact | P2 | Earlier case rows omitted full request grids, snapshots and much of each hashed observation. Evidence v2 archives all 60 full request/snapshot/observation records and verifies every identity and case-to-observation binding before writing. Tampered input/output/request/case controls must fail. |

The evidence manifest additionally records the runner, graph modules, API/golden/
Wolfram documents, workflow, tests and dependency definition hashes, as well as
CI run/attempt context. It refuses an imported backend outside the checked-out
source. Physical identities and tolerance thresholds are unchanged; only the
separate **evidence** format advances to v2. Original comparators remain pinned.

The four living architecture/data/plan/ledger documents are updated together.
Escaped Markdown fences in the original PR additions are repaired so their system
and data diagrams render. Existing OG-3, legacy source inventory, Experiment038/
039 oracle, performance contracts and Studio changes are outside this PR.

## Decision boundary and provenance

The final receipt must link fresh corrected-HEAD Python 3.11/3.12/3.13 and mypy,
OG-3 preservation, dedicated OG-4 CI, dual identical v2 evidence with SHA sidecars,
all 288 Python and separately 24 frozen Wolfram comparisons, three wrong-law
controls, frozen Experiment028/029 decisions, and two real X2a physical Takes.
Wrong-HEAD and stale-output refusal must pass. Prior green runs do not attest the
corrected implementation. Machine evidence retains a non-adoption decision;
Gate C is a separate explicit technical judgment.

**Reviewer independence:** the two critical scopes above are sequential AI audits
in one review conversation with shared context; the reviewer also authored these
fixes. Wolfram was independently executed, but no independent human or empirical
review is claimed. The earlier separate Codex review request was blocked by usage
limits and is not counted as an approval. Parent #106 requires a distinct Codex
review **if available**; its unavailability is disclosed rather than hidden.

The possible GO covers only the exact fixed three-tube, one ideal passive junction,
eight frequencies, three areas/scales and four C loads in the normative
[API](./og4-branch3-api-v1.md). It grants no general graph, vocal anatomy, motion,
new speech/WAV or Studio interoperability claim. Realistic radiation/losses,
moving geometry and physical source coupling require later separately falsifiable
gates. Merge itself remains a separate action; use a freshly verified SHA guard.
