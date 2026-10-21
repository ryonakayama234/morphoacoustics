(* SMC-1: independently check inherited Exp011 timing constraints.
   This does NOT assert /a/ or /i/ phonetic identity, body realization, or audio. *)
ClearAll[aOn, aOff, bOn, bOff, lag, overlap, residual];
aOn = 8/100;
aOff = aOn + 18/100;
Table[
 lag = k;
 bOn = aOff + lag;
 bOff = bOn + 18/100;
 overlap = Max[0, Min[aOff, bOff] - Max[aOn, bOn]];
 residual = Max[Abs[aOff-aOn-18/100],
   Abs[bOn-aOff-lag], Abs[bOff-bOn-18/100]];
 <|"lag_s" -> N[lag, 16],
   "A_s" -> N[{aOn,aOff},16],
   "B_s" -> N[{bOn,bOff},16],
   "overlap_s" -> N[overlap,16],
   "max_constraint_residual" -> N[residual,16]|>,
 {k, {0,-6/100}}
]
