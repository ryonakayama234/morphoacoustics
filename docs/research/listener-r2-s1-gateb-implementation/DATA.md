# DATA — computed SI port records and oracle coverage

Primary A x L x f = 2 x 3 x 3 = **18 synthetic model cases**: A={3e-5,6e-5}m², L={.020,.025,.030}m, f={1000,3000,7000}Hz, rho=1.21kg/m³, c=343m/s, ps=1+0iPa peak, **fixed absolute** Zs=13834333.333333334 and Zt=27668666.666666668 Pa·s/m³.

**Solution quantities** `p0,U0,pL,UL` are complex port states; **derived quantities** `Zc,Zin,Gamma_in,H_drive,H_canal,H_total`, source/entrance/terminal/source-loss powers, two residuals, determinant, numerical denominator diagnostics; **provenance** exact Gate A head, SHA-pinned WL/JSON Git blobs, SHA256 Core primitive, runtime version. These are computed, not physically measured.

Frozen Wolfram JSON has ordered columns: `area_m2,length_m,frequency_hz,terminal_pressure_real_pa,terminal_pressure_imag_pa,entrance_pressure_real_pa,entrance_pressure_imag_pa,source_mean_power_w,terminal_mean_power_w,source_resistor_dissipation_w`. It **does not** contain independently calculated U0,UL,Pentrance or H factorization; verify these with source/terminal/matrix boundary residuals and power conservation. All complex values serialized as finite `[real,imag]`, SI units in field names; no dBFS/audio-normalization.

`source_reference_plane=SOURCE_EQUIVALENT` is **virtual**; `entrance_plane=CANAL_ENTRANCE`, `terminal_plane=TERMINAL_SIDE`. `phasor=peak_exp_plus_iwt`, `positive_u=entrance_to_terminal`. `source_calibration=NUMERIC_EQUIVALENT_FIXTURE_NOT_EMPIRICAL`.

Error taxonomy: malformed/nonfinite/bools/invalid sign => INVALID; physically meaningful excluded reactive load, f=0, out-of-model frequency/geometry, small-signal guard violation => UNSUPPORTED; unresolvable finite numeric calculation => NUMERICALLY_UNRESOLVED. Valid zero drive solves zero ports/powers with undefined transfer ratios represented by null. Distinguish input status from scientific PASS/FAIL. No motor `INFEASIBLE` classification.

`run.py` writes 18 full serializable typed rows and a summary with discrepancy maxima and row-scoped failures. SHA pin failure stops the runner before science verdict; oracle alteration is not a data point to quietly relabel.