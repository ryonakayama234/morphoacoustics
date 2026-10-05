(* Experiment 015 independent Embodiment calibration oracle *)

ClearAll[c, l0, epsilons, modes, freq, points, centralSensitivity, result];

c = 343;
l0 = 17/100;
epsilons = {-1/10, -1/20, 0, 1/20, 1/10};
modes = Range[3];

freq[n_, length_] := (2 n - 1) c/(4 length);

points = Table[
  <|
    "relative_change" -> N[e, 17],
    "length_m" -> N[l0 (1 + e), 17],
    "modes_hz" -> Table[N[freq[n, l0 (1 + e)], 17], {n, modes}]
  |>,
  {e, epsilons}
];

centralSensitivity[mode_, e_] :=
  (Log[freq[mode, l0 (1 + e)]] - Log[freq[mode, l0 (1 - e)]])/
  (Log[1 + e] - Log[1 - e]);

result = <|
  "sound_speed_m_s" -> N[c, 17],
  "baseline_length_m" -> N[l0, 17],
  "area_m2" -> N[3/10000, 17],
  "sweep" -> points,
  "log_sensitivity_exact" -> -1.0,
  "central_log_sensitivity_eps_0_05" ->
    Table[N[centralSensitivity[n, 1/20], 17], {n, modes}],
  "central_log_sensitivity_eps_0_10" ->
    Table[N[centralSensitivity[n, 1/10], 17], {n, modes}],
  "ratio_L_plus_10pct" -> N[freq[1, (11/10) l0]/freq[1, l0], 17],
  "ratio_L_minus_10pct" -> N[freq[1, (9/10) l0]/freq[1, l0], 17]
|>;

Export[
  FileNameJoin[{DirectoryName[$InputFileName], "embodiment_oracle.json"}],
  result,
  "RawJSON"
];
result
