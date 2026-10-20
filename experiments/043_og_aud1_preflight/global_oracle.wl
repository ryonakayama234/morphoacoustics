(* OG-AUD1 pre-Gate-A exploratory oracle; not preregistered and not production. *)
ClearAll[ogaudGlobal, ogaudScalar];

ogaudScalar[area_, f_] := Module[
 {rho = 1.2, c = 343., areaA = .0003, lenA = .08, za, zb, zc, zj, theta},
 za = rho c/areaA; zb = za; zc = rho c/area;
 zj = 1/(1/zb + 1/zc);
 theta = 2 Pi f lenA/c;
 za (zj Cos[theta] + I za Sin[theta])/
  (za Cos[theta] + I zj Sin[theta])
];

ogaudGlobal[areaC_, f_, lenB_: .09, lenC_: .06, wrongParticleLaw_: False] := Module[
 {rho = 1.2, c = 343., areaA = .0003, lenA = .08,
 zref, m, rhs, tubes, q, len, ar, z, co, si, state,
 zin, pin, pout, ppow, normCond, jFlow},
 zref = rho c/areaA;
 m = ConstantArray[0.0 + 0.0 I, {12, 12}];
 rhs = ConstantArray[0.0 + 0.0 I, 12];
 tubes = {{1, lenA, areaA}, {2, lenB, areaA}, {3, lenC, areaC}};
 Do[
  q = tube[[1]]; len = tube[[2]]; ar = tube[[3]];
  z = rho c/ar; co = Cos[2 Pi f len/c]; si = Sin[2 Pi f len/c];
  m[[2 q - 1, 4 q - 3]] = 1;
  m[[2 q - 1, 4 q - 1]] = -co;
  m[[2 q - 1, 4 q]] = -I (z/zref) si;
  m[[2 q, 4 q - 2]] = 1;
  m[[2 q, 4 q - 1]] = -I (zref/z) si;
  m[[2 q, 4 q]] = -co;
  , {tube, tubes}];
 (* p_A.out = p_B.in = p_C.in *)
 m[[7, 3]] = 1; m[[7, 5]] = -1;
 m[[8, 3]] = 1; m[[8, 9]] = -1;
 (* correct junction: U_A.out = U_B.in + U_C.in *)
 m[[9, 4]] = 1; m[[9, 6]] = -1;
 m[[9, 10]] = If[TrueQ[wrongParticleLaw], -areaA/areaC, -1];
 (* matched B/C distal loads *)
 m[[10, 7]] = 1; m[[10, 8]] = -1;
 m[[11, 11]] = 1; m[[11, 12]] = -(rho c/areaC)/zref;
 (* source boundary: volume-flow phasor at A.in *)
 m[[12, 2]] = 1; rhs[[12]] = zref (1.0 + .4 I) 10^-6;
 state = LinearSolve[m, rhs];
 zin = state[[1]]/((1.0 + .4 I) 10^-6);
 pin = Re[state[[1]] Conjugate[state[[2]]]]/(2 zref);
 pout = Re[state[[7]] Conjugate[state[[8]]] +
  state[[11]] Conjugate[state[[12]]]]/(2 zref);
 jFlow = (state[[4]] - state[[6]] - state[[10]])/zref;
 normCond = Norm[m, 2] Norm[Inverse[m], 2];
 <|"Zin" -> zin, "PressurePaPeak" -> Abs[state[[1]]],
   "NormalizedMatrixCond2" -> normCond,
   "PowerResidualW" -> Abs[pin - pout],
   "VolumeFlowResidualM3s" -> Abs[jFlow],
   "GlobalVsScalarRelError" -> Abs[zin - ogaudScalar[areaC, f]]/
     Abs[ogaudScalar[areaC, f]]|>
];

Module[{anchors = {80, 733, 997, 4000}, areas = {.00015, .0006},
 rows, mutantDiff, nullDiff},
 rows = Flatten[Table[
  With[{g = ogaudGlobal[a, f]},
   {a, f, N[g["PressurePaPeak"], 10], N[g["NormalizedMatrixCond2"], 8],
    N[g["GlobalVsScalarRelError"], 4],
    N[g["PowerResidualW"], 4],
    N[g["VolumeFlowResidualM3s"], 4]}],
  {a, areas}, {f, anchors}], 1];
 mutantDiff = Table[
  With[{m = ogaudGlobal[a, f, .09, .06, True]},
   {a, f, N[Abs[m["Zin"] - ogaudScalar[a, f]]/Abs[ogaudScalar[a, f]], 8]}],
  {a, areas}, {f, anchors}];
 nullDiff = Table[
  With[{b = ogaudGlobal[a, f], swapped = ogaudGlobal[a, f, .13, .025]},
   {a, f, N[Abs[swapped["Zin"] - b["Zin"]]/Abs[b["Zin"]], 4]}],
  {a, areas}, {f, anchors}];
 <|"dataset" -> rows,
   "maxScalarRelativeError" -> Max[rows[[All, 5]]],
   "maxNormalizedCond2" -> Max[rows[[All, 4]]],
   "maxPowerResidualW" -> Max[rows[[All, 6]]],
   "maxFlowResidualM3s" -> Max[rows[[All, 7]]],
   "wrongParticleVelocityMutants" -> mutantDiff,
   "matchedBranchLengthNulls" -> nullDiff,
   "status" -> "EXPLORATORY_ONLY_NOT_GATE_B"|>
]
