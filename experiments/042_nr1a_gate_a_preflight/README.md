# Experiment 042 — NR-1a Gate A mutant-detectability preflight

**Status: EXPLORATORY / PRE-GATE-A / NOT CONFIRMATORY / NOT ADOPTED.**

This instrument prepares a reviewer-inspectable pre-registration for [NR-1a #118](https://github.com/ryonakayama234/morphoacoustics/issues/118). It is NOT the new, preregistered confirmation run (Gate B). Previous [Experiment 041](../041_nr1_static_oral_nasal_route/) N/O/M outputs remain exploratory and are not reused as confirmatory results.

```mermaid
flowchart LR
 Fixed["Frozen-candidate A/B/C 3-tube fixture"] --> Matrix["12 complex unknowns: dimensionless global matrix"]
 Matrix --> Base["Candidate correct physical law"]
 Matrix --> Mut["5 candidate wrong physical laws"]
 Base --> Compare["State-deviation margin per case × frequency"]
 Mut --> Compare
 Compare --> Review["Critical Gate A review; do NOT auto-accept"]
```

## Instrument inventory
- [preflight.py](./preflight.py): stand-alone NumPy 12×12 linear-equation assembly, 3 cases × 8 frequency anchors × 5 **law-level** mutants. It does not import Core or the archived Wolfram goldens. Test-only diagnostics; it is *not* an independent golden oracle for the future Gate B.
- [wolfram_preflight.wl](./wolfram_preflight.wl): Wolfram Language 12-state assembly with exact rational geometry and 35-digit preparation. It was evaluated separately through the Wolfram connector on 2026-10-17, and the aggregate 24×5 candidate margins agreed with local Python. It is not run in hosted CI, nor is the tool-result output itself an immutable scientific receipt.
- [Python tests](../../tests/test_experiment_042_nr1a_preflight.py): 24-fixture structural checks, actual matrix law mutations (not only corrupting output), preserved reactive closed distal branch, 733 Hz historical powers and independently scoped M quarter-wave local-pole check.

## Running as a design preflight
```bash
python -m pytest tests/test_experiment_042_nr1a_preflight.py -q
python experiments/042_nr1a_gate_a_preflight/preflight.py --output /tmp/nr1a-gate-a-exploratory.json
wolframscript -file experiments/042_nr1a_gate_a_preflight/wolfram_preflight.wl
```

Do not label the generated JSON a prospective Gate B receipt. External Wolfram requires a locally accessible licensed Wolfram runtime; hosted CI does not silently supply one.

## Raw exploratory observations (not preregistered thresholds)
The two independently programmed linear systems agreed on 2026-10-17:
- Maximum 2-norm global matrix condition among all 24 correct fixtures: **~354.604480860**.
- Minimum (across 24) max-component dimensionless state deviation per mutant:
  - `tube_sign_A`: **~0.1692590094**, O at 80 Hz
  - `phasor_sign`: **~0.3008534468**, O at 80 Hz
  - `junction_particle_velocity`: **~0.04653672882**, N at 80 Hz
  - `wrong_B_terminal`: **~0.7881360092**, O at 400 Hz
  - `wrong_C_terminal`: **~0.3603832285**, N at 80 Hz
- Mouth-closed B quarter-wave local admittance pole (952.7777778 Hz) is **not** a singular global 12×12 system in this frozen fixture; independent Wolfram global condition ~**74.839905915**.
- Machine-precision local Python test run: **8 passed**. This is a local exploratory tool test, not the GitHub exact-HEAD CI verdict.

The scales are **p_ref=1.372 Pa** and **U_ref=1e-6 m³/s**; the recorded margin is the largest absolute difference among all twelve dimensionless complex state entries. This is *not* a relative error ratio and not a proof of mutant detectability for other geometries or frequencies. The `phasor_sign` mutant flips propagation phases but keeps the prescribed complex inlet U unchanged. A true test of the mean-power formula and mutation of stale provenance remain to be preregistered separately (the 041 tests currently contain exploratory examples).

## Reviewer decision still required
Before Gate B:
1. Freeze complete mutant inventory, exact matrix injection loci and expected case×frequency detection bounds; justify any insensitive points rather than exclude them.
2. Approve forward-error tolerances **independently** of exploratory observations, global-condition and fail-closed numeric rule.
3. Freeze raw exact-HEAD Wolfram reproduction receipt and two independent trial receipt formats.
4. Conduct distinct physics/numerical and code/API reviews. Only a written Gate A acceptance permits a new confirmatory Gate B execution.

No public OG-4 capability, real velopharyngeal port disconnection, voice, waveform or Studio API is created here.
