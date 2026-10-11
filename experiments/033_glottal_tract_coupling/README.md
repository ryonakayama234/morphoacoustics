# Experiment 033 — strongly coupled glottal flow and fixed 1D vocal tract

**RESEARCH ONLY.** This is the first strictly-open-glottis experiment with the **actual causal inlet pressure of the fixed 1D tract fed back into a glottal flow law at the SAME midpoint time step**. This is NOT vocal-fold tissue self-oscillation, moving anatomy, calibrated human speech, closed-glottis contact or a production renderer.

Related research: [Issue #82](https://github.com/ryonakayama234/morphoacoustics/issues/82), [Draft PR #84](https://github.com/ryonakayama234/morphoacoustics/pull/84), [PREREGISTRATION.md](PREREGISTRATION.md), the fixed tract source [Draft #81](https://github.com/ryonakayama234/morphoacoustics/pull/81), and antecedent glottal law [Draft #79](https://github.com/ryonakayama234/morphoacoustics/pull/79).

## Dependency and branch topology (must be understood before review)

This is a **stacked PR**: its base is `research/sfi2-time-domain-tract-20261010` (Draft #81) so `coupled.py` imports the ORIGINAL `experiments/032_passive_time_domain_tract/waveguide.py` directly, without changing it. The base/head are not `main`; nothing is being merged. The scalar glottal law matches #79's `Ig Udot + Rg U + rho/(2Cd²Ag²) U|U| = Psub-p_in`, but is deliberately discretized by **implicit midpoint**, not #79's backward Euler (which also uses a passive *lumped* chamber). Neither predecessor code nor any `src/` contract changes in this PR. A future rebase onto main requires both reviewed prerequisites to be understood; do not merge the stack automatically.

## Reproduction (WSL2/Linux, Python 3.11+)

From a checkout **of the Experiment 033 stacked head branch**:

```bash
python -m pip install "numpy==2.4.6"
python -m pip install -e .
python -m unittest discover -s experiments/033_glottal_tract_coupling -p 'test_*.py' -v
python experiments/033_glottal_tract_coupling/run.py --output-dir /tmp/experiment-033-output
```

`--output-dir` must be absent or empty; replay with stale outputs is rejected. CI does the same on Python 3.11, 3.12 and 3.13, enforces scientific gates, and publishes four complete CSV numerical traces and `summary.json`. All eligible scientific gates must pass for process exit 0, while real voice/naturalness and contact treatment explicitly stay `NOT_TESTED`/`UNSUPPORTED`.

## Physical and numerical structure

- Fixed 10 × 17mm serial tube from `Geometry` in the original Exp032, one middle (index 5) section optionally narrowed by half, passive *matched* resistive outlet, 4 acoustic cells per original section.
- Positive prescribed glottal opening `Ag=3e-5 m²`; `Psub=800Pa`; `Ig=1200Pa s²/m³`, `Rg=1.5e6Pa s/m³`, `Cd=0.7`, density `rho=1.21kg/m³`; run 48kHz, 0.030s. These are numerical fixtures, not fitted biological parameters.
- At the same midpoint `U_mid=(Uold+Unew)/2`, balance valve equation against `p_in,mid`, the **power-conjugate** acoustic inlet pressure returned by the Exp032 waveguide. The original waveguide also includes an inlet half-cell acoustic inertance; that energy is counted ONLY inside `E_tract`.
- Construct affine port response `p_in,mid = intercept + slope * Unew` by temporary *noncommitting* waveguide probes. The two probes at initialization determine the constant positive slope of this stationary linear tract. At each physical time step, solve **one monotone nonlinear scalar** with the tract input port, then advance the actual tract exactly once with the calculated volume flow. Check the final port pressure against the affine relation and valve equation.
- Total state energy `E_total=Ig U²/2+E_tract`. For the strong-feedback candidate the exact discrete midpoint budget is `DeltaE = dt*(Psub U_mid - Rg U_mid² - b(Ag)|U_mid|³ - R_out Uout_mid²)`. No arbitrary gains, learned waveform, normalization, lagged pressure or output EQ.
- Open-loop null C0 removes the pressure term from the glottal equation while keeping the same waveguide state/output. The missing feedback power `+dt*p_in U_mid` is recorded explicitly as **nonreciprocal work**. C0 is NOT described as a passive closed physical system.

## Scope restrictions and critical limitations

`Ag=0` is **rejected** as `CLOSED_GLOTTIS_UNSUPPORTED`. This is deliberate; simply projecting the midpoint boundary flow at exact closure would need its own contact, body-work and inlet-half-face kinetic-energy budget. Periodic opening that reaches zero, tissue self-oscillation, vocal tract movement, lip radiation physics, nasal branching, turbulence, human-specific body calibration and listener/phonetic evaluation are independent future gates. This experiment establishes only **level-1 fixed-area, fixed-tract acoustic pressure↔flow interaction within a toy 1D rigid model**.

Wolfram reference: `wolfram/independent_oracle.wl` and `wolfram/oracle.json` for one acoustic cell's exact port slope, first coupled update, pressure and the symbolic 0-residual discrete power balance. The frozen numeric, scientific and causal thresholds are listed in the preregistration, not tuned after observing the results.

Primary background reference: Titze (2008), *Nonlinear source–filter coupling in phonation: Theory*, https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/.
