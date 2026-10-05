(* Experiment 021 independent material-conditioned multi-mode transient oracle *)

ClearAll["Global`*"];

n=10; j=7; target=1/6; lambda=1; omega=25;
durations={1/25,2/25,3/25,1/5,8/25};
primaryT=3/25;
q0=ConstantArray[1,n];

laplacian=Normal@SparseArray[
 Join[
  Table[{i,i}->If[i==1||i==n,1,2],{i,1,n}],
  Table[{i,i+1}->-1,{i,1,n-1}],
  Table[{i+1,i}->-1,{i,1,n-1}]
 ],
 {n,n}
];

kFor[stiff_]:=ReplacePart[ConstantArray[1,n],6->stiff];
hFor[k_]:=DiagonalMatrix[k]+lambda laplacian;

qStar[k_]:=Module[{h=hFor[k],e=UnitVector[n,j],kkt,rhs},
 kkt=Join[Join[h,Transpose[{e}],2],{Append[e,0]}];
 rhs=Join[k,{target}];
 Take[LinearSolve[kkt,rhs],n]
];

sortedEigensystem[h_]:=Module[{vals,vecs,pairs},
 {vals,vecs}=Eigensystem[N[h,70]];
 pairs=SortBy[Transpose[{vals,vecs}],First];
 {pairs[[All,1]],pairs[[All,2]]}
];

r2State[qs_,t_]:=Module[
 {a=1-(1+omega t)Exp[-omega t],v=omega^2 t Exp[-omega t]},
 {N[q0+a(qs-q0),70],N[v(qs-q0),70]}
];

r3State[h_,qs_,t_]:=Module[
 {vals,vecs,rates,delta,coeff,activation,velocity,q,qd},
 {vals,vecs}=sortedEigensystem[h];
 rates=omega Sqrt[vals];
 delta=N[qs-q0,70];
 coeff=vecs.delta;
 activation=1-(1+rates t)Exp[-rates t];
 velocity=rates^2 t Exp[-rates t];
 q=N[q0+Transpose[vecs].(activation coeff),70];
 qd=N[Transpose[vecs].(velocity coeff),70];
 {q,qd,vals,rates}
];

metrics[qs_,state_]:=Module[{q=state[[1]],delta,s,perp,err,targetErr},
 delta=N[qs-q0,70];
 s=delta.(q-q0)/(delta.delta);
 perp=Norm[(q-q0)-s delta]/Norm[delta];
 err=Norm[qs-q]/Norm[delta];
 targetErr=Abs[(3/10000)q[[j]]-1/20000];
 <|
  "path_progress"->N[s,18],
  "orthogonal_fraction"->N[perp,18],
  "normalized_equilibrium_error"->N[err,18],
  "target_area_abs_error_m2"->N[targetErr,18]
 |>
];

rho=121/100; soundSpeed=343; tractLength=17/100; restArea=3/10000;

tm[len_,area_,f_]:=Module[{waveNumber=2 Pi f/soundSpeed,impedance=rho soundSpeed/area},
 {{Cos[waveNumber len],I impedance Sin[waveNumber len]},
  {I Sin[waveNumber len]/impedance,Cos[waveNumber len]}}
];

denom[qs_,f_]:=Re[
 (Dot@@Table[tm[tractLength/n,restArea qs[[i]],f],{i,1,n}])[[2,2]]
];

roots[qs_,guesses_]:=Table[
 N[
  x/.FindRoot[
   denom[N[qs,65],x]==0,
   {x,SetPrecision[g,65]},
   WorkingPrecision->60,
   AccuracyGoal->40,
   PrecisionGoal->40
  ],
  18
 ],
 {g,guesses}
];

names={"baseline","stiff"};
stiffValues={1,4};

materials=Association@Table[
 With[{name=names[[ii]],stiff=stiffValues[[ii]]},
  Module[{k=kFor[stiff],h,qs,vals,vecs,rates},
   h=hFor[k]; qs=qStar[k];
   {vals,vecs}=sortedEigensystem[h];
   rates=omega Sqrt[vals];
   name-><|
    "relative_stiffness"->k,
    "equilibrium_ratios"->N[qs,18],
    "hessian_eigenvalues"->N[vals,18],
    "modal_rates_per_s"->N[rates,18],
    "equilibrium_resonances_hz"->roots[qs,{384,1735,2205}]
   |>
  ]
 ],
 {ii,2}
];

primary=Association@Table[
 With[{name=names[[ii]],stiff=stiffValues[[ii]]},
  Module[{k=kFor[stiff],h,qs,r2,r3},
   h=hFor[k]; qs=qStar[k];
   r2=r2State[qs,primaryT];
   r3=r3State[h,qs,primaryT];
   name-><|
    "R2"->metrics[qs,r2],
    "R3"->Join[
     metrics[qs,r3],
     <|"q"->N[r3[[1]],18],"qdot_per_s"->N[r3[[2]],18]|>
    ]
   |>
  ]
 ],
 {ii,2}
];

durationObservables=Association@Table[
 With[{name=names[[ii]],stiff=stiffValues[[ii]]},
  Module[{k=kFor[stiff],h,qs},
   h=hFor[k]; qs=qStar[k];
   name->Table[
    Join[<|"duration_s"->N[t,18]|>,metrics[qs,r3State[h,qs,t]]],
    {t,durations}
   ]
  ]
 ],
 {ii,2}
];

primaryAcoustic=Association@Table[
 With[{name=names[[ii]],stiff=stiffValues[[ii]]},
  Module[{k=kFor[stiff],h,qs,r2,r3,r2Roots,r3Roots},
   h=hFor[k]; qs=qStar[k];
   r2=r2State[qs,primaryT];
   r3=r3State[h,qs,primaryT];
   r2Roots=roots[r2[[1]],{440,1670,2350}];
   r3Roots=roots[r3[[1]],{420,1690,2270}];
   name-><|
    "R2_resonances_hz"->r2Roots,
    "R3_resonances_hz"->r3Roots,
    "R3_minus_R2_hz"->N[r3Roots-r2Roots,18]
   |>
  ]
 ],
 {ii,2}
];

result=<|
 "oracle_version"->1,
 "provenance"-><|
  "engine"->"Wolfram Language",
  "python_candidate_used"->False,
  "arithmetic"->"exact rational fixture; 70-digit modal calculation; 60-digit acoustic root solve"
 |>,
 "parameters"-><|
  "omega_per_s"->25,
  "tract_length_m"->N[17/100,18],
  "section_count"->10,
  "rest_area_m2"->N[3/10000,18],
  "target_section_index_zero_based"->6,
  "target_area_ratio"->N[1/6,18],
  "target_area_m2"->N[1/20000,18],
  "smoothness_lambda"->1,
  "primary_duration_s"->N[primaryT,18],
  "durations_s"->N[durations,18]
 |>,
 "materials"->materials,
 "r2_primary_normalized_error"->N[(1+omega primaryT)Exp[-omega primaryT],18],
 "primary_120ms"->primary,
 "duration_observables"->durationObservables,
 "primary_acoustic"->primaryAcoustic
|>;

Export[
 FileNameJoin[{DirectoryName[$InputFileName],"multimode_transient_oracle.json"}],
 result,
 "RawJSON"
];

result
