# Experiment 039 / OG-2 — pre-implementation protocol (research only)

Issue: #96. Core adopted baseline: `main@8868df1188443fc4523533c6cb0bb9cd72995c32`.
Existing upstream OG-0 #90/#93, OG-1 #94 / Draft PR #95 remain **NOT ADOPTED / REVIEW PENDING**.
**This protocol is committed before any OG-2 implementation.** Values were informed by disclosed exploratory Wolfram planning on 2026-10-13; this is a prospective *implementation* gate, not an independent blind replication and not retroactive preregistration of the preliminary algebra.

## One falsifiable ability

Prepare a graph made of exactly **two separately identified, immutable, passive, rigid, uniform 1D tube organs** and exactly **one explicitly typed 2-port acoustic ideal series junction** to a backend-specific physical graph; compute the complex transfer response using the already adopted `morphoacoustics.acoustics.UniformTube`, retaining every node ID/revision, port and edge identity and the physical mapping.

**Claim if successful:** *this specific linear lossless serial topology* can be prepared reproducibly and is acoustically equivalent to the independently derived reference. This does **not** demonstrate arbitrary graphs, anatomical phonation, deformable walls, flow-driven vocal folds, intelligible speech, waveform synthesis, 3D physics, realistic radiation, or Studio UX.

H0: graph preparation does not satisfy at least one of the physical, identity, rejection or deterministic provenance gates.
H1: all locked gates pass. Any failure → `REJECT` or `INCONCLUSIVE`, no automatic production promotion.

## Immutable fixture and controls

- Acoustic variables: peak-phasor pressure `p` (Pa) and **volume velocity** `U` (m³/s), not particle velocity.
- Convention: `exp(+i ω t)`; propagation direction A inlet → A outlet → B inlet → B outlet.
- `[p_in,U_in]^T = T [p_out,U_out]^T`; `T_A @ J @ T_B`, where ideal lossless 2-port junction enforces `p_A,out=p_B,in` and `U_A,out=U_B,in`, so **J=I in p/U coordinates**. Never silently coerce mismatched interface areas into equal-area tubes.
- Air: `rho=1.21 kg/m³`, `c=343 m/s`, common medium.
- Node A: ID `organ-A`, revision `r1`, length `0.08 m`, area `0.0003 m²`.
- Node B: ID `organ-B`, revision `r1`, length `0.09 m`; equal-area control `0.0003 m²`; intervention `0.0006 m²`.
- Port IDs `organ-A.in`, `organ-A.out`, `organ-B.in`, `organ-B.out`; type `acoustic.p_u`, direction `inlet/outlet`. Junction ID `edge-AB`, law `ideal.series.p_u`, endpoints `organ-A.out` and `organ-B.in`.
- Excitation inlet `organ-A.in`; explicit terminal outlet `organ-B.out`; boundary type `matched` with the *B* characteristic impedance. A pressure-release terminal is a distinct boundary and may not be treated as matched. The transfer matrix itself is load-independent.
- Frozen frequency grid [80,200,400,733,1200,2200,4000] Hz; plane-wave lossless mathematical study only. Cross-section max effective radius `sqrt(0.0006/pi)≈0.01382 m`; cutoff applicability to real anatomy is not claimed.
- Reference characteristic impedance `Zref=rho*c/S_A`; nondimensionalizing `S=diag(1,Zref)`, compare `S T S⁻¹` to the independently prepared oracle. Do not compare the raw mixed-unit matrix against a common absolute entrywise tolerance.
- `[p,U]` complex full two-port state is observable. Optional scattering/power experiment is on an **isolated ideal area discontinuity with matched traveling-wave terminations**, not on the finite tube's pressure-release endpoint.

## Prospective quantitative pass/fail gates (fixed before implementation)

