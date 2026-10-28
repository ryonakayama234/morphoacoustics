# VQ-1 G1-S — static force DATA and dimensions

Status: prospective research-local types, NOT public JSON schema and NOT a Character property.

| Field | Meaning | Rule |
|---|---|---|
| `PressureDrop(tap_id, wall, drop_pa, uncertainty_pa, source_kind)` | D_j=p0-p_wall at the specific **measured** marker [Pa] | side-specific; no unknown or negative uncertainty; source kind retained |
| `SurfacePatch(tap_id, wall, area_m2, projection)` | independent wetted-wall quadrature [m²], mode projection (dimensionless) | positive area, signed projection in [-1,1]; not synthesized from tap z |
| `Reference(p0_gauge_pa, pext_gauge_pa, p0_unc_pa, pext_unc_pa)` | common gauge pressure and uncertainty [Pa] | mandatory; never assume p0=ΔP or outside=0 without a source |
| `ForceInterval(force_n, conservative_uncertainty_n, status)` | signed static generalized force [N] | no wall motion, no FSI |
| `EvidenceReceipt` | exact code SHA, test outcome, synthetic controls, absent-real-data HOLD | G1-S source/physiology/voice remains distinct |

All numbers in this implementation's included runnable cases are **synthetic analytic test inputs**, not extracted experimental M5 pressure measurements.

M5 main source context from original article / research Draft #220: M5 uniform, Fig 2B, d=0.02 cm, life-size transglottal drive 10 cmH2O; measured drop D=p0-p_i, p0 at tracheal tap 0; z6=0.211 cm, z11=0.413 cm, z13=0.511 cm; FW versus NFW must not be silently collapsed. Same-study Q=64.7 cm³/s, k_ent=1.447 are NOT wall-pressure samples. Source Figure axis scale and independent dual readings are not qualified here; no values are generated for missing taps.

The conservative interval half-width is

```
u_F = abs(sum(A_j*s_j))*(u_p0 + u_pext)
      + sum(abs(A_j*s_j)*u_Dj).
```

The first term is the **shared gauge reference**. It must not be treated as independent point noise (such treatment can falsely reduce uncertainty when many patches are present). Independent surface geometry/mode uncertainty is deliberately outside this bound: the output is CONDITIONAL_ON_DECLARED_GEOMETRY and cannot claim total physical uncertainty.

Output status is always `ALGEBRA_ONLY_NOT_SOURCE_OR_FORCE_VALIDATED` on successful synthetic numeric controls. Incomplete real input => explicit `SCIENTIFIC_HOLD` with reasons, not `INFEASIBLE` or `UNSUPPORTED` (those have different meanings in public Core).

Versioning/ownership: experiment-local Python dataclasses; Studio does not store them in Character, Script, Direction, Scene, Take or panel registry. Future validated receipts could be inspected in `research.drawer`, subject to a separate UI authorization.

## Recorded research receipt — 2026-10-28

Evidence: [exact-source-head CI #40709820069](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40709820069), [JSON artifact 12826410001](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40709820069/artifacts/12826410001). Test outcome 13/13 PASS **only** for declared synthetic algebra; example input: `p0=100 Pa, pext=0 Pa, D6=25 Pa, area=.1 m², projection=1, u_p0=3 Pa, u_ext=5 Pa, u_D=2 Pa`. The **synthetic** output force is 7.5 N with conservative **pressure-only** half-width 1.0 N (not an animal/in vivo geometry). Source figure digital points: 0 qualified; actual wet-surface patches: 0 qualified; real common-gauge references: 0 qualified; waveforms: 0. Output `G1_S_SOURCE_HOLD`, `G1_D_HOLD`, `G4_NO_GO`. These are distinct from the conditional synthetic number. New documentation commits require new exact-head checks before any further adoption discussion.

## Data amendment — RED evidence atomicity

The research receipt additionally carries nullable `synthetic_force_example`, `analytic_control_error` and optional `runner_error` / `source_refusal_error`. On any analytic or runner exception, the scientific state remains `NUMERICALLY_UNRESOLVED`, source/geometry remain unqualified, and G1-D and voice remain HOLD/NO-GO. A test failure cannot prevent creation of the machine-readable STOP receipt (unless writing the filesystem itself fails). No new public fields/contracts or creator data are created. The original 13/13 code SHA receipt is historical and shall not be advertised as review of repaired runner logic.
