(* SMC-2 exact rational timing oracle. Numeric fixture, not validated Japanese. *)
ClearAll[d, overlap, t0, onsets, offsets, contradiction, checks];
d=9/50; overlap=3/50; t0=2/25;
onsets=Table[t0+(i-1)(d-overlap),{i,1,4}];
offsets=onsets+d;
contradiction=Reduce[{x==y+d-overlap,x==y+d},{x,y},Reals];
checks=<|"onsets"->(onsets==={2/25,1/5,8/25,11/25}),
"offsets"->(offsets==={13/50,19/50,1/2,31/50}),
"duration"->(offsets-onsets===ConstantArray[d,4]),
"overlap"->(Most[offsets]-Rest[onsets]===ConstantArray[overlap,3]),
"contradiction"->(contradiction===False)|>;
Print[checks];
If[!And@@Values[checks],Exit[1]];
