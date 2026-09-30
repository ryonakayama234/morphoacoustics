(* Independent analytic reference for Experiment 008. *)

ClearAll[x, s, ramp, steps, bounds, result];
s[x_] := 3 x^2 - 2 x^3;
ramp = 0.05;
steps = {0.01, 0.005, 0.0025, 0.00125};

bounds = AssociationThread[
  ToString /@ steps,
  N[(6/8) (steps/ramp)^2, 16]
];

result = <|
  "source" -> "Wolfram Language independent analytic check",
  "smoothstep" -> "s(x)=3 x^2-2 x^3",
  "smoothstep_second_derivative_max_abs" ->
    MaxValue[{Abs[D[s[x], {x, 2}]], 0 <= x <= 1}, x],
  "ramp_s" -> ramp,
  "smoothstep_linear_interpolation_abs_error_bounds" -> bounds,
  "explicit_event_reference" -> <|
    "onset_s" -> 0.05,
    "offset_s" -> 0.35,
    "onset_abs_error_s" -> 0,
    "offset_abs_error_s" -> 0,
    "event_order_preserved" -> True
  |>
|>;

Print[Dataset[result]];
Export[
  FileNameJoin[{DirectoryName[$InputFileName], "event_trajectory_oracle.generated.json"}],
  result,
  "RawJSON"
];
