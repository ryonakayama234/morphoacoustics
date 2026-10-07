(* Experiment 029 independent V3c reachability oracle.
   Evaluated before Python Experiment-029 execution.
   The source emits the complete JSON schema consumed by Python. *)

ClearAll["Global`*"];

taskPlan = {
  <|"task" -> "OPEN", "location" -> 0.3424849103873983,
    "degree" -> 0.5921764128805103, "onset_s" -> 0.15,
    "offset_s" -> 0.35|>,
  <|"task" -> "CONSTRICT", "location" -> 0.7167402543883221,
    "degree" -> 0.9235962908995712, "onset_s" -> 0.15,
    "offset_s" -> 0.35|>,
  <|"task" -> "CONSTRICT", "location" -> 1.0,
    "degree" -> 0.04495226070116771, "onset_s" -> 0.15,
    "offset_s" -> 0.35|>
};

totalLength = 0.160;
targetTaskIndex = 1;
targetLocation = taskPlan[[targetTaskIndex + 1, "location"]];

conditionSpec = {
  {"M_plus", 0.75},
  {"M_boundary", targetLocation},
  {"M_minus", 0.70}
};

conditions = Map[
  Function[row,
    With[
      {
        name = row[[1]],
        reachEnd = row[[2]],
        margin = row[[2]] - targetLocation
      },
      <|
        "condition" -> name,
        "oral_shaper_reachable_end" -> reachEnd,
        "target_task_index" -> targetTaskIndex,
        "target_location" -> targetLocation,
        "normalized_margin" -> N[margin, 17],
        "metric_margin_m" -> N[margin totalLength, 17],
        "expected_status" -> If[margin >= 0, "FEASIBLE", "INFEASIBLE"]
      |>
    ]
  ],
  conditionSpec
];

oracle = <|
  "provenance" -> <|
    "tool" -> "Wolfram Language evaluator",
    "evaluated_before_python_experiment" -> True,
    "date" -> "2026-10-08",
    "purpose" -> "independent V3c reachability-boundary oracle for the frozen Experiment-027/028 three-task plan"
  |>,
  "task_plan" -> taskPlan,
  "fixture" -> <|
    "total_length_m" -> totalLength,
    "section_count" -> 16,
    "section_length_m" -> 0.010,
    "oral_shaper_reachable_start" -> 0.0,
    "lip_reachable_start" -> 0.95,
    "lip_reachable_end" -> 1.0
  |>,
  "capability_policy" -> <|
    "outlet_location" -> 1.0,
    "outlet_articulator_kind" -> "lip",
    "interior_articulator_kind" -> "oral-shaper",
    "supported_task_kinds" -> {"OPEN", "CONSTRICT"},
    "reach_interval_semantics" -> "inclusive"
  |>,
  "conditions" -> conditions,
  "frozen_gate" -> <|
    "margin_abs_tolerance" -> 1.*^-15,
    "expected_unreachable_issue_code" -> "LOCATION_UNREACHABLE",
    "expected_unreachable_task_index" -> 1,
    "infeasible_acoustic_call_count" -> 0,
    "require_feasible_endpoint_exact_equality" -> True,
    "require_feasible_waveform_exact_equality" -> True
  |>
|>;

Export["v3c_oracle.generated.json", oracle, "RawJSON"];
ExportString[oracle, "RawJSON", "Compact" -> False]
