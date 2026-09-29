(* Independent oracle for Experiment 009.
   This deliberately uses the closed-form uniform-tube denominator rather than
   reproducing the Python segmented-matrix loop. *)

c = 343.;
rho = 1.21;
area = 3.*10^-4;
len = 0.17;
alpha = 0.4;
loadFraction = 0.05;
zc = rho c/area;
zl = loadFraction zc;

h[f_?NumericQ] := 1/(
  Cos[(2 Pi f/c - I alpha) len] +
  I (zl/zc) Sin[(2 Pi f/c - I alpha) len]
);

grid = Table[{f, Abs[h[f]]}, {f, 100., 5000., 0.25}];
triples = Partition[grid, 3, 1];
maxima = Select[
  triples,
  #[[2, 2]] > #[[1, 2]] && #[[2, 2]] >= #[[3, 2]] &
];
firstFive = Take[maxima[[All, 2]], UpTo[5]];

Export[
  "uniform_reference.json",
  <|
    "frequency_step_hz" -> 0.25,
    "peaks" -> Map[
      <|"frequency_hz" -> #[[1]], "magnitude" -> #[[2]]|> &,
      firstFive
    ]
  |>,
  "RawJSON"
];

firstFive
