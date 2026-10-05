(* Experiment 022 independent shared-body multi-Gesture oracle *)

ClearAll["Global`*"];

n = 10;
lambda = 1;
omega = 25;
q0 = ConstantArray[1, n];

laplacian = Normal@SparseArray[
  Join[
    Table[{i, i} -> If[i == 1 || i == n, 1, 2], {i, 1, n}],
    Table[{i, i + 1} -> -1, {i, 1, n - 1}],
    Table[{i + 1, i} -> -1, {i, 1, n - 1}]
  ],
  {n, n}
];

k = ConstantArray[1, n];
h = DiagonalMatrix[k] + lambda laplacian;

solveEquilibrium[constraints_List] := Module[
  {c, d, kkt, rhs},
  c = Table[UnitVector[n, constraint[[1]]], {constraint, constraints}];
  d = constraints[[All, 2]];
  kkt = ArrayFlatten[
    {
      {h, Transpose[c]},
      {c, ConstantArray[0, {Length[d], Length[d]}]}
    }
  ];
  rhs = Join[k, d];
  Take[LinearSolve[kkt, rhs], n]
];

qA = solveEquilibrium[{{7, 1/6}}];
qB = solveEquilibrium[{{5, 1/3}}];
qAB = solveEquilibrium[{{7, 1/6}, {5, 1/3}}];
qOverlay = qA + qB - q0;

{eigenvalues, eigenvectors} = Eigensystem[N[h, 80]];
order = Ordering[eigenvalues];
eigenvalues = eigenvalues[[order]];
eigenvectors = eigenvectors[[order]];
rates = omega Sqrt[eigenvalues];

propagate[q_, v_, target_, dt_] := Module[
  {error0, velocity0, b, decay, error1, velocity1},
  error0 = eigenvectors . (q - target);
  velocity0 = eigenvectors . v;
  b = velocity0 + rates error0;
  decay = Exp[-rates dt];
  error1 = (error0 + b dt) decay;
  velocity1 = (velocity0 - rates b dt) decay;
  {
    N[target + Transpose[eigenvectors] . error1, 60],
    N[Transpose[eigenvectors] . velocity1, 60]
  }
];

zero = ConstantArray[0, n];

shared0 = {N[q0, 60], N[zero, 60]};
shared80 = propagate[shared0[[1]], shared0[[2]], qA, 2/25];
shared200 = propagate[shared80[[1]], shared80[[2]], qAB, 3/25];
shared280 = propagate[shared200[[1]], shared200[[2]], qB, 2/25];
shared400 = propagate[shared280[[1]], shared280[[2]], q0, 3/25];

a80 = propagate[q0, zero, qA, 2/25];
a200 = propagate[a80[[1]], a80[[2]], qA, 3/25];
a280 = propagate[a200[[1]], a200[[2]], q0, 2/25];
a400 = propagate[a280[[1]], a280[[2]], q0, 3/25];

b80 = {N[q0, 60], N[zero, 60]};
b200 = propagate[b80[[1]], b80[[2]], qB, 3/25];
b280 = propagate[b200[[1]], b200[[2]], qB, 2/25];
b400 = propagate[b280[[1]], b280[[2]], q0, 3/25];

nullState[a_, b_] := {
  a[[1]] + b[[1]] - q0,
  a[[2]] + b[[2]]
};

null80 = nullState[a80, b80];
null200 = nullState[a200, b200];
null280 = nullState[a280, b280];
null400 = nullState[a400, b400];

scale = Norm[qAB - q0];

oracleNumber[x_] := Module[{value = N[x, 18]},
  If[Abs[value] < 10^-30, 0.0, value]
];

eventMetrics[t_, shared_, independent_] := <|
  "time_s" -> N[t, 18],
  "shared_null_l2" ->
    oracleNumber[Norm[shared[[1]] - independent[[1]]]],
  "normalized_shared_null" ->
    oracleNumber[Norm[shared[[1]] - independent[[1]]] / scale],
  "shared_null_velocity_l2" ->
    oracleNumber[Norm[shared[[2]] - independent[[2]]]],
  "minimum_shared_ratio" -> N[Min[shared[[1]]], 18],
  "minimum_null_ratio" -> N[Min[independent[[1]]], 18]
|>;

rho = 121/100;
soundSpeed = 343;
tractLength = 17/100;
restArea = 3/10000;

transferMatrix[len_, area_, f_] := Module[
  {waveNumber = 2 Pi f/soundSpeed, impedance = rho soundSpeed/area},
  {
    {Cos[waveNumber len], I impedance Sin[waveNumber len]},
    {I Sin[waveNumber len]/impedance, Cos[waveNumber len]}
  }
];

denominator[q_, f_] := Re[
  (Dot @@ Table[
    transferMatrix[tractLength/n, restArea q[[i]], f],
    {i, 1, n}
  ])[[2, 2]]
];

