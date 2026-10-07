(* Experiment 026 independent Wolfram oracle.
   Evaluated before Python Experiment-026 execution on 2026-10-07.
   This source is provenance only; the Python runner reads v2_oracle.json. *)

ClearAll["Global`*"];

c = 343.;
rho = 1.21;
att = 0.4;
len = 0.01;
loadFrac = 0.05;
freqs = Range[100., 5000., 0.25];

aDiam = Reverse[{32, 28, 30, 34, 34, 38, 34, 30, 26, 20, 14, 12, 16, 26, 12, 12}];
iDiam = Reverse[{24, 14, 12, 10, 10, 10, 16, 24, 32, 32, 32, 32, 32, 32, 12, 12}];

area[d_] := Pi (d/1000./2)^2;
a = area /@ aDiam;
i = area /@ iDiam;
linearMid = (a + i)/2;
logMid = Sqrt[a i];

peaks[areas_] := Module[{mag, zcOut, load, m, sec, k, idx},
  zcOut = rho c/Last[areas];
  load = loadFrac zcOut;
  mag = Table[
    k = 2 Pi f/c - I att;
    m = IdentityMatrix[2];
    Do[
      sec = {{Cos[k len], I (rho c/ar) Sin[k len]},
             {I Sin[k len]/(rho c/ar), Cos[k len]}};
      m = m.sec,
      {ar, areas}
    ];
    Abs[1/(m[[2, 1]] load + m[[2, 2]])],
    {f, freqs}
  ];
  idx = Select[Range[2, Length[mag] - 1],
    mag[[#]] > mag[[# - 1]] && mag[[#]] >= mag[[# + 1]] &];
  Take[freqs[[idx]], UpTo[5]]
];

t0 = .15;
t1 = .35;
duration = t1 - t0;
smooth[u_] := u^2 (3 - 2 u);
lambda[t_] := Piecewise[
  {{0, t <= t0}, {smooth[(t - t0)/duration], t0 < t < t1}, {1, t >= t1}}
];

reconstructionError[h_] := Module[{grid, vals, interp, ts},
  grid = Range[-h, .5 + h, h];
  vals = lambda /@ grid;
  interp = Interpolation[Transpose[{grid, vals}], InterpolationOrder -> 1];
  ts = Range[0, .5, .00001];
  Max[Abs[(lambda /@ ts) - (interp /@ ts)]]
];

<|
  "a_peaks_hz" -> peaks[a],
  "i_peaks_hz" -> peaks[i],
  "linear_midpoint_peaks_hz" -> peaks[linearMid],
  "log_midpoint_peaks_hz" -> peaks[logMid],
  "linear_midpoint_areas_m2" -> N[linearMid, 16],
  "log_midpoint_areas_m2" -> N[logMid, 16],
  "min_endpoint_area_m2" -> Min[Join[a, i]],
  "min_linear_midpoint_area_m2" -> Min[linearMid],
  "min_log_midpoint_area_m2" -> Min[logMid],
  "5ms_max_abs_lambda_error" -> N[reconstructionError[.005], 16],
  "2p5ms_max_abs_lambda_error" -> N[reconstructionError[.0025], 16],
  "midpoint_lambda" -> N[lambda[.25], 16],
  "quarter_wave_014_hz" -> N[Table[(2 n - 1) c/(4 .14), {n, 1, 3}], 16],
  "quarter_wave_017_hz" -> N[Table[(2 n - 1) c/(4 .17), {n, 1, 3}], 16],
  "quarter_wave_020_hz" -> N[Table[(2 n - 1) c/(4 .20), {n, 1, 3}], 16]
|>
