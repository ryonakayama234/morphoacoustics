# VF-1B2 SYSTEM — proposed causal architecture and minimal physical equations
**Design-only, not yet accepted or implemented; no universal OrganGraph ABI.**

## Causal dataflow
```mermaid
flowchart TD
  STC["Studio Character: body/organ revision (future slot)"] -. "not connected" .-> FIX["Research fixture: two tissue elements + prepared tract"]
  STM["Studio Motion: effort / Gesture intent (future slot)"] -. "not connected" .-> DRIVE["Declared nonperiodic reservoir Psub(t)"]
  FIX --> T["Tissue: x_lower,x_upper and v_lower,v_upper, m/k/d"]
  FIX --> F["Glottal fluid: A(z,t), density, momentum, p(z,t), inlet/outlet flow"]
  DRIVE --> F
  T <-->|"F_i v_i and moving volume; same step"| F
  F <-->|"p/U conjugate port; same step"| W["SFI-3 / SFI-2 pinned passive 1D tract"]
  W --> LOAD["Matched outlet: proxy only; SA-2B later"]
  T --> OBS["Independent SI mass, momentum, energy and work observer"]
  F --> OBS
  W --> OBS
  OBS --> REC["Core research receipt: G0/G1/G2/G3 separately"]
  W -. "not an ear-pressure claim" .-> SC["Studio Scene / Listener"]
  REC -. "no creative Take" .-> TK["Studio research.drawer; Take dock unchanged"]
```

## Sign and coordinate convention — freeze precisely at B2a
- x_L, x_U [m] = **outward** displacement of lower and upper symmetrical wall pairs, away from the glottal midline; positive x increases opening.
- z [m] = axial distance from subglottal lower boundary to supraglottal upper boundary, 0 <= z <= L_g; transverse length/depth ell [m].
- Two shape functions: phi_L(z)=1-z/L_g; phi_U(z)=z/L_g. Proposed half-gap h(z,t) = h0(z) + phi_L(z)x_L(t) + phi_U(z)x_U(t).
- Moving airway A(z,t)=2 ell h(z,t) [m^2]; V_g(t)=integral_0^Lg A(z,t) dz [m^3]; no-contact A>A_floor everywhere, otherwise UNSUPPORTED_CONTACT.
- Pressure p(z,t), Psub(t), p_tract(t) in Pa **gauge relative to declared external tissue pressure**; pressure difference and momentum use a consistent absolute-pressure density reference. U(z,t) [m^3/s] positive towards mouth; both subsystem ports use opposing outward-normal orientations.
- Proposed tissue elastic/kinetic energy, no contact: E_t = sum_i (m_i v_i^2/2 + k_i x_i^2/2) + k_c(x_L-x_U)^2/2. All m,k,d nonnegative with positive masses and stiffness; damping power D_t = sum_i d_i v_i^2 >= 0 [W].
- Local generalized aerodynamic force on tissue, F_i(t) = integral_0^Lg [p(z,t)-p_ext] (partial A/partial x_i)(z,t) dz [N]. Mechanical power sum_i F_i v_i [W]. In the **fluid** balance the same interface power must appear with the opposite sign; do not also insert legacy g dot v pressure work a second time.
- Distinguish pressure at the *glottal wall*, pressure at the *tract inlet* and pressure at *the mouth port*. They are not interchangeable. Do not call mouth-port p an ear measurement.

## Fluid and mathematical solver choice
**Proposed primary reference:** at least two control volumes, moving-area compressible/weakly compressible barotropic conservation of mass and axial momentum, with time-evolving density and momentum states and pressure derived from a stated equation of state. Initial reference EOS: barotropic isentropic small-compression air closure around a declared atmospheric reference; dissipative viscosity/separation is explicitly exported as a nonnegative heat/loss sink, not discarded. The specific EOS, face interpolation, momentum flux and thermal assumption must be **derived and registered in B2a** before numerical code.

Mass in cell j: m_j = rho_j V_j and d m_j/dt = rho_in U_in - rho_out U_out [kg/s]; V_j is geometry dependent. A moving wall changes V_j and thus density/pressure. A naive Uin=Uout or the old Uin=q-g dot v cannot be used as an independent imposed law.

**Reference flow alternatives, not substituted ad hoc:** (a) fixed-wall Bernoulli + measured viscous/separation corrections to check p(z), U, pressure losses; (b) independent momentum-based reduced flow formulation; (c) higher-fidelity measured/CFD results for discrepancy investigation. The moving-wall model cannot inherit an arbitrary separation location or coefficient tuned until sound appears. Reverse-flow outside the calibrated law must be UNSUPPORTED, not silently mirrored.

Use the existing passive tract as an independently testable acoustic subsystem. For each timestep solve the coupled nonlinear unknowns **tissue, cell mass/momentum, wall force, p/U tract inlet**, then advance all subsystem states once. Use an implicit midpoint/discrete-gradient energy-consistent approach where applicable, with declared nonlinear residuals and backtracking; fail NUMERICALLY_UNRESOLVED instead of clipping/concealing an unstable solve. Continuous states must persist between timesteps.