roots[q_, guesses_] := Table[
  N[
    x /. FindRoot[
      denominator[N[q, 70], x] == 0,
      {x, SetPrecision[g, 50]},
      WorkingPrecision -> 45,
      AccuracyGoal -> 30,
      PrecisionGoal -> 30
    ],
    18
  ],
  {g, guesses}
];

sharedRoots = roots[shared200[[1]], {405, 1700, 2343}];
nullRoots = roots[null200[[1]], {357, 1725, 2236}];

compatibleC = {UnitVector[n, 7], UnitVector[n, 5]};
compatibleD = {1/6, 1/3};
conflictC = {UnitVector[n, 7], UnitVector[n, 7]};
conflictD = {1/6, 1/3};

result = <|
  "oracle_version" -> 1,
  "provenance" -> <|
    "engine" -> "Wolfram Language",
    "python_candidate_used" -> False,
    "arithmetic" ->
      "exact rational fixture; high-precision modal calculation and acoustic root solve"
  |>,
  "parameters" -> <|
    "tract_length_m" -> N[tractLength, 18],
    "section_count" -> n,
    "rest_area_m2" -> N[restArea, 18],
    "smoothness_lambda" -> lambda,
    "omega_per_s" -> omega,
    "gesture_a" -> <|
      "location" -> N[13/20, 18],
      "section_index_zero_based" -> 6,
      "target_area_m2" -> N[1/20000, 18],
      "target_ratio" -> N[1/6, 18],
      "onset_s" -> 0,
      "offset_s" -> N[1/5, 18]
    |>,
    "gesture_b" -> <|
      "location" -> N[9/20, 18],
      "section_index_zero_based" -> 4,
      "target_area_m2" -> N[1/10000, 18],
      "target_ratio" -> N[1/3, 18],
      "onset_s" -> N[2/25, 18],
      "offset_s" -> N[7/25, 18]
    |>,
    "end_time_s" -> N[2/5, 18]
  |>,
  "modal" -> <|
    "eigenvalues" -> N[eigenvalues, 18],
    "rates_per_s" -> N[rates, 18]
  |>,
  "equilibria" -> <|
    "a" -> N[qA, 18],
    "b" -> N[qB, 18],
    "shared_ab" -> N[qAB, 18],
    "independent_overlay_ab" -> N[qOverlay, 18],
    "shared_overlay_l2" -> N[Norm[qAB - qOverlay], 18],
    "normalized_nonadditivity" ->
      N[Norm[qAB - qOverlay]/Norm[qAB - q0], 18],
    "shared_task_residuals" ->
      N[{qAB[[7]] - 1/6, qAB[[5]] - 1/3}, 18],
    "overlay_task_residuals" ->
      N[{qOverlay[[7]] - 1/6, qOverlay[[5]] - 1/3}, 18],
    "minimum_shared_ratio" -> N[Min[qAB], 18],
    "minimum_overlay_ratio" -> N[Min[qOverlay], 18]
  |>,
  "primary_200ms" -> <|
    "shared_q" -> N[shared200[[1]], 18],
    "shared_qdot_per_s" -> N[shared200[[2]], 18],
    "null_q" -> N[null200[[1]], 18],
    "null_qdot_per_s" -> N[null200[[2]], 18],
    "shared_null_l2" ->
      N[Norm[shared200[[1]] - null200[[1]]], 18],
    "normalized_shared_null" ->
      N[Norm[shared200[[1]] - null200[[1]]] / scale, 18],
    "shared_null_velocity_l2" ->
      N[Norm[shared200[[2]] - null200[[2]]], 18]
  |>,
  "events" -> {
    eventMetrics[2/25, shared80, null80],
    eventMetrics[1/5, shared200, null200],
    eventMetrics[7/25, shared280, null280],
    eventMetrics[2/5, shared400, null400]
  },
  "primary_acoustic" -> <|
    "time_s" -> N[1/5, 18],
    "shared_resonances_hz" -> sharedRoots,
    "null_resonances_hz" -> nullRoots,
    "shared_minus_null_hz" -> N[sharedRoots - nullRoots, 18]
  |>,
  "constraint_consistency" -> <|
    "compatible_rank_c" -> MatrixRank[compatibleC],
    "compatible_rank_augmented" ->
      MatrixRank[MapThread[Append, {compatibleC, compatibleD}]],
    "conflict_rank_c" -> MatrixRank[conflictC],
    "conflict_rank_augmented" ->
      MatrixRank[MapThread[Append, {conflictC, conflictD}]],
    "conflict_target_gap" -> N[Abs[1/3 - 1/6], 18]
  |>
|>;

Export[
  FileNameJoin[
    {
      DirectoryName[$InputFileName],
      "shared_body_multigesture_oracle.json"
    }
  ],
  result,
  "RawJSON"
];

result
