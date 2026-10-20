(* OG-AUD1 adoption audit independent 12-unknown global acoustic-port oracle.
   Documentation-only, 2026-10-20. KNOWN exploratory 16 cases, NOT
   prospective Gate-B confirmation. All laws are 1D ideal acoustic ducts.
   State order: {pAin,qAin,pAout,qAout,pBin,qBin,pBout,qBout,pCin,qCin,pCout,qCout}
   q=Zref U for numerical conditioning, so reported SI volume flow U=q/Zref.
*)
ClearAll[ogaAuditGlobal, ogaAuditAnalytic];
ogaAuditGlobal[a_, f_] := Module[
 {rho=1.2, c=343., areas={.0003,.0003,a}, lengths={.08,.09,.06},
  z,zref,v,eq={},ph,zscale,sol,s,uin,pin,pout},
 z=rho c/areas;zref=z[[1]];v=Array[x,12];
 Do[
  ph=2 Pi f lengths[[i]]/c;
  zscale=z[[i]]/zref;
  AppendTo[eq,v[[4i-3]]==Cos[ph] v[[4i-1]]+
                                      I zscale Sin[ph] v[[4i]]];
  AppendTo[eq,v[[4i-2]]==I Sin[ph]/zscale v[[4i-1]]+
                                      Cos[ph] v[[4i]]],
  {i,1,3}];
 eq=Join[eq,{v[[3]]==v[[5]],v[[3]]==v[[9]],
             v[[4]]==v[[6]]+v[[10]],
             v[[7]]==z[[2]]/zref v[[8]],
             v[[11]]==z[[3]]/zref v[[12]],
             v[[2]]==zref 10^-6 (1+.4 I)}];
 sol=Solve[eq,v];
 If[Length[sol]!=1,Return[Missing["Unsolvable"]]];
 s=v/.First[sol];
 uin=s[[2]]/zref;
 pin=Re[s[[1]] Conjugate[uin]]/2;
 pout=Re[(s[[7]] Conjugate[s[[8]]]+
          s[[11]] Conjugate[s[[12]]])/zref]/2;
 <|"Zin"->s[[1]]/uin,
   "JFlowResidualM3s"->Abs[s[[4]]-s[[6]]-s[[10]]]/zref,
   "RelativePowerResidual"->Abs[pin-pout]/Max[Abs[pin],10^-30],
   "ReZin"->Re[s[[1]]/uin]|>
];
ogaAuditAnalytic[a_,f_]:=Module[
 {rho=1.2,c=343.,z0,zb,zc,zj,r,theta},
 z0=rho c/.0003;zb=z0;zc=rho c/a;zj=1/(1/zb+1/zc);
 r=(zj-z0)/(zj+z0);theta=4 Pi f .08/c;
 z0 (1+r Exp[-I theta])/(1-r Exp[-I theta])
];
Module[{data,frequencies={137,431,619,1129,1607,2459,3571,3989},
 areas={.00015,.0006},rows},
 rows=Flatten[Table[
  With[{g=ogaAuditGlobal[a,f],z=ogaAuditAnalytic[a,f]},
   {a,f,Abs[g["Zin"]-z]/Abs[z],
    g["JFlowResidualM3s"],g["RelativePowerResidual"],g["ReZin"]}],
  {a,areas},{f,frequencies}],1];
 <|"status"->"PROPOSED_HOLDOUT_NOT_INDEPENDENTLY_RATIFIED",
   "rows"->rows,
   "maxRelativeComplexImpedanceError"->Max[rows[[All,3]]],
   "maxSignedJunctionFlowResidualM3s"->Max[rows[[All,4]]],
   "maxRelativePowerResidual"->Max[rows[[All,5]]],
   "minimumReZin"->Min[rows[[All,6]]]|>
]