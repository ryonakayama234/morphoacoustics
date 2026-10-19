(* NR-1a independent global 12-complex-state acoustic oracle.
   Wolfram Language, exact geometry and 35-digit evaluation.
   NO Python/Core import; NOT the experiment-only impedance solver.
   Writes machine-readable JSON between markers for harvesting by tools.
   STATUS: Candidate pre-Gate-A; freeze and review required before a Gate B claim. *)
ClearAll[nr1Oracle];
nr1Oracle[] := Module[
  {rho=6/5, c=343, lengths={2/25,9/100,3/50},
   areas={3/10000,3/10000,3/20000},
   freq={80,250,400,733,997,1200,2000,4000},
   src=1+2 I/5, p, u, unknowns, solve, row, pair, watts, records},
  p=Array[nr1p,{3,2}];
  u=Array[nr1u,{3,2}];
  unknowns=Join[Flatten[p],Flatten[u]];
  pair[z_]:={N[Re[z],MachinePrecision],N[Im[z],MachinePrecision]};
  watts[a_,b_]:=N[Re[a Conjugate[b]]/(2*10^6),MachinePrecision];
  solve[case_,f_] := Module[
    {theta=N[2 Pi f lengths/c,35],z=N[(rho c/areas)/10^6,35],
     cs,ss,eqs,sol,pp,uu,portP,portU,b,c},
    cs=Cos[theta]; ss=Sin[theta];
    {b,c}=Switch[case,"N",{"matched","rigid_closed"},
                          "O",{"matched","matched"},
                          "M",{"rigid_closed","matched"}];
    eqs=Flatten[Table[{
       p[[i,1]]==cs[[i]] p[[i,2]]+I z[[i]] ss[[i]] u[[i,2]],
       u[[i,1]]==I ss[[i]]/z[[i]] p[[i,2]]+cs[[i]] u[[i,2]]
       },{i,3}]];
    eqs=Join[eqs,{
      p[[1,2]]==p[[2,1]],p[[1,2]]==p[[3,1]],
      u[[1,2]]==u[[2,1]]+u[[3,1]],u[[1,1]]==src,
      If[b=="matched",p[[2,2]]==z[[2]]u[[2,2]],u[[2,2]]==0],
      If[c=="matched",p[[3,2]]==z[[3]]u[[3,2]],u[[3,2]]==0]
    }];
    sol=First[Solve[eqs,unknowns]];
    pp=p/.sol; uu=u/.sol;
    portP=Flatten[pp]; portU=Flatten[uu]/10^6;
    <|
      "case"->case,"frequency_hz"->f,
      "pressure_pa"->(pair /@ portP),
      "volume_flow_m3_s"->(pair /@ portU),
      "mean_power_w"->MapThread[watts,{Flatten[pp],Flatten[uu]}],
      "input_impedance_pa_s_m3"->pair[pp[[1,1]]/(src/10^6)]
    |>
  ];
  records=Flatten[Table[solve[case,f],{case,{"N","O","M"}},{f,freq}],1];
  <|
    "schema"->"nr1a.wolfram.global12.oracle.v0",
    "status"->"CANDIDATE_NOT_FROZEN",
    "phasor"->"exp(+i*omega*t) peak",
    "u_unknown_scale_m3_s"->10^-6,
    "port_ids"->{"A.in","A.out","B.in","B.out","C.in","C.out"},
    "frequencies_hz"->freq,
    "source_volume_flow_m3_s"->{1.*10^-6,4.*10^-7},
    "lengths_m"->(N[#,MachinePrecision]& /@ lengths),
    "areas_m2"->(N[#,MachinePrecision]& /@ areas),
    "rho_kg_m3"->1.2,"c_m_s"->343.,
    "records"->records
  |>
];
Print["NR1A_ORACLE_BEGIN"];
Print[ExportString[nr1Oracle[], "RawJSON"]];
Print["NR1A_ORACLE_END"];
