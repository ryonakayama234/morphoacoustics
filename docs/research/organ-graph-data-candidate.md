# Organ Graph data contracts — experiment-local candidate (2026-10-14)

> **OG-5 Gate B3 active, not adopted (2026-10-16):** [B3 experiment+architecture/data diagrams](./og5-gate-b3-trial.md) | [separate Wolfram oracle](./og5-gate-b3-independent-oracle.wl) | [Core-vs-reference scorer](../../checks/check_og5_gate_b3.py) | [Draft PR #112](https://github.com/ryonakayama234/morphoacoustics/pull/112). Eight case shards × 18, 144 full 10-port p/U records from independent global and recursive solvers archived. **Reference-only** check succeeded; Core exact-HEAD score/twin artifacts, eight mutants, regressions and separate Gate C still require completed receipts. Frozen Gate A/A1 remains controlling.


**Current production-facing exception (2026-10-16):** the *specific* typed two-node passive serial graph schema in `src/morphoacoustics_graph/` is **adopted limited on Core main**, [Gate C decision](./og3-gate-c-limited-adoption.md). The older *general* graph schema and separate `CreatureSpec`/Studio body-binding contract described below remain candidate and **NOT adopted**. Two exact geometries, fixed common medium and full unloaded complex response only; no aliasing UI coordinates or physical time state.

**NOT A PUBLISHED API.** This is a reviewable, minimal conceptual schema for [Core OG-2 #96](https://github.com/ryonakayama234/morphoacoustics/issues/96), not a replacement for `CreatureSpec`, `PreparedMorphology[T]`, `Tract1DGeometry` or the Studio Performance Contract v0. Exact field names and JSON serialization are unapproved.

## Four different objects — do not collapse them

```mermaid
flowchart LR
  Sem["Semantic morphology: CreatureSpec / cavity IDs"]
  Blueprint["Editable/persisted Blueprint: organ and typed port refs"]
  Prepared["Validated, immutable PreparedGraph [backend]"]
  State["Simulation state x(t) / p,U / moving geometry"]
  Obs["Observation: transfer/WAV/trace"]
  Sem --> Blueprint -->|"validate + prepare"| Prepared -->|"solve"| State --> Obs
```

- A `CreatureSpec.CavityConnection(source_id,target_id,kind)` provides semantic relationships, **not** a complete physical port equation. The new preparation layer must explicitly bind identities and constraints, not reinterpret such a connection as a mathematically verified junction.
- A `Blueprint` describes a creator-chosen anatomical/numerical configuration. It contains **persistent parameters**, not instantaneous values of pressure, velocity or wave samples.
- `PreparedGraph` is a backend-bound immutable object with validated resolved ports, solver rest state, mapping, preparation provenance, and a digest. Its existence must not imply every gesture or future dynamic behavior is feasible.
- Simulation state / observables are evaluated later and are not part of the blueprint digest.

## Candidate serial 2-organ fixed passive example

```json
{
  "schema_version": "organ-graph-candidate/v0",
  "model_scope": "fixed-rigid-linear-1d-passive",
  "organs": [
    {"id":"organ-A","revision":"1","kind":"rigid-tube-1d","length_m":0.08,"area_m2":0.0003,
     "ports":[{"id":"in","kind":"acoustic-pu","role":"inlet"},
              {"id":"out","kind":"acoustic-pu","role":"outlet"}]},
    {"id":"organ-B","revision":"1","kind":"rigid-tube-1d","length_m":0.09,"area_m2":0.0006,
     "ports":[{"id":"in","kind":"acoustic-pu","role":"inlet"},
              {"id":"out","kind":"acoustic-pu","role":"outlet"}]}
  ],
  "medium": {"rho_kg_m3": 1.2, "c_m_s": 343},
  "edges": [
    {"id":"edge-A-B","from":"organ-A.out","to":"organ-B.in",
     "law":"ideal-series-pu/v1"}
  ],
  "boundaries": [
    {"port":"organ-A.in","kind":"excitation","value_ref":"fixture-input"},
    {"port":"organ-B.out","kind":"matched-impedance"}
  ]
}
```

This is an *illustrative fixture*, not a production schema or a new experiment result. Fixed source and boundary conditions used by a solver may instead be kept in an **evaluation request** rather than a reusable blueprint; the experimental gate must make this separation explicit.

## Type and law constraints

| Quantity | Unit | Role |
| --- | --- | --- |
| acoustic pressure perturbation `p` | Pa | **computed** port state |
| acoustic volume velocity `U` | m³/s | **computed** port state; local signed direction |
| acoustic characteristic impedance `Zc = rho*c/A` | Pa·s/m³ | **derived** and must remain finite |
| cross-sectional area `A` | m² | static input in this 1D candidate |
| tube length `L` | m | static input |
| acoustic power `p U` | W | power audit, with appropriate mean/phasor convention |

At ideal zero-volume fixed passive series connection, `p_A.out = p_B.in` and global-direction `U_A.out = U_B.in`; with local outward signed flows their sum is zero. **Do not impose particle-velocity equality** across unequal areas; it is a falsifying wrong law. For an ideal three-port junction, all port pressures are equal and outward signed volume velocities sum to zero. Both are limited small-signal 1D laws.

**Never assume** an edge between `acoustic-pu` and `mechanical-force-velocity` is legal without an explicit transduction model. A graphically connected node must be physically validated.

## Preparation output proposal

```text
PreparationResult
  ├ outcome: BOUND | INVALID | UNSUPPORTED | NUMERICALLY_UNRESOLVED
  ├ prepared_graph: backend-specific rest topology, ONLY on success
  ├ resolved_mappings: semantic ID ↔ numeric organ/port/edge IDs
  ├ capability: fixed passive serial p/U (not general anatomy)
  ├ provenance: schema / organ revisions / law versions / backend / settings
  ├ graph_digest: canonical content hash independent of UI coordinates
  └ diagnostics: path, code, failed law/boundary, context
```

Preparation failure codes here are **proposal vocabulary**. Keep the adopted Core realization statuses unchanged: `INFEASIBLE` describes a *supported physical task* that a body cannot realize, not an invalid or unsupported graph. Numerical singularity is not a plausible audio fallback. `FAILED` belongs to execution infrastructure, not biological capability.

## Digest and versioning

The canonical graph/preparation digest should include topology, organ IDs/revisions, SI-valued parameters, medium, port roles and coupling law IDs, boundary definitions when they affect prepared identity, backend + numerical configuration, and canonicalization/schema version. It should **exclude** visual canvas coordinates, selection state, derived WAV, transient p/U state, and UI theme. Define separately the **input/blueprint digest**, **prepared rest-state digest**, **run/evidence hash**, and **immutable Take hash**.

Changing organ B area or revision must change the appropriate digest while A's identity stays fixed. Reordering JSON arrays of otherwise identical named nodes/edges should not change a canonical structural digest if canonicalization intentionally sorts IDs. Old Takes must retain the old exact revision and resolved hash.

## Core ↔ Studio contract boundary

Creative `CharacterSpec` is *not* `CreatureSpec`; Studio appearance mesh is not the numerical acoustic/solid mesh. A reusable Character/Body binding selects an exact validated body revision; [Draft v1 contract PR #101](https://github.com/ryonakayama234/morphoacoustics/pull/101) now carries selected `preset_id` + `preset_revision` in the request and actual `preparation_digest` / `backend_id` in result; the source of truth is the still-unadopted `contracts/performance/v1` proposal, with unchanged nested creative v0 schemas. This is separately tracked by [Core #72](https://github.com/ryonakayama234/morphoacoustics/issues/72) and [Studio #14](https://github.com/ryonakayama234/morphoacoustics-studio/issues/14).

## Required counterexamples before promotion

- Same two tubes, equivalent single tube: full complex transfer equality after correct unit normalization.
- Same graph, different B area: nonzero physical reflection and digest change; unchanged A.
- Wrong port type/direction, duplicated edge, missing boundary, negative/nonfinite dimensions: fail closed as invalid.
- Well-formed legal branch supplied to a serial-only backend: `UNSUPPORTED`, never silently flattened.
- Deliberate particle-velocity junction, reversed organ order, wrong port power sign: independent oracle rejects.
- Near-zero but positive area causing derived `Zc` overflow: explicit invalid diagnostic.
- Frozen fixtures and new integrated-base conditions: exact head SHA + CI + reproducible independent machine evidence.

Companion [program](./organ-graph-program.md) and [evidence ledger](./organ-graph-experiment-ledger.md).

## 2026-10-15 evidence boundary (WP-01 / WP-03)

OG-2 Experiment039 is now **accepted only as fixed-geometry passive 1D research** via [formal #98 decision](https://github.com/ryonakayama234/morphoacoustics/issues/98#issuecomment-6182585021) and merged [#97](https://github.com/ryonakayama234/morphoacoustics/pull/97). Its experiment-local `Blueprint`/`PreparedPhysicalGraph` are **not** the illustrative JSON schema in this document, nor an adopted production interface; do not copy field names from the example and claim ABI stability. Further public promotion requires [OG-3 #100](https://github.com/ryonakayama234/morphoacoustics/issues/100).

Parallel [CC-A1 Draft PR #101](https://github.com/ryonakayama234/morphoacoustics/pull/101) defines `PerformanceRequest v1`'s exact `{preset_id,preset_revision}`, and result's `{status,preset_id,preset_revision,backend_id,preparation_digest}` **only when bound**. This creator binding is separate from physical graph law and from `CreatureSpec`, and preserves v0 creative snapshots. Status is DRAFT CONTRACT, not a new physical solver or released Studio adapter. Contract request digest hashes full v1 request + backend ID/version; resolved preparation digest remains the Core registry's physical binding digest.

## OG-3 candidate public binding (2026-10-15; NOT a published ABI)

See the [Gate A RFC](./og3-public-preparation-rfc.md) for exactly two fixed serial tubes, typed p/U law, immutable identity and separate blueprint/preparation/observation digests. The illustrative JSON and Experiment039 private types are not the public ABI. `CreatureSpec`, registry and draft CC-A1 remain separate. New code is isolated in `src/morphoacoustics_graph/`; original Core tree/manifest/pins remain byte-identical, with separately audited sibling hashes/imports and legacy regression. X2a manifest extension alone is rejected.

### OG-3 Gate A canonical-byte candidate, review pending (2026-10-15)

[OG-3 RFC §8](./og3-public-preparation-rfc.md) proposes versioned structural/preparation/observation digest domains, SI binary64 big-endian hex within canonical sorted JSON, exact named revisions, stable organ/edge sorting but **order-preserving directional port tuples**, with Python↔JS byte fixture test before cross-runtime promises. Terminal condition is Blueprint identity metadata; unloaded complex two-port `T` does not vary with load, and no observation-time termination override is provided by candidate v1. JSON complex response entries are explicit `[real,imag]`; frequency grid is nonempty 1D finite nonnegative Hz. Identifier normalization policy and resource caps require review. This is **not a published schema**; see [candidate test amendment](./og3-gate-a-protocol.md).

### Candidate normalized observation-grid bytes (Gate A review 2026-10-15)

Ordered frequencies are finite float64 SI Hz, `1<=N<=4096`, `0<=f<=4000`. Normalize ±0 before evaluation/snapshot/hash to exact binary64 hex `0000000000000000`, never `8000000000000000`. Output `(N,2,2)` complex pairs preserves order/duplicates; seven points apply only to the frozen oracle. A well-formed finite nonnegative N>4096 grid is `UNSUPPORTED` (resource limit); >4000 Hz is `UNSUPPORTED` (frequency capability). Malformed/type/nonfinite/negative input is `INVALID`. All refusals carry no observation/matrix/digest. Invalid input takes precedence, then resource cap, then band. This is numerical support, not full-band physiology. See RFC §9 and protocol boundary cases.

### Gate A approved-for-trial only: Core sibling graph type, original frozen physics unchanged

The candidate `OrganGraphBlueprint`/prepared value is now held in sibling `src/morphoacoustics_graph/`, with `UniformTube` imported unchanged from frozen `src/morphoacoustics/acoustics/`. All original 23 X2a pins and source bytes are retained, and no generic branching solver is inferred. Exact frequency capability 0..4000Hz, signed-zero normalization, identity splits and orphan invalid refusal remain the proposal. The first failed-in-frozen-tree trial and corrected machine-green sibling trial are linked in [scientific ledger](./organ-graph-experiment-ledger.md); this is not an adopted external ABI.


### Geometry-domain correction and Gate B handoff (2026-10-15)

[RFC §11](./og3-public-preparation-rfc.md) restricts every 0..4000 Hz support claim to the two frozen **ordered** fixtures (first 0.08 m/3e-4 m², second 0.09 m/{3e-4,6e-4} m²; rho 1.21, c 343). All other valid geometry/medium is UNSUPPORTED before preparation; malformed input is INVALID. No arbitrary-geometry 4 kHz claim. Caller IDs/revision labels and collection reorder remain independent of physical path. Backend candidate v2 must refuse old candidate snapshots and forged prepared values rather than bypass capability. New code stays in the sibling package; old Core tree/oracles/pins stay unchanged. The [reconciliation work order](./og3-gate-b-reconciliation.md) records #104 blockers and acceptance before its next exact-head run. Design-only merge does not release or scientifically adopt Gate B.


## Historical Gate B trial receipt retained during design reconciliation

### OG-3 Gate B proposed data implementation (Draft, 2026-10-15)

[Implementation documentation](./og3-gate-b-implementation.md) identifies concrete named immutable `OrganGraphBlueprint` and `PreparedPhysicalGraph` candidates. Python-only canonical `blueprint_digest` (explicit SI finite binary64-hex; collections sorted by node/edge ID but ordered junction endpoints retained), `preparation_digest` (backend/version/path mapping), `observation_digest` (normalized ±0, ordered f-grid, full complex real/imag bytes). Output represents **unloaded transfer** regardless of blueprint terminal metadata; no loaded impedance asserted. Compatibility: existing `CreatureSpec`, `PreparedMorphology[T]`, `BodyPresetRegistry`, experiment039, and creator contract unchanged. Cross-runtime JS/Python canonical bytes not yet demonstrated. Candidate interface not accepted until independent reviewed Gate C.

#### Gate B data placement correction (after first CI, 2026-10-15)

Proposed physical graph types are owned by sibling Core Python package `morphoacoustics_graph.model`, and prepare/observation API by `morphoacoustics_graph.preparation`, **not** the frozen `src/morphoacoustics/physical` and `preparation` Python tree. Exact typed p/U, SI, node revisions, oriented junction and three digest domains are unchanged; this change affects package distribution/import location, not physical equations or existing `CreatureSpec`. Original X2a source manifest restored. Docs above describing two newly pinned files inside the old source tree are superseded. See [correction](./og3-gate-b-implementation.md).

#### Gate B evidence identity and pristine source protection

The sibling graph package's observation stores seven ordered frequencies and all 4 complex two-port entries per frequency as explicit `[real,imag]` pairs, plus exact backend/blueprint/preparation/observation digests. A separate raw `checks/check_og3_gate_b.py` run attests Git head SHA, original Wolfram JSON hash, NumPy version and maximum normalized complex error. This **evidence identity** is distinct from immutable physical digest; no recorded X2a files are used as new audio. Dedicated CI verifies two freshly computed physical Takes.


### Gate B reconciled implementation trial (2026-10-15; verification pending)

PR #104 incorporates merged Gate A main `6d38d8b`. Sibling backend v2 enforces RFC §11's two exact geometry/medium fixtures and reconstructs prepared binding before evaluation. Old v1 candidate snapshots are refused, never rebound. Observation validation preserves original scalar types, checks all malformed values before resource/frequency capability, returns UNSUPPORTED for valid 4097-point grids, preserves N matrices/order/duplicates and hashes exact positive-zero bytes. Supplementary per-point flux threshold <=1e-12, wrong defect 0.5 and separate reverse-order controls are explicit. Tests and evidence runner match the [reconciliation work order](./og3-gate-b-reconciliation.md); current exact-head CI/artifact receipt will be attached to [#104](https://github.com/ryonakayama234/morphoacoustics/pull/104). No legacy package, source pins or experiment/oracle changes; no release/adoption. Old trial receipts above are historical and do not attest this new implementation.

### Gate C long-graph & CI dependency coverage (2026-10-16)

Well-formed large graphs remain syntactically representable although only two fixture organs have a solver. Structural validation uses iterative DFS (cycle/connectedness, full port/finite checks); a valid 1205-organ serial chain MUST return typed `UNSUPPORTED/FIXED2_SERIAL_ONLY`, not a runtime RecursionError. Its structurally malformed counterpart MUST return `INVALID` first. Dedicated OG-3 CI is re-triggered on inherited `src/**`, Experiment039 oracle/`experiments/**`, Wolfram research docs, python project configuration, tests, and checks; do not rely on a stale older PR evidence run. [Notes](./og3-gate-b-implementation.md).

### OG-4 Gate A typed data candidate (2026-10-16; design only)

[Versioned Branch3Blueprint schema candidate](./og4-three-port-public-preparation-rfc.md): 3 immutable named `PassiveTubeOrgan` values, each containing typed `acoustic.p_u` inlet/outlet, exactly 1 ordered `ideal.branch3.p_u` junction with ports `(A.out,B.in,C.in)`, explicit complex inlet source and two typed boundaries, revisioned medium/geometry (OG-1 density **1.2**, not OG-3 **1.21**), and independent blueprint/prep/observation digest domains. New branch schema/version required: **do not alias** `og3.passive.fixed2.v1` to imply branch support or change old digests. Source/boundary, graph choice and solver state remain distinct; outputs are **all six complex p/U endpoints** plus power diagnostic, not a single OG-3 unloaded two-port matrix. Separate Studio and morphological semantics are not in graph physical identity. No implementation or external ABI acceptance yet.

### OG-4 Gate A Amendment A1 — PR #107 review corrections (2026-10-16)

[Amendment A1](./og4-branch3-api-v1.md) freezes discriminated source/load objects, Complex `{real,imag}`, the blueprint/prepared-snapshot/observation schema IDs, exact backend and digest-version strings, typed framed binary64 canonical bytes and complete hashed fields. [Golden fixtures](./og4-branch3-api-golden.json) and their [encoding checker](./og4-branch3-api-vectors.py) specify identity behavior, including signed zero and fixed-vs-matched load identity.

State remains **DESIGN PROPOSED / NOT ADOPTED / no branch3 runtime**. Existing physical sources, frozen experiments and adopted OG-3 behavior remain unchanged.


## OG-4 Gate B branch3 concrete data flow (2026-10-16; Draft implementation)

```mermaid
classDiagram
  class Branch3BlueprintV1 {
    schema: og4.passive.branch3.v1
    organs: named A/B/C
    junctions: J ideal.branch3.p_u
    source: complex prescribed volume flow
    loads: B matched, C typed boundary
  }
  class PreparedBranch3 {
    blueprint_digest
    preparation_digest
    frozen UniformTube x3
    binding integrity
  }
  class ObservationV1 {
    frequencies_hz: 1..256 anchors
    port_ids: A.in,A.out,B.in,B.out,C.in,C.out
    pressure_pa: N x 6 complex
    volume_flow_m3_s: N x 6 complex
    mean_power_w: N x 6 float
    diagnostics: N x 5
    observation_digest
  }
  Branch3BlueprintV1 --> PreparedBranch3
  PreparedBranch3 --> ObservationV1
```

Blueprint is JSON-compatible and exact-key typed with `{real,imag}` complex scalars. Port identities and ordered J-port connections are semantic; graph collection ordering is not. `restore_branch3` recomputes physical binding and both digests rather than trusting persisted state. Canonical `og4.canonical.binary.v1` is separate from adopted OG-3. Observation digest includes all ordered frequencies, six complex endpoint states, powers and diagnostics. External evidence ties these physical identities to a Git HEAD and comparator hashes without contaminating physical identity with timestamps or UI metadata. A supported OG-3 fixed2 shape is explicitly NOT converted to branch3. New code is provisional until Gate B critical checks and Gate C limited decision.

### Gate B concrete serialization evidence (2026-10-16 JST)

The provisional branch3 implementation matched all 11 approved canonical binary/hash golden vectors (Python and independent JavaScript) and 122 leaf mutation controls at tested HEAD a5d0b4c. Snapshot roundtrip and forged-prepared rejection tests passed, including explicit refusal for well-formed old OG-3 fixed2 snapshots. Observations hold N×6 complex p/U state and six powers with five numeric diagnostics per sample. Physically identical matched/fixed-impedance baseline cases retain separate Blueprint identities. This evidence supports the narrow API ABI only, not Studio integration or arbitrary anatomical graphs.


### OG-4 PR #108 critical review corrections — 2026-10-16 JST

Evidence format `og4.gate-b.fresh-full-port.v2` adds `observations`: 60 records, each containing the complete prepared snapshot, full ordered request grid and complete hashed observation. Existing 288/24 case rows bind to those observations by digest; all three identities and per-case actual endpoint associations are recomputed before export. Source SHA coverage includes graph modules, runner, workflow, tests and frozen API/Wolfram fixtures, with CI run/attempt context outside physical digests. Blueprint/preparation/observation v1 ABI is unchanged. Unknown-key error paths escape JSON Pointer tokens; structural and snapshot-envelope invalidity precede capability/version decisions. See [review](./og4-gate-c-review.md).

## OG-5 five-organ, two-junction candidate contract — 2026-10-16 Gate A DRAFT

**Not a retroactive OG-3/OG-4 schema update.** [Exact candidate](./og5-tree5-api-v1.md), [four blueprint digest goldens](./og5-blueprint-goldens.json), [protocol](./og5-gate-a-protocol.md). Blueprint `og5.passive.tree5.v1` contains five named and revisioned passive Tube organisms, each with typed inlet/outlet `acoustic.p_u` (p Pa, U m³/s), two oriented three-port ideal junction constraints J1=(A.out,B.in,C.in) and J2=(B.out,D.in,E.in), one prescribed peak-phasor A.in source and loads C/D/E. Shared rho, c, fixed SI lengths/areas and explicit versioned law. The junction is not three unconstrained pairwise wires. Separate immutable PreparedTree5 with backend and source/geometry identities, physical instantaneous state (not persistent anatomy), full 10-endpoint complex Observation and future Studio Take (only reference to evidence).

```mermaid
flowchart TD
 Canvas["Studio appearance / canvas positions: NON-PHYSICAL"] -.-> Blueprint["Blueprint: organs/revisions/typed ports/J1/J2/source/loads"]
 Blueprint --> Prepare["strict structural validation + bounded capability"]
 Prepare --> Prepared["PreparedTree5: verified identity + digest"]
 Prepared --> State["complex p,U at all 10 ports"]
 State --> Observation["run outputs, power, diagnostics, exact immutable evidence"]
```

Proposal digests domain separate from OG-4; normalized binary64, ASCII strict keys, stable ID ordering (but J ports order remains semantic); source amplitude/scale/revisions/load/geometry enter body digest; UI layout and physical running state do not. Hash goldens must be ratified and prepared/observation golden extensions supplied before Gate B can start. Finite SI, typed errors and deterministic whole-input validation before capability. `INVALID`/`UNSUPPORTED`/`NUMERICALLY_UNRESOLVED` separate; never fall back to fixed OG4/3, invent a morphology or serialize solver cache.



## OG-5 Gate A Amendment A1 — 2026-10-16 JST, candidate review pending

Addresses [PR #110 R1–R4](https://github.com/ryonakayama234/morphoacoustics/pull/110#pullrequestreview-5546195786). The [normative complete handoff](./og5-gate-a-amendment-a1.md) and [complete fixtures](./og5-contract-goldens.json) define Snapshot and N×10 Observation fields/identity bytes, stable refusal codes and escaped-pointer precedence, revisions scoped per organ, and lawful vs malformed topology. The split-only connected v1 language admits trees; cycles are INVALID and a complete 7-organ/3-junction tree is the UNSUPPORTED control.

State/digest flow is Blueprint -> complete structural validation -> fixed capability -> recomputed immutable Snapshot -> rank-safe coupled solve -> atomic full Observation. Snapshot digests bind normalized anatomy/source/load; Observation digests bind exact ordered numeric outputs/diagnostics. Neither includes UI layout, timestamps or Git/CI metadata. Full SVD retains zeros; condition2<=1e4 and scaled equation residual<=1e-12 precede success. All 144 positive samples must succeed and pass independent full-state comparators; no refusal reduces the denominator. Child-slot permutation has a distinct bounded mapping identity but identical ideal junction physics; actual output identity swaps and signed/particle-velocity row mutants test numerical mistakes.

Standalone Python regeneration and an independent JavaScript encoder confirm full golden bytes/hashes; they do not implement Core validation. [A1 Wolfram receipt](./og5-wolfram-gate-a-a1-result.json) contains 144-case supplementary design maxima, eight mutant margins and numerical rank/condition/nonfinite refusals. Original 8-case exploration is preserved. No new production module, Studio support, new Core run, scientific adoption or merge is implied. Exact amended HEAD review must precede a separate Gate B Draft.


## OG-5 Gate A specification accepted — 2026-10-16 JST

Decision **ACCEPTED_FOR_GATE_B / SPECIFICATION_FROZEN**. [Acceptance and scope](./og5-gate-a-acceptance.md) supersedes the earlier pending status. Technical specification reviewed at `b7fb56c66236b0cbdb532fec8c75d46709c95bd0`; A1's schemas/bytes/refusal rules, fixed five-organ/two-junction fixture, 144/144 positive requirements and explicit numerical controls are frozen for a separate implementation trial. This accepts the design handoff only. Runtime tree5 support and scientific implementation adoption require Gate B execution and Gate C decision; #109 remains open. Original candidate receipts retain their historical status and hashes.

## OG-5 Gate B1 data boundary — 2026-10-16 (Draft)

An internal frozen `Tree5PhysicalSample` carries 10 complex p/U endpoint pairs, per-port signed mean power and Gate A numeric diagnostics; **this is not** the accepted public `og5.tree5.observation.v1` JSON payload. The B1 helper accepts explicit frozen fixture scalars, **not** `og5.passive.tree5.v1` Blueprints. Frozen v1 canonical digests, binding checks and 27 stable error receipts remain B2 acceptance obligations. See [Gate A A1](./og5-gate-a-amendment-a1.md) and [B1 report](./og5-gate-b1-trial.md).

**OG-5 B1 typing receipt:** Internal complex128 solver state remains an ndarray rather than a public serialized p/U observation. A `typing.cast` repairs static library typing only, with no data-model field added or canonical hashes changed. [Trial evidence](./og5-gate-b1-trial.md).

## Gate B2 contract checkpoint (2026-10-16; DRAFT)

OG-5 B2 now proposes a real strict `og5.passive.tree5.v1` adapter, three independent canonical SHA-256 identities, byte-encoded snapshot and full complex p/U observation; A1 is authoritative. [B2 implementation record](./og5-gate-b2-contract.md). Numerical computed fields remain distinct from immutable physical organ/revision metadata.

**OG-5 B2 contract fidelity checkpoint:** No API/schema/digest fixture change in the CI correction; response test passes the fixture's `frequencies_hz`, and duplicated organ ID rejects prior to deriving invalid connections. [Record](./og5-gate-b2-contract.md).

**B2 error state/data separation:** A1's six numerical seams produce `Tree5Error(status,code,path)` without partial Observation or digest, using matrix/solver fault injection in tests rather than making malformation part of the public physical blueprint. [Trial record](./og5-gate-b2-contract.md).
