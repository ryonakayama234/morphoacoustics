# B1 Gate A1: numerical energy residual is compared with existing stored energy
2026-10-24 JST. **POST-FAILURE PROSPECTIVE AMENDMENT / NOT RETROACTIVE PASS**.

Original immutable [Gate A](GATE_A.md) was committed at 0241f5f2439e11fc6c9a7352af3a8a450dca2f94 before any B1 implementation. First implemented source commit 37065f57bf41275e484237c9573859f055e6fe06, [failed CI #40084580650](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40084580650), ran 49 tests, **two failed**: closed-end acoustic residual test after incident drive stopped and whole experiment artifact test importing that same energy gate. Original fixed gate #3 FAILED, no outcome was promoted. The original run's 0 drive and finite stored energy gives work=loss=0, yet its threshold was 1e-8*1e-20=1e-28 J per sample. Rounding at order 1e-25 J is expected when storing finite acoustic energy around 1e-12 J; a state energy-independent absolute zero-work denominator is not a valid precision specification for a long-running conservative floating-point scheme. Both failed tests and job logs remain evidence.

Before modifying code following this amendment, freeze an *additional* A1 numerical gate, deliberately replacing ONLY original gate #3 precision denominators, not its physical equality, passivity, material coefficients or other seven gates. Each step:
 residual = (E_next-E_previous) - inlet_work + terminal_dissipation, using **independently computed state-weighted quadratic energy**; no 'force balance to zero' renormalization or postprocessing.
 |residual| <= max[ 1e-8*max(|ΔE|,|work|,|loss|,1e-20 J), 1e-12*max(E_prev,E_next,1e-20 J) ].
 Cumulative |sum residual| <= max[ 1e-8*max(sum|work|+sum|loss|,1e-20 J), 1e-10*max(E_initial,max E_trace,1e-20 J) ].
 Retain separate closed zero-drive 1000-step total-E relative drift <=1e-8 and matched/B0 monotonic E within original tolerance. Run **the original 1e-6 m3/s signed pulse amplitudes unchanged**, not selectively reduce excitation to exploit numerical floors. Gate A1 does NOT weaken error tolerances for complex H, modal dispersion, B0 original step, or negative controls.

Future source and CI must distinguish:
- `GATE_A_INITIAL_FAILED`: original gate #3 numerical denominator at initial source, immutable record.
- `GATE_A1_CORRECTED_NUMERIC_ACCEPTANCE`: engineering pass only after independently executed checks on amended code; **not** a claim that original Gate A passed.
- `B1_DUCT_PASSIVE_PROPAGATION_VERIFIED` scientifically requires independent audit of both failure rationale and re-run raw data, beyond CI tests. No main merge, Studio or voice quality claim under A1 alone.
