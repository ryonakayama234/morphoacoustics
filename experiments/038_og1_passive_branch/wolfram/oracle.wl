(* Independent tangent-load/wave oracle. No Python solver or transfer matrix. *)
ClearAll[tubeLoad, states, pair];
rho = N[6/5, 80]; speed = N[343, 80]; baseArea = N[3/10000, 80];
lengths = N[{2/25, 9/100, 3/50}, 80];
pair[z_] := N[{Re[z], Im[z]}, MachinePrecision];
tubeLoad[l_, area_, f_, kind_, load_] := Module[{z = rho speed/area, q},
  q = Tan[2 Pi f l/speed];
  If[kind == "rigid_closed", -I z/q, z (load + I z q)/(z + I load q)]
];
states[ratio_, f_, kind_] := Module[
  {areas = baseArea {1, 1, ratio}, zs, zb, zc, zj, zi, phase, uin,
   pin, pj, ua, ub, uc, pb, qb, pc, qc, load, powers},
  zs = rho speed/areas; phase = 2 Pi f lengths/speed;
  load = Switch[kind, "matched", zs[[3]], "fixed_impedance", zs[[1]], _, 0];
  zb = tubeLoad[lengths[[2]], areas[[2]], f, "matched", zs[[2]]];
  zc = tubeLoad[lengths[[3]], areas[[3]], f, kind, load];
  zj = 1/(1/zb + 1/zc);
  zi = tubeLoad[lengths[[1]], areas[[1]], f, "impedance", zj];
  uin = N[(1 + 2 I/5)/10^6, 80]; pin = zi uin;
  pj = Cos[phase[[1]]] pin - I zs[[1]] Sin[phase[[1]]] uin;
  ua = -I Sin[phase[[1]]] pin/zs[[1]] + Cos[phase[[1]]] uin;
  ub = pj/zb; uc = pj/zc;
  pb = Cos[phase[[2]]] pj - I zs[[2]] Sin[phase[[2]]] ub;
  qb = -I Sin[phase[[2]]] pj/zs[[2]] + Cos[phase[[2]]] ub;
  pc = Cos[phase[[3]]] pj - I zs[[3]] Sin[phase[[3]]] uc;
  qc = -I Sin[phase[[3]]] pj/zs[[3]] + Cos[phase[[3]]] uc;
  powers = Re[{pin Conjugate[uin], pb Conjugate[qb], pc Conjugate[qc]}]/2;
  <|"area_ratio" -> N[ratio], "frequency_hz" -> f, "load_c" -> kind,
    "ports" -> <|"A.in" -> {pair[pin], pair[uin]}, "A.out" -> {pair[pj], pair[ua]},
      "B.in" -> {pair[pj], pair[ub]}, "B.out" -> {pair[pb], pair[qb]},
      "C.in" -> {pair[pj], pair[uc]}, "C.out" -> {pair[pc], pair[qc]}|>,
    "powers_input_B_C_w" -> N[powers, MachinePrecision]|>
];
ys = {y1, y2, y3};
scattering = Table[2 ys[[j]]/Total[ys] - KroneckerDelta[i,j], {i,3}, {j,3}];
identity = FullSimplify[Transpose[scattering].DiagonalMatrix[ys].scattering -
  DiagonalMatrix[ys], Assumptions -> y1>0 && y2>0 && y3>0];
records = Flatten[Table[states[r, f, kind], {r,{1/2,1,2}}, {f,{733,997}},
  {kind,{"matched","pressure_release","rigid_closed","fixed_impedance"}}]];
ExportString[<|"method" -> "80-digit tangent-load recursion and explicit wave propagation",
  "symbolic_weighted_power_residual" -> identity, "records" -> records|>, "RawJSON"]
