# CVI-1 — FROZEN prospective Gate B1/B2 protocol v1.1 (review correction)

2026-10-28 JST. Core #223 / #227, predecessor SMC5/6 preflight Draft #226, parent design Draft #224. **Review-corrected v1.1 frozen before B1/B2 implementation or any new B data.** A frozen protocol is NOT execution approval, physics validation, independent review or a claim that the accepted SMC5 source supports model anatomy.

**Decision:** choose **model-geometric task measurand first; audit minimum realization with it**, not a new H_EXEC controller first. B1/B2 only; **B3 SMC model-semantic binding and C dynamic controller are expressly excluded**. This pilot replicates an existing *known* Exp019 10-section model, not an independent discovery or a holdout. No Studio UI or public ABI change. No main merge.


## Review-driven v1.1 correction — explicit upstream boundary (2026-10-28)

This is a **prospective revision** of [v1 at commit `84cb8ce2925f9ac8ec3d9210cfa7c1a82a9d0fde`](https://github.com/ryonakayama234/morphoacoustics/blob/84cb8ce2925f9ac8ec3d9210cfa7c1a82a9d0fde/docs/research/cvi1-body-motor-identity/GATE_B1_B2_PROTOCOL_V1.md), not a retroactive claim that v1 covered these cases. GitHub [Codex P2 mismatch guard](https://github.com/ryonakayama234/morphoacoustics/pull/235#discussion_r4397757767) and [Codex P2 constructor outcome](https://github.com/ryonakayama234/morphoacoustics/pull/235#discussion_r4397757776) correctly identified missing execution rules. **No B1/B2 code/results exist at this revision**, so the numerical thresholds, target, source commits and known Exp019 replication predictions remain **unchanged**; only the guard ownership and negative-case outcome contract are repaired. The authoritative machine fixture is `gate_b1_b2_fixture_v1_1.json`. Original v1 files and Git history are retained with a superseded notice, not deleted. This v1.1 still needs independent review.

### Layer 0: constructing domain objects is not executing Core

Validate inputs through the *real pinned constructors* without suppressing exceptions. The following outcomes are preregistered:

| Negative case | Expected phase | Expected outcome | Core reached? |
| --- | --- | --- | --- |
| N02 NaN/Inf TaskParameter value | `CONSTRUCT_PARAMETER` | native Python `ValueError("parameter value must be finite")`, **`CONSTRUCTOR_REJECTED`** | NO |
| N02 finite zero/negative `target_area` | `CORE_REALIZER` | real Core `INVALID` / `NONPOSITIVE_TARGET_AREA`, **`CORE_FEASIBILITY_REJECTED`** | YES |
| N02 wrong literal unit `mm2` | `CORE_REALIZER` | real Core `INVALID` / `UNSUPPORTED_TARGET_AREA_UNIT` | YES |
| N03 positive `target_area>A_rest` | `CORE_REALIZER` | real Core `INVALID` / `TARGET_AREA_NOT_CONSTRICTIVE` | YES |
| N04 unreachable ξ=0.95 | `CORE_REALIZER` | real Core `INFEASIBLE` / `LOCATION_UNREACHABLE` | YES |
| N12 nonpositive/nonfinite or wrong-length `ReducedMaterialProfile` | `CONSTRUCT_PROFILE` | native Python `ValueError`, **`CONSTRUCTOR_REJECTED`** | NO |
| N12 two valid simultaneous `CONSTRICT` goals | `CORE_REALIZER` | Exp019 R1 `UNSUPPORTED` / `REDUCED_MATERIAL_SINGLE_CONSTRICT_ONLY` | YES |
| N06 body identity altered with valid 10 sections | `HARNESS_PREFLIGHT` | `HARNESS_REJECTED / HARNESS_PREPARED_BODY_MISMATCH` | NO |
| N06 incorrect backend id | `HARNESS_PREFLIGHT` | `HARNESS_REJECTED / HARNESS_BACKEND_MISMATCH` | NO |
| N07 16-section prepared geometry, 10-section model | `HARNESS_PREFLIGHT` | `HARNESS_REJECTED / HARNESS_SECTION_MODEL_MISMATCH` | NO |

When a constructor raises, **no `RealizationResult` exists**. The row records the original exception class, raw message and phase; `native_feasibility=null`, `core_result_exists=false`, `core_state_present=null` (not a fake `state=None` returned by Core), `did_call_core=false`. Do not coerce exceptions to a synthetic `FeasibilityReport`. An unexpected `IndexError` inside R1 is **`UNEXPECTED_FAILURE`**, never a passing refusal.

### Layer 1: experiment-local prepared-body and representation guard

The *current* Core native `Tract1DRealizer` does **not** enforce this experiment's prepared-body hash or 10-section R1 compatibility. In particular, R0 may return `FEASIBLE` for a 16-section geometry, while the existing 10-ratio R1 implementation can index past its input and raise `IndexError`. Neither is evidence that a native Core 10↔16 check exists. This study SHALL place a **research-harness** guard **before** invoking either R0 or R1, not in production Core and not after the result.

1. **Representation compatibility first.** Require actual `Tract1DGeometry` and exactly 10 ordered finite positive sections; check the selected R1 material vector has exactly 10 positive finite values and model `SECTION_COUNT==10`. A 16-section case is `HARNESS_SECTION_MODEL_MISMATCH`, and neither R0 nor R1 runs.
2. **Backend identity second.** Require `PreparedMorphology.backend_id=="fidelity0.tract1d"`. A wrong ID is `HARNESS_BACKEND_MISMATCH` without invoking Core.
3. **Prepared-body identity third.** Extract an explicit typed canonical payload from *actual* `PreparedMorphology`: backend ID, CreatureSpec name/cavities/connections/source_organs/articulators with reachable intervals, the `Tract1DGeometry` cavity and ordered section lengths/areas, and `PreparationProvenance` source/model/notes. Compare exact fields against the pinned `prepared_body_contract` in v1.1 JSON, then compute `SHA256(UTF-8 Python json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False))`. Require equality with preregistered digest **`211740f581d685b78807ef0f2fcd1b67640add15731921924eee29bcb9bf532f`**; otherwise `HARNESS_PREPARED_BODY_MISMATCH`. This is a research fixture hash, **not a Core-provided immutable body-revision identifier**. Freeze the extraction key set; do not include the requested target, UI labels, controller output or other non-body state. Mismatched length or one area in an otherwise 10-section body is an identity failure, not a 16-section failure.
4. **Dispatch last.** Construction success and all guards above are required before calling `realize_snapshot` or reading any model state. Instrument a harness-spy/counter to prove **both R0 and R1 call counts are zero** on N06/N07 and no geometry/audio artifacts are emitted. Perform positive control: same expected prepared body passes guard and reaches **both** realizers. Native validity/capability/reachability checks happen *after* this harness gate. Negative cases must match the specified stage/code, not just “any exception”.

This guard validates the selected research **fixture**, not all legitimate species or an anatomical landmark. When valid bodies or section layouts are intentionally changed in later experiments, preregister a **different fixture+expected digest**, don't disable the gate to get a pass. A changed model-section count also requires a separately reviewed realizer/observer mapping.

### Layer 2: typed refusal/attempt artifact (constructor ≠ harness ≠ Core)

Use the exact `rejection_record_contract` from v1.1 JSON. Every attempted **rejection/exception** produces a *harness-owned* refusal record `{case_id, phase, outcome_kind, harness_code?, native_feasibility?, exception?, did_call_core, core_result_exists, core_state_present?, did_invoke_acoustics, did_emit_take, source_input_ref}`. Only if an actual Core `RealizationResult` exists may `native_feasibility` be `INVALID/UNSUPPORTED/INFEASIBLE` and `core_state_present` be a boolean. For constructor or harness rejection both are null; the original exception must be present for constructor failures, and `harness_code` only for harness rejections. Any missing attempted-case record, unexpected exception, contradictory phase or unaudited fallback is a **STOP**, not a PASS.

The `refusals.json` file contains **only rejected or unexpectedly failed attempts**, including constructor and preflight failures. Valid N01 and successful negative-control comparisons belong in `observations.csv` and the full N01–N14 inventory in `manifest.json`, never represented as a refusal. No real-valued `A_j` or zero physical residual may be imputed for failed cases. Keep native `INVALID → UNSUPPORTED → INFEASIBLE` ordering only *inside* real Core validation; do not claim it for constructors or the harness. Pin **source and case expectations** with the v1.1 machine-readable fixture and verify them before new simulation code.

**Review gate:** These are a design correction to a known limitation, not implementation of the proposed guard. No B1/B2 data, 16-section transfer, SMC model TaskDefinition or sound is newly demonstrated here.


## Immutable evidence inventory (source SHA vs candidate research data)

- Main baseline commit `f1020c568c54615bc9fdc4c9804128ddbcc3ff0d`. Resolve dependencies only at this exact source, not "latest main."
- Core geometric observer `src/morphoacoustics/physical/tract1d.py` blob `62f3ddf6d3cbf2e43072f9d8b2be6ee84f4c3ca7`. Core request validator/R0 hard projector `src/morphoacoustics/realization/tract1d.py` blob `87adb91ebe3ca2a3e2b36931f9d12d94c2ee7e0b`. Prepared-body backend naming: `src/morphoacoustics/preparation/tract1d.py` blob `90860b19a6b181ba88ff3d4a01379c10ab23e226`, constant `TRACT1D_BACKEND_ID = "fidelity0.tract1d"`.
- Exp019 existing experiment-local R1, fixture and solver `experiments/019_material_conditioned_realization/run.py` blob `b11319645569a297695644651a0813154cf67ad3`.
- Independent **mathematical** Wolfram reference `experiments/019_material_conditioned_realization/wolfram/material_realization_oracle.json` blob `122440385fc4c7d7e5180153492de27081da0779`.
- Exp019 documented [result](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/019_material_conditioned_realization/RESULTS.md) including historical observed target and state errors; Exp020/022 historical finite-time/shared-body research is **not** grafted into this pilot.
- Historical SMC preflight receipt (no bodily task capability): 3 authentic synthetic TaskGoals, 6 exact timestamps, 0/3 physical mappings, `UNMAPPED_SEMANTICS`. SMC5 + SMC6 only exist in unmerged research stack; original source candidate and timing cannot be relabelled as this pilot.
- This protocol's companion machine-readable `gate_b1_b2_fixture_v1_1.json` is authoritative for fixed quantities; drift against it is `INVALID_PROTOCOL`.

## B0 must pass *before* B1/B2 execution: independent review debt

1. Draft #226 Codex review at `ef151632` found A09 no-physics boundary unproven: prior tests checked receipt attributes but not imported physics code or side-effects. Add source scanner + actual adapter **and CLI** execution under controlled no-write/no-physics instrumentation, prove guard detects an injected write/import, test bad raw input; matrix CI 3.11/3.12/3.13 and exact-HEAD independent review. Preserve historical red-to-green and 0/3 semantic facts.
2. **Review must be assessed at exact new HEAD.** At PR #226 `35ee6c8`, independent Codex review completed with `has_any_findings=false` and `has_unresolved_findings=false` (review report), while the original historical inline thread can separately retain `is_resolved=false`; distinguish those administrative fields. The original finding has a documented repair and review, not a new physics validation. Do not infer either outcome merely from a pytest green badge.
3. Reproducible root CI must be separately characterized. Pre-existing `pytest.approx` nested-sequence failure seen at #224 old base is not a physical result; main source `f1020c` has corrected scalar assertion. This pilot's source pin excludes accidental mixing with unmerged SMC branches.

If a fresh B0 substantive technical finding is unresolved, verdict `BLOCKED_REVIEW_INTEGRITY`, no B1/B2 scientific result or claim. An old historical thread's administrative resolved flag is separately recorded and is not silently misreported. B1/B2 execution still requires v1.1 independent preregistration review, and is `NOT_RUN` in this PR.

## B1 scientific question, task and actual observer

**Target model-only quantity:** prepared body B's returned *modeled* 1D serial-tube section area,
`g_B(x)=A_{j_B(xi)}(x)` [m²].
- `xi` is dimensionless axial fraction from inlet/source =0 to outlet/radiation =1, resolved from **that prepared body**; `s=xi L` [m].
- `j_B` is a zero-based discretization index using Core's half-open intervals (last section includes outlet endpoint), not a universal tissue/articulator identity.
- **Actual measurand** is `returned_state.sections[j].area_m2`, independently extracted from the returned R0/R1 state; echoing the target constant, a source file's requested area, or an acoustic peak is *not* observation. If state is absent, `NOT_MEASURABLE`, no zero imputation.
- Candidate task is only a constrained *cross-sectional area model* at one section. No tongue/lip surfaces, closure contact, muscle law, 3D airway mapping, phonetics or acoustic sound.
- Use one body only: equal-length **10** sections, total length 0.17 m, each 0.017 m; rest `A_rest,j =3.0e-4 m²`, cavity `oral`; creature articulator reachable interval [0.30,0.80] of xi. Fixed test location `xi=0.65`, `s=0.1105 m`, **j=6**, section range [0.102,0.119) m, interior section boundary margin 0.0085 m. Fixed target `A*=5e-5 m²`, ratio `rho=1/6`; valid narrow CONSTRICT if 0 < A* ≤ A_rest,j.
- The fixture's gesture interval `[0,0.3) s` and observer snapshot `t=0.1 s` are experiment-scoped. They are not an SMC-selected performance, physical task activation time or measured onset.

**Primary B1 measurements**: body/geometry/hash, mapping xi→s→j, original rest and observed area with SI m², signed error `r=A_observed-A*` [m²], absolute error, full 10-element actual area vector. Secondary: modeled volume `V=sum_k (A_k * length_k)` [m³], adjacent areas [m²], all 10 positive and finite; *volume not conserved by this fixture* unless the model explicitly enforces it, so record change without a conservation claim.

## B2 causal model comparison with declared limit

**R0**: production Fidelity-0 direct area projector at the requested section. It is an intentionally kinematic null. A stiffness-label-only perturbation must yield identical **full 10-dimensional modeled areas**; don't count R0's zero target residual as actuator behavior.

**R1**: experiment-local Exp019 reduced quasi-static **dimensionless** constrained quadratic in ratios `q_k=A_k/A_rest,k`:
- `K=diag(k_i)` positive relative stiffness with base all k=1; intervention changes **k_5 from 1 to 4**, all else unchanged; smoothness λ=1, D is (N−1)×N first-difference, `H=K+λ DᵀD`, `c=e_6`, `rho=1/6`.
- R1 solves `min 0.5(q−1)ᵀK(q−1) + 0.5 λ ||Dq||²`, subject to `cᵀq=rho`, using Exp019's existing KKT implementation and R0's native request/feasibility validation. **No new constrained-positive solver** may be silently added. If unconstrained optimum has a nonpositive q component, existing UNSUPPORTED response wins; no clipping.
- Check with two independent *mathematical* references: (i) the pinned pre-existing Wolfram reference values, (ii) distinct rank-one formula `q=1+H⁻¹c*(rho−1)/(cᵀH⁻¹c)`. Evaluate primal target equality `|q_6-rho|`, KKT stationarity infinity norm `||Hq-K1+mu*c||∞`, `mu=(1-rho)/(cᵀH⁻¹c)`, min eigenvalue(H)>0 and condition number(H). The analytic and Wolfram references verify the **same simplified model**, not real tissue mechanics or SI force/work.
- For both R1 profiles, report actual measured `A_j`, target residual m², all positive sections, `q_5` and `q_7` neighbors, max-norm difference vs oracle, and `||q_changed-q_base||_2`. Preserve full state and same task request source/hash.

### Frozen thresholds (historical model replication, not novel hypothesis discovery)

| Check | Predetermined numerical acceptance |
| --- | --- |
| B1 xi→s and section edges, interior | `|s-0.1105|<=1e-12 m` and j==6; interval endpoints differ from 0.102/0.119 by ≤1e-12 m |
| Request validity | `0<A*=5e-5<=A_rest=3e-4 m²`, unit literal `m2`, cavity oral, backend `fidelity0.tract1d`, 10 sections |
| R0 target area and null | `|A6-A*|<=1e-18 m²`, full q-vector base-vs-label-change componentwise exactly identical; non-target q_k=1 within 1e-12 |
| R1 target area | `|A6-A*|<=1e-18 m²` (inherited Exp019 acceptance) |
| R1 q positivity | finite, all q_i>0 and A_i>0; **not** floor clipping |
| Rank-one+Wolfram q oracle | per-profile `max_i |q_i^R1-q_i^oracle|<=1e-10` for **both** references (historical Exp019 tolerance) |
| KKT primal, stationarity | `|q_6-rho|<=1e-10`, `||Hq-K1+mu*c||∞<=1e-10`; preselected conservative reduced numeric guard |
| Linear algebra validity | min eigenvalue(H)>0; condition number(H)≤1e8 (numerical model guard, no tissue inference) |
| B2 left-neighbor response | `q5_changed-q5_base >=0.1` and greater than `5 × F_num` |
| B2 right-neighbor null | `|q7_changed-q7_base|<=1e-10` |
| B2 global effect | `||q_changed-q_base||2 >=1e-3` and greater than `5 × F_num` |

**Why these are preselected:** exact numeric fixture and historical results **already known**: R1 q5 0.6816881258941345 →0.8516666666666667, L2 0.18394350598751427; existing target/reference tolerances are copied or conservatively rounded from Exp019. These cannot make this confirmatory evidence for general human anatomy, new material physics or held-out morphologies. `F_num` is independently computed **before** condition contrast inspection from max(abs same-case rerun q delta, same-case alternate algebraic oracle discrepancy, pinned Wolfram reproduction discrepancy, 1e-12), and recorded separately per profile and aggregate max; never lowered retrospectively. If an oracle mismatch exceeds its limit, report `NUMERICALLY_UNRESOLVED`, not “effect over floor”. The numerical floor cannot bound sensor/mesh/anatomical model error.

### Fixed validity and negative-control suite (execute all available)

N01 valid baseline/body/request; N02 wrong unit (`mm2` instead of `m2`), zero/negative/nonfinite target; N03 `A_target > A_rest` for CONSTRICT; N04 unreachable xi=0.95 for creature reachable range [0.30,0.80]; N05 unknown target cavity or connected-cavity capability; N06 changed prepared-body hash or backend mismatch **must be refused by the experiment-local preflight before any realizer call**; N07 10-section against 16-section representation mismatch **must be refused by the same preflight**, rather than assuming native Core support;  N08 xi=0 and xi=1 endpoint mapping, xi=0.65±0.04 staying in section 6, exact boundary xi=0.6 and ±1e-9 with documented downstream ownership (record float precision ambiguity rather than silently coercing); N09 same-input R0/R1 A/A repeat and reversed nonsemantic declaration order where supported; N10 R0 unchanged by altered R1-only stiffness metadata; N11 target-only perturbation keeping body/model fixed and reobserving returned state; N12 invalid/nonpositive/nonfinite reduced profile **raises constructor ValueError**; separately, valid-profile unsupported multi-active-gesture requests must receive native `UNSUPPORTED` with no state;  N13 no acoustic invocation, waveform or Take for a rejected request or in this B gate; N14 never call SMC5 synthetic `tract/open_closed` a Core dimensioned goal or import SMC6 `RESEARCH_OVERRIDE` as a faithful plan. Absent testable interface is `NOT_AVAILABLE` with provenance, not silently “pass”.

**Important independent-science control:** All 10 returned area readings are derived from a **modeled** geometric state, not from measured human vocal organs. Solver-algebra oracle checks and relative stiffness response are evidence of this model implementation only. Position-index resolution sensitivity is separately logged; a 10→16 conversion and held-out different body are outside this gate. No speech quality ratings requested.

## Execution design, raw artifacts and immutable decisions

**Required order:** B0 review evidence → freeze this protocol/fixture hashes **and independent audit** → implementation test-only RED on a new branch → narrow B1/B2 experiment-local code → exact-HEAD GitHub CI → independent code/model review → append-only results. Any new boundary or tolerance is a new preregistration revision and *cannot reinterpret earlier data*.

Required outputs for every attempted condition:
- `manifest.json` (exact Git/SHA, Python/NumPy, adapter if any, rest morphology, core backend/method, fixed constants and source/target hash, negative-control inventory);
- `observations.csv` (condition/xi/s/j/t, observed m², all ten sections and ratio vectors, signed and absolute errors with explicit blanks for invalid);
- `oracles.json` (Wolfram SHA, rank-one solution, KKT primal/stationarity/conditioning, test tolerances and model-only uncertainty);
- `refusals.json` (one row per attempted negative input with `phase`, `outcome_kind`, `harness_code`, nullable `native_feasibility`, original exception type/message when applicable, `did_call_core`, `core_result_exists`, nullable `core_state_present`, and no audio/Take. **No invented native Core status** for a construction or preflight refusal; use the v1.1 JSON contract);
- `decision.json` (preselected gate and reason, criteria and non-estimable cells). No text-only pass receipt without raw arrays.

Preserve native Core failure ordering `INVALID` before `UNSUPPORTED` before `INFEASIBLE` **only for inputs actually reaching Core**; constructor failures and harness refusals have separate phases, no synthesized `FeasibilityReport`. No Go on one unaccounted mandatory negative control or source change; an explicitly preregistered `NOT_AVAILABLE` status is recorded but does not silently count as a passing refusal. B1 possible `MODEL_GEOMETRIC_MEASURAND_DEFINED` or `NOT_MEASURABLE/INVALID`. B2 possible `REDUCED_QUASISTATIC_MODEL_RESPONSE` or `KINEMATIC_ONLY/UNSUPPORTED/NUMERICALLY_UNRESOLVED`. `BLOCKED_REVIEW_INTEGRITY` wins whenever B0 is unresolved. No B3, no H_EXEC, no 2-body×2-habit factorial, no clinical/biological assertion, no new sound or creator GO; their outcome is `NOT_RUN`.

## Scientific handoff after this protocol

If B1/B2 replicate, **B3 remains a distinct decision**: introduce separately versioned **model-only** SMC TaskDefinition and independently justified physical-variable/xi/cavity/capability sidecar. Old `tract/open_closed/synthetic` and its exact timing hashes stay untouched. If B3 needs unsupported TaskDefinition changes, STOP rather than rewriting the canonical compiler's truth. Real H_EXEC requires a later model with **actual named actuator input and state dynamics**, null controller, reachability/effort law, separately measured physical task attainment and review. Distinguish time markers from tissue event times. Fixed Studio V2 is unchanged.

References: Core [Issue #227](https://github.com/ryonakayama234/morphoacoustics/issues/227), [CVI Draft #224](https://github.com/ryonakayama234/morphoacoustics/pull/224), [SMC preflight Draft #226](https://github.com/ryonakayama234/morphoacoustics/pull/226), pinned Exp019 source and reference above.
