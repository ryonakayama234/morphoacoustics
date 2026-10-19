# OG-4 Gate A / Gate B acceptance protocol — design frozen BEFORE new Core backend

**Recorded:** 2026-10-16 JST. **State:** candidate acceptance plan / amended after four Codex findings; ratification pending; no OG-4 production implementation exists. Parent [#106](https://github.com/ryonakayama234/morphoacoustics/issues/106). **Preserve original OG-1 [PROTOCOL.md](../../experiments/038_og1_passive_branch/PROTOCOL.md), [Wolfram/oracle](../../experiments/038_og1_passive_branch/wolfram/oracle.json), and OG-3 experiment oracles exactly.** This plan is author-proposed, with known OG-1 results disclosed in advance, so it is **controlled inheritance**, not a blind newly preregistered experiment.

## Exact inherited canonical benchmark

```text
Common rho = 1.2 kg/m³; c = 343 m/s; harmonic sign e^(+i ωt)
A: (L=0.08m, Area=0.0003m²), B: (0.09m, 0.0003m²)
C: (0.06m, Area = {0.00015,0.0003,0.0006}m²)
J edge: one A.out → {B.in,C.in}, signed junction U_A.out=U_B.in+U_C.in
Source: U_A.in=1e-6*(1+0.4i) m³/s (scale 1,0.5,-1)
B outlet: matched. C outlet: matched, pressure_release, rigid_closed,
   fixed_impedance equal to baseline C impedance.
Original OG-1 frequency set (8): 80,250,400,733,997,1200,2000,4000 Hz
Original full-port Wolfram samples (24): f={733,997} × C ratios={.5,1,2}
   × C loads={matched,pressure_release,rigid_closed,fixed_impedance}.
Singular diagnostic fixture (not production nominal):
   3 identical L=.08m, areas equal, B/C pressure_release,
   f=343/(2*.08)=2143.75 Hz; NUMERICALLY_UNRESOLVED expected.
```

## Physics acceptance / falsification

| Property | Required criterion | Independent evidence / kill control |
| --- | --- | --- |
| All six endpoint states, each `p,U` complex | Max of 12 normalized complex endpoint errors ≤ `1e-10` for **each of 288** nominal cases vs pinned Python reference; **separately all 24** unit-scale Wolfram records | Two distinct comparators: inherited `reference.py::port_states` covers 288; frozen Wolfram JSON covers only 733/997 Hz × 3 areas × 4 loads at scale 1. Both must pass on the new backend |
| Original nominal cases | All **288** = 3 areas × 4 loads × 3 source scales × 8 Hz, no filtering | Original research reproduction alone is insufficient; fresh Gate B runner calls only the new branch3 API for actual states and the pinned research reference for expectations |
| Junction pressure continuity | `max|p_A.out-p_B.in|,|p_A.out-p_C.in| / p_ref ≤1e-10` | full port measurement; wrong pressure-sign mutation |
| Signed volume flow | `|U_A.out - U_B.in - U_C.in| / U_ref ≤1e-10` | wrong all-same-sign junction mutation must fail |
| Mean acoustic power | `abs(P_A.in-P_B.out-P_C.out) / [0.5*p_ref*U_ref*|source_scale|²] ≤1e-10`; matched vs release/closed characterized | `P=.5 Re[p conj U]`; weighted scattering and independent full-port oracle |
| Normalized 12×12 backward residual | ≤1e-12 in fixed nominal, if using the original matrix-solve form | independently reconstruct physical equations; no “solver residual only” as proof |
| 3×3 pressure-wave scattering | `max|S_SI-S_Wolfram|≤1e-12` and `S†diag(Y)S=diag(Y)` / normalized error ≤1e-12 | [new OG-4 symbolic result](./og4-wolfram-gate-a-result.json), 3 incoming bases + complex mixed incidence |
| Conditioning | Nominal spectral condition ≤1e8; otherwise `NUMERICALLY_UNRESOLVED` | Original OG-1 max 139.025; lossless singular ~1.32e16; **no damping fallback** |
| Wrong signed U | Normalized full-state oracle discrepancy >1e-3 at OG-1 mutated fixture | original wrong sign outcome ~2.2948 |
| Wrong particle-velocity condition | Normalized full-state oracle discrepancy >1e-3 at unequal-area fixture | original mutated outcome ~0.4950; new local `Y=(1,1,2)` weighted-power residual **8/9**, while equal-area negative can trivially pass |
| Altered source, geometry or boundary | Case data, port states and digests change as expected; precise refusal outside capability | fixed C baseline impedance distinct from C rematched impedance |
| Invalid vs unsupported | Graph otherwise valid but different/multi-junction -> `UNSUPPORTED`; malformed -> `INVALID` before backend; never unhandled recursive exception | wrong IDs/type, extra tube, duplicate boundary, complex/nan geometry, long graph tests |
| Frozen OG-3 preservation | Existing OG-3 `prepare_graph` still refuses branch `UNSUPPORTED`, exact 7-point full complex source unchanged | existing 536+ full suite, OG-3 dedicated science/X2a genuine two Takes |

Amendment A1 freezes the numerical resource budget, 1-D nonempty 1..256-point input, validation/refusal precedence, exact output shape and canonical digest ABI **in Gate A**: [normative API](./og4-branch3-api-v1.md), [golden input/byte/hash fixtures](./og4-branch3-api-golden.json), [executable encoding check](./og4-branch3-api-vectors.py). Gate B implements these unchanged, rather than choosing acceptance boundaries during implementation. Existing thresholds here are **inherited OG-1 gates**, not previously blind independent measurements. Any changed threshold, frequency, singular case, medium, or load definition requires an explicit dated amendment and re-review before implementation, not silent pruning.

## Mandatory Gate B API contract cases (Amendment A1)

These must run against the actual future entry points, not just the encoding helper.

| Input/control | Required outcome |
| --- | --- |
| All 4 C Load variants, all 3 areas and source scales | Exact typed acceptance and fresh full-port comparisons below |
| Extra/missing fields; Complex array/native complex; bool/nonfinite SI | INVALID before capability; no defaults/coercion |
| Matched with explicit impedance; fixed with omitted impedance; zero/negative real fixed impedance | INVALID, never silently reinterpret boundary |
| Otherwise legal fixed C impedance differing from 1372000+0i; different B load | UNSUPPORTED:FROZEN_LOAD after validity |
| Valid old fixed2 blueprint/snapshot; malformed old structure | Explicit SCHEMA_NOT_BRANCH3 refusal; malformed old structure remains INVALID |
| Snapshot roundtrip plus renamed revision, source/load mutation, forged primitive/hash/mapping | Rebuild independent primitives; accept exact roundtrip only; reject forged binding and stale digests |
| `[733]`, all 8 anchors, reversed list, duplicates, 256 repeated anchors | N-aligned complete output, preserved order/repeats and identity |
| Empty/scalar/nested/bool/complex/string/negative/nonfinite Hz | INVALID with specified shape/value path, before allocation |
| 257 repeats; 257 repeats with invalid final element; 257 zeros | Point limit; INVALID first; point limit before unverified frequency |
| Valid supported-size request with unverified Hz (including 0) | UNSUPPORTED:FREQUENCY_NOT_YET_VERIFIED, first original index |
| Legal large connected graph; legal large graph with invalid subpart | UNSUPPORTED only after full validity; invalid subpart wins; iterative traversal |
| All 11 golden byte/hash vectors on Python; non-Python port | Exact canonical bytes/digests; reproduce independently before ABI claim |
| Mutate each source/load/geometry/revision/output field; reverse collection vs semantic port/frequency order | Complete hash field coverage; only documented nonsemantic ordering is invariant |
| A numerical failure after an earlier successful sample | Atomic NUMERICALLY_UNRESOLVED; no partial observation/digest |

## Comparator provenance and fresh Gate B evidence (Amendment A1)

All pins below refer to parent design HEAD `4161e6d2c20851006d1ee5763928af5caaa668a2`.
The original files are unchanged. These are **inherited research evidence**, not
new backend results or unseen expectations.

| Source in `experiments/038_og1_passive_branch/` | Git blob | SHA-256 |
| --- | --- | --- |
| `reference.py` | `d136a70180def8d1b80431cafb128fb05537084c` | `ddc315f941d4c850d8e72f02c9064b1a8f71b684b40863e4b4f0d4ec168ee7f5` |
| `run.py` | `ee3fd92ef983f4ceae3714f0eedfc67789f2fe80` | `79b774a71211f5c10144180b959a6cf626de632c3ca221d4a020f6bc8318619b` |
| `wolfram/oracle.json` | `8f3ef44a079fe468348c7c4b1c66a42cca5c77d5` | `c840db138214668e081fa2afa9e9fa693969005b6c4c4611b739476a97886e24` |
| `wolfram/oracle.wl` | `b066307176f72c3c519feb581356f2b1ed6e55bc` | `6ddae77e57f61098d4b451b7a5a131961e38fb6a27b516ffcf6f21aba3a20cda` |

Fresh Gate B must produce **two named, independently scored comparisons**:

1. `branch3_vs_inherited_python_288`: new production API responses vs
   `reference.py::port_states(ratio,f,load,scale)` on all 288 combinations. This
   reference uses tangent impedance recursion/phase propagation, no UniformTube
   or production matrix. Normalize p errors by `p_ref=Z_A*1e-6`, U by `1e-6`
   (not by source scale), and take max over 12 complex errors per case.
2. `branch3_vs_frozen_wolfram_24`: new production API responses vs **each actual
   record** in frozen JSON, at scale 1 only. Convert its `[real,imag]` pairs into
   [API §1](./og4-branch3-api-v1.md) Complex values; do not mistake the archived representation for the public
   API representation. Compare all six p/U endpoints and its three recorded
   powers (A.in, B.out, C.out), using the protocol power normalization and
   `1e-10` bound for each normalized power discrepancy as well as state error.

Python/Wolfram comparator agreement on their 24 overlapping cases is an additional
sanity check, not a replacement for either new-backend comparison. No claim of
288 directly Wolfram-frozen states or independent Wolfram coverage at all eight
frequencies is permitted. Optional scaled Wolfram expectations derived by linearity
must be labeled *derived*, not newly independent records.

Test runners may load the pinned research reference **only as expected-value code**;
production branch3 must never import `experiments/**`, call old `network.solve`,
or read oracle states. Evidence must include per-case expected/actual endpoints,
comparison family, source hashes, runtime, actual clean git HEAD, request and all
three identity digests. Bind these in a separate evidence manifest, not physical
hashes; replay/wrong-HEAD controls must fail. Re-running old `run.py` demonstrates
research preservation only. Neither its historical result nor docs byte/hash
checks qualify as fresh OG-4 backend verification. No new solver is claimed here.

## Independent review and CI execution

1. Gate A needs two separate **critical review tasks** on the actual doc PR: symbolic/acoustic law with sign and admittance weight; separate domain/type/compatibility/identity and capability API audit. GitHub Codex review if available; AI agreement itself does not count as independent scientific experiment.
2. Gate B implementation PR must be **separate Draft**, based on accepted Gate A decision, with versioned branch3 schema and physically isolated code; no original `src/morphoacoustics/**` mutations, no old experiment/Wolfram re-frozen results.
3. Gate B dedicated CI triggers for **all source and numeric dependencies**, including `src/**`, `experiments/**`, `tests/**`, `checks/**`, Wolfram/reference docs, `pyproject.toml` and workflow itself; exact PR HEAD attestation, all 3 supported Pythons + mypy, independent four-termination full-port evidence and 3×3 mixed-wave scattering; 2 *fresh* identical graph runs with hash sidecars plus wrong HEAD/stale output negative controls; Exp038 original scientific jobs; existing OG3 full tests; Experiment028/029 decisions and actual two X2a 48kHz 0.5s WAV/pressure/trace Takes unchanged.
4. Gate C only if **no unresolved high-severity physics/code/CI findings** and actual exact-head CI & artifact linked: explicitly choose `GO_LIMITED_CORE_FIXED_3PORT`, `INCONCLUSIVE`, or `REJECT`; versioning and unverified Studio interoperability explicitly scoped. No auto merge on mere CI green.

**Do not interpret this signed plan as proof of new biologically valid mouth/nose acoustics or any human reviewer approval.**