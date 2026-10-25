# VM-1B experiment ledger — prospective record

**Design commit required before code.** [Gate A](VM1B_GATE_A.md), [SYSTEM](VM1B_SYSTEM.md), [DATA](VM1B_DATA.md), Core issue [#200](https://github.com/ryonakayama234/morphoacoustics/issues/200).

| ID | Manipulation | Independent control | Falsifier / failure result |
| --- | --- | --- | --- |
| B0 | frozen Exp028 body digest | exact Git blob SHA1; same areas M0/M1, distinct section length | hash mismatch or masked invalid area → FAIL |
| B1 | M0/M1 + ideal matched, 0.30s | 16-section matrix separate from waveguide | any full complex HpU,Zin,HU rel_err > 1e-9 → FAIL |
| B2 | same + discrete B0 0.30s | exact discrete shunt admittance, not hand-selected impedance | any full complex rel_err > 0.002 → FAIL |
| B3 | B0 0.60s vs 0.30s | identical initial conditions, native clock, geometry, source | truncation errors not decreasing or >1e-5 at 0.60s → FAIL |
| B4 | n=2,4,8 at exact 100/600 | continuous B0 R+inertance analytical limit | complex-convergence monotonicity fails → FLAG |
| B5 | incorrect model / silent source | matched substituted for B0; zero pulse; modified geometry | wrong law accidentally accepted as B0 → FAIL |
| B6 | exact software/physics provenance | per-tick original native energy ledger, source/hash/units | missing/false origin → FAIL |

**Status at preregistration:** no GitHub code or CI results are claimed. Results must be appended after actual execution with exact-head CI run, artifact SHA and review status. Preliminary **local** mathematics / prototype was used to assess prospective engineering tolerances; confirmatory CI is not independent of that exploratory tuning. No listener WAV and no quality GO, no renderer acceptance, no Studio change.

**Candidate outcome labels (not predecided):** `NUMERICALLY_CONSISTENT_WITH_DECLARED_B0`, `FAIL_NUMERICAL_REFERENCE`, `INDETERMINATE_REAL_RADIATION`. All accepted calculations remain research-only until Gate C and independent review.