# OG-4 branch3 v1 — normative Gate A API contract

**Amendment A1, 2026-10-16 JST, PR #107. DESIGN ONLY / NOT ADOPTED.**
This document completes RFC §§1, 2, 4 and the Gate B protocol. If the original
proposal is less specific, this amendment controls. No branch3 runtime is supplied.
Gate A ratification and the separate Gate B/C decisions remain pending.

## 1. Entry points and values

Future module: `morphoacoustics_graph.branch3`. Required interface:

```python
prepare_branch3(blueprint: dict[str, object]) -> PreparedBranch3
restore_branch3(snapshot: dict[str, object]) -> PreparedBranch3
PreparedBranch3.to_snapshot() -> dict[str, object]
PreparedBranch3.response(frequencies_hz: list[int | float]) -> dict[str, object]
```

Inputs use JSON-compatible dictionaries/lists. No implicit scalar broadcasting,
NumPy-array conversion, iterator consumption, tuple coercion, string-to-number
coercion or native Python complex values. JSON duplicate keys must be rejected
by any JSON adapter before constructing dictionaries. Every object has **exactly**
the listed keys; missing/extra keys are invalid. There are no omitted defaults or
optional fields. Numbers are built-in `int`/`float` excluding `bool`, converted once
to finite IEEE754 binary64 with round-to-nearest/ties-to-even (JSON adapters must
parse decimal numbers equivalently). Overflow, NaN and infinity are invalid.
Normalize every numeric zero to positive zero. All comparisons below use exact
converted binary64 values, not tolerance bands. Identifiers/revisions match
`[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}`; no Unicode normalization is involved.
Complex values are exactly `{"real": number, "imag": number}` in SI units;
strings, `[real,imag]`, polar forms and implicit imaginary zero are invalid.

Failure raises `Branch3Error(ValueError)` with string attributes `status`, `code`,
`path`; `str(error)` is `status + ":" + code + ":" + path`. Paths are JSON Pointers
(root is `""`); numerical failures use `/frequencies_hz/i`. No success object,
partial observation, digest, or cached result may escape on failure. Prepared
objects own immutable copies; every response/snapshot export revalidates their
blueprint, backend, mapping, reconstructed primitives and stored identities.
An edited/forged prepared object raises `INVALID:PREPARED_BINDING_MISMATCH` at root.
No identity is accepted solely because a stored hash looks well formed.

## 2. Blueprint schema: `og4.passive.branch3.v1`

| Object | Exact fields and structural rules |
| --- | --- |
| Blueprint | `schema` (literal above), `organs` (nonempty list), `junctions` (nonempty list), `source` (Source), `loads` (nonempty list of Load) |
| Organ | `id`, `revision` (identifiers); `length_m`, `area_m2`, `sound_speed_m_s`, `air_density_kg_m3` (positive finite numbers); `inlet`, `outlet` (Port) |
| Port | `id` (identifier), `kind="acoustic.p_u"`, `direction="inlet"` for inlet, `"outlet"` for outlet |
| Junction | `id` (identifier), `law` (`"ideal.series.p_u"` or `"ideal.branch3.p_u"`), `ports` (ordered port-ID list, respectively 2 or 3 entries) |
| Source | `kind="prescribed_volume_flow"`, `phasor_schema="og4.peak.exp_plus_i.v1"`, `port` (inlet port-ID), `amplitude_m3_s` (Complex), `scale` (finite real number) |
| Matched Load | `port` (outlet port-ID), `kind="matched"` |
| Release Load | `port` (outlet port-ID), `kind="pressure_release"` |
| Closed Load | `port` (outlet port-ID), `kind="rigid_closed"` |
| Fixed Load | `port` (outlet port-ID), `kind="fixed_impedance"`, `impedance_pa_s_m3` (Complex with `real>0`) |

`Z_i=(rho_i*c_i)/area_i` and `1/Z_i` must be representable finite positive
binary64 (evaluate in that order). The scaled source's real/imaginary components
must remain finite. Zero source is structurally legal but outside v1 capability.
Fixed impedance is a frequency-independent passive complex impedance, `p=Z_load U`;
only the specific real baseline load below is supported in v1. Do not encode
closed loads as infinite impedance, or release loads as a zero fixed impedance.
Matched is `p=Z_i U`, derived from the **loaded organ's** medium and area each time;
it forbids an explicit impedance field. Release is `p=0`; closed is `U=0`.
The source imposes `U_A.in=amplitude_m3_s*scale`, a harmonic peak phasor using
`exp(+i omega t)`. It is a prescribed flow, not a pressure or Thevenin source.

