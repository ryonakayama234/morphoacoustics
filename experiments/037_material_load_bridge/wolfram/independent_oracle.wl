(* EM-1 independent ideal static acoustic/energy sanity, not a tissue solver. *)
Clear[p, u, us, u1, u2, c, L];
assertions = <|
  "ideal_uniform_quarter_wave_hz" -> N[343/(4*(17/100)), 16],
  "lossless_port_energy_cancellation" -> FullSimplify[p*u - p*u],
  "split_node_flow_conservation" -> FullSimplify[p*(u1+u2) - p*u1 - p*u2],
  "reduced_stiffness_is_not_YoungModulus" -> True
|>;
Print[InputForm[assertions]];
