(* Experiment 031 / SFI-1 — independent Wolfram Language oracle.
   Intentional independent mathematics, no Python import, no fitted simulation data.
   Run via Wolfram Language 14+ or through the Wolfram evaluator. *)
ClearAll["Global`*"];

rho = 121/100;
cd = 7/10;
area = 3/100000;
inert = 1200;
rg = 1500000;
cap = 7/20000000000;
pDrive = 800;
dt = 1/48000;
oldU = 1/20000;
oldP = 200;
b = rho/(2 cd^2 area^2);

(* Steady C1: b U|U|+(Rg+Rout)U=Psub, p=Rout U. *)
steady[rr_] := Module[{u},
  u = 2 pDrive/(rg + rr + Sqrt[(rg + rr)^2 + 4 b pDrive]);
  {u, rr u}
];

(* Single simultaneous backward-Euler step for positive fixed pressure. *)
next[rr_, feedback_] := Module[{alpha, beta, a, rhs, u, p},
  alpha = cap/(cap + dt/rr);
  beta = dt/(cap + dt/rr);
  a = inert/dt + rg + feedback beta;
  rhs = pDrive + inert oldU/dt - feedback alpha oldP;
  u = 2 rhs/(a + Sqrt[a^2 + 4 b rhs]);
  p = alpha oldP + beta u;
  {u, p}
];

(* Independently derive the discrete energy balance using both BE equations. *)
dU = un - u0;
dP = pn - p0;
eDelta = inert/2 (un^2 - u0^2) + cap/2 (pn^2 - p0^2);
eRhs = dt (ps un - rg un^2 - bb un^2 Abs[un] - pn^2/rr) -
  inert/2 dU^2 - cap/2 dP^2;
flowEq = inert dU/dt - ps + rg un + bb un Abs[un] + pn;
chamberEq = cap dP/dt - un + pn/rr;
energyResidual = FullSimplify[
  eDelta - eRhs - dt (un flowEq + pn chamberEq),
  Assumptions -> {u0 \[Element] Reals, un \[Element] Reals,
    p0 \[Element] Reals, pn \[Element] Reals, bb >= 0, rr > 0}
];

(* Ideal valve closure: U_new=0, U_old kinetic energy is projected away. *)
closureResidual = FullSimplify[
  (cap/2 (pn^2-p0^2) - inert/2 u0^2) -
    (-dt pn^2/rr - cap/2 (pn-p0)^2 - inert/2 u0^2) /.
    p0 -> pn (1 + dt/(cap rr)),
  Assumptions -> {pn \[Element] Reals, u0 \[Element] Reals, rr > 0}
];

checks = <|
  "energy_residual_identically_zero" -> TrueQ[energyResidual == 0],
  "closure_residual_identically_zero" -> TrueQ[closureResidual == 0],
  "quadratic_loss_coefficient" -> N[b, 17],
  "steady_low" -> N[steady[2000000], 17],
  "steady_high" -> N[steady[8000000], 17],
  "step_c0_low" -> N[next[2000000, 0], 17],
  "step_c0_high" -> N[next[8000000, 0], 17],
  "step_c1_low" -> N[next[2000000, 1], 17],
  "step_c1_high" -> N[next[8000000, 1], 17],
  "linear_inertive_q1_amplitude_phase_deg" -> N[{1/Sqrt[2], -45}, 17],
  "linear_inertive_q2_amplitude_phase_deg" ->
    N[{1/Sqrt[5], -180 ArcTan[2]/Pi}, 17]
|>;
Print[InputForm[checks]];
