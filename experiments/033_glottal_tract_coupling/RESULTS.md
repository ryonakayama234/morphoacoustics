# Experiment 033 — strong-coupling numeric results and audit

**Research fixture:** source–filter interaction *level 1*, fixed 1D tract / externally prescribed **strictly open** glottis. All outcomes below are **computed toy-model** results, NOT observed human voice, auditory preference or biological calibration. Source: actual GitHub Actions [experiment-033-sfi3 workflow run #38109824144](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38109824144), test and `run.py` job logs, head commit `904cf12215b1cd6f68a8b163fe977dee2c96c14e`; the later Core `Tract1DGeometry` fixture adapter commit uses identical specified physical dimensions and must be checked in subsequent CI.

## Frozen comparison and measured upstream impact

Reference fixed tract: ten 17mm sections, area `3e-4 m²` each; narrowed condition changes **only** section index 5 to `1.5e-4 m²`. `Ag=3e-5 m²` (always open), `Psub=800Pa`, `Ig=1200Pa s²/m³`, `Rg=1.5e6Pa s/m³`, `rho=1.21kg/m³`, `Cd=0.7`, `c=343m/s`, matched resistive outlet, `48kHz`, `30ms`. No output EQ or source waveform is prescribed.

| Comparison (relative RMS difference in **upstream U**, reference = first condition) | Measured |
| --- | ---: |
| C0 uniform vs C0 narrowed (nonreciprocal null) | **0.00000000** |
| C1 strongly coupled uniform vs C1 narrowed (geometry only) | **0.0046421173 = 0.46421173%** |
| C0 uniform vs C1 uniform (feedback enabled) | **0.3655712037 = 36.55712037%** |

**Important:** 0.464% is a **relative RMS difference between time series**, not the percent change in mean flow, sound pressure, perceived timbre or actual human vocal tract sensitivity. C0 is deliberately nonreciprocal; the 36.6% C0/C1 comparison is diagnostic, not a prediction of realistic phonation.

## Physical fidelity and energy

- C1 uniform: max per-step total discrete energy residual **9.020900888e-20 J**; divided by cumulative absolute pressure work **1.532775476e-17**.
- C1 narrowed: max per-step total discrete energy residual **8.343274530e-20 J**; normalized **1.419035280e-17**. All glottal and outlet dissipation terms nonnegative for both candidates.
- Glottal equation residual below **1.1e-11 Pa** in both C1 cases; source-free zero initial state stays quiescent.
- Geometry-only difference within first **0.25ms** after initiating constant pressure: max absolute `U` difference **4.85254469e-14 m³/s**, below preregistered `1e-7 m³/s` tolerance. **Implicit midpoint global linear solves can have tiny numerical pre-response**: this result validates the quantitative early-effect gate, not a mathematical strict finite-support propagation proof.
- 24k→48k normalized flow difference **3.402421585e-4**; 48k→96k **1.200500033e-4**, supporting convergence in the frozen fixture. This does not establish arbitrary high-frequency accuracy or no time-step constraints for moving geometry.

## Independent Wolfram mathematical oracle

The Wolfram Language file `wolfram/independent_oracle.wl` was executed through the Wolfram connector. For a separate **single acoustic cell** of length 17mm, area 3e-4m², same other parameters and zero initial state:
- Acoustic midpoint port sensitivity `dp_in,mid/dU_new = 1,782,466.2109735009 Pa·s/m³`.
- First coupled flow update `U_new = 1.3302951889662222e-5 m³/s`.
- Corresponding midpoint inlet pressure `p_in,mid = 23.712062249528995 Pa`.
- Total discrete midpoint energy expression simplifies to **symbolic residual 0**, under the independent tract acoustic boundary energy identity and fixed positive aperture.
- First-step Python result agrees with independent one-cell reference in an explicit scientific test.

## CI, provenance and known limitations

- Experimental work begins with preregistration-only commit `884d875`; later implementation and 12 explicit tests are separately committed. GitHub Actions (run #38109824144) passes **12/12 scientific tests on Python 3.11/3.12/3.13** and all eligible G0–G3 gates. The generic repository test/typecheck workflow also passed on that commit.
- Exact glottal closure **G4 UNSUPPORTED**. No tissue contact/projection energy budget; any `Ag=0` is explicitly refused. No time-varying A(t) tested. Anatomical articulation and biomechanical motion, wall viscoelastic losses, branching, actual radiation and near-field are not validated.
- Voice/vowels/naturalness **NOT_TESTED**. This is the first successful **open-valve, fixed-shape numerical coupling intervention**, not a self-oscillating 3D biological voice simulator.
- PR #84 is **stacked on Draft PR #81's unmerged waveguide branch**; the 033 PR must not be merged without predecessor review. Its glottal midpoint equation is adapted from the **physical law** of unmerged #79, not from the #79 BE chamber solver.
- No changes to production `src/`, contracts, Studio, Exp031 or Exp032 are part of PR #84. No merge and no production promotion.

## Reproduction

```bash
python -m unittest discover -s experiments/033_glottal_tract_coupling -p 'test_*.py' -v
python experiments/033_glottal_tract_coupling/run.py --output-dir /tmp/sfi3-033
```

Full C0/C1 × geometry CSV traces and JSON machine verdict are preserved as GitHub Actions artifacts per Python version on the workflow run.
