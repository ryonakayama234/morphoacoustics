(* Experiment 018 independent local-area sensitivity oracle *)

ClearAll[rho,c,ell,a0,ag,idx,epsilons,tm,denom,rootSet,sens,result];

rho = 121/100;
c = 343;
ell = 17/100;
a0 = 3/10000;
ag = 2/10000;
idx = 0;
epsilons = {-1/10,-1/20,0,1/20,1/10};

tm[len_,area_,f_] := Module[{k=2 Pi f/c,z=rho c/area},
  {{Cos[k len], I z Sin[k len]},
   {I Sin[k len]/z, Cos[k len]}}
];

denom[eps_,gesture_,f_] := Module[{areas,mats},
  areas = ConstantArray[a0,10];
  areas[[idx+1]] = a0 (1+eps);
  If[gesture, areas[[7]] = ag];
  mats = Table[tm[ell/10,areas[[j]],f],{j,1,10}];
  Re[(Dot@@mats)[[2,2]]]
];

restBase = Table[N[(2 n-1)c/(4 ell),24],{n,1,3}];

rootSet[eps_,gesture_,guesses_] := Table[
  N[x /. FindRoot[
    denom[eps,gesture,x] == 0,
    {x,SetPrecision[g,60]},
    WorkingPrecision->60,
    AccuracyGoal->40,
    PrecisionGoal->40
  ],20],
  {g,guesses}
];

gestureBase = rootSet[0,True,restBase];
rest = Table[rootSet[e,False,restBase],{e,epsilons}];
gesture = Table[rootSet[e,True,gestureBase],{e,epsilons}];

sens[minus_,plus_,e_] := Table[
  N[
    (Log[plus[[n]]] - Log[minus[[n]]]) /
    (Log[1+e] - Log[1-e]),
    18
  ],
  {n,1,3}
];

s5Rest = sens[rest[[2]],rest[[4]],1/20];
s10Rest = sens[rest[[1]],rest[[5]],1/10];
s5Gesture = sens[gesture[[2]],gesture[[4]],1/20];
s10Gesture = sens[gesture[[1]],gesture[[5]],1/10];

result = <|
  "parameters" -> <|
    "tract_length_m" -> N[ell,18],
    "section_count" -> 10,
    "intervention_section_index" -> 0,
    "baseline_area_m2" -> N[a0,18],
    "gesture_section_index" -> 6,
    "gesture_location_normalized" -> 0.65,
    "gesture_target_area_m2" -> N[ag,18]
  |>,
  "relative_changes" -> N[epsilons,18],
  "rest_resonances_hz" -> rest,
  "gesture_resonances_hz" -> gesture,
  "rest_sensitivity_eps_0_05" -> s5Rest,
  "rest_sensitivity_eps_0_10" -> s10Rest,
  "gesture_sensitivity_eps_0_05" -> s5Gesture,
  "gesture_sensitivity_eps_0_10" -> s10Gesture,
  "rest_abs_nonlinearity" -> N[Abs[s10Rest-s5Rest],18],
  "gesture_abs_nonlinearity" -> N[Abs[s10Gesture-s5Gesture],18],
  "expected_monotonic_direction" -> <|
    "rest" -> {"decreasing","decreasing","decreasing"},
    "gesture" -> {"decreasing","decreasing","decreasing"}
  |>
|>;

Export[
  FileNameJoin[{DirectoryName[$InputFileName],"local_area_sensitivity_oracle.json"}],
  result,
  "RawJSON"
];
result
