(* EL-R1 audit amendment A1: complete 36-fixture golden regeneration.
   Execute: wolframscript -file wolfram_oracle_36.wl > regenerated.json
   Comparison: python verify_wolfram_oracle_36.py regenerated.json
   At f=0 the power column is a formal phasor limit, NOT physical DC power. *)
Print[Module[{gam,q,h,g,p,rows,data},gam[r_]:=(r-1)/(r+1);q[f_,l_]:=Exp[-I 2 Pi f l/343];h[f_,l_,r_]:=With[{qq=q[f,l],gg=gam[r]},qq (1+gg)/(1+gg qq^2)];g[f_,l_,r_]:=gam[r]q[f,l]^2;p[f_,l_,r_]:=Abs[h[f,l,r]]^2/(2r);rows=Flatten[Table[With[{hh=h[ff,ll,rr], gg=g[ff,ll,rr],pp=p[ff,ll,rr]},{N[ll],N[rr],N[ff],N[Re[hh],17],N[Im[hh],17],N[Re[gg],17],N[Im[gg],17],N[pp,17]}],{ll,{2/100,25/1000,3/100}},{rr,{1/2,1,2}},{ff,{0,1000,3000,7000}}],2];data=<|"model"->"wolfram-el-r1-full-grid-36-v1","columns"->{"length_m","load_ratio","frequency_hz","transfer_real","transfer_imag","reflection_real","reflection_imag","normalized_formal_phasor_power"},"rows"->rows|>;ExportString[data,"RawJSON","Compact"->True]]];
