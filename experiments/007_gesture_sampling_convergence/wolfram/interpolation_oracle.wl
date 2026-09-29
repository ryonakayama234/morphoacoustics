(* Experiment 007 independent oracle.
   This file is intentionally independent of morphoacoustics implementation code. *)

s[x_] := 3 x^2 - 2 x^3;
maxSecondDerivative = MaxValue[{Abs[D[s[x], {x, 2}]], 0 <= x <= 1}, x];

ramp = 0.05;
steps = {0.01, 0.005, 0.0025, 0.00125};
bounds = Association@Table[
  ToString[1000 h] -> (maxSecondDerivative/8) (h/ramp)^2,
  {h, steps}
];

quarterWaveHz = 343/(4 0.17);

result = <|
  "oracle" -> "Wolfram Language",
  "smoothstep" -> "s(x) = 3 x^2 - 2 x^3",
  "max_abs_second_derivative" -> maxSecondDerivative,
  "ramp_s" -> ramp,
  "smoothstep_linear_interpolation_abs_error_bounds" -> bounds,
  "quarter_wave" -> <|
    "sound_speed_m_s" -> 343,
    "length_m" -> 0.17,
    "fundamental_hz" -> N[quarterWaveHz, 17]
  |>
|>;

Print[ExportString[result, "RawJSON"]];
