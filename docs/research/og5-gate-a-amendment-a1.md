# OG-5 Gate A Amendment A1 — complete bounded handoff

2026-10-16 JST. Disposition: **GATE A ACCEPTED / SPECIFICATION FROZEN / NO RUNTIME ADOPTION**.
Addresses [PR #110 review R1–R4](https://github.com/ryonakayama234/morphoacoustics/pull/110#pullrequestreview-5546195786).
This amendment is normative over conflicting original draft language in the
[API](./og5-tree5-api-v1.md) and [protocol](./og5-gate-a-protocol.md). [Gate A acceptance](./og5-gate-a-acceptance.md) authorizes a separate Gate B
implementation trial. It does not alter OG3/OG4 or claim a Core execution.
The original eight [records](./og5-wolfram-gate-a-result.json) stay byte-identical.

## A1.1 Exact values and structural language (R1, R2)

The original Blueprint key layout remains unchanged. All objects are exact-key
built-in dicts with built-in ASCII string keys (a non-string or non-ASCII key reports
INVALID_STRING at its containing object path); all arrays are built-in lists. No
subclasses, tuples, bool-as-number, coercions, unknown keys or omitted fields.
All numbers are built-in int/float converted once by round-to-nearest binary64;
overflow/nonfinite conversion is INVALID. Normalize either signed zero to +0.0.
Physical positive fields must remain positive after conversion. IDs and revisions
match `[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}` by full match. Schema/backend/digest/law/
kind markers are nonempty ASCII strings of at most 128 bytes; their supported
values are checked at capability time, except physical type/direction below.
Digest text matches `sha256:[0-9a-f]{64}`. Revisions may repeat across organs;
only organ IDs, junction IDs within their own namespaces, and port IDs globally
must be unique. No uniqueness requirement applies to revision strings.

The common Blueprint envelope always has exactly `schema,organs,junctions,source,loads`.
All schema markers, including unknown versions, go through this adapter's same
common v1 field/shape validation and structural checks before the version check.
This is a bounded envelope reader, not a decoder for arbitrary future layouts.
Each organ has exactly the eight fields in the original Blueprint schema;
each Port has `id,kind,direction`; each Junction has `id,law,ports`; each Source
has `kind,phasor_schema,port,amplitude_m3_s,scale`; each Load has `port,kind`.
`amplitude_m3_s` has `real,imag`. `organs` and `loads` are nonempty; `junctions`
may be empty. Junction `ports` has exactly three string references, even if its
law marker is unsupported. Source amplitude and scale need only be finite for
structural validity; the original fixed values are a capability constraint.

An inlet Port has `kind=acoustic.p_u,direction=inlet`; an outlet Port has
`kind=acoustic.p_u,direction=outlet`. A differently typed Port is INVALID, not
a supported acoustic-to-other-domain transducer. Source binds one inlet, loads
bind outlets, and each junction binds one parent outlet followed by inlets of
two distinct other organs. Every endpoint has exactly one external binding
(source, load or junction); a tube's internal inlet/outlet relation is not such
a binding. All references resolve. The undirected organ graph must be connected
and acyclic. Validate iteratively over the entire input before capability.

Thus valid graphs are rooted binary trees: n=2j+1, number of loads=j+1 and
number of organ-to-organ edges=2j=n-1. A cycle is INVALID:GRAPH_CYCLE;
it is not a valid-but-unsupported input in this split-only v1 language. A valid
7-organ/3-junction tree is UNSUPPORTED:TOPOLOGY_NOT_SUPPORTED. The fixtures contain
both a cycle with all endpoints singly bound (necessarily disconnected from the
source component), and a connected valid 7-organ tree. Cycle detection precedes
connectedness so the former has a deterministic GRAPH_CYCLE receipt.

Exact fixed capability is the original five named organs/geometries, J1/J2,
rho=1.2, c=343, source amplitude/scales, loads and frequency anchors. Comparison
is on normalized binary64 values, with no approximate geometry matching.
The two child slots are exchangeable *physically*, but their recorded order is
part of this bounded API's mapping/identity. A child-slot reversal has a distinct
Blueprint digest and is UNSUPPORTED:TOPOLOGY_NOT_SUPPORTED for fixed tree5;
it is not a numerical wrong-law control. Collections organs/junctions/loads are
sorted only for canonical identity, by id/id/port respectively. Requests preserve
frequency order and duplicates after numeric normalization.

## A1.2 Complete snapshot, observation and hash bytes (R1)

PreparedTree5 is an opaque immutable value. `to_snapshot()` returns fresh copies
of this exact object, with no solver cache, live state, coordinates or timestamps:

```text
Snapshot {
 schema: "og5.tree5.prepared.snapshot.v1",
 digest_version: "og5.canonical.binary.v1",
 backend_id: "og5.fixed.passive.tree5.pu.v1",
 blueprint: normalized canonical Blueprint,
 blueprint_digest: Digest,
 preparation_digest: Digest
}
```

Canonical bytes are exactly the API's d/s/l/m encoder: d+f64be, s+u32be byte length+
ASCII, l+u32be count+values, m+u32be pair count+ASCII-byte-sorted encoded key/value
pairs. Numbers always encode as d, including counts stored as data; structural
lengths use u32be. No bool/null/native-complex encoding exists. Do not serialize
JSON text before hashing. Let H(domain,payload) be `sha256:` followed by lowercase
SHA256 of ASCII(domain), a single zero byte, then the canonical payload bytes.

| Identity | Domain | Exact payload |
| --- | --- | --- |
| blueprint_digest | morphoacoustics.og5.blueprint.v1 | complete normalized Blueprint, three collections sorted |
| preparation_digest | morphoacoustics.og5.preparation.v1 | map with exactly schema,digest_version,backend_id,blueprint_digest from Snapshot |
| observation_digest | morphoacoustics.og5.observation.v1 | complete Observation below excluding only observation_digest |

Restoration validates the whole snapshot/nested blueprint, checks capability,
recomputes Blueprint hash then preparation hash in that order, and constructs
the mapping from normalized semantic data. A reordered input collection is
normalized on restore; the returned snapshot is canonical even if the input JSON
was not ordered. Never trust a stored mapping/cache.
Syntactically correct hashes cannot attest authorship: a valid supported payload
with correctly recomputed identities can be restored regardless of its origin.
An inconsistent payload/hash or a corrupted in-memory prepared binding is refused.
Before each response/to_snapshot, reconstruct the binding from the stored
normalized snapshot; no mutable caller input or forged cache is authoritative.

```text
Observation {
 schema: "og5.tree5.observation.v1",
 digest_version: "og5.canonical.binary.v1",
 backend_id: "og5.fixed.passive.tree5.pu.v1",
 blueprint_digest: Digest,
 preparation_digest: Digest,
 status: "SUCCESS",
 frequencies_hz: [N normalized binary64 numbers],
 port_ids: ["A.in","A.out","B.in","B.out","C.in","C.out",
            "D.in","D.out","E.in","E.out"],
 pressure_pa: [N rows of 10 Complex],
 volume_flow_m3_s: [N rows of 10 Complex],
 mean_power_w: [N rows of 10 binary64 numbers],
 diagnostics: [N Diagnostic objects],
 observation_digest: Digest
}
Complex {real: binary64, imag: binary64}
Diagnostic {
 condition_number_2: binary64,
 scaled_linear_residual: binary64,
 j1_scaled_pressure_residual: binary64,
 j2_scaled_pressure_residual: binary64,
 j1_scaled_flow_residual: binary64,
 j2_scaled_flow_residual: binary64,
 relative_power_defect: binary64
}
```

All output numbers must be finite normalized binary64; all power values are
signed `0.5 Re(p conjugate(U))` with positive tube inlet-to-outlet orientation,
including closed terminals' unmodified roundoff. No numerical clipping. Source
power is mean_power_w[row][0]; terminal powers are columns 5,7,9. There are no
additional source/terminal aggregates or runtime metadata inside the Observation.
Any evidence Git SHA, oracle SHA, kernel/platform version, CI run, timestamp or
review receipt belongs to an outer evidence record, not these physical identities.
Diagnostics and exact output bytes enter observation identity; separate solvers
may produce different hashes while agreeing numerically. Golden Observation
bytes test serialization of the *provided constants*, not bit-identical physics
across platforms. Runtime-vs-oracle comparisons use A1.4 tolerances.

The [complete goldens](./og5-contract-goldens.json) contain baseline/changed
revision/changed area/source sign/source half/closed load/reordered collections/
signed-zero inputs (canonicalization only; its illustrative snapshot is outside
fixed source capability and cannot be restored), complete supported snapshots,
one complete 733-Hz Observation made
from the original exploratory constants, a reordered+duplicate request
Observation, and raw canonical hex plus domain-prefixed hex and hashes. Each
variant includes its complete input rather than a prose-only mutation recipe.
[Python generator/verifier](./og5-contract-fixtures.py) and
[independent JavaScript verifier](./og5-contract-fixtures.mjs) are standalone
design tools; neither implements a production prepare/restore/response API.

## A1.3 Stable refusal contract and precedence (R1, R2)

Expected refusals raise `Tree5Error(ValueError)` with string fields
`status,code,path`; exact message is `status + ":" + code + ":" + path`.
Its error receipt is exactly `{status,code,path}` with no partial observation or
digest. RFC6901 root path is the empty string, not `/`; tokens escape `~` as
`~0` then `/` as `~1`. INVALID is malformed input/binding, UNSUPPORTED is lawful
but outside this adapter's capability, NUMERICALLY_UNRESOLVED is a supported
sample the numerical solver cannot certify. Infrastructure crashes are FAILED
at the job layer and must not be fabricated as Tree5Error or successful physics.

Operation ordering:

1. prepare: collect all common-envelope/shape/scalar errors, then all reference/
   uniqueness/binding/direction errors, then cycle, then disconnectedness, then
   capability. A phase error stops before the next phase. Within a phase choose
   lexicographically lowest *escaped* JSON Pointer in ASCII byte order; if code
   candidates share a path, use the table order below. Do not stop at the first
   visited leaf or sort the original arrays before validation. Duplicate IDs
   report each later occurrence's id path; unresolved ref uses its reference path;
   duplicate binding reports the lexically later of its binding-reference paths;
   an unbound endpoint reports its defining Port id path. All relationship
   candidates are collected before choosing. If a parent value has invalid shape,
   report that path and do not invent errors inside it.
2. restore: validate snapshot envelope and nested Blueprint in the same phases,
   prefixing nested paths `/blueprint`. Snapshot marker fields and digest syntax
   are shape/scalar checks; exact version/backend capability is checked only after
   structural validity. Then check Blueprint capability, blueprint_digest and
   preparation_digest. A hash mismatch reports that hash field's path. No partial
   restoration. A wrong field value with valid type is not silently ignored.
3. response/to_snapshot: verify/reconstruct the receiver first. Any inconsistent
   or structurally/capability-invalid receiver becomes INVALID:
   PREPARED_BINDING_INVALID at `/prepared`. After a valid receiver, response scans
   *all* frequency scalar errors before count or anchor capability. Empty request
   is INVALID; >256 fully valid samples is UNSUPPORTED, never truncation. Then
   check all anchors and evaluate in request order. On any numeric failure, return
   one error at `/frequencies_hz/i` for the first failing requested sample and no
   Observation/digest, even if previous samples succeeded.

| Status | Code (tie order) | Path / trigger |
| --- | --- | --- |
| INVALID | EXPECTED_OBJECT | offending object or root |
| INVALID | EXPECTED_LIST | offending array |
| INVALID | MISSING_FIELD | missing member path |
| INVALID | UNKNOWN_FIELD | escaped unknown member path |
| INVALID | INVALID_STRING | string type/ASCII/length/identifier/digest syntax |
| INVALID | INVALID_NUMBER | numeric type, bool, overflow, NaN, infinity |
| INVALID | NUMBER_OUT_OF_RANGE | nonpositive geometry; negative frequency |
| INVALID | INVALID_CARDINALITY | empty organs/loads or junction ports length !=3 |
| INVALID | PORT_TYPE_MISMATCH | offending Port.kind |
| INVALID | PORT_DIRECTION_MISMATCH | offending Port.direction |
| INVALID | DUPLICATE_ID | later organ/junction/Port id |
| INVALID | UNKNOWN_PORT | reference path |
| INVALID | DUPLICATE_BINDING | later binding-reference path |
| INVALID | UNBOUND_PORT | defining Port id path |
| INVALID | INVALID_CONNECTION | wrong source/load endpoint direction or junction reference roles/owners |
| INVALID | GRAPH_CYCLE | /junctions (or /blueprint/junctions) |
| INVALID | GRAPH_DISCONNECTED | /organs (or /blueprint/organs) |
| INVALID | IDENTITY_MISMATCH | /blueprint_digest, then /preparation_digest |
| INVALID | PREPARED_BINDING_INVALID | /prepared |
| INVALID | EMPTY_REQUEST | /frequencies_hz |
| UNSUPPORTED | VERSION_NOT_SUPPORTED | /schema, /digest_version, nested /blueprint/schema or source phasor_schema |
| UNSUPPORTED | BACKEND_NOT_SUPPORTED | /backend_id |
| UNSUPPORTED | LAW_NOT_SUPPORTED | offending Junction.law |
| UNSUPPORTED | SOURCE_NOT_SUPPORTED | /source or /blueprint/source |
| UNSUPPORTED | LOAD_NOT_SUPPORTED | offending Load.kind |
| UNSUPPORTED | TOPOLOGY_NOT_SUPPORTED | /organs or /blueprint/organs |
| UNSUPPORTED | GEOMETRY_NOT_SUPPORTED | offending geometry scalar |
| UNSUPPORTED | REQUEST_TOO_LARGE | /frequencies_hz |
| UNSUPPORTED | FREQUENCY_NOT_SUPPORTED | offending frequency index |
| NUMERICALLY_UNRESOLVED | NUMERIC_NONFINITE | /frequencies_hz/i |
| NUMERICALLY_UNRESOLVED | MATRIX_RANK_DEFICIENT | /frequencies_hz/i |
| NUMERICALLY_UNRESOLVED | MATRIX_ILL_CONDITIONED | /frequencies_hz/i |
| NUMERICALLY_UNRESOLVED | SOLVE_FAILED | /frequencies_hz/i |
| NUMERICALLY_UNRESOLVED | RESIDUAL_TOO_LARGE | /frequencies_hz/i |
| NUMERICALLY_UNRESOLVED | POWER_CHECK_FAILED | /frequencies_hz/i |

Within capability checks use table order, then lowest escaped pointer, except
restore checks outer versions, backend, then nested Blueprint capability. For
frequencies check oversize before unsupported anchors, after all malformed values.
Numeric check order is table order, except rank/condition precede attempting the
solve; nonfinite matrix/SVD first, then rank, then condition, then solve status,
then finite solution/metrics, residuals and power. Expected linear-algebra
nonconvergence maps to SOLVE_FAILED; unexpected software bugs remain FAILED.
JSON duplicate member keys must be rejected by the JSON adapter *before* dict
construction, as INVALID:DUPLICATE_JSON_KEY at the duplicate escaped member path.
This additional adapter code precedes the dict API and is not reconstructible
from a dict that has already lost duplicate keys. The fixture includes raw JSON.

The goldens include complete input/error receipts for malformed+unsupported
combinations, >256 requests with a late bool, escaped-key ordering, forged hashes,
snapshot extra fields, unknown version, cycle and legal larger topology. They
are normative future Gate B assertions, not evidence of an implemented validator.

## A1.4 Rank-safe numerical decision, exact norms and positive cases (R3)

Use the original 20 unknown/20 equation order in og5-wolfram-gate-a.wl. Scaled
variables P=p/p_ref, Q=U/U_ref; p_ref=1.372 Pa, U_ref=1e-6 m³/s, z_ref=1372000
Pa s/m³, all independent of source scale. These mathematical reference constants
are rounded once from decimal literals for the backend; the historical oracle
may differ by floating-point roundoff when deriving them algebraically. Identity
goldens hash supplied output constants rather than recomputing arithmetic.
In each tube row use z=Z/z_ref and
the original cos/sin matrix; junction/source rows have coefficients ±1 and the
source RHS scale*(1+0.4i); matched load row is P-z Q=0, closed load row Q=0.
No additional row equilibration enters reported condition/residual metrics.
Row order is A..E two tube rows, J1 pressure/pressure/flow, J2 likewise, source,
then C/D/E loads. Column order A.in p,U; A.out p,U; then B..E likewise.

Get all 20 singular values including zeros (`SingularValueList[M,Tolerance->0]`
in Wolfram or full NumPy SVD). Invalid count or nonfinite M/SVD is numerically
unresolved; sigma_min<=20*binary64_epsilon*sigma_max is MATRIX_RANK_DEFICIENT;
otherwise condition2=sigma_max/sigma_min. Refuse condition2>1e4. This supersedes
the draft 1e10 guard: the complete 144 design cases have max ~223.743, leaving
over 44x headroom without accepting a conditioning level with kappa*epsilon
~2.22e-6. Condition is a refusal guard, not a proof of forward accuracy.

For each supported sample, require all normalized tube/junction/source/terminal
equations and full independent comparator checks as follows:

| Metric | Exact formula | Required bound |
| --- | --- | --- |
| Full-state error | max over 10 ports of abs(p-p_oracle)/p_ref and abs(U-U_oracle)/U_ref | <=1e-10, scored separately against global and recursive paths |
| Linear residual | max(abs(M.x-b)), scaled complex absolute infinity norm | <=1e-12 |
| J pressure residual | max(abs(Pparent-Pchild1),abs(Pparent-Pchild2)) | <=1e-10 per J |
| J flow residual | abs(Qparent-Qchild1-Qchild2) | <=1e-10 per J |
| Power floor F | 0.5*p_ref*U_ref*abs(scale)^2 | strictly positive for supported scales |
| relative_power_defect | abs(Psrc-Pc-Pd-Pe)/max(abs(Psrc),F) | <=1e-10 |

Source mean power must be >0; each matched terminal >=-1e-10*F; absolute closed
terminal power <=1e-10*F. Violations are POWER_CHECK_FAILED. Residual violations
are RESIDUAL_TOO_LARGE. Comparator error belongs to the Gate B scientific scorer,
not to production code importing an oracle. Supported numerical refusal is
allowed at runtime but is **not a passed positive scientific case**.

Gate B positive acceptance requires **144/144 successful supported samples**,
each with all 20 complex values passing each independent path, plus the eight
archived comparisons scored separately. Any missing/refused/nonfinite positive
sample makes that gate INCONCLUSIVE (or REJECT if a wrong-law discrepancy is
established); never reduce the denominator. Request-repeat/order/identity and
all required negative controls must also pass. Shared already-seen samples are
not independent statistical trials. These are numerical conformance experiments,
not a population hypothesis test or evidence of biological voice.

## A1.5 Effective negative controls and singularity reachability (R4)

Every numerical wrong-law mutant uses the same unchanged supported Blueprint and
reference: f=733 Hz, C area=.00015, matched C/D/E, source scale=1. Change only the
specified assembled row or the output identity assignment, after validation.
Do not mutate the oracle. Each must produce full-state comparator error >1e-6
or an explicit numeric refusal; an unexpected crash is a failed control, not a
successful refusal. These numerical mutants are design-only test seams, never
new production input flags. The fresh A1 Wolfram receipt records their margins.

| Control | Exact mutation | Expected signal |
| --- | --- | --- |
| wrong J1 sign | Q_Aout-Q_Bin+Q_Cin=0 | full-state difference/refusal |
| wrong J2 sign | Q_Bout-Q_Din+Q_Ein=0 | full-state difference/refusal |
| particle-velocity J1 | Q_Aout-Q_Bin-Q_Cin*area_A/area_C=0 | unequal-area full-state difference/refusal |
| particle-velocity J2 | Q_Bout-Q_Din-Q_Ein*area_B/area_E=0 | unequal-area full-state difference/refusal |
| pressure sign | first J1 pressure row P_Aout+P_Bin=0 | full-state difference/refusal |
| endpoint reversal | exchange A.in and A.out column assignments only in A's two tube rows; source/J remain unchanged | full-state difference/refusal |
| wrong C load | replace C matched z_C by z_C/2 in its terminal row | full-state difference/refusal |
| output identity swap | exchange D.out and E.out reported p/U and power columns, leaving port_ids unchanged | full-state difference; control is not child-slot permutation |

Changing Blueprint C area, source scale or revision is instead a lawful input/
identity control. Area changes must alter response and digest. Scale .5/-1 must
scale p/U by .5/-1 and mean powers by .25/1 within the same fixed tolerances.
Revision-only and collection-order/signed-zero changes have exactly the documented
identity effects and no physical effect. Child-slot permutation is an identity/
unsupported-capability test, with analytically invariant junction equations.

Numerical refusal tests must reach the solver after accepting the unchanged
Blueprint and frequency anchors. At the solver boundary, inject matrices in an
isolated test double:

- rank defect: replace row 20 with row 19 and RHS 20 with RHS 19; expected
  MATRIX_RANK_DEFICIENT before solving, never finite condition inferred from a
  truncated singular-value list;
- ill-conditioning: use diag(1,...,1,1e-5) as the 20x20 coefficient matrix with
  finite RHS; rank is full but condition=1e5, expected MATRIX_ILL_CONDITIONED;
- nonfinite: insert NaN in one coefficient; expected NUMERIC_NONFINITE;
- solver failure: inject the linear algebra backend's explicit convergence
  failure; expected SOLVE_FAILED, not a swallowed programming exception;
- residual: alter one returned solution coordinate by 1e-3 while leaving M/b
  unchanged; expected RESIDUAL_TOO_LARGE;
- atomicity: request [733,997], inject the rank defect only for sample index 1;
  exact error path `/frequencies_hz/1`, no earlier sample payload or digest.

An unsupported frequency or geometry is a capability refusal and cannot stand in
for any of these controls. Gate B must execute real rank and late-sample paths;
merely mocking the condition-number function does not meet this requirement.

## A1.6 Reproduction and review disposition

Run `python docs/research/og5-contract-fixtures.py --check` then
`node docs/research/og5-contract-fixtures.mjs`. Run the A1 Wolfram script with
the sibling original source available. The standalone full-port pressure-node
review is archived as `og5-review-nodal.py`; it imports no production Core code.
Fixtures and supplementary receipts are source-only design evidence. The exact technical revision and final design acceptance are recorded in
og5-gate-a-acceptance.md. Algorithmic comparison and owner-authorized AI technical
review do not constitute an independent human signoff or Core runtime adoption.
