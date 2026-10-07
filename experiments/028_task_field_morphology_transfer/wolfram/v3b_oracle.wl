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

(* Vectorize across frequencies; retain the same 2x2 section-matrix product. *)
peaks[areas_, sectionLen_] := Module[
  {mag, zcOut, load, k, idx, cs, sn, aa, bb, cc, dd, zc},
  zcOut = rho c/Last[areas];
  load = loadFrac zcOut;
  k = 2 Pi freqs/c - I att;
  cs = Cos[k sectionLen];
  sn = I Sin[k sectionLen];
  aa = dd = ConstantArray[1., Length[freqs]];
  bb = cc = ConstantArray[0., Length[freqs]];
  Do[
    zc = rho c/ar;
    {aa, bb, cc, dd} = {
      aa cs + bb sn/zc, aa zc sn + bb cs,
      cc cs + dd sn/zc, cc zc sn + dd cs
    },
    {ar, areas}
  ];
  mag = Abs[1/(cc load + dd)];
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

(* Provenance below describes the original preregistered oracle freeze, not
   the timing of a later regeneration/verification run. *)
oracle = <|
  "provenance" -> <|
    "tool" -> "Wolfram Language evaluator",
    "evaluated_before_python_experiment" -> True,
    "date" -> "2026-10-07",
    "purpose" -> "independent V3b axial-length morphology-transfer oracle for the frozen Experiment-027 task plan"
  |>,
  "model" -> <|
    "sound_speed_m_s" -> c, "air_density_kg_m3" -> rho,
    "attenuation_np_m" -> att, "load_fraction_of_outlet_zc" -> loadFrac,
    "frequency_scan_start_hz" -> First[freqs],
    "frequency_scan_end_hz" -> Last[freqs],
    "frequency_scan_step_hz" -> 0.25, "peak_tolerance_hz" -> 0.5
  |>,
  "morphologies" -> <|
    "M0" -> <|"section_count" -> 16, "section_length_m" -> sectionLength0,
      "total_length_m" -> totalLength0|>,
    "M1" -> <|"section_count" -> 16, "section_length_m" -> sectionLength1,
      "total_length_m" -> totalLength1, "axial_scale_over_M0" -> 1.1|>
  |>,
  "realizer" -> <|
    "field_space" -> "log_diameter",
    "coordinate_mapping" -> "section slots mapped uniformly to x=j/(N-1)",
    "kappa" -> kappa, "sigma" -> sigma, "sigma_lip" -> sigmaLip
  |>,
  "task_plan" -> taskPlan,
  "metric_task_coordinates_m" -> <|"M0" -> N[coords0, 17], "M1" -> N[coords1, 17]|>,
  "peak_frequencies_hz" -> <|
    "M0_a" -> pA0, "M0_i" -> pI0, "M0_task_endpoint" -> pT0,
    "M1_a" -> pA1, "M1_i" -> pI1, "M1_task_endpoint" -> pT1
  |>,
  "metrics" -> <|
    "M0_endpoint_error_ratio" -> N[e0, 17],
    "M1_endpoint_error_ratio" -> N[e1, 17],
    "cross_body_endpoint_error_ratio_delta" -> N[Abs[e1 - e0], 17],
    "max_first_three_mode_residual_from_exact_1_over_1p1_scaling_hz" -> Max[scaleResiduals]
  |>,
  "frozen_gate" -> <|
    "M1_endpoint_error_ratio_max" -> 0.20,
    "cross_body_endpoint_error_ratio_delta_max" -> 0.005,
    "metric_coordinate_scale_abs_tolerance" -> 10.^-12,
    "body_effect_min_over_peak_tolerance" -> 5.,
    "trajectory_step_ratio_max" -> 0.20,
    "artifact_jump_ratio_max" -> 3.,
    "temporal_normalized_rms_floor_max" -> 0.20
  |>
|>;

(* Never overwrite the frozen record by default. With wolframscript:
   wolframscript -file wolfram/v3b_oracle.wl /tmp/v3b_regenerated.json
   python wolfram/verify_oracle.py /tmp/v3b_regenerated.json
   The comparison is schema-complete and exact after JSON parsing. Whitespace
   and JSON number spelling do not matter; numeric tolerances are not relaxed. *)
If[StringQ[$InputFileName] && StringLength[$InputFileName] > 0,
  outputPath = If[Length[$ScriptCommandLine] >= 2 &&
      StringEndsQ[Last[$ScriptCommandLine], ".json"],
    Last[$ScriptCommandLine],
    FileNameJoin[{DirectoryName[$InputFileName], "v3b_oracle.regenerated.json"}]
  ];
  Export[outputPath, oracle, "RawJSON"]
];
oracle
