(* EL-R1 independent Wolfram oracle, 2026-10-22. Synthetic 1D physics ONLY.
   Traveling wave solution, NOT the Core transfer matrix. exp(+i omega t). *)
ClearAll[k, ell, r, z, transfer, reflection, normalizedPower, phase, gamma];
gamma[r_] := (r - 1)/(r + 1);
phase[f_, ell_] := Exp[-I 2 Pi f ell/343];
transfer[f_, ell_, r_] := Module[{q=phase[f,ell], g=gamma[r]}, q (1+g)/(1+g q^2)];
reflection[f_, ell_, r_] := gamma[r] phase[f,ell]^2;
(* For p0=1 and Zc scaled to 1, UL=pL/r, P=(1/2)Re[pL Conjugate[UL]]. *)
normalizedPower[f_,ell_,r_] := Abs[transfer[f,ell,r]]^2/(2 r);
(* Symbolically compare independent traveling waves with ABCD transfer. *)
Print["determinant: ", FullSimplify[Det[{{Cos[k ell], I z Sin[k ell]},
                         {I Sin[k ell]/z, Cos[k ell]}}]]];
Print["analytical matrix/scattering difference: ",
  FullSimplify[ComplexExpand[1/(Cos[k ell]+I Sin[k ell]/r) -
    Exp[-I k ell] (1+gamma[r])/(1+gamma[r] Exp[-2 I k ell])],
    Assumptions->{k>0, ell>0, r>0}]];
rows = Flatten[Table[{ll, rr, Re[transfer[3000,ll,rr]], Im[transfer[3000,ll,rr]],
                    Re[reflection[3000,ll,rr]], Im[reflection[3000,ll,rr]],
                    normalizedPower[3000,ll,rr]},
              {ll, {0.02,0.025,0.03}}, {rr, {0.5,1.,2.}}], 1];
Print["rows: ", N[rows, 16]];
