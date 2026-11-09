(* SMC-3 Gate C independent symbolic oracle; research-only. *)
(* Preregistered 2026-10-23: docs/GATE_C_PROTOCOL.md.                   *)
(* Do NOT use candidate Python output as oracle input.                 *)
ClearAll[a, b, c, d, s1, e1, s2, e2, s3, e3];
consistent = {
  a == 0, b - a == 1/10, c - b == 3/20,
  d - a == 1/4, d - c == 0
};
contradictory = Append[consistent, d - a == 13/50];
underdetermined = {a == 0, b - a == 1/10, c - b == 3/20};

knownWindows = {
  {2/25, 13/50},
  {1/5, 33/100},
  {29/100, 27/50}
};
knownOverlaps = {
  knownWindows[[1, 2]] - knownWindows[[2, 1]],
  knownWindows[[2, 2]] - knownWindows[[3, 1]]
};

(* Consistency uses exact rational equations; no floating-point tolerance.
   FreeQ[Reduce[...], d] is false when d stays unconstrained; to explicitly
   demonstrate freedom, two distinct d values must each have a solution. *)
result = <|
  "consistentSolutions" -> Solve[consistent, {a, b, c, d}, Reals],
  "contradictionIsUnsat" ->
    (Length[Solve[contradictory, {a, b, c, d}, Reals]] == 0),
  "partialTwoDifferentDValuesAreAllowed" ->
    And[
      Length[Solve[Append[underdetermined, d == 0], {a, b, c, d},
                   Reals]] > 0,
      Length[Solve[Append[underdetermined, d == 1], {a, b, c, d},
                   Reals]] > 0
    ],
  "knownOverlapsSeconds" -> knownOverlaps,
  "knownOverlapsExpected" -> (knownOverlaps == {3/50, 1/25})
|>;
result

(* Each new synthetic case in the Python suite is constructed from
   rational event stamps, then encoded into redundant pairwise equalities.
   For external review, pass the preregistered fixtures to an independent
   Wolfram notebook / linear-equation solve, record version/output/SHA.
   Presence of this file is NOT evidence Wolfram executed in CI. *)