## Global signed power ledger
With all subsystem port orientations explicitly cancelled, the *target* balance is:

  Delta(E_tissue + E_glottal_fluid + E_tract + E_outlet_storage)
  = integral[Psub(t) Uin(t) - P_external(t) Uexit(t)]dt
    - (D_tissue + D_viscous + D_separation + D_tract + D_outlet)

All E and integrated D in joules. If the matched outlet is modeled as an ideal dissipative termination, E_outlet_storage=0 and D_outlet is nonnegative. Fluid internal/kinetic storage and moving control-volume work must be included; avoid treating Psub Uin and acoustic port pU as *two independent* energy sources. For any boundary model, state exactly which power is counted. This is a **required derivation**, not a proven identity of a yet-unwritten solver.

At every step compute separately:
- Tissue: Delta E_tissue - integral sum(F_i v_i)dt + D_tissue.
- Fluid: Delta E_fluid + integral sum(F_i v_i)dt - reservoir work + tract port work + D_fluid.
- Tract/outlet: Delta E_tract - incoming port work + D_tract+outlet.
The interface terms must cancel algebraically in total and in an independent, separately implemented numeric observer.

## Boundary cases
- Baseline pinned research tract: VF-1A's **10-section** frozen uniform and constricted variants, not Exp043's 16-section M0/M1; do not mix fixtures.
- First physical test strictly noncontact and no imposed periodic A, F0, wave source, negative material damping, per-case EQ or neural signal overwrite.
- Source reservoir has prescribed **constant pressure**, but actual flow is solved dynamically; a steady pressure is an external energy boundary, not a preset periodic excitation.
- SA-2B dynamic passive radiation remains a later dependency. Neither this matched outlet nor SA-2A's frequency-only piston gives a valid listener pressure.
- Projected Studio owner mapping unchanged: character.canvas = morphology/organ ref; motion.canvas = task/effort ref; scene.canvas = speaker/listener ref only; selection.inspector = selected domain entity; take.transport = qualified immutable Take; research.drawer = traces and receipts. No new slot.

## B2a design correction — total-enthalpy flux, not pressure times volume flow alone

**Prospective derivation requirement; NOT an implemented or biologically validated moving-wall model.** The earlier "target" global ledger `Psub * Uin - Pexternal * Uexit` is **not a complete generic energy boundary** for the compressible moving-area mass/momentum family above: it omits convective kinetic/internal-energy transport. It may only be reused after an explicit small-Mach/low-amplitude reduction with all retained mean-flow terms accounted for.

For a smooth noncontact quasi-1D channel with fixed axial end planes, lateral moving wall, barotropic `p=p(rho)` and axial speed `u`, a candidate continuous model must derive, with the *same pressure state*:

```text
mass:     d_t(rho*A) + d_z(rho*u*A) = 0
momentum: d_t(rho*u*A) + d_z[(rho*u^2+p)*A] = p*d_z(A) - f_drag
energy:   d_t[rho*A*(u^2/2 + e(rho))]
        + d_z[U*(rho*u^2/2 + rho*e(rho) + p)]
        = -p*d_t(A) - f_drag*u
U = u*A; de/drho = p/rho^2; f_drag*u >= 0
```

All pressure quantities must share one declared gauge/external-pressure reference and consistent energy zero. One illustration (NOT a calibrated air EOS) is `p=c^2(rho-rho0)` with `e(rho)=c^2[ln(rho/rho0)+rho0/rho-1]`; this satisfies `de/drho=p/rho^2` and `e(rho0)=0`. For the fixed axial boundaries the total fluid energy flux is `U*(rho*u^2/2+rho*e+p)`, **not simply `p*U`**. Its conservation-law derivation, sign, dimensionality and physical EOS validity must be independently audited before B2c.

The structure receives the opposite lateral wall power `+integral p*d_t(A) dz = sum_i F_i*v_i`. In the total balance the two wall powers cancel ONCE. The tract's existing acoustic `p_acoustic*U_acoustic` is a *linear perturbation port* of its declared baseline, not an automatically compatible bulk total-enthalpy port. A mean-flow / acoustic-perturbation split and any time-mean advection/pressure offsets need an explicit conservative interface. Reusing the SFI-3 open-valve port unaltered and declaring total compressible-fluid/tract energy closure is prohibited without a derivation.

The newly registered [VF-1B2 rigid Gate B0 research PR #262](https://github.com/ryonakayama234/morphoacoustics/pull/262) tests only low-Re **fixed** Stokes resistance; it cannot justify moving-wall `f_drag`, high-drive separation, realistic intraglottal pressures or true phonation. B2c must remain HOLD until these boundary conditions are independently defensible. Do not fabricate conservation by pressure-wavetable/EQ/oscillator forcing.
