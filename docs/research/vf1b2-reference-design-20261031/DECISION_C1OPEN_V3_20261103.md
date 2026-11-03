# VF-1B2 / C1-Open — Decision v3 (2026-11-03 JST)

**Status: DESIGN FINAL CANDIDATE / OWNER REVIEW PENDING / NOT A3 PREREG FREEZE / NO PHYSICAL IMPLEMENTATION / NO MAIN MERGE.**
**Primary module:** Core / Physical Execution, experiment-local. **Secondary:** future Organ Modeling & Physical Assembly. Studio, SMC, ASMR, Take, performance contracts, src/morphoacoustics and src/morphoacoustics_graph unchanged.

## One deliverable and bounded scientific claim
Deliver an audited **noncontact, subsonic, moving-area, through-flow fluid–tissue system**: 2 passive lower/upper tissue DOF, quasi-1D compressible ideal-gas mass/momentum/total-energy field, finite-volume conservative cell fluxes, boundary reservoirs, common simultaneous wall-force/pressure-work operator, independent audit and negative controls. Success is **G1 mathematical/numerical FSI capability only**, not self-oscillating phonation, human physiological validity, C2 source–tract connection, calibrated sound, or creative Take. No prescribed oscillatory flow/area/F0, negative material damping, EQ, neural output regeneration or energy-fixing post-processing.

This expands the verified sealed C1-R0 [PR #278] while **retaining it unchanged as its own analytic benchmark**. It extends the docs-only V2 architecture of [PR #259], not the source/measurements of [PR #262]. Exact Core main reference checked 2026-11-03: `17a8d6200a9eca4d1204395b176701728a41d6e4`. Stage C1 only; neither SFI-2/#81, SFI-3/#84 nor VF-1A/#209, VF-1B1/#214 may be treated as merged dependencies.

## Model/technology selection
| Family | Value | Rejection / disposition |
| --- | --- | --- |
| Bernoulli scalar valve + old q-g*v | fast | **REJECT** as coupled proof: spatial momentum/work and boundary enthalpy not closed |
| Incompressible moving-wall lumped | simple controls | **ORACLE/LIMIT ONLY**: not a full compressible power state |
| **Quasi-1D moving-area compressible full Euler + 2 DOF** | explicit transport/storage and conjugate wall work, practical small-grid research | **SELECT** for C1 low-drive, attached/inviscid mathematical validity |
| Port-Hamiltonian semi-discretization | attractive power-preserving alternative and published precedent | **INDEPENDENT METHOD/REVIEW REFERENCE**; not second production solver now |
| Full 3D FEM/CFD FSI | realistic shear, separation, wall motion | **DEFER**: cost/data; use independent discrepancy reference when needed |

**Gas:** calorically perfect gas `gamma=1.4` initial reference; `p_abs=(gamma-1)*(E_density - rho*u²/2)`, `T=p/(rho R)`; evolve *total energy* independently. Initial entropy may be uniform, but do not globally force isentropic `p=K rho^gamma` while simultaneously claiming full-energy conservation across dissipative shocks. Smooth sealed spatially uniform limit maps to C1-R0 isentropic p–V. No viscous drag/separation closure in first C1; any later closure needs measured/independent reference and an explicit heat/energy disposition, not arbitrary energy removal.

**Boundary:** left z=0 upstream total/stagnation thermodynamic reservoir `p0,T0`, right z=L downstream static-pressure reservoir; both closed by *subsonic characteristic compatibility*, not independently prescribing pressure, density and velocity at each face. Only verified low-Mach rightward throughflow; reversals, choked/supersonic and contact are explicitly unsupported. Fixed reservoir conditions are not an acoustic tract.

**Numerics:** small N=8/16/32 cells; area-weighted conservative finite volumes, stationary-well-balanced p*dA/dz momentum geometry source, Riemann numerical face flux, same-step nonlinear fluid–tissue solve and physically identical cell-volume changes in opposed wall work. Candidate common-midpoint, iterated residual scheme; commit step atomically only if residual, positivity, boundary and domain checks pass. A proposed method is not deemed conservation-proven until independent discrete identity and exact-head numerical tests pass. Start with NumPy and existing Python 3.11–3.13 experimental tooling; no public package/ABI modification or duplicate body registry.

## Corrections to prior ambiguity
1. **Closing two ends of a spatial model does NOT by itself reproduce C1-R0's uniform sealed gas**: sealed space still permits internal axial modes. Compare separately to a well-defined lumped uniform-pressure reduction/low-frequency limit, and do not set arbitrary full-grid byte equality.
2. The common fluid/tissue power is `sum_j p_abs,j * dV_j/dt` (fluid negative; tissue pressure positive minus outside pressure). A pressure-only `pU` expression and a second separate `g*v` valve correction are not permitted.
3. Nonzero mean-flow endface energy is **total enthalpy/mass flux**, not linear `p' U'`. C2 requires separately derived mean/perturbation matching.
4. Energy consistency and a positive tissue energy-transfer interval do NOT establish phonation: G2 external physical validity, G3 sustained source mechanics and G4 creator quality are different decisions.

## Dependencies and stopping boundaries
A1 continuous/discrete derivation + independently checked work signs; A2 exact reservoir characteristic closure, positivity, mathematical domain; A3 before code freeze numerical fixtures/thresholds, external-reference qualification ledger and failed examples. C1 needs fresh dynamics and negative controls. **STOP** if signed energy cannot be algebraically closed, if boundary overdetermination/reflection is unqualified, if conservative mass/momentum/energy fails, if contact/reverse/unsupported regime dominates or the solver only appears stable via hidden clipping. Review exact source and CI before any stronger claim.

Future Studio mapping is entirely within the **accepted V2** Character Canvas + selection Inspector (body/organ intent), Motion Canvas (task/respiratory intent), Take Dock (validated audio only), Research Drawer (traces/receipts), Scene Canvas (not connected). No UI/panel changes permitted before separate STOP-AND-PROPOSE approval.

## Evidence anchors
- Internal: Core #215, design Draft PR #259 V2; C1-R0 PR #278; Studio accepted ADR PR #34, preview Draft PR #33; Core OD-3 main PR #277.
- Fulcher et al. (2011) PMC3078031: rigid-glottis pressure coefficients, NOT moving-wall calibration.
- Li et al. (2020) DOI 10.1115/1.4044033: momentum-based reduced flow compared to 3D FSI.
- Le Gorec et al. (2021) DOI 10.1093/imamci/dnaa031: energy-based fluid–structure port connections.
- Risse, Hélie & Silva (2025) DOI 10.3389/frsip.2025.1525198: recent quasi-1D power-balanced vocal apparatus; precedent, NOT MORPHO validation.
Related documents in this same v3: SYSTEM, DATA, EXPERIMENT. Historical V2 docs and failures preserved, not rewritten.
