# VF-1B2 rigid Gate B0 — prospective falsification before executable source
**FROZEN PROTOCOL v1, recorded before pilot code and before any computed score.** Parent: #215, design Draft #259, Foundation #199. This is NOT approval of the eventual moving-wall model.

## Aim
Test a transparent and independently solvable low-Re, fixed-wall pressure/flow boundary and virtual wall-force *instrument* before attempting moving-wall FSI. Test a *physical boundary condition*, not a phonator or speaker.

## Fixed inputs
L=0.01m; w=0.01m; h0=0.00012m; mu=1.81e-5Pa s; rho=1.21kg/m3; c=343m/s; taper s=-0.2,0,+0.2; DeltaP=0,0.1,0.2,0.4Pa; midpoint N=4,8,16,32. Signed boundary conventions and analytic formula in SYSTEM.md. No adaptive parameter fitting.

## Independent expected results
- H0-constant: s=0 midpoint resistance Q must match exact closed form at all N to relative <= 1e-12 when DeltaP>0.
- H1-taper: for abs(s)=0.2, at N=32 |Q_numeric/Q_exact-1| <1e-4; successive N4->N8->N16->N32 relative error contraction factor >=3.8 for both slopes and each positive pressure.
- H2-orientation: reversing s preserves exact and discrete Q within 1e-12 relative; internal pressure p(x) for +/- s differs on at least one interior face under DeltaP>0; inlet/outlet gauge pressures preserved.
- H3-passivity: DeltaP*Q >=0; discrete power residual |DeltaP Q - sum_j Q^2 r_j dz| <= 1e-12 * max(DeltaP Q, 1e-18 W) for positive pressure; all pressure drops nonnegative.
- H4-static-forces: for s=0, analytic F_lower=2wL DeltaP/3 and F_upper=wL DeltaP/3; candidate midpoint virtual-force estimate has error decreasing on N=4,8,16,32; recorded forces are NOT mechanical work or a moving-wall benchmark.
- H5-fail closed: negative pressure difference, zero/negative dimension, nonfinite values, impossible slope, wrong signs/losses, and declared higher-Re stress (800Pa) must reject, not emit a positive or voiced PASS.

## Independent verification policy
Candidate uses midpoint cell resistance and pressure integration; oracle uses the analytically integrated continuous channel equation. No reference-module import into the candidate. Tests independently compute expected Q and global pressure/power identities; tampered pressure/drop/loss fields must cause validation failure. All exceptions are recorded without audio fallback. Run tests with unittest and standard-library Python; no stochastic seeds.

## Gate decision
G0 PASS requires frozen schema/constants and evidence; G1 PASS requires all predeclared tests, dimensional validity and convergence. G2=INDETERMINATE_NOT_BIOPHYSICALLY_VALIDATED; G3=NOT_APPLICABLE_RIGID_WALL; G4=NO_CREATOR_AUDIO. No scientific status can be upgraded merely because a program or GitHub workflow succeeds. Record any unexpected result without changing this preregistration; source and Results will be subsequent commits.

## Coupled B2a/B2c dependency STOP
This control does NOT supply an adequate moving-wall closure. Before B2c: select and independently derive moving compressible fluid mass/momentum/energy including advective enthalpy, cell-volume wall work and consistent glottal-to-SFI acoustic port (mean flow vs acoustic perturbations); rigid M5/M6 references and loss/separation law must be independently qualified. If not demonstrable, STOP at this limited control; never set self-oscillation/voice GO.
