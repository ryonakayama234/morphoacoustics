(* OG-3 Gate A: independently reevaluable planning sanity only.
   NOT a newly frozen replacement oracle or evidence for implemented public API.
   e^(+I omega t), [p_in,U_in] = T [p_out,U_out], U is volume velocity.
   Exact rational physical inputs; shared reference Z_A.
   Run in Wolfram Language: wolframscript -file docs/research/og3-wolfram-gate-a.wl
*)
Module[
 {rho=121/100,c=343,aa=3/10000,ab=6/10000,
  la=8/100,lb=9/100,grid={80,200,400,733,1200,2200,4000},
  za,zb,s,si,t,scaled,wrong,swapped,reflected,transmitted,rows,
  jFlux,fluxDefect,fluxTolerance=10^-12,mutationMinimum=10^-3,
  theta,z,q,template,exactFluxIdentities,correctMax,wrongMax,controlsPass},
 za=rho*c/aa; zb=rho*c/ab;
 s=DiagonalMatrix[{1,za}];
 si=DiagonalMatrix[{1,1/za}];
 t[l_,a_,f_]:=With[{theta=2*Pi*f*l/c,z=rho*c/a},
    {{Cos[theta],I*z*Sin[theta]},{I*Sin[theta]/z,Cos[theta]}}];
 scaled[f_,a_]:=s.t[la,aa,f].t[lb,a,f].si;
 wrong[f_]:=s.t[la,aa,f].DiagonalMatrix[{1,aa/ab}].t[lb,ab,f].si;
 swapped[f_]:=s.t[lb,ab,f].t[la,aa,f].si;
 (* For dimensionless state [p,Z_A U], mean power is
    state^dagger.JFlux.state/(4 Z_A). This is NOT the junction matrix.
    No determinant-only proxy; compare all entries of M^dagger.JFlux.M-JFlux. *)
 jFlux={{0,1},{1,0}};
 fluxDefect[m_]:=Max[Abs[Flatten[ConjugateTranspose[m].jFlux.m-jFlux]]];
 template={{Cos[theta],I*z*Sin[theta]},
           {I*Sin[theta]/z,Cos[theta]}};
 exactFluxIdentities=FullSimplify[
   {ConjugateTranspose[template].jFlux.template==jFlux,
    ConjugateTranspose[DiagonalMatrix[{1,q}]].jFlux.
      DiagonalMatrix[{1,q}]==q*jFlux},
   Assumptions->Element[{theta,z,q},Reals] && z>0];
 reflected=(zb-za)/(za+zb); transmitted=1+reflected;
 rows=Table[
  Module[{m=N[scaled[f,ab],50],equal=N[scaled[f,aa],50],
     reference=N[s.t[la+lb,aa,f].si,50],
     falseFlow=N[wrong[f],50],falseOrder=N[swapped[f],50]},
   <|"frequency_hz"->f,
     "equal_area_max_error"->N[Max[Abs[Flatten[equal-reference]]],MachinePrecision],
     "b_area_intervention_max_difference"->N[Max[Abs[Flatten[m-equal]]],MachinePrecision],
     "wrong_particle_velocity_max_difference"->N[Max[Abs[Flatten[m-falseFlow]]],MachinePrecision],
     "swapped_order_max_difference"->N[Max[Abs[Flatten[m-falseOrder]]],MachinePrecision],
     "correct_flux_defect"->N[fluxDefect[m],MachinePrecision],
     "wrong_particle_velocity_flux_defect"->N[fluxDefect[falseFlow],MachinePrecision],
     "unequal_area_matrix_rowmajor_re_im"->Map[
       {N[Re[#],MachinePrecision],N[Im[#],MachinePrecision]}&,Flatten[m]]
   |>],
  {f,grid}];
 correctMax=Max[Lookup[rows,"correct_flux_defect"]];
 wrongMax=Max[Lookup[rows,"wrong_particle_velocity_flux_defect"]];
 controlsPass=TrueQ[And@@exactFluxIdentities] &&
   TrueQ[correctMax<=fluxTolerance] &&
   TrueQ[Min[Lookup[rows,"wrong_particle_velocity_flux_defect"]]>mutationMinimum] &&
   TrueQ[Max[Abs[Lookup[rows,"wrong_particle_velocity_flux_defect"]-1/2]]<=fluxTolerance];
 Print[ExportString[
   <|"scope"->"Gate A independent analytic planning, not public API acceptance",
     "wolfram_version"->$Version,
     "base_sha"->"1fb6c9f691f94558c6d5ccaf4b018eb05389cafe",
     "pressure_reflection"->ToString[InputForm[reflected]],
     "pressure_transmission"->ToString[InputForm[transmitted]],
     "power_reflection"->ToString[InputForm[reflected^2]],
     "power_transmission"->ToString[InputForm[(za/zb)*transmitted^2]],
     "power_sum"->ToString[InputForm[reflected^2+(za/zb)*transmitted^2]],
     "flux_control"-><|
       "normalization"->"M=S T S^-1; S=diag(1,Z_A); J_flux={{0,1},{1,0}}",
       "defect"->"max_abs_entry(ConjugateTranspose[M].J_flux.M-J_flux)",
       "exact_tube_and_wrong_junction_identities"->exactFluxIdentities,
       "absolute_tolerance"->N[fluxTolerance],
       "mutation_minimum_exclusive"->N[mutationMinimum],
       "correct_max_defect"->N[correctMax,MachinePrecision],
       "wrong_particle_velocity_max_defect"->N[wrongMax,MachinePrecision],
       "expected_wrong_defect"->N[1/2],
       "all_controls_pass"->controlsPass|>,
     "rows"->rows|>,
   "RawJSON"]];
 If[!controlsPass,Exit[1]]
]
