(* SFI-3 Experiment 033, independent one-cell and symbolic strong coupling
   computed 2026-10-11 by Wolfram kernel, not Python code. *)
ClearAll["Global`*"];
rho = 121/100; sound = 343; tractArea = 3/10000; dx = 17/1000;
dt = 1/48000; glottalInertia = 1200; rg = 1500000;
glottalArea = 3/100000; cd = 7/10; pDrive = 800;
z = rho sound/tractArea;
faceMass = rho dx/(2 tractArea);
cellC = tractArea dx/(rho sound^2);
outletBeta = 1/(2 faceMass/dt + z);
(* The 1-cell tridiagonal midpoint acoustic model:
   pMid=UinMid/(2 C/dt + beta) at zero initial state.
   inlet port adds M0*(Unew-Uold)/dt. *)
portSlope = faceMass/dt + 1/(2*(2 cellC/dt + outletBeta));
bern = rho/(2 cd^2 glottalArea^2);
coefficient = glottalInertia/dt + rg/2 + portSlope;
quadratic = bern/4;
flowNew = 2 pDrive/(coefficient + Sqrt[coefficient^2 + 4 quadratic pDrive]);
flowMid = flowNew/2;
pressureMid = portSlope flowNew;
(* Energy proof uses previously independent exact Exp032 port identity.
   Glottal E+tract E changes under shared midpoint port. *)
x = (uOld + uNew)/2;
eGlChange = ig/2*(uNew^2-uOld^2);
eTrChange = h*(port*x-load*uOut^2);
eTotalChange = eGlChange + eTrChange;
powerBalance = h*(psub*x - rGl*x^2 - bGl*Abs[x]^3-load*uOut^2);
glEq = ig*(uNew-uOld)/h + rGl*x + bGl*x*Abs[x]+port;
energyResidual = FullSimplify[
  (eTotalChange - powerBalance) /. psub -> glEq,
  Assumptions -> {uOld \[Element] Reals, uNew \[Element] Reals,
    port \[Element] Reals, uOut \[Element] Reals, h > 0,
    ig>0, rGl>=0, bGl>=0, load>=0}
];
Print[InputForm[<|
 "one_cell_port_slope"->N[portSlope,17],
 "one_cell_first_flow_new"->N[flowNew,17],
 "one_cell_first_flow_mid"->N[flowMid,17],
 "one_cell_first_port_pressure_mid"->N[pressureMid,17],
 "one_cell_scalar_equation_residual"->N[coefficient*flowNew+quadratic*flowNew^2-pDrive,18],
 "coupled_midpoint_energy_residual"->energyResidual,
 "port_slope_strictly_positive"->TrueQ[portSlope>0]
|>]];
