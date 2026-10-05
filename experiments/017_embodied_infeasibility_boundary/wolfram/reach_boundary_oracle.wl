(* Experiment 017 independent reach-boundary oracle *)

ClearAll[tractLength, gestureLocation, reachableEnds, conditions, result];

tractLength = 17/100;
gestureLocation = 13/20;
reachableEnds = {7/10, 13/20, 3/5};

conditions = Table[
  Module[{margin = reachableEnd - gestureLocation},
    <|
      "reachable_end" -> N[reachableEnd, 17],
      "gesture_location" -> N[gestureLocation, 17],
      "normalized_reach_margin" -> N[margin, 17],
      "gesture_position_m" -> N[tractLength gestureLocation, 17],
      "reach_end_position_m" -> N[tractLength reachableEnd, 17],
      "physical_reach_margin_m" -> N[tractLength margin, 17],
      "expected_status" -> If[margin >= 0, "FEASIBLE", "INFEASIBLE"]
    |>
  ],
  {reachableEnd, reachableEnds}
];

result = <|
  "tract_length_m" -> N[tractLength, 17],
  "gesture_location" -> N[gestureLocation, 17],
  "boundary_rule" -> "reachable_start <= location <= reachable_end",
  "conditions" -> conditions,
  "positive_and_negative_physical_margin_symmetry_m" ->
    N[
      {
        tractLength (7/10 - gestureLocation),
        tractLength (3/5 - gestureLocation)
      },
      17
    ]
|>;

Export[
  FileNameJoin[{DirectoryName[$InputFileName], "reach_boundary_oracle.json"}],
  result,
  "RawJSON"
];
result
