# EL-R1 Gate B — research-only listener acoustic port

Not a production runtime, user-ear simulation, synthesizer, SOFA HRTF processor or Studio component. See [research INDEX](../../docs/research/listener-r1/INDEX.md) and preregistered [EXPERIMENT](../../docs/research/listener-r1/EXPERIMENT.md), tracker [#152](https://github.com/ryonakayama234/morphoacoustics/issues/152).

## Physics
Reuse existing Core UniformTube **unchanged** for a rigid-wall, lossless, 1D plane wave tube. One entrance total-pressure phasor is prescribed, while its volume velocity is solved using a finite positive resistive terminal load. Results report **both** reference planes' complex peak phasors p [Pa], U [m³/s], input impedance, reflection and mean active power [W]. Determinant/passivity checks are implemented; tested against **independent traveling-wave Wolfram** results.

## Run (Python 3.11+, bash or WSL2)
~~~bash
python -m pip install -e '.[dev]'
python experiments/043_el_r1_ear_port/run.py > /tmp/el-r1.json
python experiments/043_el_r1_ear_port/run.py --length-m 0.02 --load-ratio 1 --frequencies-hz 0,1000,3000 > /tmp/el-r1-matched.json
python -m pytest -q tests/test_experiment_el_r1.py
~~~

## Audit / reproduction
- Wolfram Language code: [wolfram_oracle.wl](./wolfram_oracle.wl)
- Frozen numeric output: [wolfram_oracle.json](./wolfram_oracle.json), derived from independent traveling-wave expression.
- The numeric oracle checks 9 combinations of L={.02,.025,.03} m and R={.5,1,2} at 3000 Hz, with fixture c=343 m/s, rho=1.21 kg/m³ and A=3e-5 m²; additional tests cover 0/1000/3000/7000 Hz, energy, matched load, input errors and phase mutations.
- Version and independent source fixture recorded in JSON with a canonical SHA-256. No waveform or real measured human-ear calibration is claimed. The 8000 Hz software limit is a research guardrail, not a physiology validation.
- Synthetic standing-wave terminal pressure gain **does not** imply net energy gain.

## Post-audit A1 amendment
Research result schema **el-r1.passive.uniform.v0a1** explicitly distinguishes f=0 mathematical limit from physical AC mean power (null at DC), and enforces the declared engineering small-signal pressure envelope. The **total-pressure** source boundary is not an incident-wave or external sound field source. See [audit A1](../../docs/research/listener-r1/AUDIT-AMENDMENT-A1.md), [36-case Wolfram generator](./wolfram_oracle_36.wl), [frozen numerical oracle](./wolfram_oracle_36.json) and [regeneration verifier](./verify_wolfram_oracle_36.py). All A1 tests are post-registration.
