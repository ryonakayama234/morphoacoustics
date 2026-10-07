Module[
  {
    fs = 48000., f0 = 100., duration = 0.5, ramp = 0.01,
    harmonicCount = 40, p = 2., sampleCount, t, envelope,
    source, boundaries, rms, jumpRatio, pairs, tract, sourceRatio,
    observerDelta, rendered
  },
  sampleCount = Round[fs duration];
  t = Range[0, sampleCount - 1]/fs;
  envelope = ConstantArray[1., sampleCount];
  Module[{r = Round[fs ramp], phase, rv},
    phase = Subdivide[0., Pi/2., r][[1 ;; r]];
    rv = Sin[phase]^2;
    envelope[[1 ;; r]] *= rv;
    envelope[[-r ;; -1]] *= Reverse[rv];
  ];

  source = envelope Sum[
    Cos[2 Pi n f0 t]/n^p,
    {n, 1, harmonicCount}
  ];

  rms[x_] := Sqrt[Mean[x^2]];
  boundaries = Range[Round[fs/f0] + 1, sampleCount, Round[fs/f0]];
  jumpRatio = Max[Abs[source[[boundaries]] - source[[boundaries - 1]]]]/rms[source];

  pairs = <|"a" -> {7, 13}, "i" -> {3, 23}, "u" -> {4, 15}|>;
  tract = <|"a" -> 1.3340, "i" -> 3.8173, "u" -> -3.2705|>;

  sourceRatio[v_] := Module[{n1 = pairs[v][[1]], n2 = pairs[v][[2]]},
    20 Log10[(n2^-p)/(n1^-p)]
  ];
  observerDelta[v_] := Module[{n1 = pairs[v][[1]], n2 = pairs[v][[2]]},
    20 Log10[n2/n1]
  ];
  rendered[v_] := tract[v] + sourceRatio[v] + observerDelta[v];

  <|
    "predicted_cycle_boundary_jump_per_rms" -> N[jumpRatio],
    "source_p2_over_p1_db" -> AssociationMap[N[sourceRatio[#]] &, Keys[pairs]],
    "observer_delta_db" -> AssociationMap[N[observerDelta[#]] &, Keys[pairs]],
    "tract_p2_over_p1_db" -> tract,
    "predicted_listening_pressure_p2_over_p1_db" -> AssociationMap[N[rendered[#]] &, Keys[pairs]],
    "predicted_i_improvement_vs_s0_db" -> N[rendered["i"] - (-28.7989)]
  |>
]
