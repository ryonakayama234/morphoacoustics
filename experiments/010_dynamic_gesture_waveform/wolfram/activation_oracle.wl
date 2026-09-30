(* Independent analytic oracle for Experiment 010. *)
s[x_] := 3 x^2 - 2 x^3;
maxSecond = MaxValue[{Abs[D[s[x], {x, 2}]], 0 <= x <= 1}, x];
bound[h_, ramp_] := N[(maxSecond/8) (h/ramp)^2, 17];

result = <|
  "smoothstep" -> "3 x^2 - 2 x^3",
  "endpoint_values" -> {s[0], s[1]},
  "endpoint_first_derivatives" -> {D[s[x], x] /. x -> 0, D[s[x], x] /. x -> 1},
  "max_abs_second_derivative_unit_interval" -> maxSecond,
  "linear_interpolation_activation_max_abs_error_bounds" -> <|
    "fast" -> <|
      "ramp_s" -> 0.03,
      "5ms" -> bound[0.005, 0.03],
      "2.5ms" -> bound[0.0025, 0.03]
    |>,
    "slow" -> <|
      "ramp_s" -> 0.09,
      "5ms" -> bound[0.005, 0.09],
      "2.5ms" -> bound[0.0025, 0.09]
    |>
  |>
|>;

Export[FileNameJoin[{DirectoryName[$InputFileName], "activation_oracle.json"}], result, "RawJSON"];
Print[result];
