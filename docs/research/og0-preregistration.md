# OG-0 — frozen candidate protocol, review before adoption

Status: **DRAFT PR / CANDIDATE PREREGISTRATION**. This document is proposed *before* the implementation experiment. Numerical research is not approved or preregistered until independent physical and code review; this PR does **not** license changing criteria after observing implementation outcomes.

Parent issue: [#90](https://github.com/ryonakayama234/morphoacoustics/issues/90). Baseline main commit: `8868df1188443fc4523533c6cb0bb9cd72995c32`. Existing specification: [docs/fidelity-0.md](../../fidelity-0.md). Existing equal-segment regression: `tests/test_acoustics_segmented_tube.py`.

## Hypothesis

Two **separately identified** rigid, lossless, constant-area one-dimensional organ modules, explicitly linked A.out→B.in by a validated acoustic port junction, give the same physical transfer as the equivalent serial tube. The junction conserves continuous perturbation pressure and signed volume velocity and does not create energy. Area mismatch produces correct plane-wave reflection. Invalid / unsupported topology is explicit.

This tests physical port connection **only**, not general graph solvers, branching, moving tissue, sources, gestures or waveform synthesis. `CreatureSpec.CavityConnection` already names cavities but does not define ports, physical coupling laws or units; do not change universal domain or `simulate_snapshot`.

## Definitions and controlled conditions

- Time factor `exp(+j omega t)`, `[p_in,U_in]^T = T [p_out,U_out]^T`, inlet→outlet ordering.
- `p` acoustic pressure in Pa; `U` volume velocity in m³/s (not particle velocity). A.out and B.in use common positive axial direction, so `p_A,out=p_B,in` and `U_A,out=U_B,in`. In each organ's outward-normal flow convention, the latter is `U_A,outward + U_B,outward = 0`.
- Linear plane wave, zero-volume ideal junction, **rigid**, **lossless**, no mean flow, `rho=1.2 kg/m³`, `c=343 m/s`. Both organs use identical medium. Component impedance `Zc=rho*c/S`.
- For each tube `T=[[cos(theta),j Zc sin(theta)],[j sin(theta)/Zc,cos(theta)]]`, `theta=2 pi f L/c`. The ideal junction `J=I` in `[p,U]` variables; **do not add an area-step factor**. Thus `Tgraph=T_A T_B`.
- Dimensions: A `LA=0.08m, SA=3e-4m²`, B `LB=0.09m, SB=3e-4m²` (equal-area) or `SB=6e-4m²` (mismatch).
- Frequency grid fixed: `[80,250,400,733,1200,2000,4000] Hz`. For finite-tube input impedance `Zout=0` ideal pressure release, `Zin=T01/T11` in zero-based indexing, excluding singular `T11≈0`. The exposed A.in is an observation/source-side boundary; B.out is the explicitly assigned pressure-release boundary. **They are not an invalid missing edge.**
- Reference scaling `Zref=rho*c/SA`. Compare dimensionless `D^-1 T D` where `D=diag(Zref,1)`, equivalently `[[T00,T01/Zref],[Zref*T10,T11]]` (the conjugation convention yields same stated components). Never compare an unscaled max norm over dimensional matrix elements.

## Independent oracles and expected values

Wolfram Language arithmetic computed **before** implementing experimental connection code:
1. Equal-area `T_A T_B ≈ T_uniform(0.17m)`, max normalized-matrix absolute discrepancy `4.440892098500626e-16` over grid; `max |det(T_A T_B)-1|=3.3306690738754696e-16`. `f1=c/(4*.17)=504.4117647058824 Hz`.
2. Area step local progressive incidence, **matched/semi-infinite downstream**, `r=(Z_B-Z_A)/(Z_A+Z_B)=-1/3`, power `R=|r|²=1/9`, `T=4*ZA*ZB/(ZA+ZB)^2=8/9`. `R+T=1`. These fractions do **not** describe finite pressure-release termination with multiple reflections.
3. Mismatched tube A+B at `f=733Hz` and `Zout=0`: `Zin ≈ -3.0275149008453414e6 j Pa·s/m³`, independently obtained by transfer matrix and outlet→inlet load recursion. No use of the experimental graph solver to generate oracle data.
4. Port continuity/conservation: at junction `pAout-pBin=0`, `UAout-UBin=0`, `0.5 Re[pAout Conjugate[UAout]-pBin Conjugate[UBin]]=0` in global coordinate. For power audit with nonzero signal use e.g. B.out flow `1e-6m³/s`, pBout=0 and frequency 733 Hz. Normalize pressure residual by `max(1 Pa,|pAout|,|pBin|)`, flow by `max(1e-12m³/s,|UAout|,|UBin|)` and power by `max(1e-12W,|P_A|,|P_B|)`.
5. Structural negative controls: missing organ, wrong/unknown port, invalid role/orientation, duplicate edge, unconnected required junction, duplicate identifiers, zero/negative/nonfinite dimensions, cycles/branches, changed medium parameters. `INVALID` for structurally incorrect requests, `UNSUPPORTED` for well-formed but unimplemented topologies; **no `INFEASIBLE` without a physical gesture/realizer**.
6. Trace/digest: input graph independent of module ordering in provided collection, but not of physical A→B edge. Include explicit IDs, physical values, `rho,c`, inlet/outlet boundaries, frequency grid, algorithm version, backend version/pins, canonical numerical identity for reproducibility. On change of `SB`, `SA` stays fixed; trace changes.

## Acceptance candidate (to freeze after independent review, before running experiment)

- Existing baseline tests unchanged and passing. Experimental test exercises the actual port/graph validation path rather than just manually passing sections into `SegmentedTube`.
- Normalized transfer matrix relative+absolute tolerance `1e-11` (candidate); determinant max `1e-11`; scattering reflection/power `1e-12` relative/absolute; independent `Zin` relative tolerance `1e-10` and absolute `1e-4 Pa·s/m³`. Residual normalized tolerances `1e-11` for pressure/flow/power. Thresholds are deliberately *candidates*, require floor audit and reviewer signoff before treating gate as frozen.
- Compare complex `Zin` at 733 Hz away from poles. Do not evaluate unbounded impedance near ideal quarter-wave poles as a pass/fail metric.
- A failed test must not cause retroactive tuning of fixture or gate to manufacture a PASS. If discovered flaw, explicitly version a new protocol and mark original `NUMERICALLY_UNRESOLVED` or `FAILED`.
- Evidence artifact: machine-readable oracle with exact provenance; experiment `README.md`, `RESULTS.md` documenting command/platform/result; independent code and physics audit, both pending until independently conducted.

## Scope and decision

Proposed experimental file set: `experiments/030_og0_passive_port_connection/` with small model/validator/solver/runner; `tests/test_experiment_030_og0.py` and independent `tests/scientific/oracles/og0_wolfram.json`. Do not edit `domain`, production `acoustics`, `preparation`, Studio, or `Performance Contract v0`.

Allowed decision after audit: `SUPPORT_PASSIVE_PORT_CONNECTION`, `NUMERICALLY_UNRESOLVED`, `UNSUPPORTED`, `FAILED`. A PASS cannot be claimed as general organ graph implementation or actual voiced phonation.
