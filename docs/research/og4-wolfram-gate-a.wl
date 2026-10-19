(* OG-4 Gate A symbolic three-port check. NOT a general solver or Core adoption.
   p_i=a_i+b_i and outward U_i=Y_i (b_i-a_i).
   Continuity of pressure and sum of signed outward volume flows zero
   imply S_ij=2 Y_j/Sum(Y)-KroneckerDelta[i,j].
   OG-1 rigid passive 1D acoustic assumptions; no anatomical voice claim. *)
Module[
 {y={yA,yB,yC},sy,symEnergy,symReciprocity,symPower,ss,
  ratios={1/2,1,2},wrong,rows},
 ss[ys_]:=Table[2 ys[[j]]/Total[ys]-KroneckerDelta[i,j],
             {i,3},{j,3}];
 sy=ss[y];
 symEnergy=FullSimplify[
   Transpose[sy].DiagonalMatrix[y].sy-DiagonalMatrix[y],
   Assumptions->yA>0&&yB>0&&yC>0];
 symReciprocity=FullSimplify[
   DiagonalMatrix[y].sy-Transpose[DiagonalMatrix[y].sy],
   Assumptions->yA>0&&yB>0&&yC>0];
 symPower=FullSimplify[
   Transpose[DiagonalMatrix[Sqrt[y]].sy.DiagonalMatrix[1/Sqrt[y]]].
   DiagonalMatrix[Sqrt[y]].sy.DiagonalMatrix[1/Sqrt[y]]-
   IdentityMatrix[3],Assumptions->yA>0&&yB>0&&yC>0];
 wrong=Table[2/3-KroneckerDelta[i,j],{i,3},{j,3}];
 rows=Table[
   Module[{ys={1,1,r},m,pow,defect},
     m=ss[ys]; pow=FullSimplify[{m[[1,1]]^2,
       ys[[2]]/ys[[1]] m[[2,1]]^2,
       ys[[3]]/ys[[1]] m[[3,1]]^2}];
     defect=Transpose[wrong].DiagonalMatrix[ys].wrong-DiagonalMatrix[ys];
     <|"C_to_A_area_ratio"->ToString[InputForm[r]],
       "S_rowmajor_rationals"->Map[ToString[InputForm[#]]&,Flatten[m]],
       "power_fractions_reflected_B_C_rationals"->
          (ToString[InputForm[#]]&/@pow),
       "power_sum"->ToString[InputForm[Total[pow]]],
       "wrong_particle_velocity_max_weighted_power_defect"->
          ToString[InputForm[Max[Abs[Flatten[defect]]]]]|>
   ],{r,ratios}];
 ExportString[
  <|"status"->"GATE_A_SYMBOLIC_PLANNING_ONLY_NOT_ADOPTED",
    "source"->"Independent three-port weighted scattering symbolic check",
    "port_types"->{"acoustic.p_u","acoustic.p_u","acoustic.p_u"},
    "orientation"->"outward-from-junction (-U_A.out,+U_B.in,+U_C.in)",
    "scattering_law"->"S_ij=2*Y_j/Sum(Y)-delta_ij",
    "symbolic_weighted_power_residual"->symEnergy,
    "symbolic_reciprocity_residual"->symReciprocity,
    "symbolic_power_normalized_orthogonality_residual"->symPower,
    "area_ratio_rows"->rows|>,"RawJSON"]
]
