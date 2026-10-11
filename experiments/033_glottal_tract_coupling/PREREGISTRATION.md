# Experiment 033 / SFI-3 — preregistration of power-port strong coupling

Date: 2026-10-11 JST. **This first commit is preregistration only.** Research candidate; not production and not natural voice. Parent issue [#82](https://github.com/ryonakayama234/morphoacoustics/issues/82).

## Dependency topology (critical)
- **This PR is stacked on Draft PR #81's branch** (`research/sfi2-time-domain-tract-20261010`, pinned parent SHA `6cdd21768fd92167bbc56c57264fc161c35e7dda`) so it can import `experiments/032_passive_time_domain_tract/waveguide.py` unchanged. No claim that 032 exists on `main` yet.
- Glottal law is mathematically equivalent to prescribed-area flow in Draft PR #79 (SHA `958065a40ae2619a47acaf3d4af326f77741f69c`), but its backward-Euler chamber state **must not** be connected to the midpoint tract. Experiment 033 therefore implements only a small **midpoint glottal law local to 033**, reusing the original density, `Cd`, glottal inertia and resistance fixture; never treats LF *flow* as glottal *area*. No experimental predecessor PR is edited or merged.
- Once #81 is merged following review, rebase or retarget this PR to main, independently verifying dependencies. #79 stays an independent reference, not merged implicitly.

## Scientific question, fixed intervention, observable

At the same **strictly positive prescribed glottal area**, same subglottal pressure and same glottal inertance/resistance/air density, does a change of **one middle tract section** from 3e-4 to 1.5e-4 m² change upstream U(t) through causally reflected pressure, and does the total coupled energy remain passive?

Fixture: fixed `Tract1DGeometry` with 10×0.017 m tube sections; uniform areas 3e-4 m², or section index 5 area 1.5e-4 m² only; `rho=1.21 kg/m³`, `c=343 m/s`, `dt=1/48000 s`, 4 acoustic cells/section, outlet *matched resistive* termination `R_L = rho*c/A_out` (same geometry's outlet in both cases). This outlet is not realistic lip radiation. Start all pressure and flow states at zero. Constant `A_g=3e-5 m²`, `Psub=800 Pa` for 0.03s, `I_g=1200 Pa*s²/m³`, `Rg=1.5e6 Pa*s/m³`, `Cd=0.7`, `b(A)=rho/(2 Cd² A²)`.

Conditions:
- C0-uniform, C0-constricted: open-loop pressure **does not feed back** to glottal midpoint source. Same waveguide receiving prescribed source, intentionally nonreciprocal null. Zero flow difference between these two is required.
- C1-uniform, C1-constricted: same complete midpoint glottal law and *simultaneously coupled* passive tract port. Only section index 5 area changes.
- Optional diagnostic: Psub=0, zero initial state ⇒ exactly quiescent and no spontaneous energy generation; negative pressure must remain finite.
- Exact closure `Ag=0`: **UNSUPPORTED** in this first experiment, fail-closed. Periodic opening that reaches zero, contact mechanics, tissue self-oscillation and moving geometry require separate gate. Optional strictly positive periodic area may be studied after fixed open validation, never mixed with closed-glottis claim.

## Strong port and derivation

At each time step midpoint `u_m=(u_n+u_{n+1})/2`,
`I_g (u_{n+1}-u_n)/dt = Psub - Rg*u_m - b(A)*u_m*abs(u_m) - p_in,m`.

The current *linear* waveguide `PassiveTract.step(u_{n+1})` yields `p_in,m = d + k*u_{n+1}` for fixed prior tract state and time step, with a positive `k` arising from passive acoustic boundary inertance/compliance. Before final advancement evaluate the affine port response without permanently advancing the tract; evaluate the scalar monotone equation for `u_m`; then advance the tract **exactly once** with the solved `u_{n+1}`, and verify port-affine consistency. Do not run staggered or sample-lagged feedback as the candidate. Do not double count inlet-half-cell inertia: it belongs to `E_tract`.

For the candidate, total energy `E = (I_g/2)*u² + E_tract`. Fully coupled discrete midpoint energy identity at each open step:
`E_{n+1}-E_n = dt*(Psub*u_m - Rg*u_m² - b(A)*abs(u_m)^3 - R_L*u_out,m²)`.
Independent Wolfram symbolic oracle for this cancellation will be committed before claims. C0 instead needs an explicit *nonreciprocal port work* `+ dt*p_in,m*u_m`, and is **not passive as a closed system**. All outputs include individual input work, glottal losses, outlet loss, port pressures, flow, total energy, and per-step residual.

## Frozen pass/fail gates (non-retunable)

- G0: exact Wolfram one-cell port slope and one-step flow oracle, global midpoint-energy algebra residual 0; port affine slope >0; no NaN/Inf; input validation and failure on Ag=0, negative area, negative outlet resistance.
- G1: C0 geometry-only source-flow difference ≤ 1e-12 normalized RMS, C1 geometry-only upstream relative RMS difference > 0.001 (0.1%, base = C1 uniform). Also with same geometry, C0 vs C1 source-flow difference >0.001. A and Psub exactly identical across conditions. No acoustic-output filtering used to cause the intervention.
- G2: for coupled cases max per-step absolute total energy residual / max(cumulative absolute driving work, 1e-14 J) ≤1e-9, absolute max ≤1e-13 J, all dissipation nonnegative. Source-free zero state stays zero; positive and negative constant pressure drive stable and energy-bounded for this fixture. Validate time-step convergence at 24/48/96kHz (48 vs 96 error below 24 vs 48 error for upstream flow on aligned samples) and no significant effect of constriction before reflection can return from the changed section. Precise causality window: first 0.00025 s after t=0 must have geometry-only upstream abs delta < 1e-7 m³/s (intentionally conservative; depends on acoustic discretization).
- G3: compatible real Core `Tract1DGeometry` geometry and actual 032 `PassiveTract` imported from pinned stacked parent; no duplicate waveguide solver and no edit to predecessor.
- G4: `UNSUPPORTED` closed glottis, self-oscillating tissue, moving tract, acoustic branch/loss/radiation details. `NOT_TESTED` natural voice/listening, phonetic identity, continuous gestures. Do not reframe a numerical flow difference as audible quality.

## Process, artifacts, and audit

First document commit only, then independently computed Wolfram oracle source `.wl` and immutable checked-in `oracle.json`, then local `coupled.py`, `run.py`, `test_*.py` plus dedicated 3.11/3.12/3.13 GitHub Actions, reproduction instructions, CSV/JSON/energy traces, falsifiable `RESULTS.md`. Strict CI failure on failed eligible gates, no merge and PR stays Draft. Record the baseline SHAs and references in PR and issue #82.

References: Titze (2008), https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/ ; existing #79 glottal flow law and #81 fixed acoustic waveguide.
