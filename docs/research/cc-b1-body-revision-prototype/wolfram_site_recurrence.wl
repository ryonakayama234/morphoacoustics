(* Independent 16-tube acoustic input-impedance recurrence; NOT a confirmatory
   physical simulation, human hearing test or audibility Gate.
   Recalculates PR #144's post-hoc selected sites by a different numerical
   formulation from the PR #144 2x2 ABCD matrix multiplication. *)
Module[{diam, a, x, deformation, restAtEnd, phase, zIn, freqs, f2, edit, rows},
  diam = {12, 12, 26, 16, 12, 14, 20, 26, 30, 34, 38, 34, 34, 30, 28, 32};
  a = N[Pi (diam/2000.)^2]; (* diameter in mm -> area in SI m^2 *)
  x = N[Range[0,15]/15];
  deformation = 3 (
    0.5921764128805103 Exp[-(x - 0.3424849103873983)^2/(2 .16^2)]
    - 0.9235962908995712 Exp[-(x - 0.7167402543883221)^2/(2 .16^2)]
    - 0.04495226070116771 Exp[-(x - 1)^2/(2 .10^2)]
  );
  restAtEnd = a Exp[deformation];
  zIn[f_, areas_] := Module[{z = 0.0 + 0. I, ze,
                               ph = 2 Pi f .01/343.},
    Do[
      ze = 1.2 343./areas[[j]];
      z = ze (z + I ze Tan[ph])/(ze + I z Tan[ph]),
      {j, Length[areas], 1, -1}
    ];
    Abs[z]
  ];
  freqs = Range[1800,2440,5];
  f2[areas_] := freqs[[First[Ordering[zIn[#, areas] & /@ freqs, -1]]]];
  edit[j_, ratio_] := ReplacePart[restAtEnd, j -> restAtEnd[[j]] ratio];
  rows = Table[
    With[{low = f2[edit[j, .90]], high = f2[edit[j, 1.10]]},
      <|"zero_based_site" -> j-1,
        "minus_f2_hz" -> low,
        "plus_f2_hz" -> high,
        "span_hz" -> Abs[high-low]|>
    ],
    {j, {1,3,5}}
  ];
  <|"scientific_status" -> "POSTHOC_IDEAL_1D_CORROBORATION_ONLY",
    "independent_method" -> "right-to-left impedance recurrence",
    "baseline_f2_hz" -> f2[restAtEnd],
    "f2_search_step_hz" -> 5,
    "selected_sites" -> rows|>
]
