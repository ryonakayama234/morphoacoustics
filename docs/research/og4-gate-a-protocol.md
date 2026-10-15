# OG-4 Gate A / Gate B acceptance protocol — design frozen BEFORE new Core backend

**Recorded:** 2026-10-16 JST. **State:** candidate acceptance plan / not yet externally reviewed; no OG-4 production implementation exists. Parent [#106](https://github.com/ryonakayama234/morphoacoustics/issues/106). **Preserve original OG-1 [PROTOCOL.md](../../experiments/038_og1_passive_branch/PROTOCOL.md), [Wolfram/oracle](../../experiments/038_og1_passive_branch/wolfram/oracle.json), and OG-3 experiment oracles exactly.** This plan is author-proposed, with known OG-1 results disclosed in advance, so it is **controlled inheritance**, not a blind newly preregistered experiment.

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
| All six endpoint states, each `p,U` complex | Max of 12 normalized complex endpoint errors ≤ `1e-10` for each inherited case | Frozen [OG-1 tangent/wave Wolfram](../../experiments/038_og1_passive_branch/wolfram/oracle.json), independent of production solver |
| Original nominal cases | All **288** OG-1 samples retained, no filtered frequencies, areas, loads or amplitude scalings | Frozen research runner/test; use new separate Gate B evidence for promotion |
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

Set prospective new OG-4 numerical resource budget, input shape, canonical hash test fixture and “supported eight frequencies” rejection code in **Gate B preregistration before code**, not after observing failures. Existing thresholds here are **inherited OG-1 gates**, not previously blind independent measurements. Any changed threshold, frequency, singular case, medium, or load definition requires an explicit dated amendment and re-review before implementation, not silent pruning.

## Independent review and CI execution

1. Gate A needs two separate **critical review tasks** on the actual doc PR: symbolic/acoustic law with sign and admittance weight; separate domain/type/compatibility/identity and capability API audit. GitHub Codex review if available; AI agreement itself does not count as independent scientific experiment.
2. Gate B implementation PR must be **separate Draft**, based on accepted Gate A decision, with versioned branch3 schema and physically isolated code; no original `src/morphoacoustics/**` mutations, no old experiment/Wolfram re-frozen results.
3. Gate B dedicated CI triggers for **all source and numeric dependencies**, including `src/**`, `experiments/**`, `tests/**`, `checks/**`, Wolfram/reference docs, `pyproject.toml` and workflow itself; exact PR HEAD attestation, all 3 supported Pythons + mypy, independent four-termination full-port evidence and 3×3 mixed-wave scattering; 2 *fresh* identical graph runs with hash sidecars plus wrong HEAD/stale output negative controls; Exp038 original scientific jobs; existing OG3 full tests; Experiment028/029 decisions and actual two X2a 48kHz 0.5s WAV/pressure/trace Takes unchanged.
4. Gate C only if **no unresolved high-severity physics/code/CI findings** and actual exact-head CI & artifact linked: explicitly choose `GO_LIMITED_CORE_FIXED_3PORT`, `INCONCLUSIVE`, or `REJECT`; versioning and unverified Studio interoperability explicitly scoped. No auto merge on mere CI green.

**Do not interpret this signed plan as proof of new biologically valid mouth/nose acoustics or any human reviewer approval.**