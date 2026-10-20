(* OG-AUD1 off-anchor FFT-bin Wolfram global oracle. EXPLORATORY ONLY. *)
(* Requires companion Experiment 043 and does not call OG-4's adopted 8-point API. *)
here = DirectoryName[$InputFileName];
Get[FileNameJoin[{here,"..","043_og_aud1_preflight","global_oracle.wl"}]];
(* Origin scalar and 12x12 global equations retained unchanged in Experiment 043. *)
bins = {0,912,2000,3000,6000,10000};
areas = {.00015,.0006};
data = Table[
 With[{f=N[k*48000/131072,16],g=ogaudGlobal[a,N[k*48000/131072,16]]},
  {a,k,f,N[Re[g["Zin"]],13],N[Im[g["Zin"]],13],
   N[g["NormalizedMatrixCond2"],8],N[g["GlobalVsScalarRelError"],8]}],
 {a,areas},{k,bins}];
data
