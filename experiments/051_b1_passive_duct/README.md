# Experiment 051: B1 passive lossless 1D acoustic duct

**Research-only / not adopted.** [Frozen Gate A](../../docs/research/sa-2b-b1/GATE_A.md), commit `0241f5f2439e11fc6c9a7352af3a8a450dca2f94`, registered before B1 implementation. [Issue #177](https://github.com/ryonakayama234/morphoacoustics/issues/177).

This module numerically solves sound pressure/volume flow inside one uniform rigid lossless duct using an energy-preserving finite-volume/port-Hamiltonian formulation and implicit-midpoint time update. It connects the **unaltered** experiment 050 causal B0 mouth termination as a physical p/U one-port, or substitutes explicit closed and matched controls.

It is **not** a genuine 16-section M0 time simulation (B2), not VF-1 vocal-fold self-excitation, not a WAV/speaker API, not a Studio asset, and not evidence of good timbre.

```bash
python -m pip install -e '.[dev]'
python -m pip install 'scipy>=1.11,<2'
python -m pytest -q tests/test_experiment_050_sa2b_b0.py tests/test_experiment_051_sa2b_b1.py
python experiments/051_b1_passive_duct/run.py --out /tmp/sa2b-b1-fresh
```

No arbitrary DSP, no hard-rounded physical lengths; validated 48k/96k/192k geometry resolutions are explicit. The physical trace `.npy` values remain in Pa, m³/s and J. Re-running into an existing directory is refused. A manifest SHA is **not** a substitute for a trusted exact source GitHub Actions run and independently downloaded artifact.

See [SYSTEM](../../docs/research/sa-2b-b1/SYSTEM.md), [DATA](../../docs/research/sa-2b-b1/DATA.md), [EXPERIMENT](../../docs/research/sa-2b-b1/EXPERIMENT.md), and [INDEX](../../docs/research/sa-2b-b1/INDEX.md). B1 PASS, if achieved, only allows beginning B2 validation; user-facing claims require later source, radiated observation and listening tests.
