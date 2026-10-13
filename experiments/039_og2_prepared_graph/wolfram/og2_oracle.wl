(* OG-2 Experiment 039: independent Wolfram Language oracle.
   Baseline: main@8868df1188443fc4523533c6cb0bb9cd72995c32
   This is not the Python algorithm; exact-rational medium and geometry,
   arbitrary-precision trigonometric evaluation, and dimensionless
   independent 2-port reference, scaled as S T S^-1 with\n   S=diag(1,rho*c/S_A). exp(+i omega t), [p_in,U_in]=T[p_out,U_out].
   The result is ExportString[..., "RawJSON"] and then converted to plain
   JSON finite decimals for the checked-in oracle table. *)
Module[{rho=121/100,c=343,sa=3/10000,sb=6/10000,
  la=8/100,lb=9/100,grid={80,200,400,733,1200,2200,4000},
  ts,matrices,entries,za,zb,reflected,transmitted},
  ts[l_,area_,f_]:=Module[{phase=2 Pi f l/c,rel=sa/area},
    {{Cos[phase],I rel Sin[phase]},{I Sin[phase]/rel,Cos[phase]}}];
  matrices=Table[N[ts[la,sa,f].ts[lb,sb,f],18],{f,grid}];
  entries=Map[Function[m,Map[
    Function[v,{ToString[InputForm[Re[v]]],ToString[InputForm[Im[v]]]}],
    Flatten[m]]],matrices];
  za=rho c/sa;zb=rho c/sb;
  reflected=(zb-za)/(zb+za);transmitted=1+reflected;
  ExportString[
    <|"frequencies_hz"->grid,
      "normalized_ab_mismatch_pU_matrix_rowmajor_re_im_strings"->entries,
      "reflected_pressure"->ToString[InputForm[reflected]],
      "transmitted_pressure"->ToString[InputForm[transmitted]],
      "reflected_power"->ToString[InputForm[reflected^2]],
      "transmitted_power"->ToString[InputForm[(za/zb) transmitted^2]]
      |>,
    "RawJSON"]
]
