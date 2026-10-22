(* Ideal two equal-length lossless ducts, terminal pressure release.
   Independent symbolic sanity check; NOT the audited 16-tube Core solver. *)
Clear[c, len, a1, r, f];
c = 343; len = 8/100; a1 = 3/10000;
f[q_] := c/(2 Pi len) ArcTan[Sqrt[q]];
r = {9/10, 1, 11/10};
<|
  "ratios" -> r,
  "resonanceHz" -> N[f /@ r, 16],
  "ordered" -> And @@ Thread[Differences[N[f /@ r]] > 0],
  "modelScope" -> "Ideal lossless two-tube sanity only; not real 16-section pressure, voice quality, or ABX"
|>
