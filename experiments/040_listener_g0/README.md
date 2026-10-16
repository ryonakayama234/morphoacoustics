# Experiment 040 — EL-G0 independent binaural reception null

**Status: research-only, no ListenerSpec/InteractionScene API, no human or ASMR claims.** Tracks [Issue #113](https://github.com/ryonakayama234/morphoacoustics/issues/113). This is an independently calibrated ideal monopole and two mathematical pressure probes. Scope originates in parked [PR #83](https://github.com/ryonakayama234/morphoacoustics/pull/83), especially EL-H01/H02 and NF-0.

## Reproduce (WSL2/Linux/bash, Python >=3.11)

```bash
python -m pip install -e '.[dev]'
python -m pytest tests/test_experiment_040_listener_g0.py -q
python experiments/040_listener_g0/run.py --output /tmp/EL-G0-$(date +%s)/RESULTS.json
```

Use a new output path. The runner refuses to overwrite an existing evidence file. It has no external library dependency. Its JSON includes fixture, units, phasor pressures, source file SHA-256, gate checks and strict claim limit.

## Physics and sign convention

```text
source volume velocity Q(f) [m^3/s]
    |
    v
outgoing 3D free-space monopole, time factor exp(+i omega t)
    |
    +--> left point probe pL(f), travel time rL/c
    |
    +--> right point probe pR(f), travel time rR/c
                 |
                 v
      delay R-L [s], level R/L [dB]
```

`p=i omega rho Q exp(-i k r)/(4 pi r)`, `k=omega/c`. This is ideal unbounded linear acoustic theory, not a near-contact HRTF. The observation points represent receiver probes only; do not call them measured ears or eardrums.

## Gate and interpretation

Consult [frozen preregistration](../../docs/research/listener-g0/PREREGISTRATION.md) **before** inspecting outcome. The gate is only for a correct analytic null implementation, not for validation against a human ear. See [RESULTS](../../docs/research/listener-g0/RESULTS.md), [system diagrams](../../docs/research/listener-g0/SYSTEM.md), and [data schema](../../docs/research/listener-g0/DATA.md).

The earliest recorded modeling correction was the written phasor-time convention: the physical formula exp(-ikr) with prefactor +i omega requires time factor exp(+i omega t). This labeling defect was corrected before any claimed execution result; the formula itself and frozen numeric oracle were unchanged.
