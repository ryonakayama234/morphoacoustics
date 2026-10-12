# Experiment 030 / OG-0 — two organ acoustic port connection

Tracks [Core issue #90](https://github.com/ryonakayama234/morphoacoustics/issues/90). Protocol candidate [Draft PR #91](https://github.com/ryonakayama234/morphoacoustics/pull/91). **Research only, not a Fidelity-0 production API or an adopted scientific conclusion.**

## Hypothesis

Two independently identified rigid, constant-area 1D organ modules A and B, connected through one typed acoustic port edge A.out -> B.in, give the expected lossless serial transfer. The physical connection law is **pressure continuity** and **signed volume-flow conservation**. In common inlet→outlet coordinates both are equal across the edge; its transfer matrix is identity. Never add a second 'area step' scattering matrix: wave reflection arises from distinct `Zc=rho*c/S`.

This experiment reuses existing `morphoacoustics.acoustics.UniformTube` without changing `src/`, `CreatureSpec`, `simulate_snapshot`, Studio or Performance Contract. Only two organs/one junction: **no branching, tissue/FEM/FSI, glottal source, waveform, physical motor task or UI**.

## Reproduce

Run from a checked-out repository with its dev extras installed:

```bash
python experiments/030_og0_passive_port_connection/run.py
pytest -q tests/test_experiment_030_og0.py
```

The runner emits JSON to stdout, including reproducible graph and run identities, numerical errors, explicit acceptance-candidate checks and environment. It never writes output files or changes main.

## Reference conditions (exploratory baseline and post-exploratory amendment)

Independent [Wolfram oracle](../../tests/scientific/oracles/og0_wolfram.json) was computed before experiment implementation; physical/scientific review still pending. A is L=0.08m, S=3e-4m²; B is L=0.09m, S=3e-4m² (identity) or 6e-4m² (mismatch). Air rho=1.2kg/m³, c=343m/s; frequency grid 80/250/400/733/1200/2000/4000Hz; Fourier exp(+j omega t). 

Wolfram yielded first equal-area mode 504.41176Hz and mismatched finite pressure-release input impedance at 733Hz of about `-3.0275149008453414e6j Pa.s/m³`. **Separate** matched-load, local single-junction scattering gives pressure reflection -1/3, reflected power 1/9, transmitted power 8/9. The latter is not the net reflection of the finite pressure-release tube.

For transfer comparisons, non-dimensionalize T by reference impedance; near ideal quarter-wave poles, avoid unbounded Z_in comparisons. Different tests use a pressure-release outlet (input impedance) versus a locally matched outlet (nonzero power/scattering audit). Numerical tolerances in [PR #91](https://github.com/ryonakayama234/morphoacoustics/pull/91) remain proposals until reviewed and fixed.

## Failure semantics and evidence

Incorrect port role/type, missing/duplicated connection, unknown ID, nonpositive dimensional parameter or wrong exterior boundary -> `INVALID`; well-formed additional organ / multi-edge topology -> `UNSUPPORTED`. There is no `INFEASIBLE` physical motor task in this experiment.

### Amendment 01: independent wave oracle (post-exploratory)

The original [Wolfram oracle](../../tests/scientific/oracles/og0_wolfram.json) is preserved unchanged. After the first exploratory CI pass, a physically mistaken protocol description was identified: the pressure-release terminal `p_out=0` has **zero** outgoing mean power and cannot serve as a nonzero-power load fixture. [Draft PR #91 amendment 01](https://github.com/ryonakayama234/morphoacoustics/blob/research/og0-prereg/docs/research/og0-amendment-01.md) explicitly corrects this.

The separately versioned [post-exploratory Wolfram wave oracle](../../tests/scientific/oracles/og0_wave_amendment01_wolfram.json) now tests incident/reflected/transmitted pressure wave states across all seven fixed frequencies and both area-matched/area-mismatched cases, plus an incorrect particle-velocity continuity junction mutation that **must fail**. Independent Wolfram source: [wolfram/og0_oracle.wl](./wolfram/og0_oracle.wl). The runner emits numeric error, deliberate mutation error, and SHA-256 signatures of code and both oracle files.

The added results are **controlled regression evidence on previously observed fixtures, not an independently preregistered confirmatory experiment**. A future unseen fixture plus independently approved protocol would be required for that stronger scientific status.

Scientific adoption status remains **NOT ADOPTED** even when provisional automated checks pass. Independent code and physics review and a recorded frozen-gate judgment are still necessary.
