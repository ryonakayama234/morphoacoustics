(* OG-5 Gate B3 independent, archival Wolfram 15.0.1 physics oracle.
   NO Python/Core imports, NO input taken from Core. Run in a fresh Wolfram kernel.
   Fixed v1 fixture only; not a biological vocal tract. *)
ClearAll[og5ReferenceCase,og5ReferenceCases,og5Pair,og5InputImpedance,
 og5BackPropagate,og5Frequencies,og5Areas,og5Loads,og5Scales];
og5Frequencies={80,250,400,733,997,1200,2000,4000};
og5Areas={.00015,.0003,.0006};
og5Loads={"matched","rigid_closed"};
og5Scales={1.,.5,-1.};
og5Pair[v_]:=N[{Re[v],Im[v]},16];
og5InputImpedance[zc_,t_,zl_]:=zc (zl+I zc Tan[t])/(zc+I zl Tan[t]);
og5BackPropagate[v_,zc_,t_]:={
  Cos[t] v[[1]]-I zc Sin[t] v[[2]],
  -I Sin[t] v[[1]]/zc+Cos[t] v[[2]]
};
og5ReferenceCase[f_,cArea_,cLoad_,scale_]:=Module[
 {areas,lengths,rho=1.2,speed=343.,pr=1.372,ur=1.*^-6,zr=1372000.,
  z,angles,mat,rhs,sol,global,rec,sourceU,zJ2,zB,zC,zJ1,zA,
  aI,aO,bI,bO,cI,cO,dI,dO,eI,eO,globalError,energy,j1p,j2p,j1q,j2q,put,m,t,k,row},
 areas={.0003,.0003,cArea,.0003,.0006};
 lengths={.08,.09,.06,.07,.05};
 z=rho speed/areas;
 angles=2 Pi f lengths/speed;
 mat=ConstantArray[0.+0.I,{20,20}];
 rhs=ConstantArray[0.+0.I,20];
 Do[
  k=4 (i-1);row=2 (i-1);
  m={{Cos[angles[[i]]],I z[[i]]/zr Sin[angles[[i]]]},
     {I zr/z[[i]] Sin[angles[[i]]],Cos[angles[[i]]]}};
  mat[[row+1,k+1]]=1.;mat[[row+1,k+3]]=-m[[1,1]];mat[[row+1,k+4]]=-m[[1,2]];
  mat[[row+2,k+2]]=1.;mat[[row+2,k+3]]=-m[[2,1]];mat[[row+2,k+4]]=-m[[2,2]],
  {i,1,5}];
 (* Global junction equations; two distinct ideal zero-volume 3-port laws. *)
 mat[[11,3]]=1.;mat[[11,5]]=-1.;
 mat[[12,3]]=1.;mat[[12,9]]=-1.;
 mat[[13,4]]=1.;mat[[13,6]]=-1.;mat[[13,10]]=-1.;
 mat[[14,7]]=1.;mat[[14,13]]=-1.;
 mat[[15,7]]=1.;mat[[15,17]]=-1.;
 mat[[16,8]]=1.;mat[[16,14]]=-1.;mat[[16,18]]=-1.;
 mat[[17,2]]=1.;rhs[[17]]=scale (1.+.4 I);
 If[cLoad==="rigid_closed",mat[[18,12]]=1.,
   mat[[18,11]]=1.;mat[[18,12]]=-z[[3]]/zr];
 mat[[19,15]]=1.;mat[[19,16]]=-z[[4]]/zr;
 mat[[20,19]]=1.;mat[[20,20]]=-z[[5]]/zr;
 sol=LinearSolve[mat,rhs];
 global=Table[{sol[[2 i-1]] pr,sol[[2 i]] ur},{i,1,10}];
 (* Separate impedance recursion and reconstruction, never using mat/rhs/sol. *)
 sourceU=ur scale (1.+.4 I);
 zJ2=1/(1/z[[4]]+1/z[[5]]);
 zB=og5InputImpedance[z[[2]],angles[[2]],zJ2];
 zC=If[cLoad==="rigid_closed",-I z[[3]] Cot[angles[[3]]],
       og5InputImpedance[z[[3]],angles[[3]],z[[3]]]];
 zJ1=1/(1/zB+1/zC);
 zA=og5InputImpedance[z[[1]],angles[[1]],zJ1];
 aI={zA sourceU,sourceU};
 aO=og5BackPropagate[aI,z[[1]],angles[[1]]];
 bI={aO[[1]],aO[[1]]/zB};
 cI={aO[[1]],aO[[1]]/zC};
 bO=og5BackPropagate[bI,z[[2]],angles[[2]]];
 cO=og5BackPropagate[cI,z[[3]],angles[[3]]];
 dI={bO[[1]],bO[[1]]/z[[4]]};
 eI={bO[[1]],bO[[1]]/z[[5]]};
 dO=og5BackPropagate[dI,z[[4]],angles[[4]]];
 eO=og5BackPropagate[eI,z[[5]],angles[[5]]];
 rec={aI,aO,bI,bO,cI,cO,dI,dO,eI,eO};
 globalError=Max[Flatten[Table[
   {Abs[global[[i,1]]-rec[[i,1]]]/pr,
    Abs[global[[i,2]]-rec[[i,2]]]/ur},{i,1,10}]]];
 put[v_]:=.5 Re[v[[1]] Conjugate[v[[2]]]];
 energy=Abs[put[rec[[1]]]-put[rec[[6]]]-put[rec[[8]]]-put[rec[[10]]]]/
   Max[Abs[put[rec[[1]]]],.5 pr ur Abs[scale]^2];
 j1p=Max[Abs[aO[[1]]-bI[[1]]],Abs[aO[[1]]-cI[[1]]]]/pr;
 j2p=Max[Abs[bO[[1]]-dI[[1]]],Abs[bO[[1]]-eI[[1]]]]/pr;
 j1q=Abs[aO[[2]]-bI[[2]]-cI[[2]]]/ur;
 j2q=Abs[bO[[2]]-dI[[2]]-eI[[2]]]/ur;
 <|"frequency_hz"->f,"c_area_m2"->cArea,"c_load"->cLoad,"scale"->scale,
 "global"-><|"pressure_pa"->(og5Pair/@global[[All,1]]),
             "volume_flow_m3_s"->(og5Pair/@global[[All,2]])|>,
 "recursive"-><|"pressure_pa"->(og5Pair/@rec[[All,1]]),
                "volume_flow_m3_s"->(og5Pair/@rec[[All,2]])|>,
 "oracle_max_scaled_difference"->globalError,
 "recursive_relative_power_defect"->energy,
 "recursive_max_scaled_pressure_residual"->Max[j1p,j2p],
 "recursive_max_scaled_flow_residual"->Max[j1q,j2q]|>
];
og5ReferenceCases[]:=Flatten[
  Table[og5ReferenceCase[f,a,l,s],
    {f,og5Frequencies},{a,og5Areas},{l,og5Loads},{s,og5Scales}],3
];
