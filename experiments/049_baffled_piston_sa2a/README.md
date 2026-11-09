# Experiment 049 / SA-2A: baffled-piston physical radiation boundary

**RESEARCH ONLY / NOT_ADOPTED.** Preregistered at commit [38f27596](https://github.com/ryonakayama234/morphoacoustics/commit/38f27596b91c47f7307d34af225f8293afb6268a), before implementation. Follow [SA-2 issue #171](https://github.com/ryonakayama234/morphoacoustics/issues/171) and [Draft #172](https://github.com/ryonakayama234/morphoacoustics/pull/172). Read [SYSTEM](../../docs/research/sa-2/SYSTEM.md) and [EXPERIMENT](../../docs/research/sa-2/EXPERIMENT.md).

This experiment implements a canonical *flanged circular aperture / baffled uniform piston* with a single physics family for the **lip load** (Bessel/Struve radiation resistance/reactance) and **exterior far-field pressure** (hemisphere Rayleigh radiation / circular piston directivity). It does not model a human mouth, unflanged duct, near-field microphone, head/body baffle or vocal-fold self-oscillation.

Independence tests:

- normalized closed-form radiation impedance p_lip/U_lip against *separate Rayleigh disk-overlap distance quadrature* (not implemented using special functions);
- real port radiated power against integral of the *same baffled piston far-field over a hemisphere*, with the physically necessary 2π rather than unrelated 4π geometry;
- low-ka limits, passive real impedance, conjugate symmetry, area conversion between mechanical F/v and acoustic p/U;
- exact frozen CC-A2 M0 prepared body after SV-1 preflight, actual legacy lossy tube 2×2 transfer, phasor port relations and separate legacy Exp009 observer comparison. No waveform re-rendering at SA-2A (complex-frequency steady-state only).

Research-only SciPy dependency is deliberately installed in the SA-2A workflow rather than added to the public Core package. Existing public Core/Studio, SMC, ASMR, JET-P0 and SA-1 artifacts and acceptance criteria stay unchanged.

The experiment refuses overwriting an existing evidence output directory. Example for WSL2/Linux prepared checkout:

```bash
python -m pip install -e '.[dev]'
python -m pip install scipy
python -m pytest -q tests/test_experiment_049_sa2a.py
python experiments/049_baffled_piston_sa2a/run.py --out /tmp/sa2a-fresh
```

The manifest contains raw frequency arrays and SHA256 checksums but reports code provenance from GitHub Actions exact-run receipt, not an embedded placeholder. SA-2A numerical PASS is not SA-2B verified **causal time-domain** positive-real termination. In particular, do not IFFT this impedance, apply post-WAV EQ or claim physically valid FSI or natural voice from a frequency-domain test.
