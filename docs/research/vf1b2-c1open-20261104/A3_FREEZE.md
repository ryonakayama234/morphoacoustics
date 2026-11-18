# VF-1B2 C1-Open — A3 PRE-IMPLEMENTATION FREEZE (2026-11-04)
**This scientific protocol precedes any source pushed to GitHub. Research-only; parent Issue #282 / #215.**
Core main parent `17a8d6200a9eca4d1204395b176701728a41d6e4`; accepted design V3 `4a86abc44c86a5f4ae548e43aaca90b5cb8aa51e`; C1-R0 PR #278 remains untouched. **No physical implementation, SMC/ASMR, Studio, sound, public ABI or new `src/morphoacoustics*` allowed by this freeze.**

## Mathematical A1 model
Coordinates: z=0 (upstream) to z=Lg (downstream). Positive xL/xU opens the glottis. `h(z,t)=h0+(1-z/Lg)*xL+(z/Lg)*xU`; `A=2 ell h`. For cell j, `Vj=integral_j A dz=Vj0+sum_i gji xi`, where `gji=integral_j 2 ell phi_i dz` [m²]. **Use the exact same gji** for `dVj/dt=sum_i gji vi`, fluid wall power `-sum_j pj dVj/dt` and tissue force `Fi=sum_j (pj-Pext) gji`. No old scalar q-g*v correction, no imposed periodic force, no negative damping.
Fluid state per cell `mj=rho Vj` [kg], `qj=rho u Vj` [kg m/s], `Ej=rho(e+u²/2)Vj` [J], with `pj=(gamma-1)(Ej-qj²/(2mj))/Vj` [Pa]. Quasi-1D smooth Euler:
```text
d/dt(rho A)+d/dz(rho u A)=0
d/dt(rho u A)+d/dz[(rho u²+p)A]=p dA/dz
d/dt(Evol A)+d/dz[(Evol+p)u A]=-p dA/dt
```
Tissue `x'=v`, `M v'=gT(p-Pext)-Kx-Dv`. Quadratic `Et=0.5*vT M v+0.5*xT K x`; relative global `H=sum Ej+Et+Pext(Vtot-Vtot0)`; exact power `H'=PhiE,left-PhiE,right-vT D v`, with `PhiE=mdot(e+p/rho+u²/2)` (not just pU). This is a quasi-1D assumption, NOT rigorous 3D/turbulence/viscous/contact physics.
Independent analytic check: for `pg(z)=b+a z/Lg`, `FL=ell Lg(b+a/3)`, `FU=ell Lg(b+2a/3)`; ell=Lg=.01m,b=100Pa,a=120Pa -> FL=.014N,FU=.018N.

## Technology A2 / geometry/physics domain
Ideal gas gamma=1.4, R=287.05 J/kg/K, T0=293.15 K, Patm=Pext=101325 Pa. Lg=ell=.01m, h0=.00020m; tissue masses (1e-4,1e-4) kg; kL=150,kU=220,kc=40 N/m; damping .02,.03 N s/m. Reference initial x=(0,0),v=(0,0), static gas p=Patm, T=T0; optional intervention x=(3e-6,-1e-6). Stationary fixed-wall pressure equilibrium is an oracle. C1 throughflow reservoir deltas `0,10,50 Pa` above Patm **numerical control only**. Each end uses only physically admissible subsonic characteristics: left prescribed stagnation p0,T0 and outgoing (u-c) invariant; right prescribed static pressure and outgoing (u+c) invariant with entropy extrapolation. Do not over-specify p, rho and u. Stop if this does not give lawful positive solution, if reverse/choked/sonic, or if `h<=.00010m`, Mach>0.1, p<=0, rho<=0.
**Chosen numerical method for *smooth* G1 controls:** experiment-local explicit stage-*synchronous* RK4, bounded CFL `dt<=0.2 dz/(c+|u|max)`, not one-tick delayed weak coupling. This is an A2 change from V3's *candidate* implicit midpoint, justified by simple reproducible stage-conjugate work and convergence. It is not exactly energy-preserving, shock-capturing, or unconditionally stable. Cell-centered positive finite-volume mass/momentum/energy update, Rusanov Euler flux times instantaneous interface area; momentum `+p_cell(A_right-A_left)` well-balances fixed-area uniform p,u=0. Atomic state acceptance. N=8,16,32; horizon 0.00030 s; no audio clock/F0 relation.

## Predeclared hypotheses and gates
- H0: uniform pressure fixed wall at rest retains numerical equilibrium.
- H1: `Delta Vj=sum_i gji Delta xi`; open/closed mass agrees with signed endface flux, including swept wall volume.
- H2: rigid nonuniform-area constant-p equilibrium has zero artificial momentum acceleration.
- H3: lower/upper pressure forces match independent linear-gradient analytic oracle, including zero antisymmetric uniform case.
- H4: full energy agrees with signed endface *total enthalpy* plus tissue damping, including external pressure work; omitted, doubled, reversed terms must fail.
- H5: **positive bidirectional intervention**: tissue displacement must alter fluid state vs fixed wall, and known applied pressure gradient must cause distinct lower/upper forces/tissue response; force/response beyond independent numerical noise; an all-null outcome fails.
- H6: nonphysical contact, reverse/choked, negative pressure/density, nonconvergence and invalid fixtures must refuse (no fake WAV/Take).
- H7: C1-R0 sealed spatially *uniform* gas is only a separate lumped limit; closing 2 ends of distributed Euler is NOT byte-identical to it.
- H8: nonperiodic pressure cannot be labeled autonomous voiced sound; G2 physiologic, G3 source self-oscillation, G4 creative audio remain untested.
Engineering preliminary cutoffs fixed **before new source results**: volume identity abs <=1e-12 SI, linear-gradient force abs <=1e-10 N, stationary derivative <=1e-11 SI (component scale reported). Independent mass relative <=1e-9, momentum relative <=1e-6, global energy normalized <=1e-5 plus absolute <=1e-10 J for 0.3 ms; normalization denominator max(|H0|,|Hend|,integral|total-enthalpy endflux|,integral damping,1e-10J). Publish signed raw SI residuals, not only a normalized ratio. Smooth observable error should decrease under (N,dt) refinement against a declared finer reference; unresolved => HOLD, not retuned thresholds.
Mutants must be rejected: interior mass/p/velocity falsification, cut or replaced initial trace, force sign, absent wall work, pU substituted for enthalpy, doubled external-pressure work, negative damping, clipped body dynamics, corrupt digest. Independent observer recomputes identities from raw records and DOES NOT import solver energy/receipt helper.

## A3 architecture / data / stop
`FixtureRevision -> PreparedGeometry/CharacteristicBC -> same-stage FV+2DOF -> immutable raw state+flux/work traces -> independent mass,momentum,energy,force audit -> science verdict`. Evidence: DECISION / SYSTEM / DATA / EXPERIMENT / RESULTS / AUDIT at every step, bad results append-only; exact Git source SHA and workflow artifacts. No modifications to Core main, `morphoacoustics_graph`, Studio V2 UI, SMC, ASMR, Take or Performance Contract.
**STOP:** unknown signed wall work, reservoir overdetermination, unclosed balances, no independent testable oracle, systematic nonconvergence, hidden clipping, excluded flow/contact, or attempting biological claims without external reference. If math passes only `GO_LIMITED_G1_C1OPEN`; physical realism `G2_REFERENCE_UNAVAILABLE`, self-excitation and audio `NOT_TESTED`. Never merge into main automatically.
