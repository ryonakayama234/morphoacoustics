(* OG-5 Gate A deliberate wrong-law controls, Wolfram.
  Original exploration on 2026-10-16 JST, A/B/C/D/E 733Hz, matched terminations,
  C area 0.00015 m^2 (unequal area to kill particle-velocity substitution).
  Formula source independent from Core; use WolframLanguageEvaluator or
  wolframscript -file docs/research/og5-gate-a-negative-controls.wl.
  Invalid mutations are NEVER approved physics and MUST fail the full-port oracle.
*)
r=6/5; c=343; f=733; ur=10^-6; zr=r c/(3/10000); pr=zr ur;
lengths=<|"A"->2/25,"B"->9/100,"C"->3/50,"D"->7/100,"E"->1/20|>;
areas=<|"A"->3/10000,"B"->3/10000,"C"->3/20000,"D"->3/10000,"E"->3/5000|>;
ns={"A","B","C","D","E"};
p[s_,end_]:=Symbol["P5"<>s<>end];
u[s_,end_]:=Symbol["U5"<>s<>end];
v=Flatten[Table[{p[s,"i"],u[s,"i"],p[s,"o"],u[s,"o"]},{s,ns}]];
zz[s_]:=r c/areas[s]/zr;
tr[s_]:=With[{a=N[2 Pi f lengths[s]/c,32],z=zz[s]},
 {{Cos[a],I z Sin[a]},{I Sin[a]/z,Cos[a]}}];
tubes=Flatten[Table[With[{m=tr[s]},{
 p[s,"i"]-m[[1,1]] p[s,"o"]-m[[1,2]] u[s,"o"],
 u[s,"i"]-m[[2,1]] p[s,"o"]-m[[2,2]] u[s,"o"]}],{s,ns}]];
junctions={p["A","o"]-p["B","i"],p["A","o"]-p["C","i"],
 u["A","o"]-u["B","i"]-u["C","i"],
 p["B","o"]-p["D","i"],p["B","o"]-p["E","i"],
 u["B","o"]-u["D","i"]-u["E","i"]};
loads=Table[p[s,"o"]-zz[s]u[s,"o"],{s,{"C","D","E"}}];

construct[j_,l_]:=Module[{arr,m,rhs},
 arr=CoefficientArrays[Join[tubes,j,{u["A","i"]-(1+2I/5)},l],v];
 {rhs,m}=Normal/@arr;
 Thread[v->LinearSolve[N[m,30],-N[rhs,30]]]];
good=construct[junctions,loads];
wrongParticle=ReplacePart[junctions,3->
 (u["A","o"]/areas["A"]-u["B","i"]/areas["B"]-u["C","i"]/areas["C"])];
wrongSign=ReplacePart[junctions,3->(u["A","o"]+u["B","i"]-u["C","i"])];
wrongLoad=ReplacePart[loads,1->(p["C","o"]-u["C","o"])];
compare[case_,jr_]:=Module[{bad,delta,flow,pin,pout},
 bad=construct[jr,If[case==="bad_load",wrongLoad,loads]];
 delta=N[Max[Abs[(v/.bad)-(v/.good)]]/Max[1,Max[Abs[v/.good]]],12];
 flow=N[Abs[(u["A","o"]-u["B","i"]-u["C","i"])/.bad],12];
 pin=N[Re[(pr ur/2 p["A","i"]Conjugate[u["A","i"]])/.bad],12];
 pout=N[Total[Table[
  Re[(pr ur/2 p[s,"o"]Conjugate[u[s,"o"]])/.bad],
  {s,{"C","D","E"}}]],12];
 <|"mutation"->case,"full_port_error"->delta,
 "physical_J1_flow_defect"->flow,
 "power_relative_defect"->N[Abs[pin-pout]/Max[10^-30,Abs[pin]],12]|>];
result={compare["particle_velocity",wrongParticle],
 compare["wrong_sign",wrongSign],compare["bad_load",junctions]};
Print["OG5_GATE_A_NEGATIVE_CONTROLS=",InputForm[result]];
