(* NR-1a exploratory independent Wolfram probe, 2026-10-17.
   NOT a frozen oracle, NOT Core-vs-Wolfram test, and NOT biological nasal phonation.
   All physical quantities SI. Numerics scale volume-flow unknowns by 1e6,
   so w=1 corresponds to 1e-6 m^3/s. Peak phasors use exp(+i omega t). *)
Module[
 {rho=SetPrecision[6/5,40], c=343, fr=733,
  ln={2/25,9/100,3/50}, ar={3/10000,3/10000,3/20000},
  src=1+2 I/5, prs, flows, vars, run},
 prs=Array[p,{3,2}]; flows=Array[w,{3,2}];
 vars=Join[Flatten[prs],Flatten[flows]];
 run[b_,d_]:=Module[
  {cs=N[Cos[2 Pi fr ln/c],35],
   ss=N[Sin[2 Pi fr ln/c],35],
   z=N[(rho c/ar)/10^6,35], eqs, sol, pp, uu,
   powB,powC,powIn},
  eqs=Flatten[
   Table[{
    prs[[j,1]]==cs[[j]] prs[[j,2]]+I z[[j]] ss[[j]] flows[[j,2]],
    flows[[j,1]]==I ss[[j]]/z[[j]] prs[[j,2]]+
       cs[[j]] flows[[j,2]]
   },{j,3}]
  ];
  eqs=Join[eqs,{
   prs[[1,2]]==prs[[2,1]],
   prs[[1,2]]==prs[[3,1]],
   flows[[1,2]]==flows[[2,1]]+flows[[3,1]],
   flows[[1,1]]==src,
   If[b=="matched",prs[[2,2]]==z[[2]]flows[[2,2]],flows[[2,2]]==0],
   If[d=="matched",prs[[3,2]]==z[[3]]flows[[3,2]],flows[[3,2]]==0]
  }];
  sol=First[Solve[eqs,vars]];
  pp=prs/.sol; uu=flows/.sol;
  powB=N[Re[pp[[2,2]] Conjugate[uu[[2,2]]]]/(2 10^6),16];
  powC=N[Re[pp[[3,2]] Conjugate[uu[[3,2]]]]/(2 10^6),16];
  powIn=N[Re[pp[[1,1]] Conjugate[src]]/(2 10^6),16];
  <|"B_load"->b,"C_load"->d,
    "source_pressure_Pa"->N[pp[[1,1]],10],
    "input_power_W"->powIn,
    "mouth_terminal_power_W"->powB,
    "nose_terminal_power_W"->powC,
    "relative_power_defect"->
      N[Abs[powIn-powB-powC]/Max[Abs[powIn],10^-30],7]|>
 ];
 Print[InputForm[{
   run["matched","rigid_closed"],
   run["matched","matched"],
   run["rigid_closed","matched"]
 }]];
]
