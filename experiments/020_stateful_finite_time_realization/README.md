# Experiment 020 — Stateful finite-time task realization (G1-B)

Issue: #40

Depends on Experiment 019 / PR #47.

## Research question

Can one unchanged task intent produce **duration-dependent, stateful physical realization** under a minimal finite-time task model, while the Experiment-019 quasi-static R1 reference predicts immediate task attainment?

This experiment is designed to distinguish:

- **R1 — quasi-static:** the active task is at its equilibrium realization immediately;
- **R2 — stateful finite-time:** a reduced task state approaches and leaves that equilibrium through continuous second-order dynamics.

The goal is not to claim general Task Dynamics or biological articulator mechanics. The goal is to add one falsifiable temporal state variable without changing production APIs.

## Why this is not Experiment 006/010 again

Experiments 006–010 already established that a prescribed continuous activation trajectory can be sampled, reconstructed, and propagated through quasi-stationary acoustics.

Experiment 020 tests a different proposition:

> the physical/task state at time t depends on the previous state, not only on the absolute time and a prescribed envelope.

R2 therefore carries the experiment-local state

\`\`\`text
(activation, activation_velocity)
\`\`\`

across onset and offset events.

## Fixed physical fixture

Experiment 020 reuses the Experiment-019 baseline material fixture:

- tract length: 0.170 m
- 10 equal-length sections
- rest area: 3e-4 m² in every section
- normalized CONSTRICT location: 0.65
- target section: zero-based section 6
- target area: 5e-5 m²
- reduced relative stiffness: all sections = 1
- smoothness lambda = 1
- same CreatureSpec and articulator reach
- same Fidelity-0 segmented-tube acoustics

The Experiment-019 R1 equilibrium geometry remains the physical endpoint.

## Representation intervention

The task intent is fixed across all conditions:

\`\`\`text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=5e-5 m²
)
\`\`\`

Only Gesture duration changes:

\`\`\`text
40, 80, 120, 200, 320 ms
\`\`\`

The full GestureScore hashes differ because offset time is the intervention. A separate task-intent hash excludes onset/offset and must remain identical across every condition.

No omega, velocity, solver state, area vector, resonance target, or waveform target is stored in Gesture.

## R1 — quasi-static reference

R1 uses the same convex minimum-energy equilibrium as Experiment 019:

\`\`\`text
E(q) =
    1/2 sum_i (q_i - 1)^2
  + 1/2 sum_i (q_{i+1} - q_i)^2
\`\`\`

subject to

\`\`\`text
q_6 = 1/6
\`\`\`

R1 predicts:

- zero task error throughout the active interval;
- no duration dependence of the active equilibrium geometry;
- immediate return to the rest state at offset in this comparison model.

The equilibrium state and first three resonances must regress to the independent Wolfram reference from Experiment 019.

## R2 — critically damped stateful task model

R2 introduces one dimensionless task activation state a with velocity v:

\`\`\`text
a'' + 2 omega a' + omega² (a - u) = 0
\`\`\`

with:

\`\`\`text
omega = 25 s^-1
u = 1 during the active Gesture
u = 0 after offset
initial state = (a=0, v=0)
\`\`\`

The rate constant is a fixture parameter, not a biological tissue or muscle parameter.

For a constant target u, Python uses the exact state transition of the critically damped system rather than a numerical ODE integrator. This deliberately separates the scientific dynamics question from integrator error.

The realized geometry is:

\`\`\`text
q(t) = 1 + a(t) (q_R1 - 1)
\`\`\`

so R1 remains the body/material-specific endpoint and R2 only adds finite-time task state.

## Independent Wolfram oracle

\`wolfram/stateful_dynamics_oracle.wl\` independently derives the critically damped step/release response, recomputes the Experiment-019 R1 equilibrium, and evaluates the resulting offset-minus geometries with an independently written lossless transfer-matrix model.

For onset from rest:

\`\`\`text
a(t) = 1 - (1 + omega t) exp(-omega t)
v(t) = omega² t exp(-omega t)
\`\`\`

The preregistered duration sweep predicts:

| duration | omega T | a(T-) | task error |
|---:|---:|---:|---:|
| 40 ms | 1 | 0.264241 | 0.735759 |
| 80 ms | 2 | 0.593994 | 0.406006 |
| 120 ms | 3 | 0.800852 | 0.199148 |
| 200 ms | 5 | 0.959572 | 0.040428 |
| 320 ms | 8 | 0.996981 | 0.003019 |

The same oracle gives 95% / 99% step-settling times of approximately:

\`\`\`text
189.755 ms
265.534 ms
\`\`\`

## Stateful release prediction

At the exact offset event the target changes from 1 to 0, but the R2 state must not jump:

\`\`\`text
a(T+) = a(T-)
v(T+) = v(T-)
\`\`\`

The subsequent state is history-dependent.

For example, 50 ms after release the activation oracle predicts approximately:

\`\`\`text
40 ms prior Gesture  -> 0.302088
80 ms prior Gesture  -> 0.479845
120 ms prior Gesture -> 0.569749
200 ms prior Gesture -> 0.630640
320 ms prior Gesture -> 0.643651
\`\`\`

At that observation time every condition has the same current input \`u=0\`, yet the states differ because their prior durations differ.

That is the primary state-memory discriminator.

## Acoustic prediction

At offset-minus, each R2 geometry is observed with the existing segmented-tube acoustics.

Independent Wolfram roots:

| duration | mode 1 | mode 2 | mode 3 |
|---:|---:|---:|---:|
| 40 ms | 492.228 Hz | 1556.126 Hz | 2490.453 Hz |
| 80 ms | 467.771 Hz | 1623.558 Hz | 2424.800 Hz |
| 120 ms | 440.025 Hz | 1675.980 Hz | 2348.532 Hz |
| 200 ms | 400.093 Hz | 1722.438 Hz | 2244.192 Hz |
| 320 ms | 385.269 Hz | 1734.154 Hz | 2208.703 Hz |
| R1 equilibrium | 383.922 Hz | 1735.111 Hz | 2205.581 Hz |

Thus the R2 acoustic state must converge toward R1 as duration increases.

Candidate peak grid: 0.05 Hz.

Reference grid: 0.01 Hz.

## Preregistered gates

### G0 — Representation isolation

- task-intent hash is identical across all durations;
- only Gesture offset/duration changes;
- dynamics parameters remain experiment-local.

Failure: \`REPRESENTATION_LEAK\`.

### G1 — Request validity

Every duration-specific Gesture remains a valid FEASIBLE CONSTRICT request and resolves to section 6 under the production Fidelity-0 validator.

Failure: \`TASK_REQUEST_INVALID\`.

### G2 — R1 regression

R1 equilibrium state must match the Wolfram oracle within max absolute error <= 1e-10.

Candidate/reference R1 resonance peaks must match within 0.05 / 0.01 Hz.

Failure: \`R1_REGRESSION\`.

### G3 — Dynamic oracle

For every duration, offset-minus activation/velocity/task error and 50/100 ms release state must match the independent Wolfram oracle within 1e-12.

Failure: \`DYNAMIC_ORACLE_MISMATCH\`.

### G4 — Stateful propagation consistency

One exact propagation over T and four exact propagations over T/4 must agree within 1e-12.

Failure: \`DYNAMIC_PROPAGATION_INCONSISTENT\`.

### G5 — Event continuity

Changing the target at offset must introduce no jump in activation or velocity within 1e-12.

Failure: \`EVENT_CONTINUITY_FAILED\`.

### G6 — Duration ordering / convergence

Across 40 -> 320 ms:

- offset activation strictly increases;
- offset task error strictly decreases;
- physical L2 distance from R1 strictly decreases;
- absolute acoustic distance from R1 strictly decreases for all three modes;
- 40 ms task error > 0.50;
- 320 ms task error < 0.005.

Failure: \`DURATION_ORDERING_FAILED\`.

### G7 — State memory

At both 50 and 100 ms after offset:

- every R2 activation remains > 0.10;
- release activations differ systematically with prior duration.

The corresponding R1 comparison state is rest immediately after offset.

Failure: \`STATE_MEMORY_FAILED\`.

### G8 — Acoustic oracle

Every duration-specific candidate/reference resonance must match Wolfram within 0.05 / 0.01 Hz.

Failure: \`ACOUSTIC_ORACLE_MISMATCH\`.

### G9 — R1 vs R2 discrimination

At every duration and for all three modes:

\`\`\`text
|f_R2 - f_R1| / local_numerical_floor > 5
\`\`\`

and the measured shift sign must match the independent oracle.

Failure: \`MODEL_DISCRIMINATION_UNRESOLVED\`.

## Decision

### SUPPORT_STATEFUL_FINITE_TIME_REALIZATION

A pass supports only:

> In this fixed reduced morphology/material fixture, a single scalar stateful finite-time task model makes duration- and history-dependent physical/acoustic predictions that differ from, and converge toward, the Experiment-019 quasi-static equilibrium while preserving the same task intent.

It does not establish:

- general Task Dynamics;
- biological stiffness, inertia, or damping;
- force/muscle actuation;
- multi-task competition;
- nonlinear or viscoelastic tissue mechanics;
- FEM / XPBD / FSI;
- phonetic validity;
- perceptual naturalness;
- a production temporal API.

## Run

\`\`\`bash
python experiments/020_stateful_finite_time_realization/run.py \
  --output-dir experiment-020-output
\`\`\`

Outputs:

- \`duration_summary.csv\`
- \`state_trace.csv\`
- \`resonances.csv\`
- \`effects.csv\`
- \`decision.json\`