Organ IDs are unique among organs, junction IDs among junctions, and port IDs
among all ports (the three namespaces are distinct). Each port is assigned
**exactly once** to a junction, source or load. All references must resolve.
Junction `ports[0]` belongs to an outlet; other entries to inlets of different
organs. Duplicate assignments, self-connections, missing boundaries, unknown laws,
wrong directions and disconnected undirected graphs are invalid. Traverse
iteratively. A structurally connected cycle or a larger valid graph is unsupported,
not simulated. Organ/junction/load collection order is irrelevant; junction port
order is semantic. ID labels are physical identity, not display metadata.

### Exact v1 capability after full structural validation

Require organs with IDs A/B/C (any valid revision), ports `A.in,A.out,B.in,B.out,C.in,C.out`,
one junction `id="J",law="ideal.branch3.p_u",ports=["A.out","B.in","C.in"]`,
source at A.in and loads at B.out/C.out. No other organs/ports/junctions/boundaries.
Require lengths A=.08, B=.09, C=.06 m; A/B areas=.0003 m²;
C area in {.00015,.0003,.0006} m²; each rho=1.2 kg/m³ and c=343 m/s.
Require source amplitude `{"real":0.000001,"imag":0.0000004}` and scale
in {1,.5,-1}; separate amplitude/scale fields remain distinct identity even when
products could coincide. B load must be matched; C may use any Load variant, but
fixed C must be exactly `{"real":1372000,"imag":0}` Pa·s/m³. This equals the
baseline `1.2*343/.0003`, independent of the current C area. Matched C is respectively
2744000, 1372000, 686000 at the three supported areas. Matched and fixed remain
**different identities even at baseline**, where their numerical solutions coincide.
Other structurally legal source/load/geometry/topology choices are unsupported.

### Snapshot: `og4.branch3.prepared.snapshot.v1`

Exact keys: `schema` (this literal), `digest_version="og4.canonical.binary.v1"`,
`backend_id="og4.fixed.passive.branch3.pu.v1"`, `blueprint` (full Blueprint),
`blueprint_digest`, `preparation_digest` (each `sha256:` plus 64 lowercase hex).
`restore_branch3` validates every field and the embedded graph, prepares a fresh
independent object, recomputes both hashes and compares them. No matrix, object
address, pickle, cached result or opaque solver state is deserialized. Hash mismatch
is `INVALID:SNAPSHOT_DIGEST_MISMATCH` at the mismatching hash field. A well-typed
unknown backend/digest version is `UNSUPPORTED:SNAPSHOT_VERSION` at its field.
An unknown snapshot schema is `UNSUPPORTED:SNAPSHOT_SCHEMA` at `/schema`.
Malformed envelope keys/types/hash spellings are invalid before these decisions. If both version/backend are unsupported, check digest_version before backend_id. If both hashes mismatch, report blueprint_digest first.

### Old fixed2 and unknown schema refusal

A blueprint declaring `og3.passive.fixed2.v1` is parsed with the existing OG-3
snapshot parser and structural `validate_graph`, **not** its backend capability
check. Preserve any invalid structure as `INVALID:LEGACY_INVALID` (path root).
If structurally valid, refuse `UNSUPPORTED:SCHEMA_NOT_BRANCH3` at `/schema`.
Never upgrade rho, invent a C tube/load/source or silently call fixed2. This also
applies to a well-formed `og3.prepared.snapshot.v1` at `restore_branch3`: validate
its legacy envelope/graph/digests using OG-3 restoration, then refuse
`UNSUPPORTED:SCHEMA_NOT_BRANCH3` at `/schema`. Unknown schema strings are refused
`UNSUPPORTED:UNKNOWN_SCHEMA` at `/schema`; schema absence/wrong type is invalid.
Existing OG-3 APIs, schema/digests and branch refusal are unchanged.

## 3. Response shape, bounds and deterministic refusal order

Only a **nonempty one-dimensional built-in list** is accepted, length 1..256.
Nested lists, scalar, bool, string, complex, NaN, infinity and negative Hz are
invalid. All elements are type-checked before casting; order and duplicates are
preserved, without sorting/deduplication of returned samples or hashed frequencies.
Supported Hz = {80,250,400,733,997,1200,2000,4000}; exact membership after conversion.
Zero (including -0.0) is valid nonnegative input, but unsupported frequency.
A 256-element repeated grid is supported. A well-typed 257-element repeated grid
is `UNSUPPORTED:FREQUENCY_POINT_LIMIT` at `/frequencies_hz`. Check every input
value for invalidity before this size refusal; allocate no result arrays first.

