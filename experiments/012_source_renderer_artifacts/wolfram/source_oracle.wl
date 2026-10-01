(* Experiment 012 independent source-only oracle. *)
ClearAll["Global`*"];

f0 = 100.;
fs = 48000.;
duration = 0.5;
peak = 1.;
openQuotient = 0.6;

t = Range[0, Round[fs duration] - 1]/fs;
normalize[x_] := x/Max[Abs[x]] peak;
harmonic[n_, p_] := normalize[Total[Table[k^-p Sin[2 Pi k f0 t], {k, 1, n}]]];
smoothFlow = normalize[
  Map[
    Function[x,
      With[{phase = FractionalPart[f0 x]},
        If[phase < openQuotient, Sin[Pi phase/openQuotient]^2, 0.]
      ]
    ],
    t
  ]
];

highFrequencyRatio[x_] := Module[{power, oneSided, frequencies},
  power = Abs[Fourier[x, FourierParameters -> {1, -1}]]^2;
  oneSided = Take[power, Floor[Length[power]/2] + 1];
  frequencies = Range[0, Length[oneSided] - 1] fs/Length[x];
  Total[Pick[oneSided, Map[# >= 2000. &, frequencies]]]/Total[oneSided]
];

metrics[name_, x_] := <|
  "name" -> name,
  "crest_factor" -> Max[Abs[x]]/Sqrt[Mean[x^2]],
  "max_abs_derivative_per_rms" -> Max[Abs[Differences[x]]] fs/Sqrt[Mean[x^2]],
  "energy_ratio_ge_2khz" -> highFrequencyRatio[x]
|>;

result = <|
  "sample_rate_hz" -> fs,
  "f0_hz" -> f0,
  "duration_s" -> duration,
  "smooth_flow_open_quotient" -> openQuotient,
  "sources" -> {
    metrics["current40_p1.2", harmonic[40, 1.2]],
    metrics["harmonic10_p1.2", harmonic[10, 1.2]],
    metrics["harmonic40_p2.0", harmonic[40, 2.0]],
    metrics["smooth_flow_oq0.6", smoothFlow]
  }
|>;

Export[FileNameJoin[{DirectoryName[$InputFileName], "source_oracle.json"}], result, "RawJSON"];
result
