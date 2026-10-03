(* Experiment 016 independent scale-covariance oracle *)

ClearAll[rho, c, a0, ag, l0, l1, scale, tm, denom, root, modes, result];

rho = 121/100;
c = 343;
a0 = 3/10000;
ag = 2/10000;
l0 = 17/100;
scale = 11/10;
l1 = scale l0;

tm[len_, area_, f_] := Module[{k = 2 Pi f/c, z = rho c/area},
  {{Cos[k len], I z Sin[k len]},
   {I Sin[k len]/z, Cos[k len]}}
];

denom[length_, gesture_, f_] := Module[{areas, matrices},
  areas = ConstantArray[a0, 10];
  If[gesture, areas[[7]] = ag];
  matrices = Table[tm[length/10, areas[[j]], f], {j, 1, 10}];
  Re[(Dot @@ matrices)[[2, 2]]]
];

root[length_, gesture_, guess_] := Module[{x},
  x /. FindRoot[
    denom[length, gesture, x] == 0,
    {x, SetPrecision[guess, 60]},
    WorkingPrecision -> 60,
    AccuracyGoal -> 45,
    PrecisionGoal -> 45
  ]
];

modes[length_, gesture_] := Table[
  N[root[length, gesture, (2 n - 1) c/(4 length)], 18],
  {n, 1, 3}
];

r0 = modes[l0, False];
g0 = modes[l0, True];
r1 = modes[l1, False];
g1 = modes[l1, True];

result = <|
  "parameters" -> <|
    "sound_speed_m_s" -> N[c, 18],
    "air_density_kg_m3" -> N[rho, 18],
    "rest_area_m2" -> N[a0, 18],
    "target_area_m2" -> N[ag, 18],
    "section_count" -> 10,
    "gesture_location_normalized" -> N[13/20, 18],
    "length_m0_m" -> N[l0, 18],
    "length_m1_m" -> N[l1, 18],
    "length_scale_m1_over_m0" -> N[scale, 18],
    "expected_frequency_scale_m1_over_m0" -> N[1/scale, 18]
  |>,
  "conditions" -> <|
    "M0_rest" -> r0,
    "M0_gesture" -> g0,
    "M1_rest" -> r1,
    "M1_gesture" -> g1
  |>,
  "physical_prediction" -> <|
    "target_axial_position_m" ->
      {N[(13/20) l0, 18], N[(13/20) l1, 18]},
    "constricted_section_length_m" ->
      {N[l0/10, 18], N[l1/10, 18]},
    "expected_axial_scale" -> N[scale, 18]
  |>,
  "cross_body_frequency_ratios" -> <|
    "rest" -> N[r1/r0, 18],
    "gesture" -> N[g1/g0, 18]
  |>,
  "within_body_gesture_over_rest_ratios" -> <|
    "M0" -> N[g0/r0, 18],
    "M1" -> N[g1/r1, 18]
  |>,
  "within_body_log_gesture_effects" -> <|
    "M0" -> N[Log[g0/r0], 18],
    "M1" -> N[Log[g1/r1], 18]
  |>,
  "cross_body_log_effect_difference" ->
    N[Log[g1/r1] - Log[g0/r0], 18]
|>;

Export[
  FileNameJoin[{DirectoryName[$InputFileName], "scale_covariance_oracle.json"}],
  result,
  "RawJSON"
];
result
