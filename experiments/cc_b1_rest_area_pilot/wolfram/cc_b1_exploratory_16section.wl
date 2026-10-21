(* CC-B1 exploratory, independent lossless 16-section input-impedance oracle.
   Run in a Wolfram Language kernel. NOT a preregistered confirmatory Gate B.
   Extracting reference /a/ glottis->lips diameters from Experiment023
   and task-field parameters from the frozen Experiment027.
   Matrix: [p_in,U_in] = TransferMatrix . [p_out,U_out];
   pressure-release p_out=0 => Z_in=M12/M22. No radiation losses.
*)
ClearAll["Global`*"];
diamMm = {12,12,26,16,12,14,20,26,30,34,38,34,34,30,28,32};
baseArea = Pi (N[diamMm]/2000.)^2;
x = N[Range[0,15]/15];
kappa = 1.5;
deltaLogArea = 2 kappa (
  .5921764128805103 Exp[-(x - .3424849103873983)^2/(2 .16^2)] -
  .9235962908995712 Exp[-(x - .7167402543883221)^2/(2 .16^2)] -
  .04495226070116771 Exp[-(x - 1)^2/(2 .10^2)]);
freqHz = N[Range[100,3500,5]];
transfer[f_, areas_] := Fold[Dot, IdentityMatrix[2],
  Table[With[{phase = 2 Pi f .01/343., z = 1.2 343./areas[[j]]},
    {{Cos[phase], I z Sin[phase]}, {I Sin[phase]/z, Cos[phase]}}], {j,16}]];
inputZ[f_, areas_] := With[{m = transfer[f, areas]}, Abs[m[[1,2]]/m[[2,2]]]];
localPeaks[areas_] := Module[{z, idx},
  z = inputZ[#, areas] & /@ freqHz;
  idx = Select[Range[2, Length[z]-1],
    z[[#]] > z[[#-1]] && z[[#]] > z[[#+1]] &];
  Take[Sort[freqHz[[idx]]], UpTo[3]]];
conditions = Association@Table[
  With[{modified = ReplacePart[baseArea, 1 -> baseArea[[1]] ratio]},
    ToString@NumberForm[ratio, {3,2}, NumberPadding -> {"","0"}] ->
      <|"rest_peak_hz" -> localPeaks[modified],
        "final_peak_hz" -> localPeaks[modified Exp[deltaLogArea]]|>
  ], {ratio, {.90,1.00,1.10}}];
<|"model" -> "exploratory-16x10mm-input-impedance-p-release-v0",
  "area_edit_section_zero_based" -> 0,
  "grid_start_hz" -> 100, "grid_end_hz" -> 3500, "grid_step_hz" -> 5,
  "conditions" -> conditions,
  "scientific_status" -> "EXPLORATORY_NOT_PREREGISTERED"|>
