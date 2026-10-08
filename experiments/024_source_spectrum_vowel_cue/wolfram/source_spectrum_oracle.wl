Module[
  {
    c = 343., rho = 1.21, alpha = 0.4, dx = 0.01,
    loadFraction = 0.05, f0 = 100., fixtures, harmonics,
    transferMagnitude, sourceRatioDb, observerRatioDb, tractRatioDb, predictedDb
  },

  fixtures = <|
    "a" -> Reverse[{32, 28, 30, 34, 34, 38, 34, 30, 26, 20, 14, 12, 16, 26, 12, 12}],
    "i" -> Reverse[{24, 14, 12, 10, 10, 10, 16, 24, 32, 32, 32, 32, 32, 32, 12, 12}],
    "u" -> Reverse[{16, 14, 20, 22, 22, 24, 22, 14, 18, 26, 30, 30, 30, 30, 12, 12}]
  |>;

  harmonics = <|
    "a" -> {7, 13},
    "i" -> {3, 23},
    "u" -> {4, 15}
  |>;

  transferMagnitude[diameters_List, frequency_] := Module[
    {areas, total, k, zc, matrix, zcOut, load, denominator},
    areas = Pi ((diameters/1000.)/2.)^2;
    total = IdentityMatrix[2];
    k = 2 Pi frequency/c - I alpha;
    Do[
      zc = rho c/areas[[j]];
      matrix = {
        {Cos[k dx], I zc Sin[k dx]},
        {I Sin[k dx]/zc, Cos[k dx]}
      };
      total = total . matrix,
      {j, Length[areas]}
    ];
    zcOut = rho c/Last[areas];
    load = loadFraction zcOut;
    denominator = total[[2, 1]] load + total[[2, 2]];
    Abs[1/denominator]
  ];

  sourceRatioDb[v_] := Module[{n1, n2},
    {n1, n2} = harmonics[v];
    N[20 Log10[n1/n2]]
  ];

  observerRatioDb[v_] := Module[{n1, n2},
    {n1, n2} = harmonics[v];
    N[20 Log10[n2/n1]]
  ];

  tractRatioDb[v_] := Module[{n1, n2, h1, h2},
    {n1, n2} = harmonics[v];
    h1 = transferMagnitude[fixtures[v], n1 f0];
    h2 = transferMagnitude[fixtures[v], n2 f0];
    20 Log10[h2/h1]
  ];

  predictedDb[v_] := sourceRatioDb[v] + observerRatioDb[v] + tractRatioDb[v];

  Export[
    "source_spectrum_oracle.json",
    <|
      "f0_hz" -> f0,
      "harmonic_count" -> 40,
      "source_model" -> "A_n proportional to 1/n",
      "source_p2_over_p1_db" -> AssociationMap[sourceRatioDb, Keys[fixtures]],
      "observer_scaling_p2_over_p1_db" -> AssociationMap[observerRatioDb, Keys[fixtures]],
      "tract_p2_over_p1_db" -> AssociationMap[tractRatioDb, Keys[fixtures]],
      "predicted_listening_pressure_p2_over_p1_db" -> AssociationMap[predictedDb, Keys[fixtures]],
      "source_ratio_tolerance_db" -> 0.25,
      "rendered_ratio_tolerance_db" -> 2.0,
      "minimum_i_improvement_db" -> 10.0
    |>,
    "RawJSON"
  ]
]
