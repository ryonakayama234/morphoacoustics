(* Experiment 028 independent Wolfram oracle.
   Evaluated before Python Experiment-028 execution on 2026-10-07.
   The frozen Experiment-027 task plan and realizer constants are unchanged. *)

ClearAll["Global`*"];

c = 343.;
rho = 1.21;
att = 0.4;
loadFrac = 0.05;
freqs = Range[100., 5000., 0.25];

sectionLength0 = 0.010;
sectionLength1 = 0.011;
totalLength0 = 16 sectionLength0;
totalLength1 = 16 sectionLength1;

aDiam = Reverse[{32, 28, 30, 34, 34, 38, 34, 30, 26, 20, 14, 12, 16, 26, 12, 12}];
iDiam = Reverse[{24, 14, 12, 10, 10, 10, 16, 24, 32, 32, 32, 32, 32, 32, 12, 12}];
area[d_] := Pi (d/1000./2)^2;
a = area /@ aDiam;
i = area /@ iDiam;

x = N[(Range[16] - 1)/15];
kappa = 1.5;
sigma = 0.16;
sigmaLip = 0.10;

openLocation = 0.3424849103873983;
openDegree = 0.5921764128805103;
constrictLocation = 0.7167402543883221;
constrictDegree = 0.9235962908995712;
lipLocation = 1.0;
lipDegree = 0.04495226070116771;
onset = 0.15;
offset = 0.35;

taskPlan = {
  <|"task" -> "OPEN", "location" -> openLocation, "degree" -> openDegree,
    "onset_s" -> onset, "offset_s" -> offset|>,
  <|"task" -> "CONSTRICT", "location" -> constrictLocation, "degree" -> constrictDegree,
    "onset_s" -> onset, "offset_s" -> offset|>,
  <|"task" -> "CONSTRICT", "location" -> lipLocation, "degree" -> lipDegree,
    "onset_s" -> onset, "offset_s" -> offset|>
};

kernel[xx_, loc_, sig_] := Exp[-(xx - loc)^2/(2 sig^2)];
delta = kappa (
  openDegree kernel[x, openLocation, sigma]
  - constrictDegree kernel[x, constrictLocation, sigma]
  - lipDegree kernel[x, lipLocation, sigmaLip]
);
taskEndpoint = a Exp[2 delta];

peaks[areas_, sectionLen_] := Module[{mag, zcOut, load, m, sec, k, idx},
  zcOut = rho c/Last[areas];
  load = loadFrac zcOut;
  mag = Table[
    k = 2 Pi f/c - I att;
    m = IdentityMatrix[2];
    Do[
      sec = {{Cos[k sectionLen], I (rho c/ar) Sin[k sectionLen]},
             {I Sin[k sectionLen]/(rho c/ar), Cos[k sectionLen]}};
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

pA0 = peaks[a, sectionLength0];
pI0 = peaks[i, sectionLength0];
pT0 = peaks[taskEndpoint, sectionLength0];
pA1 = peaks[a, sectionLength1];
pI1 = peaks[i, sectionLength1];
pT1 = peaks[taskEndpoint, sectionLength1];

e0 = Norm[pT0[[1 ;; 2]] - pI0[[1 ;; 2]]]/
  Norm[pA0[[1 ;; 2]] - pI0[[1 ;; 2]]];
e1 = Norm[pT1[[1 ;; 2]] - pI1[[1 ;; 2]]]/
  Norm[pA1[[1 ;; 2]] - pI1[[1 ;; 2]]];

coords0 = {openLocation, constrictLocation, lipLocation} totalLength0;
coords1 = {openLocation, constrictLocation, lipLocation} totalLength1;

scaleResiduals = Abs[Join[
  pA1[[1 ;; 3]] - pA0[[1 ;; 3]]/1.1,
  pI1[[1 ;; 3]] - pI0[[1 ;; 3]]/1.1,
  pT1[[1 ;; 3]] - pT0[[1 ;; 3]]/1.1
]];

<|
  "task_plan" -> taskPlan,
  "metric_task_coordinates_m" -> <|"M0" -> N[coords0, 17], "M1" -> N[coords1, 17]|>,
  "M0_a_peaks_hz" -> pA0,
  "M0_i_peaks_hz" -> pI0,
  "M0_task_endpoint_peaks_hz" -> pT0,
  "M1_a_peaks_hz" -> pA1,
  "M1_i_peaks_hz" -> pI1,
  "M1_task_endpoint_peaks_hz" -> pT1,
  "M0_endpoint_error_ratio" -> N[e0, 17],
  "M1_endpoint_error_ratio" -> N[e1, 17],
  "cross_body_endpoint_error_ratio_delta" -> N[Abs[e1 - e0], 17],
  "max_first_three_mode_residual_from_exact_1_over_1p1_scaling_hz" -> Max[scaleResiduals]
|>
