(* Experiment 019 independent reduced material-conditioned realization oracle *)

ClearAll[
  n,j,target,lambda,q0,laplacian,solveState,
  rho,c,ell,a0,ag,tm,denom,roots,r0,base,stiff,result
];

n = 10;
j = 7;
target = 1/6;
lambda = 1;
q0 = ConstantArray[1,n];

laplacian = Normal@SparseArray[
  Join[
    Table[{i,i}->If[i==1||i==n,1,2],{i,1,n}],
    Table[{i,i+1}->-1,{i,1,n-1}],
    Table[{i+1,i}->-1,{i,1,n-1}]
  ],
  {n,n}
];

solveState[kleft_] := Module[{kk,h,e,a,b,sol},
  kk = ConstantArray[1,n];
  kk[[j-1]] = kleft;
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

base = solveState[1];
stiff = solveState[4];

rho = 121/100;
c = 343;
ell = 17/100;
a0 = 3/10000;
ag = 1/20000;

tm[len_,area_,f_] := Module[{k=2 Pi f/c,z=rho c/area},
  {{Cos[k len], I z Sin[k len]},
   {I Sin[k len]/z, Cos[k len]}}
];

denom[xs_,f_] := Re[
  (Dot@@Table[tm[ell/n,a0 xs[[m]],f],{m,1,n}])[[2,2]]
];

roots[xs_,guesses_] := Table[
  N[x /. FindRoot[
    denom[xs,x] == 0,
    {x,SetPrecision[g,60]},
    WorkingPrecision->60,
    AccuracyGoal->40,
    PrecisionGoal->40
  ],20],
  {g,guesses}
];

r0 = ReplacePart[ConstantArray[1,n],j->target];

result = <|
  "parameters" -> <|
    "section_count" -> n,
    "target_section_index_zero_based" -> j-1,
    "left_neighbor_section_index_zero_based" -> j-2,
    "right_neighbor_section_index_zero_based" -> j,
    "target_ratio" -> N[target,20],
    "smoothness_lambda" -> N[lambda,20],
    "baseline_left_relative_stiffness" -> 1.,
    "candidate_left_relative_stiffness" -> 4.,
    "rest_area_m2" -> N[a0,20],
    "gesture_target_area_m2" -> N[ag,20],
    "tract_length_m" -> N[ell,20]
  |>,
  "r0_hard_projector_state_ratio" -> N[r0,20],
  "r1_baseline_state_ratio" -> N[base,20],
  "r1_candidate_state_ratio" -> N[stiff,20],
  "r1_candidate_minus_baseline_l2" -> N[Norm[stiff-base],20],
  "r1_baseline_left_neighbor_ratio" -> N[base[[j-1]],20],
  "r1_candidate_left_neighbor_ratio" -> N[stiff[[j-1]],20],
  "r1_baseline_right_neighbor_ratio" -> N[base[[j+1]],20],
  "r1_candidate_right_neighbor_ratio" -> N[stiff[[j+1]],20],
  "r0_resonances_hz" -> roots[r0,{390,1650,2050}],
  "r1_baseline_resonances_hz" -> roots[base,{380,1740,2210}],
  "r1_candidate_resonances_hz" -> roots[stiff,{380,1710,2190}]
|>;

result = Append[
  result,
  "r1_candidate_minus_baseline_resonance_hz" ->
    N[
      result["r1_candidate_resonances_hz"] -
      result["r1_baseline_resonances_hz"],
      20
    ]
];

Export[
  FileNameJoin[
    {DirectoryName[$InputFileName],"material_realization_oracle.json"}
  ],
  result,
  "RawJSON"
];
result
