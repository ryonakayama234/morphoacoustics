(* OG-3 Gate A: independently reevaluable planning sanity only.
   NOT a newly frozen replacement oracle or evidence for implemented public API.
   e^(+I omega t), [p_in,U_in] = T [p_out,U_out], U is volume velocity.
   Exact rational physical inputs; shared reference Z_A.
   Run in Wolfram Language: wolframscript -file docs/research/og3-wolfram-gate-a.wl
*)
Module[
 {rho=121/100,c=343,aa=3/10000,ab=6/10000,
  la=8/100,lb=9/100,grid={80,200,400,733,1200,2200,4000},
  za,zb,s,si,t,scaled,wrong,swapped,reflected,transmitted,rows},
 za=rho*c/aa; zb=rho*c/ab;
 s=DiagonalMatrix[{1,za}];
 si=DiagonalMatrix[{1,1/za}];
 t[l_,a_,f_]:=With[{theta=2*Pi*f*l/c,z=rho*c/a},
    {{Cos[theta],I*z*Sin[theta]},{I*Sin[theta]/z,Cos[theta]}}];
 scaled[f_,a_]:=s.t[la,aa,f].t[lb,a,f].si;
 wrong[f_]:=s.t[la,aa,f].DiagonalMatrix[{1,aa/ab}].t[lb,ab,f].si;
 swapped[f_]:=s.t[lb,ab,f].t[la,aa,f].si;
 reflected=(zb-za)/(za+zb); transmitted=1+reflected;
 rows=Table[
  Module[{m=N[scaled[f,ab],30],equal=N[scaled[f,aa],30],
     reference=N[s.t[la+lb,aa,f].si,30],
     falseFlow=N[wrong[f],30],falseOrder=N[swapped[f],30]},
   <|"frequency_hz"->f,
     "equal_area_max_error"->N[Max[Abs[Flatten[equal-reference]]],12],
     "b_area_intervention_max_difference"->N[Max[Abs[Flatten[m-equal]]],12],
     "wrong_particle_velocity_max_difference"->N[Max[Abs[Flatten[m-falseFlow]]],12],
     "swapped_order_max_difference"->N[Max[Abs[Flatten[m-falseOrder]]],12],
     "unequal_area_matrix_rowmajor_re_im"->Map[
       {N[Re[#],15],N[Im[#],15]}&,Flatten[m]]
   |>],
  {f,grid}];
 Print[ExportString[
   <|"scope"->"Gate A independent analytic planning, not public API acceptance",
     "base_sha"->"1fb6c9f691f94558c6d5ccaf4b018eb05389cafe",
     "pressure_reflection"->ToString[InputForm[reflected]],
     "pressure_transmission"->ToString[InputForm[transmitted]],
     "power_reflection"->ToString[InputForm[reflected^2]],
     "power_transmission"->ToString[InputForm[(za/zb)*transmitted^2]],
     "power_sum"->ToString[InputForm[reflected^2+(za/zb)*transmitted^2]],
     "rows"->rows|>,
   "RawJSON"]]
]
