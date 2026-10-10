# Experiment 032 — passive causal time-domain 1D vocal-tract acoustics

**Research-only, fixed geometry**. Tracks [#80](https://github.com/ryonakayama234/morphoacoustics/issues/80) and the [SFI-2 Draft PR](https://github.com/ryonakayama234/morphoacoustics/pull/81). [PREREGISTRATION.md](PREREGISTRATION.md) was committed **before** implementation. No production integration, neural components, glottal-valve feedback, vocal-fold self-oscillation, phonetic fidelity or naturalness claims.

## Reproduction (WSL2/Linux; Python >=3.11, numpy >=2.0)

From repository root:

```bash
python -m pip install -e '.[dev]'
python -m unittest discover -s experiments/032_passive_time_domain_tract -p 'test_*.py' -v
python experiments/032_passive_time_domain_tract/run.py --output-dir /tmp/exp032-sfi2
```

The output directory must be empty or absent. The run generates three CSV traces (`uniform_matched.csv`, `uniform_pressure_release.csv`, `constricted_matched.csv`) and `summary.json` with measured reflection arrival, complex input impedance probes, discretized free modes, discrete energy budgets and flags for unsupported future functionality. A nonpassing numerical gate exits code 1. CI repeats the tests on Python 3.11/3.12/3.13 and saves generated data as Actions artifacts.

## Scientific implementation

`waveguide.py` implements a lossless fixed-geometry 1D finite-volume acoustic transmission line. The **same section lengths and areas** are read via `Geometry.from_tract1d()` from actual Core `Tract1DGeometry`; a 10×17mm uniform tract and a second tract with one middle section narrowed by half are frozen fixtures. Each physical section is split into 4 positive-area acoustic cells for the transient tests. Pressure is cell-centered, volume flow is at interfaces, and a prescribed volume-flow test signal drives the inlet.

Cell compliance `C_i=A_i dx_i/(rho c²)`; internal face inertance `M_j=rho*(dx_left/(2A_left)+dx_right/(2A_right))`; inlet and outlet face inertances use half-cells. Outlet has passive resistive load `R_L >= 0` (either `R_L=Z_c` or ideal pressure release `R_L=0`). A **fully coupled implicit midpoint** method solves a positive symmetric tridiagonal system, reused each step. Stored energy includes the *prescribed inlet half-face inertance*, for which the physical inlet port pressure adds `M_0 dU_in/dt` to the first cell pressure.

Exactly, in the discrete midpoint convention:

```text
E_next - E_previous = dt*(p_in_mid * U_in_mid - R_L * U_out_mid²)
```

For fixed geometry and nonnegative termination impedance, the solver is passive; no biological pressure loss, wall motion, glottal contact or detailed lip radiation is modeled. The ideal matched resistive termination is a benchmark, not a full exterior-field impedance.

## Tests and research gates

- Wolfram `wolfram/independent_oracle.wl`: rational-value tube impedance, 0.17m travel time, ideal quarter-wave modes, area-junction reflection/power identity, and algebraically **zero** two-cell midpoint energy residual. `wolfram/oracle.json` is a checked-in machine oracle, read by the main diagnostic run.
- `test_waveguide.py`: ten experiment-local tests, including the independent Core `SegmentedTube` baseline, noncausal-reflection exclusion, impulse return delay, impedance phase/magnitude under matched outlet, near-zero energy residual and monotonic spatial convergence.
- Passive **waveform output is not yet voiced speech**. No LF phonation shape is used in this experiment; the input is a test flow pulse or sine. An existing frame-FFT transfer is not called a time-domain feedback solver.
- The *future* source-tract feedback coupling is an independent scientific intervention after review of this experiment, not an implicit capability of this PR.

See [RESULTS.md](RESULTS.md) for the locally observed reference results and strict limitations.
