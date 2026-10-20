(* Experiment 045 independent analytic-vs-delayed-series check; exploratory *)
ClearAll[closed, echoes, reflect];
z0 = 1.2 343/.0003;
tau = 2 .08/343;
reflect[a_] := Module[{zb=1.2 343/.0003, zc=1.2 343/a, zj},
  zj=1/(1/zb+1/zc); (zj-z0)/(zj+z0)];
closed[a_, f_] := z0 (1+reflect[a] Exp[-I 2 Pi f tau])/
                         (1-reflect[a] Exp[-I 2 Pi f tau]);
echoes[a_, f_, n_:60] := z0 (1+2 Sum[reflect[a]^k Exp[-I 2 Pi f tau k],{k,1,n}]);
Table[{a,N[reflect[a],12],N[closed[a,733],15],
       N[Abs[(closed[a,733]-echoes[a,733])/closed[a,733]],12]},
      {a,{.00015,.0006}}]
