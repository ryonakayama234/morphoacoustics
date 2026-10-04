(* Experiment 020 independent stateful finite-time task oracle *)

ClearAll[
  n,j,target,lambda,laplacian,solveQStar,
  omega,aOn,vOn,releaseState,qAt,
  rho,c,ell,a0,tm,denom,roots,durations,result,t95,t99
];

n = 10;
j = 7;
target = 1/6;
lambda = 1;
omega = 25;

laplacian = Normal@SparseArray[
  Join[
    Table[{i,i}->If[i==1||i==n,1,2],{i,1,n}],
    Table[{i,i+1}->-1,{i,1,n-1}],
    Table[{i+1,i}->-1,{i,1,n-1}]
  ],
  {n,n}
];

solveQStar[] := Module[{kk,h,e,a,b,sol},
  kk = ConstantArray[1,n];
  h = DiagonalMatrix[kk] + lambda laplacian;
  e = UnitVector[n,j];
  a = Join[
    Join[h,Transpose[{e}],2],
    {Append[e,0]}
  ];
  b = Join[kk,{target}];
  sol = LinearSolve[a,b];
  Take[sol,n]
];

qstar = solveQStar[];

aOn[t_] := 1-(1+omega t) Exp[-omega t];
vOn[t_] := omega^2 t Exp[-omega t];

releaseState[dur_,tau_] := Module[{aa,vv,b},
  aa = aOn[dur];
  vv = vOn[dur];
  b = vv + omega aa;
  {
    (aa + b tau) Exp[-omega tau],
    (vv - omega b tau) Exp[-omega tau]
  }
];

qAt[aa_] :=
  ConstantArray[1,n]
  + aa (qstar-ConstantArray[1,n]);

rho = 121/100;
c = 343;
ell = 17/100;
a0 = 3/10000;

tm[len_,area_,f_] := Module[{k=2 Pi f/c,z=rho c/area},
  {
    {Cos[k len], I z Sin[k len]},
    {I Sin[k len]/z, Cos[k len]}
  }
];

denom[qs_,f_] := Re[
  (Dot@@Table[
    tm[ell/n,a0 qs[[i]],f],
    {i,1,n}
  ])[[2,2]]
];

roots[qs_,guesses_] := Table[
  N[
    x /. FindRoot[
      denom[qs,x] == 0,
      {x,SetPrecision[g,70]},
      WorkingPrecision->70,
      AccuracyGoal->45,
      PrecisionGoal->45
    ],
    18
  ],
  {g,guesses}
];

durations = {1/25,2/25,3/25,1/5,8/25};

rows = Table[
  Module[{aa,vv,r50,r100,qs},
    aa = aOn[dur];
    vv = vOn[dur];
    r50 = releaseState[dur,1/20];
    r100 = releaseState[dur,1/10];
    qs = qAt[aa];

    <|
      "duration_s" -> N[dur,18],
      "duration_ms" -> N[1000 dur,18],
      "omegaT" -> N[omega dur,18],
      "activation_offset_minus" -> N[aa,18],
      "velocity_offset_minus_per_s" -> N[vv,18],
      "task_error_fraction_offset_minus" -> N[1-aa,18],
      "target_area_m2_offset_minus" -> N[a0 qs[[j]],18],
      "target_area_abs_error_m2" ->
        N[Abs[a0 qs[[j]]-a0 target],18],
      "release_50ms_activation" -> N[r50[[1]],18],
      "release_50ms_velocity_per_s" -> N[r50[[2]],18],
      "release_100ms_activation" -> N[r100[[1]],18],
      "release_100ms_velocity_per_s" -> N[r100[[2]],18],
      "resonances_hz_offset_minus" ->
        roots[qs,{450,1650,2350}]
    |>
  ],
  {dur,durations}
];

t95 = t /. FindRoot[
  (1+omega t) Exp[-omega t] == 0.05,
  {t,0.19}
];

t99 = t /. FindRoot[
  (1+omega t) Exp[-omega t] == 0.01,
  {t,0.27}
];

result = <|
  "parameters" -> <|
    "omega_per_s" -> 25.,
    "tract_length_m" -> 0.17,
    "section_count" -> 10,
    "rest_area_m2" -> 0.0003,
    "target_section_index_zero_based" -> 6,
    "target_area_ratio" -> N[target,18],
    "target_area_m2" -> 0.00005,
    "smoothness_lambda" -> 1.
  |>,
  "r1_equilibrium_state_ratio" -> N[qstar,18],
  "r1_equilibrium_resonances_hz" ->
    roots[qstar,{380,1740,2210}],
  "settling_95_ms" -> N[1000 t95,18],
  "settling_99_ms" -> N[1000 t99,18],
  "duration_rows" -> rows
|>;

Export[
  FileNameJoin[
    {DirectoryName[$InputFileName],"stateful_dynamics_oracle.json"}
  ],
  result,
  "RawJSON"
];

result
