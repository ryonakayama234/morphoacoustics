(* CC-B1 Gate A 2026-10-22: FROZEN before any new site08 Core physical execution.
  Site index j=9 in Wolfram (zero-based 8), fixed from midpoint study.
  This is NOT a previously unseen theoretical site: prior scan inspected all16.
  Independent implementations of ideal ABCD and right-to-left impedance recurrence.
*)
Module[{dia,rest,x,dlog,terminal,rho=1.2,c=343.,l=.01,frequencies,ab,rec,pk,table,j=9},
 dia={12,12,26,16,12,14,20,26,30,34,38,34,34,30,28,32};
 rest=Pi(N[dia]/2000.)^2; x=N[Range[0,15]/15];
 dlog=3.(.5921764128805103 Exp[-(x-.3424849103873983)^2/(2*.16^2)]-
 .9235962908995712 Exp[-(x-.7167402543883221)^2/(2*.16^2)]-
 .04495226070116771 Exp[-(x-1)^2/(2*.1^2)]);
 terminal=rest Exp[dlog]; frequencies=N[Range[100,3500,5]];
 ab[f_,areas_]:=With[{m=Fold[Dot,IdentityMatrix[2],
 Table[With[{phase=2 Pi f l/c,z=rho c/areas[[q]]},
 {{Cos[phase],I z Sin[phase]},{I Sin[phase]/z,Cos[phase]}}],{q,16}]]},
 Abs[m[[1,2]]/m[[2,2]]]];
 rec[f_,areas_]:=Module[{out=0.,z,theta=2 Pi f l/c},
 Do[z=rho c/areas[[q]];out=z(out+I z Tan[theta])/(z+I out Tan[theta]),{q,16,1,-1}];Abs[out]];
 pk[fn_,areas_]:=Module[{v,idx},v=fn[#,areas]&/@frequencies;
 idx=Select[Range[2,Length[v]-1],v[[#]]>v[[#-1]]&&v[[#]]>v[[#+1]]&];
 Take[frequencies[[idx]],UpTo[3]]];
 table=Table[With[{ar=ReplacePart[rest,j->rest[[j]]*ratio],
 at=ReplacePart[terminal,j->terminal[[j]]*ratio]},
 <|"ratio"->ratio,"rest_abcd"->pk[ab,ar],"rest_recurrence"->pk[rec,ar],
 "terminal_abcd"->pk[ab,at],"terminal_recurrence"->pk[rec,at]|>],
 {ratio,{.9,1.,1.1}}];
 <|"zero_based_site"->8,"rows"->table,"theoretical_not_unseen"->True,
 "core_run_after_freeze_required"->True|>
]
