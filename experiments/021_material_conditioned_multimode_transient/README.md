# Experiment 021 — Material-conditioned multi-mode transient realization (G1-C)

Issue: #49

Baseline: `d8f1b4665ce843b5fe2a8d5402a7c922b9851821`.

## Research question

Can one unchanged CONSTRICT task produce a finite-time physical trajectory that falsifies the Experiment-020 scalar-path null, while a reduced material intervention predictably changes the normalized transient and preserves the same material-specific Experiment-019 equilibrium endpoint?

This experiment adds exactly one layer beyond G1-B: a 10-dimensional experiment-local modal physical state. It does not add multiple Gestures, muscle activation, calibrated biological tissue parameters, FEM/XPBD/FSI, production temporal/material APIs, Studio controls, or neural components.

## Fixed fixture

- tract length: 0.170 m
- 10 equal-length sections
- rest area: 3e-4 m²
- CONSTRICT location: 0.65
- target section: zero-based 6
- target area: 5e-5 m²
- smoothness lambda: 1
- omega: 25 s^-1
- durations: 40 / 80 / 120 / 200 / 320 ms
- primary comparison: **120 ms**
- M0 baseline: all relative stiffnesses = 1
- M1 stiff: section index 5 stiffness = 4; all others = 1

Canonical task intent is unchanged across model, material, and duration.

## R2 scalar-path null

[
a''+2\omega a'+\omega^2(a-u)=0,
\qquad
q_{R2}(t)=q_0+a(t)(q^*-q_0).
]

Thus the trajectory remains in the span of (delta=q^*-q_0):

[
d_\perp(t)=0,
\qquad
e_{R2}(t)=1-a(t).
]

At 120 ms the independent Wolfram oracle predicts

[
e_{R2}=0.199148273471455772
]

for both M0 and M1.

## R3 material-conditioned multi-mode candidate

Using the Experiment-019 reduced material Hessian

[
H(K)=\operatorname{diag}(k)+\lambda L,
]

R3 advances

[
\ddot q+2\omega H^{1/2}\dot q+\omega^2H(q-q^*(u))=0.
]

For (H=V\Lambda V^T), each mode is critically damped with

[
r_i=\omega\sqrt{\lambda_i}.
]

For modal error (e_i=z_i-z_i^*), arbitrary initial error (e_{i0}), velocity (v_{i0}), and a constant target:

[
e_i(\tau)=[e_{i0}+(v_{i0}+r_i e_{i0})\tau]e^{-r_i\tau}
]

[
v_i(\tau)=[v_{i0}-r_i(v_{i0}+r_i e_{i0})\tau]e^{-r_i\tau}.
]

Python must use this exact modal transition rather than a generic ODE integrator.

## Primary discriminator

[
s(t)=\frac{\delta^T(q(t)-q_0)}{\delta^T\delta},
\qquad
r_\perp(t)=(q(t)-q_0)-s(t)\delta
]

[
d_\perp(t)=\frac{\lVert r_\perp(t)\rVert}{\lVert\delta\rVert}.
]

Independent Wolfram predictions at 120 ms:

| condition | path progress | d_perp | normalized error |
|---|---:|---:|---:|
| R2 M0 | 0.800851726528544 | 0 | 0.199148273471456 |
| R2 M1 | 0.800851726528544 | 0 | 0.199148273471456 |
| R3 M0 | 0.863095641755240 | 0.0642727926210942 | 0.151240851550511 |
| R3 M1 | 0.901454285446781 | 0.0552394435765393 | 0.112971916791078 |

The primary tests are: (1) R3 breaks the scalar-path null; (2) the normalized R3 transient changes under the material intervention.

## Independent oracle

`wolfram/multimode_transient_oracle.wl` is the independent source program.

`wolfram/multimode_transient_oracle.json` is checked in **before the Python R3 candidate exists** and freezes material equilibria, all 10 eigenvalues/rates, 120-ms R3 q/qdot, full duration observables, and 120-ms R2/R3 acoustic roots.

## Preregistered gates

- G1 representation isolation → `REPRESENTATION_LEAK`
- G2 request validity → `TASK_REQUEST_INVALID`
- G2 equilibrium regression, max state error <= 1e-10 → `EQUILIBRIUM_REGRESSION_FAILED`
- G3 modal oracle, primary state max error <= 1e-11 → `MULTIMODE_ORACLE_MISMATCH`
- G4 split/single <= 1e-11; dt=0 switch jump <= 1e-12 → `STATE_PROPAGATION_FAILED`
- G5 at 120 ms R2 d_perp <= 1e-12 and both R3 d_perp > 0.05 → `MULTIMODE_EFFECT_UNRESOLVED`
- G6 R2 material delta <= 1e-12; R3 material delta matches oracle, M1<M0, |delta|>0.03 → `MATERIAL_TRANSIENT_EFFECT_UNRESOLVED`
- G7 first three 120-ms acoustic peaks match Wolfram within candidate/reference 0.05/0.01 Hz; shifts have preregistered signs and exceed 5x numerical floor → `ACOUSTIC_ORACLE_MISMATCH` / `NUMERICALLY_UNRESOLVED`

Downstream gates not evaluated after an upstream failure must be `null`, never synthetic PASS.

## Artifacts

- `modal_spectrum.csv`
- `duration_summary.csv`
- `state_trace.csv`
- `physical_effects.csv`
- `resonances.csv`
- `acoustic_effects.csv`
- `decision.json`

## Claim ceiling

Success supports only that, in this 10-section reduced fixture, preserving the same task intent and Experiment-019 material-specific equilibrium concept, a scalar finite-time path can be falsified by a multi-mode physical trajectory and the reduced material intervention predictably changes normalized transient realization and downstream acoustics.

It does not establish biological tongue dynamics, calibrated tissue mechanics, human speech motor control, or correct multi-Gesture competition.
