(* A1 supplementary design exploration; no Core implementation. The original
   eight-result JSON is immutable. Run with the original sibling source. *)
Get[FileNameJoin[{DirectoryName[$InputFileName],"og5-wolfram-gate-a.wl"}]];
allA1=Flatten[Table[og5Case[f,a,l,s],
 {f,{80,250,400,733,997,1200,2000,4000}},
 {a,{.00015,.0003,.0006}},{l,{"matched","closed"}},{s,{1.,.5,-1.}}],3];

(* Independently rebuild the supported 733-Hz matrix for explicit mutations.
   Production never imports this source or any stored oracle. *)
ClearAll[a1P,a1Q,a1Rows,a1Solve];
a1P[s_,e_]:=Symbol["a1P"<>s<>e];
a1Q[s_,e_]:=Symbol["a1Q"<>s<>e];
a1Names={"A","B","C","D","E"};
a1Area=<|"A"->.0003,"B"->.0003,"C"->.00015,"D"->.0003,"E"->.0006|>;
a1Vars=Flatten[Table[{a1P[s,"i"],a1Q[s,"i"],a1P[s,"o"],a1Q[s,"o"]},{s,a1Names}]];
a1Z[s_]:=(1.2*343./a1Area[s])/zRef;
a1T[s_]:=With[{t=2 Pi 733 lengths[s]/343.,z=a1Z[s]},
 {{Cos[t],I z Sin[t]},{I Sin[t]/z,Cos[t]}}];
a1Rows=Join[Flatten[Table[{
 a1P[s,"i"]-a1T[s][[1,1]]a1P[s,"o"]-a1T[s][[1,2]]a1Q[s,"o"],
 a1Q[s,"i"]-a1T[s][[2,1]]a1P[s,"o"]-a1T[s][[2,2]]a1Q[s,"o"]},{s,a1Names}]],{
 a1P["A","o"]-a1P["B","i"],a1P["A","o"]-a1P["C","i"],
 a1Q["A","o"]-a1Q["B","i"]-a1Q["C","i"],
 a1P["B","o"]-a1P["D","i"],a1P["B","o"]-a1P["E","i"],
 a1Q["B","o"]-a1Q["D","i"]-a1Q["E","i"],
 a1Q["A","i"]-(1.+.4 I),
 a1P["C","o"]-a1Z["C"]a1Q["C","o"],
 a1P["D","o"]-a1Z["D"]a1Q["D","o"],
 a1P["E","o"]-a1Z["E"]a1Q["E","o"]}];
a1Solve[rows_]:=Module[{ca=CoefficientArrays[rows,a1Vars]},
 LinearSolve[N[Normal[ca[[2]]]],-N[Normal[ca[[1]]]]]];
a1Baseline=a1Solve[a1Rows];
a1MutationRows=<|
 "wrong_j1_sign"->ReplacePart[a1Rows,13->a1Q["A","o"]-a1Q["B","i"]+a1Q["C","i"]],
 "wrong_j2_sign"->ReplacePart[a1Rows,16->a1Q["B","o"]-a1Q["D","i"]+a1Q["E","i"]],
 "particle_velocity_j1"->ReplacePart[a1Rows,13->a1Q["A","o"]-a1Q["B","i"]-2 a1Q["C","i"]],
 "particle_velocity_j2"->ReplacePart[a1Rows,16->a1Q["B","o"]-a1Q["D","i"]-.5 a1Q["E","i"]],
 "pressure_sign"->ReplacePart[a1Rows,11->a1P["A","o"]+a1P["B","i"]],
 "endpoint_reversal"->Join[(Take[a1Rows,2]/.{a1P["A","i"]->a1P["A","o"],a1P["A","o"]->a1P["A","i"],a1Q["A","i"]->a1Q["A","o"],a1Q["A","o"]->a1Q["A","i"]}),Drop[a1Rows,2]],
 "wrong_c_load"->ReplacePart[a1Rows,18->a1P["C","o"]-.5 a1Z["C"]a1Q["C","o"]]|>;
a1MutationErrors=Map[Max[Abs[a1Solve[#]-a1Baseline]]&,a1MutationRows];
a1Swapped=a1Baseline;a1Swapped[[{15,16,19,20}]]=a1Baseline[[{19,20,15,16}]];
a1MutationErrors["output_identity_swap"]=Max[Abs[a1Swapped-a1Baseline]];
a1Ca=CoefficientArrays[a1Rows,a1Vars];a1M=N[Normal[a1Ca[[2]]]];
a1Bad=ReplacePart[a1M,20->a1M[[19]]];
a1Diag=DiagonalMatrix[Join[ConstantArray[1.,19],{1.*^-5}]];
a1Nan=ReplacePart[a1M,{1,1}->Indeterminate];
a1Negative=<|"duplicate_row"->og5MatrixDiagnostic[a1Bad],
 "ill_conditioned_full_rank"->og5MatrixDiagnostic[a1Diag],
 "nonfinite_matrix"->og5MatrixDiagnostic[a1Nan],
 "legacy_svd_drops_zero"->SingularValueList[DiagonalMatrix[{1.,0.}]],
 "full_svd_retains_zero"->SingularValueList[DiagonalMatrix[{1.,0.}],Tolerance->0]|>;
a1Summary=<|"status"->"SUPPLEMENTARY_DESIGN_EXPLORATION_NOT_CORE_OR_ADOPTION",
 "kernel_version"->$Version,"positive_cases"->Length[allA1],
 "successful_positive_cases"->Count[allA1,_Association?(KeyExistsQ[#,"port_states"]&)],
 "max_condition_number_2"->Max[Lookup[allA1,"condition_number_2"]],
 "max_scaled_comparator_error"->Max[Lookup[allA1,"global_vs_recursive_max_scaled_complex_error"]],
 "max_scaled_linear_residual"->Max[Lookup[allA1,"global_scaled_linear_residual"]],
 "max_relative_power_defect_with_floor"->Max[(Abs[#["source_mean_power_w"]-#["terminal_mean_power_w"]]/Max[Abs[#["source_mean_power_w"]],.5 pRef uRef Abs[#["source_scale"]]^2])&/@allA1],
 "mutation_max_scaled_state_errors"->a1MutationErrors,
 "all_eight_mutants_exceed_1e_minus6"->And@@Map[#>1.*^-6&,Values[a1MutationErrors]],
 "child_permutation_law_invariant"->(Sort[{pa-pb,pa-pc,ua-ub-uc}]===Sort[{pa-pc,pa-pb,ua-uc-ub}]),
 "numerical_negative_controls"->a1Negative,
 "tube_determinant"->FullSimplify[Det[{{Cos[t],I zz Sin[t]},{I Sin[t]/zz,Cos[t]}}]],
 "tube_power_identity"->(FullSimplify[ConjugateTranspose[{{Cos[t],I zz Sin[t]},{I Sin[t]/zz,Cos[t]}}].{{0,1},{1,0}}.{{Cos[t],I zz Sin[t]},{I Sin[t]/zz,Cos[t]}}-{{0,1},{1,0}},Assumptions->Element[{t,zz},Reals]&&zz>0]===ConstantArray[0,{2,2}])|>;
Print[ExportString[a1Summary,"RawJSON"]];
a1Summary
