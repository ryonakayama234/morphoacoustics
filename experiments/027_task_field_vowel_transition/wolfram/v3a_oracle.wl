(* Experiment 027 independent Wolfram oracle.
   Fixed candidate values were selected before Python Experiment-027 execution.
   This source verifies the frozen task field; it does not refit the candidate. *)

ClearAll["Global`*"];

c = 343.;
rho = 1.21;
att = 0.4;
len = 0.01;
loadFrac = 0.05;
freqs = Range[100., 5000., 0.25];

aDiam = Reverse[{32, 28, 30, 34, 34, 38, 34, 30, 26, 20, 14, 12, 16, 26, 12, 12}];
iDiam = Reverse[{24, 14, 12, 10, 10, 10, 16, 24, 32, 32, 32, 32, 32, 32, 12, 12}];
x = N[(Range[Length[aDiam]] - 1)/(Length[aDiam] - 1)];

kappa = 1.5;
sigma = 0.16;
sigmaLip = 0.10;

openLocation = 0.3424849103873983;
openDegree = 0.5921764128805103;
constrictLocation = 0.7167402543883221;
constrictDegree = 0.9235962908995712;
lipLocation = 1.0;
lipDegree = 0.04495226070116771;

kernel[xx_, loc_, sig_] := Exp[-(xx - loc)^2/(2 sig^2)];

delta = kappa (
    openDegree kernel[x, openLocation, sigma]
    - constrictDegree kernel[x, constrictLocation, sigma]
    - lipDegree kernel[x, lipLocation, sigmaLip]
);

taskDiam = Exp[Log[N[aDiam]] + delta];
area[d_] := Pi (d/1000./2)^2;
a = area /@ aDiam;
i = area /@ iDiam;
task = area /@ taskDiam;

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

aPeaks = peaks[a];
iPeaks = peaks[i];
taskPeaks = peaks[task];
endpointDistance = Norm[aPeaks[[1 ;; 2]] - iPeaks[[1 ;; 2]]];
taskToI = Norm[taskPeaks[[1 ;; 2]] - iPeaks[[1 ;; 2]]];
taskToA = Norm[taskPeaks[[1 ;; 2]] - aPeaks[[1 ;; 2]]];

<|
  "task_endpoint_diameters_mm" -> N[taskDiam, 17],
  "task_endpoint_areas_m2" -> N[task, 17],
  "a_peaks_hz" -> aPeaks,
  "i_peaks_hz" -> iPeaks,
  "task_endpoint_peaks_hz" -> taskPeaks,
  "a_to_i_p1p2_distance_hz" -> N[endpointDistance, 17],
  "task_to_i_p1p2_distance_hz" -> N[taskToI, 17],
  "task_to_i_over_a_to_i" -> N[taskToI/endpointDistance, 17],
  "task_to_a_p1p2_distance_hz" -> N[taskToA, 17],
  "task_to_a_over_task_to_i" -> N[taskToA/taskToI, 17]
|>
