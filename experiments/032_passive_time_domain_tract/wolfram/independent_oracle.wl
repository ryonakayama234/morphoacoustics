(* Experiment 032: independent Wolfram Language analytical oracle, 2026-10-10.
   No Python imports. Fixed uniform 1D rigid plane-wave tube; numerical scheme
   checked independently by a generic two-cell midpoint energy identity. *)
ClearAll["Global`*"];
rho = 121/100; c = 343; area = 3/10000; length = 17/100;
zc = rho*c/area;
zin[zl_, omega_] := FullSimplify[
  zc*(zl + I*zc*Tan[omega*length/c]) /
  (zc + I*zl*Tan[omega*length/c])
];
frequencies = Table[(2 k - 1)*c/(4 length), {k, 1, 3}];
roundTrip = 2 length/c;
rArea = (a1 - a2)/(a1 + a2);
junctionPower = FullSimplify[
  rArea^2 + 4 a1 a2/(a1 + a2)^2,
  Assumptions -> {a1 > 0, a2 > 0}
];

(* Generic two-cell energy of staggered p0,p1 and faces U0,U1,U2.
   U0 is prescribed at inlet, and the inlet half-face inertance m0 is included.
   The passive resistive outlet consumes R*U2mid^2. *)
pm0 = (op0 + np0)/2; pm1 = (op1 + np1)/2;
um0 = (ou0 + nu0)/2; um1 = (ou1 + nu1)/2; um2 = (ou2 + nu2)/2;
deltaE = (
    c0*(np0^2 - op0^2) + c1*(np1^2 - op1^2) +
    m0*(nu0^2 - ou0^2) + m1*(nu1^2 - ou1^2) +
    m2*(nu2^2 - ou2^2))/2;
workMinusLoss = h*((pm0 + m0*(nu0-ou0)/h)*um0 - rout*um2^2);
pressureEquation0 = c0*(np0-op0)/h - (um0-um1);
pressureEquation1 = c1*(np1-op1)/h - (um1-um2);
flowEquation1 = m1*(nu1-ou1)/h - (pm0-pm1);
flowEquation2 = m2*(nu2-ou2)/h - (pm1-rout*um2);
symbolicResidual = FullSimplify[
  deltaE - workMinusLoss -
  h*(pm0*pressureEquation0 + pm1*pressureEquation1 +
     um1*flowEquation1 + um2*flowEquation2)
];

checks = <|
  "uniform_length_m" -> N[length, 17],
  "characteristic_impedance" -> N[zc, 17],
  "round_trip_seconds" -> N[roundTrip, 17],
  "quarter_wave_modes_hz" -> N[frequencies, 17],
  "matched_load_is_constant" -> TrueQ[FullSimplify[zin[zc,w] == zc, Assumptions -> Element[w, Reals]]],
  "pressure_release_input_impedance" -> zin[0,w],
  "junction_reflection_half_area" -> rArea /. a2 -> a1/2,
  "junction_reflection_equal_area" -> rArea /. a2 -> a1,
  "junction_energy_fraction_sum" -> junctionPower,
  "two_cell_midpoint_energy_residual" -> symbolicResidual
|>;
Print[InputForm[checks]];
