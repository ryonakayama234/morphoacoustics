# VF-1B2 Gate B0 — rigid-wall Stokes/lubrication control
Status: PROSPECTIVE ANALYTICAL CONTROL. Not a glottal physiology or sound model.
Owner: Core experiment-local; Studio V2 locked Character/Motion/Scene slots are unchanged.

## Physical scope
A *fixed* thin air channel of axial length L and width w, half-height h(z) = h0[1+s(2z/L-1)], with s in {-0.2,0,+0.2}, positive h, rigid zero-velocity walls. Air is modeled as steady incompressible Newtonian laminar flow in the lubrication/Stokes limit; no source-induced oscillation, no acoustics, no separation or variable tissue force. Upstream gauge pressure DeltaP and downstream 0 Pa. Positive flow from upstream to downstream; reverse flow is explicitly outside the elected one-way research domain.

Local resistance per length r(z)=3 mu/[2 w h(z)^3] [Pa s m^-4]. Thus R=integral_0^L r(z)dz [Pa s m^-3] and Q=DeltaP/R [m^3 s^-1]. The finite-volume *pilot* integrates cell-midpoint r(z), derives pressure drops by Q r_i dz, reports face pressures, and computes port work DeltaP Q = sum Q^2 r_i dz >=0. This is an intentionally independent low-Re limiting control, NOT the non-steady, compressible moving-wall VF-1B2 model.

## Independent exact analytic oracle (not imported by candidate)
For s != 0, integral_0^L dz/h(z)^3 = L/[h0^3(1-s^2)^2], and the partial integral to x is L/[4 s h0^3] [(1-s)^-2 -(1-s+2s x/L)^-2]. For s=0 the partial integral is x/h0^3. Consequently Q_exact = 2 w h0^3 (1-s^2)^2 DeltaP/(3 mu L). Reversing s leaves Q unchanged in this Stokes model, but reverses the axial pressure profile, so lower and upper wall generalized-force distributions may differ.

For a wall-geometry virtual displacement x_L,x_U with shape functions phi_L=1-z/L and phi_U=z/L and area A=2w h, F_i = integral_0^L p(z)*2w phi_i(z) dz. The fixed wall has no mechanical power F_i dx_i/dt=0. Force is diagnostic only; no moving-wall validation claim.

## Dimensional and physical capability limits
p [Pa], Q [m^3/s], r [Pa s/m^4], R [Pa s/m^3], loss DeltaP Q [W], virtual F [N]. Pilot checks slenderness 2hmax/L <=0.05; width/(2hmax)>=20; hydraulic Re = rho * |Q|/[2w h_min] * (4 hmax)/mu <=1; Mach of maximum average velocity <= 0.01. This is an *engineering applicability guard* and not a proof that all neglected terms are negligible at the bound. Values outside the guard must be UNSUPPORTED_REGIME, never used as a substitute for 400/800/1200 Pa measured human glottal benchmarks.

## Boundary and history
Do not import PR #81/#84/#209/#214 (unmerged); preserve their independently pinned code/results for later coupled stages. This calculation does not exercise SFI-3, active tissue, and cannot produce a Studio Take. Character.canvas owns eventual organ design; Motion.canvas future motor intents; take.transport only qualified immutable audio; research.drawer later scientific receipts. No UI/schema edits.
