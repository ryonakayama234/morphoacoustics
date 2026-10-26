# Experiment 050: SA-2B/B0 passive causal aperture radiation

**RESEARCH ONLY / NOT ADOPTED.** Strict Gate A frozen [64a11695](https://github.com/ryonakayama234/morphoacoustics/commit/64a116950117a161f69b1b9831c733b9343db444) before code. Issue [#173](https://github.com/ryonakayama234/morphoacoustics/issues/173). Draft PR [#176](https://github.com/ryonakayama234/morphoacoustics/pull/176).

This standalone experiment tests a **small-signal acoustic radiation one-port**, not a voice generator. The flanged circular-baffle acoustic load consists of physical parallel radiation inertance M and resistor R, both derived from genuine lip area, air density and sound speed. An incident pressure wave enters a causally updated **midpoint** state machine; it returns reflected pressure wave, signed pressure/volume-flow power, stored inertial energy, and energy dissipated at R.

The independent physics test gates compare:
- same-step wave work = Δ stored energy + resistor dissipation, including stored-state discharge;
- complex digital reflection transfer against independent state-space formula and measured sine responses (200, 1000, 2600Hz);
- continuous vs discrete (48/96k) sampling phase warping;
- frequency model approximation error relative to SA-2A Bessel/Struve analytic model (two distinct budgets);
- genuine CC-A2 M0 prepared 16-section body vs invented calibration aperture sizes, morphology derived coefficients and equal-incoming-power control;
- zero, impulse, signed alternating pulses, seeded broadband incident pressure waves, nonzero stored energy, non-physical geometry rejection and 3000Hz OUT-OF-DOMAIN label for M0.

For WSL2/Linux in a checkout:
~~~bash
python -m pip install -e '.[dev]'
python -m pip install 'scipy>=1.11,<2'
python -m pytest -q tests/test_experiment_050_sa2b_b0.py
python experiments/050_b0_passive_radiation/run.py --out /tmp/sa2b-b0-fresh
~~~

The research-only SciPy dependency is not added to the public Core package. The evidence manifest embeds array SHA256 and frozen source refs. Only the **separate GitHub Actions exact-GITHUB_SHA receipt** is executed source provenance. Output directories cannot be overwritten. All field traces are **physical pressure and volume flow at the lip port**, not observed air pressure at the listener or mastered WAVs.

**Pass means SA2B_BOUNDARY_VERIFIED_DUCT_PENDING only.** A positive-real one-port is not yet coupled to the vocal-tract PDE; B1/B2/B3, a physical far-field observer, VF-1 self-oscillation, Studio release and full humanlike voice remain unimplemented.
