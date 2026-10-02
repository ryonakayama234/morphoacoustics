Module[
  {
    c = 343.,
    rho = 1.21,
    alpha = 0.4,
    dx = 0.01,
    loadFraction = 0.05,
    frequencies,
    fixtures,
    calculatePeaks
  },

  frequencies = N@Range[100, 5000, 0.25];

  fixtures = <|
    "a" -> Reverse[{32, 28, 30, 34, 34, 38, 34, 30, 26, 20, 14, 12, 16, 26, 12, 12}],
    "i" -> Reverse[{24, 14, 12, 10, 10, 10, 16, 24, 32, 32, 32, 32, 32, 32, 12, 12}],
    "u" -> Reverse[{16, 14, 20, 22, 22, 24, 22, 14, 18, 26, 30, 30, 30, 30, 12, 12}]
  |>;

  calculatePeaks[diameters_List] := Module[
    {areas, total, k, zc, matrix, zcOut, load, denominator, magnitude, indices},

    areas = Pi ((diameters/1000.)/2.)^2;
    total = Table[IdentityMatrix[2], {Length[frequencies]}];

    Do[
      k = 2 Pi frequencies/c - I alpha;
      zc = rho c/areas[[j]];
      matrix = Map[
        {
          {Cos[# dx], I zc Sin[# dx]},
          {I Sin[# dx]/zc, Cos[# dx]}
        } &,
        k
      ];
      total = MapThread[Dot, {total, matrix}],
      {j, Length[areas]}
    ];

    zcOut = rho c/Last[areas];
    load = loadFraction zcOut;
    denominator = total[[All, 2, 1]] load + total[[All, 2, 2]];
    magnitude = Abs[1/denominator];

    indices = Select[
      Range[2, Length[magnitude] - 1],
      magnitude[[#]] > magnitude[[# - 1]] &&
      magnitude[[#]] >= magnitude[[# + 1]] &
    ];

    Take[
      Transpose[{frequencies[[indices]], magnitude[[indices]]}],
      Min[5, Length[indices]]
    ]
  ];

  Export[
    "vowel_tube_oracle.json",
    <|
      "model" -> <|
        "sound_speed_m_s" -> c,
        "air_density_kg_m3" -> rho,
        "attenuation_np_m" -> alpha,
        "section_length_m" -> dx,
        "load_fraction_of_outlet_zc" -> loadFraction,
        "scan_start_hz" -> First[frequencies],
        "scan_end_hz" -> Last[frequencies],
        "scan_step_hz" -> 0.25
      |>,
      "peaks" -> AssociationMap[calculatePeaks, fixtures]
    |>,
    "RawJSON"
  ]
]
