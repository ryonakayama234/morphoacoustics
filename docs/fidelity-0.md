# Fidelity 0 contract

Fidelity 0 is the smallest falsifiable end-to-end model in `morphoacoustics`.
It is not intended to be a realistic voice synthesizer. Its purpose is to
establish a validated causal path from task-level gesture through a simple
morphology-specific physical state to a simple acoustic observation.

The limitations below are part of the Fidelity-0 model contract. They are not
universal restrictions on `CreatureSpec`, `GestureScore`, or future backends.

## Contract summary

Fidelity 0 is deliberately:

- **static snapshot only** — no physical time evolution,
- **one-dimensional** — plane-wave propagation in a discretized tract,
- **rigid-wall**,
- **lossless** — no viscothermal, wall, or other dissipative losses,
- **serial tract only** — no branching/side cavities,
- **CONSTRICT-only realization** for active gestures,
- **source-free** — no glottal or other acoustic source,
- **waveform-free** — it returns a frequency-domain acoustic response rather than synthesized audio,
- terminated by an **ideal pressure-release outlet** in the Fidelity-0 acoustic backend.

A morphology or task outside these capabilities must be reported as
`UNSUPPORTED`; unsupported structure must not be silently ignored.

## Physical state

Fidelity 0 represents one selected cavity as `Tract1DGeometry`: an ordered
sequence of rigid, constant-area tube sections. This type is a backend-specific
physical representation, not a domain morphology primitive.

Normalized axial coordinates use:

```text
0 = inlet / source side
1 = outlet / radiation side
```

Internal section boundaries belong to the downstream section. The current
`CONSTRICT` realization changes one discrete section. Consequently, the axial
extent of a constriction is mesh-dependent in Fidelity 0; mesh-independent
constriction width is intentionally deferred to a later physical model.

## Realization semantics

Fidelity 0 realizes an active `CONSTRICT(location, target_area)` by:

1. checking that the selected cavity is representable as an isolated serial tract,
2. checking that an articulator in that cavity can reach the normalized location,
3. mapping the location to one 1D section,
4. replacing that section area with the requested smaller target area.

Simultaneous constrictions mapped to the same section are combined
commutatively: the tightest target area wins. Gesture tuple order therefore
does not act as an implicit physical priority.

Other active task kinds such as `PHONATE`, `OPEN`, and `PRESSURIZE` are
`UNSUPPORTED` at Fidelity 0. Invalid parameters are `INVALID`, not
`INFEASIBLE`. A valid supported constriction outside the creature's articulator
reach is `INFEASIBLE`.

## Acoustic state and convention

The acoustic state is pressure `p` and volume velocity `U`. Solver internals
use SI units. The Fourier convention is

```text
exp(+j omega t)
```

and each tube transfer matrix maps the outlet state to the inlet state:

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

For serial sections ordered inlet to outlet, the composite matrix is

```text
T_total = T1 @ T2 @ ... @ Tn
```

The determinant is one for this reciprocal lossless two-port.

## Outlet boundary and ideal resonances

The Fidelity-0 acoustic backend uses an ideal pressure-release outlet:

```text
Z_load = 0
```

This is a deliberate ideal boundary condition, not a model of realistic lip
radiation. Radiation impedance and end correction belong to a later fidelity.

For a uniform tract with an acoustically closed input and this pressure-release
outlet, the impedance maxima follow the quarter-wave pattern:

```text
f_n = (2n - 1)c / (4L),  n = 1, 2, 3, ...
```

Scientific tests compare this analytical prediction, written independently in
the test, with maxima obtained numerically from the transfer-matrix impedance.
An additional asymmetric unequal-area test checks section ordering against an
independent outlet-to-inlet impedance recursion.

## Explicitly outside Fidelity 0

The following are not partially approximated by this backend:

- physical state trajectories or tissue dynamics,
- branching oral/nasal/side cavities,
- viscothermal, wall, or radiation losses,
- compliant walls,
- glottal or other acoustic sources,
- waveform synthesis,
- radiation impedance,
- turbulent noise,
- nonlinear acoustics,
- source-filter coupling,
- mesh-independent constriction extent.

These are later-fidelity interventions, not bugs in Fidelity 0.

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
