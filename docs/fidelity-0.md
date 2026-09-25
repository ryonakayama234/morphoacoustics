# Fidelity 0 acoustics

Fidelity 0 is the smallest falsifiable acoustic model in `morphoacoustics`.
It is not intended to be a realistic voice synthesizer. Its purpose is to
establish a validated physical path from simple morphology to acoustic
behavior before source models, gestures, losses, radiation, and coupling are
added.

## Uniform-tube assumptions

The first primitive is a stationary tube with:

- one-dimensional plane-wave propagation,
- constant cross-sectional area,
- rigid walls,
- linear acoustics,
- no viscothermal or wall losses,
- no source-filter feedback,
- no time-varying geometry,
- an ideal pressure-release outlet when the default load is used.

These are fidelity-0 assumptions, not restrictions on the domain model.
`CreatureSpec` remains free to represent morphologies that this backend cannot
solve.

## State and convention

The acoustic state is pressure `p` and volume velocity `U`. Solver internals
use SI units. The Fourier convention is

```text
exp(+j omega t)
```

and a tube transfer matrix maps the outlet state to the inlet state:

```text
[p_in]   [A B] [p_out]
[U_in] = [C D] [U_out]
```

For a lossless uniform tube of length `L`, cross-sectional area `S`, density
`rho`, and sound speed `c`,

```text
k  = omega / c
Zc = rho c / S

T = [[cos(kL),      j Zc sin(kL)],
     [j sin(kL)/Zc,    cos(kL)   ]]
```

The determinant is one for this reciprocal lossless two-port.

## Ideal closed-open resonances

With an acoustically closed glottal end and an ideal pressure-release outlet,
the uniform tube is a quarter-wave resonator:

```text
f_n = (2n - 1)c / (4L),  n = 1, 2, 3, ...
```

The analytical prediction is intentionally kept separate from the numerical
input-impedance calculation. `tests/scientific/test_uniform_tube.py` checks
that impedance maxima occur at the analytical frequencies within the scan-grid
resolution.

This gives the next solver an oracle: a piecewise-constant transmission-line
implementation must reduce to the same result when every section has the same
area.

## Deliberately deferred physics

Fidelity 0 does not yet include:

- glottal or other acoustic sources,
- waveform synthesis,
- radiation impedance,
- area-function realization from `CreatureSpec`,
- gesture-driven geometry,
- branching cavities,
- losses or compliant walls,
- nonlinear acoustics,
- source-filter coupling.

Each of these should be introduced as a separate intervention whose effect can
be compared against the validated simpler model.

## References

- MIT OpenCourseWare, *Source-filter theory / uniform-tube model*: the vocal
  tract is introduced as a tube closed at the glottis and open at the lips,
  giving the quarter-wave resonance pattern.
  https://ocw.mit.edu/courses/24-910-topics-in-linguistic-theory-laboratory-phonology-spring-2007/resources/lec3_src_filterb/
- Zörner et al. (2023), *An Investigation of Acoustic Back-Coupling in Human
  Phonation on a Synthetic Larynx Model*: vocal-tract pressure and volume
  velocity are propagated with cascaded 2x2 transmission-line matrices, and
  input-impedance maxima identify resonances.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10740801/
- Keefe et al. formulation summarized in *Procedures for ambient-pressure and
  tympanometric tests...*: for a lossless acoustic transmission line,
  characteristic impedance for volume flow is `Zc = rho c / S`.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4684573/
- Stepp & Voss (2015), *Acoustical transmission-line model of the middle-ear
  cavities and mastoid air cells*: uses the `exp(+j omega t)` convention and
  notes unit determinant for reciprocal transfer matrices.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4417022/
