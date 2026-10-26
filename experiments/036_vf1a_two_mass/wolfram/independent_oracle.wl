(* VF-1A independent Wolfram analytic oracle, 2026-10-26.
   Generic two-mass compliant-aperture model, NOT a biological oracle.
   Evaluated separately in Wolfram kernel before numerical CI evidence.
   This source is not imported by the Python physics solver. *)
ClearAll[p,q,u,g1,g2,v1,v2,psub,rl,b,d1,d2,dt,loss,em,ef,ea,total,expected];
em=dt (p (g1 v1+g2 v2)-d1 v1^2-d2 v2^2);
ef=dt ((psub-p) q-rl q^2-b Abs[q]^3);
ea=dt p u-loss;
total=em+ef+ea;
expected=dt (psub q-rl q^2-b Abs[q]^3-d1 v1^2-d2 v2^2)-loss;
balance=FullSimplify[(total-expected)/.u->(q-g1 v1-g2 v2)];
omegaSym=Sqrt[30/(1.2 10^-4)];
omegaAnti=Sqrt[(30+2 8)/(1.2 10^-4)];
freqSym=N[omegaSym/(2 Pi),14];
freqAnti=N[omegaAnti/(2 Pi),14];
thetaAnti=N[2 ArcTan[omegaAnti/(2 48000)],14];
Print["midpoint_full_power_identity_residual=",InputForm[balance]];
Print["symmetric_hz=",InputForm[freqSym]];
Print["antisymmetric_hz=",InputForm[freqAnti]];
Print["antisymmetric_48k_rad_per_step=",InputForm[thetaAnti]];
If[balance=!=0,Exit[1]];