Validation phases, in order (stop at first failing phase):

1. Prepared binding (or blueprint/snapshot envelope, schema dispatch and graph
   validation at prepare/restore). For known branch3 graph, complete all field,
   numeric, ID/reference and connectivity checks before any capability refusal.
2. Blueprint capability: topology/port labels, medium, dimensions, source, loads,
   in that order, using codes `BRANCH3_TOPOLOGY_ONLY`, `FROZEN_MEDIUM`,
   `FROZEN_GEOMETRY`, `FROZEN_SOURCE`, `FROZEN_LOAD` and paths respectively
   `/junctions`, `/organs`, `/organs`, `/source`, `/loads` (all UNSUPPORTED).
3. Response shape/element validity (`INVALID:FREQUENCY_SHAPE` or
   `INVALID:FREQUENCY_VALUE`); shape failures always use `/frequencies_hz`, value failures `/frequencies_hz/i`. First check the list is nonempty and has no list-valued elements (otherwise shape failure), then scan scalar elements in index order.
4. Point count limit, then first unsupported Hz in original index order
   (`UNSUPPORTED:FREQUENCY_NOT_YET_VERIFIED`, `/frequencies_hz/i`).
5. Numerical evaluation in request order. Nonfinite condition or `cond_2(M)>1e8`,
   rank/solve failure, nonfinite state or nonfinite diagnostic -> `NUMERICALLY_UNRESOLVED:CONDITION_OR_SOLVE`;
   backward residual >1e-12 -> `NUMERICALLY_UNRESOLVED:BACKWARD_RESIDUAL`;
   pressure/flow/power errors >1e-10 -> `NUMERICALLY_UNRESOLVED:PHYSICAL_RESIDUAL`.
   Return one complete observation only after every sample passes. Never damp,
   clip, substitute least squares, or return a success for a filtered subset.

Other structural failures use `INVALID:BLUEPRINT_STRUCTURE` at the failing field.
For multiple structural failures choose the lexicographically smallest JSON Pointer
(ASCII order) after the structural scan. Unknown keys are reported at their own
pointer; missing keys at the missing field's pointer. Relational failures use
`/organs` (duplicate organ/port IDs), `/junctions` (duplicate junction IDs,
self-connection, wrong junction assignment), `/source/port` or `/loads` (bad
boundary assignment), or root (unassigned port/disconnected graph). Malformed
snapshot envelopes use `INVALID:SNAPSHOT_STRUCTURE`. Early type failures stop
traversal of that subtree but do not skip validly structured siblings. An invalid
subpart of a larger unsupported graph still wins over topology refusal.

Examples: `[733]*257 + [True]` -> INVALID at index 257;
`[0]*257` -> point-limit refusal; `[733,0]` -> unverified frequency at index 1;
`[[733]]` -> shape invalid; empty list -> shape invalid. No arbitrary multidimensional
batch shape or unbounded output is implied.

## 4. Successful observation: `og4.branch3.observation.v1`

Exact fields:

| Field | Meaning/shape |
| --- | --- |
| `schema`, `status` | literal above, `"OK"` |
| `digest_version`, `backend_id` | literals from snapshot |
| `preparation_digest` | prepared identity |
| `frequencies_hz` | converted list length N, same order/duplicates as request |
| `port_ids` | exactly `["A.in","A.out","B.in","B.out","C.in","C.out"]` |
| `pressure_pa`, `volume_flow_m3_s` | each N rows × 6 Complex values, aligned with port_ids |
| `mean_power_w` | N rows × 6 real finite values, `.5*Re(p*conj(U))` at each oriented port |
| `diagnostics` | N objects, exact keys `condition_2`, `backward_error`, `junction_pressure_error`, `junction_flow_error`, `power_error`; finite nonnegative numbers |
| `observation_digest` | hash specified below |

At N=256 output is at most 3072 Complex values, 1536 powers, 1280 diagnostics,
and 256 frequencies (9216 binary64 real components total). No optional full matrix,
permutation expansion, per-sample repeated blueprint or unbounded diagnostic text.
Numerical success is a software result, not physiological or adoption approval.

