(* Experiment 011 independent coordination oracle *)
ClearAll[s, act, g1, g2seq, g2ov, energy, overlapIntegral, overlapCoefficient];

ramp = 0.03;
s[x_] := Piecewise[{{0, x <= 0}, {3 x^2 - 2 x^3, 0 < x < 1}, {1, x >= 1}}];
act[t_, on_, off_] := s[(t - on)/ramp] s[(off - t)/ramp];

g1[t_] := act[t, 0.08, 0.26];
g2seq[t_] := act[t, 0.26, 0.44];
g2ov[t_] := act[t, 0.20, 0.38];

energy[f_] := NIntegrate[f[t]^2, {t, 0, 0.5}, WorkingPrecision -> 50];
overlapIntegral[f_, g_] := NIntegrate[f[t] g[t], {t, 0, 0.5}, WorkingPrecision -> 50];
overlapCoefficient[f_, g_] := overlapIntegral[f, g]/Sqrt[energy[f] energy[g]];

result = <|
  "activation_integral_s" -> NIntegrate[g1[t], {t, 0, 0.5}, WorkingPrecision -> 50],
  "activation_squared_integral_s" -> energy[g1],
  "sequential_overlap_integral_s" -> overlapIntegral[g1, g2seq],
  "sequential_normalized_overlap" -> overlapCoefficient[g1, g2seq],
  "overlap_overlap_integral_s" -> overlapIntegral[g1, g2ov],
  "overlap_normalized_overlap" -> overlapCoefficient[g1, g2ov],
  "linear_interpolation_activation_max_abs_error_bounds" -> <|
    "5ms" -> N[(6/8) (0.005/ramp)^2, 30],
    "2.5ms" -> N[(6/8) (0.0025/ramp)^2, 30]
  |>
|>;

Export[FileNameJoin[{DirectoryName[$InputFileName], "coordination_oracle.json"}], result, "RawJSON"];
result
