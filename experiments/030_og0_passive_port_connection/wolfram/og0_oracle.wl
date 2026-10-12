(* OG-0 independent Wolfram Language oracle.
Pressure and VOLUME velocity U; exp(+I omega t); ideal zero-length
junction, same positive axial coordinate. No Python graph imports. *)

ClearAll[rho,c,lenA,lenB,areaA,areaBEq,areaBMismatch,freqs,za,zb,tm,normalize];
rho = 6/5; c = 343;
lenA = 2/25; lenB = 9/100;
areaA = 3/10000; areaBEq = areaA; areaBMismatch = 3/5000;
freqs = {80, 250, 400, 733, 1200, 2000, 4000};
za = rho c/areaA; zb = rho c/areaBMismatch;

tm[len_, area_, f_] := Module[{z = rho c/area, phase},
  phase = N[2 Pi f len/c, 30];
  {{Cos[phase], I z Sin[phase]}, {I Sin[phase]/z, Cos[phase]}}
];
normalize[m_] := {{m[[1, 1]], m[[1, 2]]/za},
                  {za m[[2, 1]], m[[2, 2]]}};

equalErrors = Table[
  Max[Abs[Flatten[normalize[tm[lenA, areaA, f].tm[lenB, areaBEq, f]] -
    normalize[tm[lenA + lenB, areaA, f]]]]],
  {f, freqs}
];
equalDetErrors = Table[
  Abs[Det[normalize[tm[lenA, areaA, f].tm[lenB, areaBEq, f]]] - 1],
  {f, freqs}
];

mismatch = tm[lenA, areaA, 733].tm[lenB, areaBMismatch, 733];
zIn = mismatch[[1, 2]]/mismatch[[2, 2]];
outletImpedance = I zb Tan[N[2 Pi 733 lenB/c, 30]];
zInRecursion = za (outletImpedance + I za Tan[N[2 Pi 733 lenA/c, 30]])/
                  (za + I outletImpedance Tan[N[2 Pi 733 lenA/c, 30]]);

(* Nonzero-power check uses matched outlet p_out=zb U_out and U_out=1e-6.
This is distinct from the finite pressure-release input impedance. *)
junction = tm[lenB, areaBMismatch, 733].{zb/10^6, 1/10^6};
junctionPower = Re[junction[[1]] Conjugate[junction[[2]]]]/2;
pressureReflection = (zb - za)/(zb + za);
reflectedFraction = pressureReflection^2;
transmittedFraction = 4 za zb/(za + zb)^2;

out = <|
  "frequency_grid_hz" -> freqs,
  "equal_normalized_matrix_max_discrepancy" -> N[Max[equalErrors], 16],
  "equal_det_max_discrepancy" -> N[Max[equalDetErrors], 16],
  "first_quarter_wave_hz" -> N[c/(4 (lenA+lenB)), 16],
  "characteristic_impedance_A" -> N[za],
  "characteristic_impedance_B" -> N[zb],
  "pressure_reflection_coefficient" -> N[pressureReflection],
  "reflected_power_fraction" -> N[reflectedFraction],
  "transmitted_power_fraction" -> N[transmittedFraction],
  "power_fraction_sum" -> N[reflectedFraction+transmittedFraction],
  "pressure_release_733hz_zin_re_im" -> N[{Re[zIn], Im[zIn]}, 16],
  "impedance_recursion_difference" -> N[Abs[zIn-zInRecursion], 16],
  "matched_733hz_junction_pressure_re_im" ->
    N[{Re[junction[[1]]], Im[junction[[1]]]}, 16],
  "matched_733hz_junction_volume_velocity_re_im" ->
    N[{Re[junction[[2]]], Im[junction[[2]]]}, 16],
  "matched_733hz_average_power_w" -> N[junctionPower, 16]
|>;
Print[out];
