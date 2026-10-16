(* OG-5 Gate A independent 5-tube, two-3-port ideal lossless 1D acoustic oracle.
   Not a Core implementation or adoption. Peak exp(+i omega t). SI p/U,
   all unknowns scaled as P=p/(Zref Uref), Q=U/Uref. *)
ClearAll[og5Case,og5P,og5Q,og5Pair,og5FiniteQ,og5MatrixDiagnostic];
(* Amendment A1: do not discard zero singular values; never report a finite
   condition number for a rank-deficient matrix. This guard is design-only. *)
og5FiniteQ[v_]:=NumberQ[v] && FreeQ[v,Indeterminate|_DirectedInfinity];
og5MatrixDiagnostic[a_]:=Module[{n=Length[a],sv},
 If[Dimensions[a]=!={n,n} || !VectorQ[Flatten[a],og5FiniteQ],
  Return[<|"status"->"NUMERICALLY_UNRESOLVED","code"->"NUMERIC_NONFINITE"|>]];
 sv=SingularValueList[N[a],Tolerance->0];
 If[Length[sv]=!=n || !VectorQ[sv,og5FiniteQ],
  Return[<|"status"->"NUMERICALLY_UNRESOLVED","code"->"NUMERIC_NONFINITE"|>]];
 If[Min[sv]<=n*$MachineEpsilon*Max[sv],
  Return[<|"status"->"NUMERICALLY_UNRESOLVED","code"->"MATRIX_RANK_DEFICIENT",
    "singular_value_count"->Length[sv]|>]];
 If[Max[sv]/Min[sv]>1.*^4,
  Return[<|"status"->"NUMERICALLY_UNRESOLVED","code"->"MATRIX_ILL_CONDITIONED"|>]];
 <|"status"->"SUCCESS","singular_value_count"->Length[sv],
   "condition_number_2"->N[Max[sv]/Min[sv],15]|>
];
uRef=1.*^-6; zRef=1.2*343./.0003; pRef=zRef*uRef;
names={"A","B","C","D","E"};
lengths=<|"A"->.08,"B"->.09,"C"->.06,"D"->.07,"E"->.05|>;
og5P[s_,e_]:=Symbol["og5P"<>s<>e];
og5Q[s_,e_]:=Symbol["og5Q"<>s<>e];
og5Pair[z_]:=N[{Re[z],Im[z]},16];
og5Case[f_,cArea_,cLoad_,scale_]:=Module[
 {areas,z,m,vars,eqs,ca,mat,rhs,x,rules,zin,zd,ze,zc,zj2,zb,zj1,za,back,
  rec,j,ports,diff,power,pIn,pOut,sv,resid,c1,c2,p1,p2,source,guard},
 areas=<|"A"->.0003,"B"->.0003,"C"->cArea,"D"->.0003,"E"->.0006|>;
 z[s_]:=(1.2*343./areas[s])/zRef;
 m[s_]:=With[{theta=2 Pi f lengths[s]/343.,r=z[s]},
  {{Cos[theta],I*r*Sin[theta]},{I*Sin[theta]/r,Cos[theta]}}];
 vars=Flatten[Table[{og5P[s,"i"],og5Q[s,"i"],og5P[s,"o"],og5Q[s,"o"]},{s,names}]];
 source=scale*(1.+.4 I);
 eqs=Flatten[Table[
 {og5P[s,"i"]==m[s][[1,1]] og5P[s,"o"]+m[s][[1,2]] og5Q[s,"o"],
  og5Q[s,"i"]==m[s][[2,1]] og5P[s,"o"]+m[s][[2,2]] og5Q[s,"o"]},{s,names}]];
 eqs=Join[eqs,{
  og5P["A","o"]==og5P["B","i"],og5P["A","o"]==og5P["C","i"],
  og5Q["A","o"]==og5Q["B","i"]+og5Q["C","i"],
  og5P["B","o"]==og5P["D","i"],og5P["B","o"]==og5P["E","i"],
  og5Q["B","o"]==og5Q["D","i"]+og5Q["E","i"],
  og5Q["A","i"]==source,
  If[cLoad==="matched",og5P["C","o"]==z["C"] og5Q["C","o"],og5Q["C","o"]==0],
  og5P["D","o"]==z["D"] og5Q["D","o"],
  og5P["E","o"]==z["E"] og5Q["E","o"]}];
 ca=CoefficientArrays[Subtract@@@eqs,vars];
 mat=N[Normal[ca[[2]]]]; rhs=-N[Normal[ca[[1]]]];
 guard=og5MatrixDiagnostic[mat];
 If[guard["status"]=!="SUCCESS",Return[guard]];
 x=LinearSolve[mat,rhs]; rules=Thread[vars->x];
 (* Separate recursion; no global matrix, source numerical solution or shared solver *)
 zin[s_,load_]:=With[{t=m[s]},
  If[load==="closed",t[[1,1]]/t[[2,1]],
   (t[[1,1]] load+t[[1,2]])/(t[[2,1]] load+t[[2,2]])]];
 zd=zin["D",z["D"]]; ze=zin["E",z["E"]];
 zc=zin["C",If[cLoad==="matched",z["C"],"closed"]];
 zj2=1/(1/zd+1/ze); zb=zin["B",zj2];
 zj1=1/(1/zb+1/zc); za=zin["A",zj1];
 back[s_,v_]:=With[{t=m[s]},
  {t[[2,2]] v[[1]]-t[[1,2]] v[[2]],-t[[2,1]] v[[1]]+t[[1,1]] v[[2]]}];
 rec=<||>; rec["A.in"]={za source,source};
 rec["A.out"]=back["A",rec["A.in"]];j=rec["A.out"][[1]];
 rec["B.in"]={j,j/zb};rec["C.in"]={j,j/zc};
 rec["B.out"]=back["B",rec["B.in"]];rec["C.out"]=back["C",rec["C.in"]];
 j=rec["B.out"][[1]];
 rec["D.in"]={j,j/zd};rec["E.in"]={j,j/ze};
 rec["D.out"]=back["D",rec["D.in"]];rec["E.out"]=back["E",rec["E.in"]];
 ports=Association@Flatten[Table[With[{key=s<>"."<>If[e==="i","in","out"]},
    key-><|"p_pa"->og5Pair[pRef*(og5P[s,e]/.rules)],
           "u_m3_s"->og5Pair[uRef*(og5Q[s,e]/.rules)]|>],
   {s,names},{e,{"i","o"}}],1];
 diff=Max[Flatten[Table[With[{key=s<>"."<>If[e==="i","in","out"]},
  {Abs[(og5P[s,e]/.rules)-rec[key][[1]]],
   Abs[(og5Q[s,e]/.rules)-rec[key][[2]]]}],{s,names},{e,{"i","o"}}]]];
 power[s_,e_]:=.5 pRef uRef Re[(og5P[s,e] Conjugate[og5Q[s,e]])/.rules];
 pIn=power["A","i"];pOut=Total[power[#,"o"]&/@{"C","D","E"}];
 sv=SingularValueList[mat,Tolerance->0];
 resid=Max[Abs[mat.x-rhs]];
 c1=Abs[(og5Q["A","o"]-og5Q["B","i"]-og5Q["C","i"])/.rules];
 c2=Abs[(og5Q["B","o"]-og5Q["D","i"]-og5Q["E","i"])/.rules];
 p1=Max[Abs[(og5P["A","o"]-og5P["B","i"])/.rules],
        Abs[(og5P["A","o"]-og5P["C","i"])/.rules]];
 p2=Max[Abs[(og5P["B","o"]-og5P["D","i"])/.rules],
        Abs[(og5P["B","o"]-og5P["E","i"])/.rules]];
 <|"frequency_hz"->f,"c_area_m2"->cArea,"c_load"->cLoad,
   "source_scale"->scale,"port_states"->ports,
   "condition_number_2"->N[Max[sv]/Min[sv],15],
   "global_vs_recursive_max_scaled_complex_error"->N[diff,15],
   "global_scaled_linear_residual"->N[resid,15],
   "j1_scaled_flow_residual"->N[c1,15],"j2_scaled_flow_residual"->N[c2,15],
   "j1_scaled_pressure_residual"->N[p1,15],
   "j2_scaled_pressure_residual"->N[p2,15],
   "source_mean_power_w"->N[pIn,15],
   "terminal_mean_power_w"->N[pOut,15],
   "c_terminal_power_fraction"->N[power["C","o"]/pIn,15]|>
];
records=Flatten[Table[og5Case[f,a,load,1.],
  {f,{733,997}},{a,{.00015,.0006}},{load,{"matched","closed"}}],2];
summary=<|"status"->"EXPLORATORY_GATE_A_PROPOSAL_NOT_ADOPTED",
 "source_convention"->"peak exp(+i omega t)",
 "global_solver"->"20x20 nondimensional linear system",
 "independent_comparator"->"recursive complex impedances and state propagation",
 "source_u_m3_s"->{.000001,.0000004},
 "rho_kg_m3"->1.2,"sound_speed_m_s"->343.,"cases"->Length[records],
 "port_endpoint_count_per_case"->10,
 "max_scaled_comparator_error"->Max[Lookup[records,"global_vs_recursive_max_scaled_complex_error"]],
 "max_scaled_linear_residual"->Max[Lookup[records,"global_scaled_linear_residual"]],
 "max_scaled_junction_flow_residual"->Max[Join[Lookup[records,"j1_scaled_flow_residual"],Lookup[records,"j2_scaled_flow_residual"]]],
 "max_scaled_junction_pressure_residual"->Max[Join[Lookup[records,"j1_scaled_pressure_residual"],Lookup[records,"j2_scaled_pressure_residual"]]],
 "max_relative_power_defect"->Max[Abs[(#["source_mean_power_w"]-#["terminal_mean_power_w"])/#["source_mean_power_w"]]&/@records],
 "max_matrix_condition_2"->Max[Lookup[records,"condition_number_2"]]|>;
Print["OG5JSONSTART"];
Print[ExportString[<|"summary"->summary,"records"->records|>,"RawJSON","Compact"->True]];
Print["OG5JSONEND"];
summary

