(* Deterministic independent WL-source vs checked-in frozen JSON verification.
   Requires wolframscript and does not modify or overwrite the oracle.
   Run: wolframscript -file experiments/039_og2_prepared_graph/wolfram/verify_og2_oracle.wl
   This is a post-review reproducibility check, NOT a newly preregistered gate. *)
Module[{dir, generated, frozen, computed, reference, flatDiff,
        frac, checks, tol=10^-13, grid, error},
  dir=DirectoryName[$InputFileName];
  generated=ImportString[Get[FileNameJoin[{dir,"og2_oracle.wl"}]],"RawJSON"];
  frozen=Import[FileNameJoin[{dir,"og2_oracle.json"}],"RawJSON"];
  grid=generated["frequencies_hz"];
  If[grid=!=frozen["frequencies_hz"] || Length[grid]=!=7,
    Print["FAIL: frozen frequency grid differs from independent source"];Exit[1]];
  computed=Map[ToExpression, generated[
    "normalized_ab_mismatch_pU_matrix_rowmajor_re_im_strings"],{3}];
  reference=frozen["normalized_matrix_rowmajor_re_im"];
  If[Dimensions[computed]=!={7,4,2} || Dimensions[reference]=!={7,4,2},
    Print["FAIL: matrix dimensions"];Exit[1]];
  error=Max[Abs[Flatten[N[computed,16]-N[reference,16]]]];
  frac={generated["reflected_pressure"], generated["transmitted_pressure"],
        generated["reflected_power"], generated["transmitted_power"]};
  checks=And@@MapThread[(Abs[N[ToExpression[#1],16]-N[#2,16]]<=tol)&,
    {frac,Lookup[frozen["isolated_interface"],
      {"pressure_reflection","pressure_transmission","power_reflection","power_transmission"}]}];
  If[!TrueQ[error<=tol] || !TrueQ[checks],
    Print["FAIL: Wolfram source disagrees with frozen JSON; max error=",error];
    Exit[1]];
  Print[ExportString[<|"status"->"PASS","grid_size"->Length[grid],
    "matrix_components"->56,"max_absolute_decimal_error"->N[error,8],
    "exact_interface_fractions_verified"->True|>,"RawJSON"]];
]
