(* OG-5 Gate A independent Wolfram oracle. 2026-10-16 JST.
   DESIGN EXPLORATION ONLY: not validated against Core tree5 (does not exist).
   Two formulations: global 20x20 scaled p/U, and separate recursive impedance + full-port propagation.
   Run: wolframscript -file docs/research/og5-gate-a-oracle.wl
   Output is a 3-case receipt, followed by 144-case proposed grid aggregate.
   No existing production code or frozen OG3/OG4 oracle imported.
*)
rho=6/5; c=343; ur=10^-6; zr=rho c/(3/10000); pr=zr ur;
ids={"A","B","C","D","E"};
len=<|"A"->2/25,"B"->9/100,"C"->3/50,"D"->7/100,"E"->1/20|>;
pp[s_,side_]:=Symbol["OG5P"<>s<>side]; qq[s_,side_]:=Symbol["OG5Q"<>s<>side];
vars=Flatten[Table[{pp[s,"i"],qq[s,"i"],pp[s,"o"],qq[s,"o"]},{s,ids}]];

check[f_,ac_,cl_,sc_]:=Module[
 {area,z,t,inpZ,zC,zD,zE,zB,zA,eq,coef,rhs,sol,ref,ai,ao,bi,bo,ci,co,di,do,ei,eo,psrc,pout,err,flow,pfrac,cond},
 area=<|"A"->3/10000,"B"->3/10000,"C"->ac,"D"->3/10000,"E"->6/10000|>;
 z[s_]:=rho c/(area[s] zr);
 t[s_]:=With[{a=N[2 Pi f len[s]/c,34],v=z[s]},
  {{Cos[a],I v Sin[a]},{I Sin[a]/v,Cos[a]}}];
 inpZ[s_,load_]:=With[{m=t[s]},
  If[load==="closed",m[[1,1]]/m[[2,1]],
   (m[[1,1]] z[s]+m[[1,2]])/(m[[2,1]] z[s]+m[[2,2]])]];
 zC=inpZ["C",cl]; zD=inpZ["D","matched"]; zE=inpZ["E","matched"];
 zB=With[{m=t["B"],l=1/(1/zD+1/zE)},
  (m[[1,1]] l+m[[1,2]])/(m[[2,1]] l+m[[2,2]])];
 zA=With[{m=t["A"],l=1/(1/zB+1/zC)},
  (m[[1,1]] l+m[[1,2]])/(m[[2,1]] l+m[[2,2]])];

 (* First construction: the full system, no recursion shortcut. *)
 eq=Flatten[Table[With[{m=t[s]},
  {pp[s,"i"]-m[[1,1]] pp[s,"o"]-m[[1,2]] qq[s,"o"],
   qq[s,"i"]-m[[2,1]] pp[s,"o"]-m[[2,2]] qq[s,"o"]}],{s,ids}]];
 eq=Join[eq,{
  pp["A","o"]-pp["B","i"],pp["A","o"]-pp["C","i"],
  qq["A","o"]-qq["B","i"]-qq["C","i"],
  pp["B","o"]-pp["D","i"],pp["B","o"]-pp["E","i"],
  qq["B","o"]-qq["D","i"]-qq["E","i"],
  qq["A","i"]-(1+2 I/5) sc
 },Table[If[s==="C"&&cl==="closed",qq[s,"o"],
  pp[s,"o"]-z[s] qq[s,"o"]],{s,{"C","D","E"}}]];
 {rhs,coef}=Normal/@CoefficientArrays[eq,vars];
 sol=Thread[vars->LinearSolve[N[coef,30],-N[rhs,30]]];

 (* Second independent construction: load impedances recursively, full port propagation. *)
 ai={zA (1+2 I/5) sc,(1+2 I/5) sc}; ao=LinearSolve[t["A"],ai];
 bi={ao[[1]],ao[[1]]/zB}; ci={ao[[1]],ao[[1]]/zC};
 bo=LinearSolve[t["B"],bi]; co=LinearSolve[t["C"],ci];
 di={bo[[1]],bo[[1]]/zD}; ei={bo[[1]],bo[[1]]/zE};
 do=LinearSolve[t["D"],di]; eo=LinearSolve[t["E"],ei];
 ref=Thread[vars->Flatten[{ai,ao,bi,bo,ci,co,di,do,ei,eo}]];

 err=N[Max[Abs[(vars/.sol)-(vars/.ref)]]/
  Max[1,Max[Abs[vars/.ref]]],10];
 psrc=N[Re[(pr ur/2 pp["A","i"] Conjugate[qq["A","i"]])/.sol],14];
 pout=N[Total[Table[Re[(pr ur/2 pp[s,"o"] Conjugate[qq[s,"o"]])/.sol],
  {s,{"C","D","E"}}]],14];
 flow=N[Max[
  Abs[(qq["A","o"]-qq["B","i"]-qq["C","i"])/.sol],
  Abs[(qq["B","o"]-qq["D","i"]-qq["E","i"])/.sol]],10];
 pfrac=N[Re[(pr ur/2 pp["C","o"] Conjugate[qq["C","o"]])/.sol]/psrc,12];
 cond=N[Max[SingularValueList[N[coef,16]]]/
  Min[SingularValueList[N[coef,16]]],9];
 <|"f"->f,"areaC"->N[ac,7],"loadC"->cl,"scale"->sc,
   "max20diff"->err,"cond2"->cond,
   "pAiRealPa"->N[Re[(pr pp["A","i"])/.sol],14],
   "pAiImagPa"->N[Im[(pr pp["A","i"])/.sol],14],
   "pInW"->psrc,"pOutW"->pout,
   "powerResidual"->N[Abs[psrc-pout]/Max[10^-30,Abs[psrc]],9],
   "junctionResidual"->flow,"CpowerShare"->pfrac|>
];

(* Print machine-readable InputForm; these are exploratory, NOT production goldens. *)
examples={check[733,3/20000,"matched",1],
 check[733,3/5000,"matched",1],
 check[733,3/20000,"closed",1]};
Print["OG5_GATE_A_THREE_EXAMPLES=",InputForm[examples]];

(* Candidate 144-case discovery sweep, not a frozen/blind study. Record separately
   and do not claim successful preregistration solely because this script exits. *)
frequencies={80,250,400,733,997,1200,2000,4000};
sweep=Flatten[Table[check[f,a,l,s],{a,{3/20000,3/10000,3/5000}},
 {f,frequencies},{l,{"matched","closed"}},{s,{1,1/2,-1}}],3];
Print["OG5_GATE_A_SWEEP_COUNT=",Length[sweep]];
Print["OG5_GATE_A_SWEEP_MAX_FULL_PORT_ERROR=",
 InputForm[Max[Lookup[sweep,"max20diff"]]]];
Print["OG5_GATE_A_SWEEP_MAX_POWER_DEFECT=",
 InputForm[Max[Lookup[sweep,"powerResidual"]]]];
Print["OG5_GATE_A_SWEEP_MAX_COND2=",
 InputForm[Max[Lookup[sweep,"cond2"]]]];
