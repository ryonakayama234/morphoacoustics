# OG-3 Gate A — narrow public Organ Graph preparation RFC (candidate)

Date: 2026-10-15 JST · Tracker: [Core #100](https://github.com/ryonakayama234/morphoacoustics/issues/100) · Base: `1fb6c9f691f94558c6d5ccaf4b018eb05389cafe`

**Status: DESIGN REVIEW; documentation-only merge under review. No production implementation or public API adoption in this PR.**

**Mandatory geometry capability:** every 0..4000 Hz statement below applies only to the two frozen ordered fixtures in §11. Well-formed other geometry/medium is UNSUPPORTED before preparation, not silently admitted by the frequency window.
This RFC is an actionable proposed public boundary, NOT a published schema or proof that OG-3 works. Prior OG-0, OG-1 and OG-2 results are **limited research evidence**, not a generic solver. Inherited fixtures are controlled regression, not prospective independent scientific replication. Preserve original Experiment039 evidence and post-hoc amendment.

## 1. One strictly bounded API capability

A Core client constructs **exactly two immutable named fixed rigid uniform 1D passive acoustic tubes**, each with inlet/outlet acoustic p/U ports, and exactly one typed zero-volume serial junction. Core validates and prepares an immutable backend-specific graph preserving identities, exact revisions, units, endpoints and terminal conditions; it returns a full complex frequency-domain two-port response and provenance. No 3D physiology, nonlinear airflow, organ deformation, actual voice, WAV, self-oscillation, arbitrary topology, branched public solver or Studio graph editor is claimed.

### Product / causal boundary

```mermaid
flowchart TD
 Studio["Future Studio / external caller: editor layout + selected blueprint"] --> BP["OrganGraphBlueprint: physical node/port/edge refs + exact revisions"]
 BP --> V["Core structural/unit/port/edge/boundary validation"]
 V -->|valid| C["Core backend capability check: 2 fixed serial tubes only"]
 V -->|malformed| I["INVALID + path diagnostics"]
 C -->|not supported| U["UNSUPPORTED + capability diagnostics"]
 C -->|supported| P["Core deterministic preparation"]
 P --> PG["PreparedPhysicalGraph: immutable ordered tubes + mapping + preparation digest"]
 PG --> S["Existing UniformTube physical transfer primitive"]
 S --> O["Observation: full complex [p,U] 2-port + numerical diagnostic + evidence"]
 O --> T["Caller stores immutable result/Take reference (future Studio)"]
```

A drawn Studio edge is never automatically a legal acoustic coupling. Core alone owns physical laws, units, capability and feasibility.

## 2. Relationship to current adopted types — no conflation

| Existing authority | OG-3 mapping / non-disruption |
| --- | --- |
| `CreatureSpec` and `CavityConnection` | Semantic cavity/source/articulator relationships; no metric lengths, area or p/U conservation equations. Preserve unchanged. An explicit identity mapping may link them to physical graph nodes, but DO NOT infer a validated junction from `CavityConnection`. |
| `PreparedMorphology[T]`, `PreparationProvenance` | Established generic semantic-to-backend binding. OG-3 prepared *physical graph* is a typed numerical topology; decide a composition/adapter route without changing the universal domain schema or claiming each graph directly satisfies an existing `Tract1DGeometry` contract. |
| `UniformTube` | Adopted fixed lossless plane-wave primitive: reuse `transfer_matrix` and its sign/units without cloning mathematical tube law. |
| `BodyPresetRegistry` | Existing exact-version registry is specifically `PreparedMorphology[Tract1DGeometry]`. Do not insert a graph into this typed registry or silently widen it. A separately reviewed adapter/migration may follow. |
| Performance Contract v0 and **draft** v1 PR #101 | Creative identity, Script, Direction and selected exact body preset are separate from graph preparation. No v0 changes and no dependency on unreleased v1. |
| X2a limited live integration | The **entire src/morphoacoustics Python inventory** and audited git blobs are frozen. Merely adding a new .py file will fail its source preflight. See §6. |
| Experiment039 `og2.py` | Preserve research code, original Wolfram oracle, regression and amendment unchanged; extract/reimplement minimal generalizable implementation behind a new reviewed public contract, then compare without importing experiment code in the public API. |

## 3. Candidate stable public surface, not yet named ABI

- **Input:** the physical capability is limited by §11; schema/canonicalization version; exactly two immutable organ IDs and exact revisions; SI `length_m`, `area_m2`, common `rho_kg_m3`, `sound_speed_m_s`; named inlet/outlet `acoustic.p_u` ports; one `ideal.series.p_u` law/version with explicit orientation; one specified input boundary and one output termination (`matched` or `pressure_release` for the fixed tests).
- **Preparation:** distinct `validate_graph` then `prepare_graph` operations (final naming delegated). Structural validation precedes capability check. Preparation returns `BOUND` or a typed diagnostic, never a silent fallback.
- **Prepared value:** immutably resolves named node/port/edge to **two separately retained `UniformTube` objects**; maintains physical path order, exact module revisions, backend/coupling/canonicalization versions, input graph digest and preparation digest. NEVER flatten away organ identity.
- **Observation request:** finite supported frequency grid (no hidden default), explicit observation/termination metadata; backend uses `[p_in,U_in]^T=T_A T_B[p_out,U_out]^T` with `e^(+i ω t)`. `p` in Pa, **volume flow** `U` in m³/s; `Z_c=ρc/A` in Pa·s/m³. Normalization of entire 2x2 matrix: `S T S^-1` with `S=diag(1,Z_ref)`, `Z_ref=Z_c,A`.
- **Observation output:** one full **complex** 2×2 matrix per requested frequency, shape `(N,2,2)`, in request order, plus evaluation settings and numerical diagnostics. Every supported grid with `1 <= N <= 4096` follows this rule, including repeated or unsorted values; seven frequencies are required only for the frozen Gate B oracle fixture. WAV, formants and p/U transients are not supplied. See §9 for mandatory frequency/refusal/zero-byte rules.
- **Status semantics:** malformed graph or primitive/derived impedance: `INVALID` with precise path; well-formed three-way branch or mixed medium outside backend: `UNSUPPORTED`; numerical singularity/conditioning only when relevant: `NUMERICALLY_UNRESOLVED`; runtime infrastructure failure: `FAILED` at execution layer. `INFEASIBLE` belongs to supported task/body realization and must not be reused for invalid wiring. No fabricated response on any failure.

## 4. Canonical identity, stored data and compatibility

```mermaid
flowchart LR
 Sem["Semantic CreatureSpec<br/>stable cavity IDs"] -. "explicit mapping only" .-> BP["Blueprint<br/>SI + exact revisions"]
 BP --> Prep["Prepared backend graph<br/>typed resolved mapping"]
 Prep --> Obs["Observation + diagnostics"]
 Obs --> Take["Stored immutable Take / experiment evidence"]
 View["Studio canvas coordinates / visual styling"] -. "excluded from graph digest" .-> BP
```

Declare separate hash domains:
1. **Blueprint hash**: schema/canonicalization version, organ IDs/exact revisions and SI parameters, medium, typed port references/directions, coupling law/version and identity-relevant boundary semantics; sort named organ/edge collections consistently; exclude presentation coordinates.
2. **Preparation digest**: blueprint hash plus actually resolved backend/version, solver preparation settings and stable numerical mapping; reject positive-but-subnormal areas when `ρc/A` or reciprocal overflows or underflows to invalid numbers.
3. **Observation/evidence digest**: prepared digest + ordered frequency grid, chosen termination/evaluation, complex raw results, algorithm/code SHA, dependency versions and oracle/run identity.
4. **Historical Take reference**: resolved immutable body/preparation identity and observation artifact. Updating a preset must never retroactively rebind old Takes.

Do not claim cross-language canonical SHA identity until JavaScript/Python fixture byte-for-byte tests exist; Core-computed digest is authoritative meanwhile. Specify float encoding/nonfinite rejection and version namespace before public ABI adoption.

## 5. Thin-slice execution & review gates

**Implementation candidate paths (reconciled with §10):** `src/morphoacoustics_graph/model.py` for typed graph and `src/morphoacoustics_graph/preparation.py` for validation/preparation/observation, explicitly imported through the sibling package. Reuse the unchanged `morphoacoustics.acoustics.uniform_tube.UniformTube`. Keep the entire `src/morphoacoustics/` tree and X2a manifest byte-identical; no OG-3 modules or initializer exports may be added there. Tests: `tests/test_prepared_graph_public.py`, `tests/scientific/test_graph_port_physics.py`, and dedicated CI. Internal splitting within the sibling package is implementer discretion; physical contract/data invariants are not.

- Gate A (this PR): design and proposed pre-implementation gates only. Independent critical review should approve semantics, defaults, failure taxonomy, hash domains and old API mapping before Gate B.
- Gate B: implement a two-node **clean-room client from production imports only**; pass frozen Experiment039 full complex 7-frequency oracle, equal-area tube identity, area-only causal intervention, orientation/particle-velocity mutations, invalid/unsupported refusal and roundtrip/provenance, Python 3.11–3.13, mypy, complete regressions. Pin exact HEAD and source/oracle/evidence SHA; produce raw outputs and link green CI.
- Gate C: separate physics/numerics and code/API adversarial audits, disclose correlated AI model/context, independent executable Wolfram oracle (machine path only), inspect all blocking findings and make explicit public **GO / INCONCLUSIVE / REJECT** decision. CI green is not scientific validity or API adoption.

No implementation/merge/rerecording legacy oracles is authorized by Gate A alone.

## 6. CRITICAL BLOCKER — X2a frozen package inventory

`src/morphoacoustics/integration/limited_live.py` audits **all 23 other package Python files** and rejects added/removed files, including files not imported by the experiment. `tests/test_limited_live_policy.py::test_frozen_package_source_inventory_is_complete_and_matches_checkout` enforces it. New OG-3 production `.py` modules, even if only additive, will break this audited runtime.

**Gate B cannot be considered regression-green by bypassing this check.** Use sibling-package isolation (§5/§10); extending only X2a's manifest failed Experiment028/029 source fingerprints. Audit imports and packaging: frozen Core must not eagerly import the sibling; the sibling reuses the unchanged tube primitive and reviewed dependencies, never experiment code. Require byte-identical original package inventory, manifest and 23 pins; record new sibling source hashes separately in OG-3 evidence. Preserve unknown/tampered-file refusal tests and run original Experiment028/029 plus X2a CLI preflight/physical WAV smoke on exact Gate B HEAD. No legacy oracle, fingerprint or pin may be weakened or recaptured. A failed audit blocks promotion; Gate A itself adds no production source.

## 7. Decision questions for independent Gate A review

1. Is a narrow new typed physical graph object correctly distinguished from `CreatureSpec` and `PreparedMorphology[T]`?
2. Are the fixed 2-port law, `e^(+iωt)`, port sign/orientation, shared medium, boundaries and dimensionless similarity transform unambiguous?
3. Does the graph fingerprint exclude view data but preserve exact body/solver/coupling versions?
4. Are malformed topology, valid unsupported branches, infeasible gestures, numerical unresolved and execution failures mutually meaningful?
5. Does sibling-package isolation preserve the entire frozen Core tree/manifest, legacy source fingerprints and fail-closed import/inventory checks without expanding physical claims?
6. Is the seven-frequency OG-2 regression correctly distinguished from a new prospective biological validation?

**If any answer is unclear: record BLOCKED/INCONCLUSIVE and amend this RFC visibly before implementation.**

See companion [Gate A physics/acceptance protocol](./og3-gate-a-protocol.md), [Wolfram verification source](./og3-wolfram-gate-a.wl), living [architecture](./organ-graph-program.md), [data map](./organ-graph-data-candidate.md), [ledger](./organ-graph-experiment-ledger.md).

## 8. Post-author self-audit candidate dispositions (2026-10-15; independent review still required)

The review was authored with the **same AI context** and is **not independent sign-off**. [Gate A self-audit PR #102 comment](https://github.com/ryonakayama234/morphoacoustics/pull/102#issuecomment-6188922718). Following definitions are proposed to **resolve RFC ambiguity for independent reviewers**, not yet frozen public ABI.

**X2a compatibility choice — revised by §10:** use explicitly imported sibling `src/morphoacoustics_graph/` modules. The original in-package extra-pin proposal failed legacy source fingerprints and is historical only. Do not amend `AUDITED_PACKAGE_GIT_BLOBS` or any existing Core initializer/source. Audit source reachability, new sibling hashes and same-distribution packaging separately, retain unknown-file/tampered-file negative tests, and require original Experiment028/029 plus genuine X2a two-take WAV/trace smoke on exact Gate B HEAD. Trial evidence in §10 is historical, not a substitute for a fresh-head audit.

**Canonicalization candidate for reviewers:** encode physical quantities as finite Python/IEEE-754 binary64 values in SI, reject bool, NaN/Inf, nonpositive dimensions and nonfinite derived impedance or reciprocal. Stable fingerprint schema could emit each float as **16 lowercase big-endian binary64 hex digits** in a sorted-key UTF-8 JSON envelope with an explicit domain separator and canonicalization version, avoiding language-dependent decimal float rendering. Require byte-for-byte fixture tests in Python and JavaScript before calling a hash cross-runtime deterministic. Sort *collections* by stable named organ/edge ID; preserve each oriented junction's ordered port endpoints. Explicitly specify identifier Unicode normalization or an ASCII-only identifier profile and test collisions before release; not yet a frozen public ABI. Research Experiment039 raw hex digest need not equal the new versioned public digest (same physical response is the regression target). Proposed Core digest is authoritative until such tests pass.

**Three identity levels:** canonical structural `blueprint_digest` hashes schema, exact named revisions, SI physics, signed orientations, ideal law/version, designated source/load and declared termination; `preparation_digest` adds resolved backend ID, numerical/contract version and immutable port mapping; `observation_digest` adds actual ordered frequencies, normalized full complex response, requested observation kind and backend numeric configuration. Raw scientific evidence additionally stores exact Git HEAD, dependency and Wolfram/oracle SHA. Presentation coordinates never enter physical identity. Different B area/revision must change blueprint+prepared digest, not untouched organ A identity.

**Boundary decision candidate:** retain `matched` vs `pressure_release` as immutable **Blueprint terminal metadata**, as in Experiment039. The primary OG-3 `full_complex_transfer` observable is an **unloaded two-port**, invariant under changing only the terminal load. A loaded input-impedance/reflection observable is a *different, not yet supported* request and must not be silently substituted for transfer. No observation-time implicit terminal override in v1. Terminal metadata is preserved in hashes even when transfer matrix itself is identical.

**Observation ABI candidate (mandatory bounds in §9):** v1 receives an explicitly ordered, nonempty **1-D** frequency array with `1 <= N <= 4096` and finite `0 <= f <= 4000` Hz; normalize signed zero before evaluation and identity. It produces `(N,2,2)` complex128 and JSON pairs `[real,imag]` in source order, or typed refusal with no observation. Shape/type/nonfinite/negative errors are `INVALID`; a well-formed grid exceeding the resource cap or frequency window is `UNSUPPORTED`. Numerical phase/normalization overflow is a diagnostic rather than a plausible matrix. These bounds are required, not optional. Rigid circular area-equivalent B has first ideal transverse-mode estimate ~7.27 kHz, but ideal junction/real-anatomy limits may apply earlier; no full-band physiology claim follows.

**Pending independent review:** confirm the choices above, reconcile with OG-2 legacy shape and Core typed outcomes, freeze detailed schema/canonical byte fixtures and check X2a isolation before opening Gate B; absent review, this PR remains Draft.

## 9. Gate A Codex review dispositions — 2026-10-15 (author response; independent acceptance pending)

GitHub Codex's [two unresolved review threads](https://github.com/ryonakayama234/morphoacoustics/pull/102) identify previously ambiguous frequency capability and signed-zero hashing. We accept both findings and freeze the following **implementation candidate**, independently reviewable before release:

- **Backend frequency capability:** Only for the supported §11 fixtures, OG-3 accepts a nonempty 1-D ordered grid with **1 <= N <= 4096** and finite **0 ≤ f ≤ 4000 Hz**, inclusive. A well-formed finite nonnegative grid with **N > 4096** yields typed **UNSUPPORTED**, a resource-limit diagnostic and **no observation**. Values above 4000 Hz yield **UNSUPPORTED**, a frequency-capability diagnostic and no observation. Malformed containers, NaN, Inf, strings/bools and strictly negative frequencies yield **INVALID** and no observation. Validate malformed input before capability checks; for otherwise valid input exceeding both limits, report resource limit first. This is an engineering support policy, not 1D acoustic validity for arbitrary dimensions or anatomy. Only the seven original frequencies have frozen Wolfram reference; all other geometry/medium is UNSUPPORTED under §11 until separately validated and versioned.
- **Signed zero:** normalize accepted `-0.0` to `+0.0` **before** evaluation, snapshotting, binary64-hex canonicalization or observation digest. Both zero inputs must serialize to the exact ASCII hex value `0000000000000000` (eight zero bytes); `8000000000000000` must never enter the canonical frequency payload. Test identical bytes/digests/results at ±0.0. Values `f<0` remain INVALID. Exclude 0 Hz from propagating-wave/energy-flux claims, though its static transfer is identity.
- **Frozen design v1 for implementation only:** carry `matched` and `pressure_release` as blueprint terminal metadata but expose **unloaded** two-port full complex transfer only; do not compute or suggest power transmittance from pressure-release boundaries. The backend returns `UNSUPPORTED` for any new loaded-impedance observable, new topology or unsupported frequency. Use explicit versioned binary64-hex canonicalization, exact organ/port/edge revisions/IDs and no canvas data. `CreatureSpec`, preset registry, experimental source and original oracles are not changed.

**Design auditor status:** these are corrected design requirements, not public API execution or adoption. The protocol specifies boundary cases for arbitrary N, out-of-band values, oversize grids and exact zero bytes. Resolution of a design thread records that its requirement is corrected; Gate B implementation evidence and Gate C acceptance remain separate.

## 10. Gate A architecture correction, demonstrated by separate Gate B trial (2026-10-15)

**Supersedes all earlier in-package source locations and manifest-extension instructions, including §5/§6/§8 and the execution plan; those operative sections now use the sibling architecture.** The first separate [Gate B Draft PR #104](https://github.com/ryonakayama234/morphoacoustics/pull/104) failed inherited [Experiment028](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478556) and [Experiment029](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478713) fingerprints even with two new Core files added to X2a's manifest. Extending only X2a does not preserve legacy scientific source identity. Preserve this failed attempt; never weaken or repin legacy sources.

**Gate A revised candidate architecture:** a Core-owned, same-distribution **sibling Python package** `src/morphoacoustics_graph/`, exposing graph model and preparation/observation code and importing the existing immutable `morphoacoustics.acoustics.uniform_tube.UniformTube` primitive. Entire frozen `src/morphoacoustics/` subtree (including original X2a manifest) remains byte-identical. Core owns the graph's physical types/laws, backend status and provenance; no new waveform or general topology claims. This is an explicit software isolation boundary, NOT a second competing physics engine.

**Trial evidence:** corrected stacked [Gate B #104](https://github.com/ryonakayama234/morphoacoustics/pull/104), commit `ce6af25a630fb5cd19510948ce7f1393d9391780`, passed Python 3.11–3.13 and mypy [CI #38731395318](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38731395318) plus the [specialized gate #38731394921](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38731394921): original Exp028/029 decisions preserved, X2a real two Take WAV/pressure/trace stable, and new graph full complex seven-frequency error `1.915134717478395e-15 <= 1e-10`. Wrong/stale HEAD evidence rejected. These are **engineering/scientific machine checks on one exact Trial HEAD**, not an adopted Core public API or an independent human reviewer approval.

The two previously open Codex issues (frequency >4kHz and signed-zero hashing) were explicitly addressed in RFC §9 and passed positive/negative Gate B tests. An independent physical/code reviewer must still assess the changed packaging boundary, frequencies beyond the seven-point fixed reference and snapshot/hash long-term ABI before design sign-off. No PR automatically merges.


## 11. Geometry capability correction and Gate A merge decision scope (2026-10-15)

The additional Codex P2 on PR #102 is accepted. A universal 4 kHz band with arbitrary positive tube dimensions is not supported by the frozen evidence. **Restrict this candidate to the two inherited fixtures; do not introduce a new geometry-dependent cutoff model or extrapolate to arbitrary cross sections.** This section controls all earlier mentions of supported geometry/frequency.

| Resolved physical path (not array order or literal organ ID) | Length m | Area m² | Density kg/m³ | Sound speed m/s |
| --- | --- | --- | --- | --- |
| First/source-side tube | 0.08 | 0.0003 | 1.21 | 343 |
| Second/load-side tube, equal-area control | 0.09 | 0.0003 | 1.21 | 343 |
| Second/load-side tube, area intervention | 0.09 | 0.0006 | 1.21 | 343 |

Exactly one of the two second-tube rows is selected. Numeric matching is **exact after the already validated finite SI input is converted to binary64**, without tolerance or rounding to a fixture. Stable valid IDs/exact revision labels remain caller-selected; collection order is immaterial, resolved physical path order is not. Both already specified terminal metadata options remain supported. The 0.17 m single tube is an analytic comparator, not a third public graph fixture.

Validation still accepts structurally legal positive finite values; capability then refuses other dimensions, shared medium or reversed physical fixture order with `UNSUPPORTED` and a geometry/medium diagnostic, returning **no prepared graph, observation or digest**. Malformed topology/types/nonfinite or nonpositive values remain `INVALID` before capability. A valid three-port branch remains `UNSUPPORTED`. Observation and restore must not bypass this domain by directly constructing a prepared dataclass or changing a stored snapshot. Restrict 0..4000 Hz and arbitrary accepted grid lengths to these two fixtures only. This demonstrates ideal 1D software/physics regression; it does not validate anatomical shape, real area steps, speech or all frequencies experimentally.

Gate B must test each geometry/medium parameter separately, near-boundary `nextafter` changes, a large positive area, unsupported physical path reversal, source collection reorder invariance, both supported fixtures/terminations, restored snapshots and forged prepared values. Reject unsupported profiles before transfer evaluation; no fallback geometry. Version the narrowed backend as `og3.fixed.passive.serial2.pu.v2` so older candidate snapshots are not silently rebound. Exact numerical physics and old research oracles remain unchanged.

**Gate A documentation merge criterion:** no unresolved design findings, latest general CI green, analytic source/result hashes verified, and the [Gate B reconciliation work order](./og3-gate-b-reconciliation.md) recorded. Merging this design records a bounded implementation target and review history; it does not merge #104, adopt a public ABI or constitute independent human scientific approval. This task's AI review shares the conversation context; executable Wolfram/NumPy evidence is computationally separate but not a substitute for human review. User authorization to proceed includes this documentation merge after these conditions hold. Gate B remains Draft pending exact-head implementation evidence and a separate release decision.