1. **Equal-area composition:** max elementwise absolute error on dimensionless complex 2×2 matrices `S(T_A @ J @ T_B)S⁻¹` versus `S T_(L_A+L_B,S_A) S⁻¹` across entire fixed grid **<= 1e-10**. Must retain two original node and one edge mappings; concatenating and discarding identities is forbidden.
2. **Independent mismatch oracle:** independently evaluated Wolfram complex 2×2 matrix values across all 7 frequencies, compared dimensionlessly **<= 1e-10**, with no Python model calls used to generate the oracle; deliberately reversed order or a fabricated non-identity junction must be rejected by this comparison.
3. **Isolated interface power:** `Z_A=rho*c/S_A`, `Z_B=rho*c/S_B`, `r=(Z_B-Z_A)/(Z_B+Z_A)=-1/3`, `t=1+r=2/3`, `R=|r|²=1/9`, `T=(Z_A/Z_B)|t|²=8/9`; maximum error for each and `R+T=1` **<= 1e-12**. These are traveling-wave matched power fractions, not finite-tube terminal radiated power.
4. **Rejection diagnostics:** invalid: unknown/disconnected/duplicated/mis-oriented/mis-typed port, missing excitation or load boundary, orphan node, repeated ID, nonfinite or nonpositive geometry/media, unknown schema or law; return `INVALID` identifying the affected port/edge/field. Explicitly well-formed 3-port passive branch (`ideal.branch3.p_u`) reaches `UNSUPPORTED` for a serial-only backend, not `INVALID` or `INFEASIBLE`. No implicit topology repairs.
5. **Scientific negative control:** substitute the deliberately false particle-velocity continuity `J_wrong=diag(1,S_A/S_B)` for true volume-velocity continuity at the area step. This must be rejected by mismatch Wolfram matrix oracle by **> 1e-3** max dimensionless elementwise difference, and the false isolated-interface reflection `r_wrong=0` must differ from the correct `-1/3`. A broken graph mapping and reversed connection also fail.
6. **Determinism and isolation:** same canonical Blueprint, exact node revisions, coupling law, backend, and physical settings → identical SHA-256 **preparation digest**. Changing B area or revision changes digest while A parameter/ID/revision and baseline Blueprint remain identical. Digest omits process environment/frequency-grid because those pertain to the separate observation/evidence digest. Frozen prepared data must not mutate when a caller reconstructs a new Blueprint.
7. **Observations and evidence:** emit raw per-frequency measured complex matrix and error, independent oracle source+JSON hashes, source `main` SHA, full provenance/backend, typed node/edge mapping, Python/NumPy versions and single-run decision; refuse stale evidence output directories. The science test suite must pass Python 3.11/3.12/3.13 + existing project regression suite and mypy. CI logs/artifacts can verify these.
8. **Audit:** independent numerical/physics review and distinct independent code/API review, both against exact PR head. Wolfram calculations do not count as independent human reviewers. Until signed off, report `PROVISIONAL_NUMERICAL_PASS / REVIEW_PENDING / NOT_ADOPTED`.

## Representation, scope and failure taxonomy

Research-only file(s) under `experiments/039_og2_prepared_graph/`; tests in `tests/test_experiment_039_og2.py`; optional dedicated workflow. Do not edit `src/`, `CreatureSpec`, `PreparedMorphology`, v0 contracts or Studio. `PreparedPhysicalGraph` is an experiment-local name, not public API.

Validation order: schema and IDs → physical units and typed port references → endpoints/orientations/degree and required boundaries → solver topology capability → deterministic preparation. Reject any valid but unsupported graph with `UNSUPPORTED`, malformed graph with `INVALID`. `INFEASIBLE` is reserved for realizable task-to-body constraints and is not a substitute for these two categories.

## Decision

Accept only a **limited research finding** after all machine gates and human review; otherwise document `INCONCLUSIVE` or `REJECT`. Do not merge this Draft automatically, do not assert verified human voice, and do not block existing independent Studio preset-selection track Core #72 → Studio #14.
