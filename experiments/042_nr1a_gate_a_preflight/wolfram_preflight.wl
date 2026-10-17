(* NR-1a Gate A EXPLORATORY independent-matrix preflight; NOT Gate B confirmation.
   No Python/Core import, no historical golden substitution. *)
ClearAll[nrBuild,nrSolve,nrReport];
nrBuild[case_,f_,mutant_:"none"]:=Module[
 {areas={3/10000,3/10000,3/20000},lengths={2/25,9/100,3/50},
 rho=6/5,c=343,uref=10^-6,pref=1372/1000,src=1+2 I/5,z,theta,cs,ss,
 mat=ConstantArray[0,{12,12}],rhs=ConstantArray[0,{12}],s,j,r,v,lawB,lawC,law},
 z=N[rho c/areas,35];theta=N[2 Pi f lengths/c,35];cs=Cos[theta];ss=Sin[theta];
 Do[s=If[mutant=="phasor_sign",-1,1];
  If[mutant=="tube_sign_A"&&j==1,s=-s];
  r=2 j-1;v=4 j-3;
  mat[[r,v]]=1;mat[[r,v+2]]=-cs[[j]];
  mat[[r,v+3]]=-s I ss[[j]] z[[j]] uref/pref;
  mat[[r+1,v+1]]=1;
  mat[[r+1,v+2]]=-s I ss[[j]] pref/(z[[j]] uref);
  mat[[r+1,v+3]]=-cs[[j]],{j,1,3}];
 mat[[7,3]]=1;mat[[7,5]]=-1;
 mat[[8,3]]=1;mat[[8,9]]=-1;
 mat[[9,4]]=1;mat[[9,6]]=-1;
 mat[[9,10]]=If[mutant=="junction_particle_velocity",-areas[[2]]/areas[[3]],-1];
 mat[[10,2]]=1;rhs[[10]]=src;
 {lawB,lawC}=Switch[case,"N",{"matched","closed"},
  "O",{"matched","matched"},"M",{"closed","matched"}];
 If[mutant=="wrong_B_terminal",
  lawB=If[lawB=="matched","closed","matched"]];
 If[mutant=="wrong_C_terminal",
  lawC=If[lawC=="matched","closed","matched"]];
 Do[j=If[v==1,2,3];law=If[v==1,lawB,lawC];
  If[law=="matched",
   mat[[10+v,4j-1]]=1;mat[[10+v,4j]]=-z[[j]] uref/pref,
   mat[[10+v,4j]]=1],{v,1,2}];
 {N[mat,25],N[rhs,25]}];
nrSolve[case_,f_,mutant_:"none"]:=Module[{mat,rhs,s,sol},
 {mat,rhs}=nrBuild[case,f,mutant];s=SingularValueList[mat];
 sol=LinearSolve[mat,rhs];{sol,N[Max[s]/Min[s],12]}];
nrReport[]:=Module[
 {cases={"N","O","M"},freq={80,250,400,733,997,1200,2000,4000},
 muts={"tube_sign_A","phasor_sign","junction_particle_velocity",
       "wrong_B_terminal","wrong_C_terminal"},
 rows={},orig,cond,margins,ranking},
 Do[{orig,cond}=nrSolve[cs,f];
  margins=Association@Table[
   mut->N[Max[Abs[nrSolve[cs,f,mut][[1]]-orig]],12],{mut,muts}];
  AppendTo[rows,<|"case"->cs,"frequency_hz"->f,
   "condition"->cond,"mutant_margins"->margins|>],
  {cs,cases},{f,freq}];
 ranking=Association@Table[mut->Module[{row},
  row=First[MinimalBy[rows,#["mutant_margins"][mut]&]];
  <|"case"->row["case"],"frequency_hz"->row["frequency_hz"],
   "minimum_margin"->row["mutant_margins"][mut]|>],{mut,muts}];
 <|"status"->"EXPLORATORY_PRE_GATE_A",
 "conditions_count"->Length[rows],
 "max_condition_2"->Max[rows[[All,"condition"]]],
 "minimum_by_mutant"->ranking,
 "quarter_wave_M_global_condition"->nrSolve["M",343/(4*(9/100))][[2]]|>];
Print["NR1A_PREFLIGHT_BEGIN"];
Print[ExportString[nrReport[],"RawJSON"]];
Print["NR1A_PREFLIGHT_END"];