Diagnostic definitions: `p_ref=Z_A*1e-6`, `U_ref=1e-6`. State order per A,B,C is
`(p_in/p_ref,U_in/U_ref,p_out/p_ref,U_out/U_ref)`. The fixed diagnostic M has rows
0..5: two inlet-minus-UniformTube-transfer(outlet) equations per tube, pressure
rows divided by p_ref, flow rows by U_ref. Rows 6,7: A.out pressure minus B.in/C.in
pressure; row 8: A.out flow minus B.in minus C.in flow. Rows 9,10: B/C outlet
`p_hat-(Z_load/Z_A)*U_hat=0`, or `p_hat=0` for release, `U_hat=0` for closed.
Row 11: A.in flow, rhs=`source/U_ref`. Other rhs entries zero. No additional row
rescaling for diagnostics. `condition_2=sigma_max(M)/sigma_min(M)`;
`backward_error=||Mx-b||_inf/max(||M||_inf*||x||_inf+||b||_inf,1e-300)`.
Pressure error is max of the two J pressure differences / p_ref; flow error is
`abs(U_A.out-U_B.in-U_C.in)/U_ref`; power error is
`abs(P_A.in-P_B.out-P_C.out)/(.5*p_ref*U_ref*abs(scale)^2)`.
Other solver algorithms must report these same diagnostics from reconstructed
physical equations, not from a differently scaled private system.
The singular fixture is a **test-only harness**, never a public flag bypassing
capability/frequency validation; it uses the same diagnostic equations and refusal.

## 5. Canonical bytes and digest ABI

`digest_version="og4.canonical.binary.v1"`. Let `u32(n)` be 4-byte unsigned
big-endian integer, `||` byte concatenation. No whitespace, JSON text, locale,
platform repr, end marker or newline is involved. Encode recursively:

```text
E(number) = 0x64 || IEEE754_binary64_big_endian(normalized_number)   # ASCII d
E(string) = 0x73 || u32(ASCII byte length) || ASCII bytes             # ASCII s
E(list)   = 0x6c || u32(item count) || E(item0) || ...                # ASCII l
E(object) = 0x6d || u32(key count) || E(key0) || E(value0) || ...     # ASCII m
```

Object keys sorted by unsigned ASCII bytes, strictly increasing; strings are
ASCII, including identifiers, schema/version IDs and lowercase digest strings.
All numeric fields (geometry, medium, source amplitude/scale, fixed impedance,
frequencies, response real/imag, powers and diagnostics) use `E(number)`, even
integer-looking JSON values. Normalize **all** signed zeros before encoding.
`bool`, null, tuples and unsupported types have no encoding. Counts/lengths are
u32 framing, never encoded as floating-point values. Invalid data is never hashed.

`H(domain,payload)="sha256:" + lowercase_hex(SHA256(ASCII(domain)||0x00||E(payload)))`.
Domains are exactly:

| Identity | Domain | Complete payload |
| --- | --- | --- |
| blueprint_digest | `morphoacoustics.og4.blueprint.v1` | Entire Blueprint, all fields in §2; sort organs by id, junctions by id, loads by port; retain each junction's ordered ports |
| preparation_digest | `morphoacoustics.og4.preparation.v1` | Exact object `{digest_version,backend_id,blueprint_digest,port_mapping}`; port_mapping = six `[port_id,organ_id,direction]` rows in observation port order |
| observation_digest | `morphoacoustics.og4.observation.v1` | Entire §4 observation **except observation_digest itself**, including schema/status, backend/version, prep identity, ordered frequencies/ports, every p/U component, every power and diagnostic |

The preparation mapping is exactly `[["A.in","A","inlet"],["A.out","A","outlet"],
["B.in","B","inlet"],["B.out","B","outlet"],["C.in","C","inlet"],
["C.out","C","outlet"]]`. Snapshot redundant fields are validated, not separately
hashed. Snapshot schema is fixed by the restore entry point. No display names,
creator/script, timestamps, git SHA, runtime version or CI URL enter these three
physical/observation identities. Evidence manifests must bind those provenance
fields **separately**; digest equality alone cannot prove fresh execution.
Exact observation digests can differ across runtimes if numerical last bits differ;
only identical component bits yield identical digests. Physics uses tolerances.

[Golden inputs, canonical bytes and hashes](./og4-branch3-api-golden.json) cover all
three domains, four load variants, source scale/area changes and signed zero.
[Executable encoding check](./og4-branch3-api-vectors.py) must pass unchanged in
Gate B; a non-Python implementation must reproduce the same bytes/hashes before
claiming ABI interoperability. A [standalone JavaScript encoding check](./og4-branch3-api-vectors.cjs) is also provided (`node docs/research/og4-branch3-api-vectors.cjs`); Python and JavaScript were cross-checked on all 11 vectors. Observation vector inputs omit their self-digest; append the recorded `digest` as `observation_digest` for the complete object. The marked synthetic observation tests encoding
only, not acoustic correctness. Neither this check nor its data is a backend.
