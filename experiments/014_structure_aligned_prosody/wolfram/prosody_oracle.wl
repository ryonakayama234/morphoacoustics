Module[
  {
    base = 100.,
    semitone = 0.6,
    nominal = 0.05,
    scale = 1.2,
    earlyN = 3,
    lateN = 5,
    totalUnits = 8,
    activeStart = 0.05,
    activeEnd = 0.45,
    lowF0,
    highF0,
    targetUnit,
    earlyRest,
    lateRest
  },
  lowF0 = base 2^(-semitone/12);
  highF0 = base 2^(semitone/12);
  targetUnit = nominal scale;
  earlyRest =
    ((activeEnd - activeStart) - nominal (earlyN - 1) - targetUnit)/
      (totalUnits - earlyN);
  lateRest =
    ((activeEnd - activeStart) - nominal (lateN - 1) - targetUnit)/
      (totalUnits - lateN);

  Export[
    "prosody_oracle.json",
    <|
      "nominal_unit_s" -> nominal,
      "early_nominal_boundary_s" -> activeStart + earlyN nominal,
      "late_nominal_boundary_s" -> activeStart + lateN nominal,
      "duration_scale" -> scale,
      "target_unit_s" -> targetUnit,
      "early_post_boundary_unit_s" -> earlyRest,
      "late_post_boundary_unit_s" -> lateRest,
      "early_realized_boundary_s" ->
        activeStart + (earlyN - 1) nominal + targetUnit,
      "late_realized_boundary_s" ->
        activeStart + (lateN - 1) nominal + targetUnit,
      "active_duration_s" -> activeEnd - activeStart,
      "low_f0_hz" -> lowF0,
      "high_f0_hz" -> highF0,
      "reset_hz" -> highF0 - lowF0,
      "binomial_ge_7_of_8" ->
        N[Sum[Binomial[8, k], {k, 7, 8}]/2^8],
      "absolute_tolerance" -> 10^-12
    |>,
    "RawJSON"
  ]
]
