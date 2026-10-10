# Experiment 031 — prescribed-area glottal flow with passive acoustic load

Research-only implementation for [Core Issue #78](https://github.com/ryonakayama234/morphoacoustics/issues/78). The fixed plan in [PREREGISTRATION.md](PREREGISTRATION.md) was committed **before** the code. No production integration, no real vocal tract propagation, no WAV, no human-voice quality claim.

## Reproduce (WSL2 / Linux, Python >=3.11; standard library only)

From repository root:

```bash
python -m unittest discover -s experiments/031_glottal_load_feedback -p 'test_*.py' -v
python experiments/031_glottal_load_feedback/run.py --output-dir /tmp/exp031-sfi1
```

The first command tests an independent Wolfram oracle, energy budget (open, closed, forward and reverse driving), input rejection, negative controls, upstream flow intervention and time-step convergence. The second writes four full-resolution traces plus summary.json outside the tracked source tree. Each CSV includes A(t), Psub(t), upstream U(t), chamber p(t), and explicit energy terms. Optional --output-dir (without it the program prints a summary only). Exit 1 signals that at least one eligible prespecified gate failed. No audio normalization or output filtering takes place.

## Physical meaning

glottal_valve.py specifies the **area**, not the volume-velocity pulse. passive_load.py simultaneously advances U and p by backward Euler. For A>0:

```text
I dU/dt = Psub - Rg*U - [rho/(2*Cd^2*A(t)^2)]*U*abs(U) - feedback*p
C dp/dt = U - p/Rout
```

feedback=0 is an intentionally nonreciprocal **negative control**: chamber pressure continues to evolve but is excluded from the glottal equation. feedback=1 returns backpressure, making a truly bidirectional lumped flow–pressure coupling. At exactly zero area, the ideal valve projects U to zero, explicitly accounting for its lost kinetic energy as a separate contact/projection term; this is NOT a tissue contact model.

The chamber has a single compliance and outlet resistance, **not** standing-wave formants, geometry-derived input impedance, physical lip radiation, vocal fold self-oscillation or body-specific morphologies. The coefficients are exploratory, not calibrated measurements.

## Independent review

- wolfram/independent_oracle.wl derives exact steady and single-step solutions and verifies symbolic open/closed backward-Euler energy identities without calling Python.
- wolfram/oracle.json is the numeric Wolfram reference evaluated on 2026-10-10.
- test_model.py compares four one-step Python results with Wolfram and tests refinement at 24/48/96 kHz.
- RESULTS.md records the pilot, unsupported capabilities and next gates.

Next milestone (not included here): a separately verified passive *time-domain segmented waveguide or PDE acoustic backend* coupled to the valve. Existing windowed FFT transfer functions are not such a bidirectional acoustic state.
