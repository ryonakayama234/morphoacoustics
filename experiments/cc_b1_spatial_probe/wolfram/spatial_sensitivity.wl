(* CC-B1 POST-HOC location exploration. Not a prospective Gate B oracle.
   Independent 16-section, 10 mm each, rigid serial acoustic tube,
   sound speed 343 m/s, rho=1.2 kg/m3, ideal p_out=0.
   Section numbers increase from glottis toward lips, zero-based 0..15.
*)
Module[{diam,area,x,delta,final,mat,z,peak,freq1,freq2,rows},
 diam={12,12,26,16,12,14,20,26,30,34,38,34,34,30,28,32};
 area=Pi (N[diam]/2000.)^2;
 x=N[Range[0,15]/15];
 delta=2*1.5*(.5921764128805103 Exp[-(x-.3424849103873983)^2/(2*.16^2)]-
 .9235962908995712 Exp[-(x-.7167402543883221)^2/(2*.16^2)]-
 .04495226070116771 Exp[-(x-1)^2/(2*.10^2)]);
 final=area Exp[delta];
 mat[f_,areas_]:=Fold[Dot,IdentityMatrix[2],
  Table[With[{phase=2 Pi f*.01/343.,ze=1.2*343./areas[[j]]},
   {{Cos[phase],I ze Sin[phase]},{I Sin[phase]/ze,Cos[phase]}}],{j,16}]];
 z[f_,areas_]:=With[{m=mat[f,areas]},Abs[m[[1,2]]/m[[2,2]]]];
 freq1=N[Range[205,355,5]];freq2=N[Range[1800,2440,5]];
 peak[areas_]:={
  freq1[[First[Ordering[z[#,areas]&/@freq1,-1]]]],
  freq2[[First[Ordering[z[#,areas]&/@freq2,-1]]]]};
 rows=Table[With[{minus=ReplacePart[final,j->final[[j]]*.9],
  plus=ReplacePart[final,j->final[[j]]*1.1]},
  With[{a=peak[minus],b=peak[plus]},<|
   "zero_based_site"->j-1,"minus_f1_hz"->a[[1]],"plus_f1_hz"->b[[1]],
   "minus_f2_hz"->a[[2]],"plus_f2_hz"->b[[2]],
   "f1_span_hz"->Abs[a[[1]]-b[[1]]],
   "f2_span_hz"->Abs[a[[2]]-b[[2]]]|>]],{j,1,16}];
 <|"baseline_end_peaks_hz"->peak[final],
  "posthoc_warning"->"SITES CHOSEN AFTER INSPECTING THESE RESULTS",
  "grid_step_hz"->5,"results"->rows|>
]