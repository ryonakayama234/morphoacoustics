# OG-1 / Experiment 038 — fixed pre-implementation protocol v1

## Status and chronology
RESEARCH ONLY / NOT ADOPTED / NO PRODUCTION OR STUDIO API CHANGE.
This author-defined protocol is committed before any Experiment038 implementation or execution.
Earlier conversation included theoretical planning values at 733 Hz and local area ratios;
those known values are disclosed, not presented as unseen independent confirmation.
No independent external approval or prospective human preregistration is claimed.
OG-0 #90/#93 and Draft #91/#92 remain pending review. This separate exploratory successor
uses ONLY adopted main UniformTube, not unadopted OG-0 code. Integration/adoption remains gated
on OG-0 resolution plus independent OG-1 physics/code review. User authorized this isolated trial.

## Hypothesis / one capability
A typed graph of three rigid uniform tubes A/B/C and one zero-volume ideal acoustic
junction J gives finite-length frequency-domain port states consistent with independently
derived load recursion and traveling-wave scattering, preserving pressure continuity,
signed volume-flow balance, mean power and geometry intervention consequences.

## Frozen model and fixture
Base main: 8868df1188443fc4523533c6cb0bb9cd72995c32.
UniformTube blob: 8bceaf1426c2aec56eea91e2148cd402998516f2.
Common rho=1.2 kg/m3, c=343 m/s. exp(+i omega t).
LA=.08m, LB=.09m, LC=.06m; SA=SB=3e-4m2; SC in {1.5e-4,3e-4,6e-4}m2.
Edges A.out--J.a, J.b--B.in, J.c--C.in; each port belongs to exactly one edge or boundary.
Tube U is positive inlet->outlet. Junction outward flows are {-UA.out, UB.in, UC.in}.
Fixed frequency list [80,250,400,733,997,1200,2000,4000] Hz (997 is a new theoretical fixture).
Peak harmonic inlet flow 1e-6*(1+0.4i) m3/s; additional amplitude scaling cases .5 and -1.
Terminal families: B matched + C matched; B matched + C pressure_release;
B matched + C rigid_closed. Matched means p=Zc U, release p=0, closed U=0.
Matched load follows SC when SC changes; this is an ideal no-return boundary, not fixed
external load or real lip radiation. A second controlled intervention keeps C load fixed at
the BASELINE Zc while changing SC, separating geometry-only change from rematching.
No waveform, acoustic time integration, tissue motion, biological nose, voice quality,
source-filter feedback, full anatomy or graph-general solver is claimed.

## Solver and independent oracle
Production candidate: 12 complex p/U unknowns at six tube ends.
Six equations from existing UniformTube transfer matrices, two junction pressure conditions,
one signed volume-flow equation, two load conditions, one imposed inlet flow.
Scale all p by p_ref=ZA*1e-6 Pa and all U by U_ref=1e-6 m3/s.
Dense numpy.linalg.solve; explicit condition number and backward residual.
No diagonal regularization, clipping, damping or silent least-squares fallback.
Independent test oracle uses tangent load recursion and explicit traveling-wave propagation,
NOT UniformTube or the solver matrix. Wolfram evaluator source and numeric JSON are archived.
Compare all six port states, not only input impedance.
Local scattering: solve pressure/flow conditions for each of three incident basis waves
and complex mixed incidence; verify S^T diag(Y) S=diag(Y), Y=1/Zc.
Pressure coefficient powers must be weighted by each port admittance.

## Fixed gates (float64 engineering tolerances, pending independent scientific acceptance)
Normalized full-port error vs independent oracle <=1e-10.
Junction pressure and volume-flow residual / declared p_ref,U_ref <=1e-10.
Equation backward residual <=1e-12.
Mean-power imbalance / (0.5*p_ref*U_ref*|input_scale|^2) <=1e-10.
Local scattering normalized coefficient/power error <=1e-12.
All nominal fixture condition numbers <=1e8; any exceedance is NUMERICALLY_UNRESOLVED,
NOT an omitted sample. No fixture may be removed after inspection.
Mutation controls: wrong UA+UB+UC=0 and wrong particle-velocity continuity must each
show normalized oracle error >1e-3 for SC=6e-4,733Hz,matched outlets.
Non-reflecting local exact fractions:
SC/SA=.5: {1/25,16/25,8/25}; 1: {1/9,4/9,4/9}; 2: {1/4,1/4,1/2}.
Matched outlets: input mean power = sum output powers.
Pressure release or rigid closed outlet: zero terminal mean power, NOT zero branch field.
Invalid schema controls (unknown IDs, duplicate edge/port, dangling required port,
nonfinite/nonpositive dimensions, wrong type, unknown law) -> INVALID.
A well-formed larger graph or loop -> UNSUPPORTED, after full schema validation.
Missing boundaries -> INVALID. Actuating geometry is not offered.
Permutation of input node/edge ordering must preserve canonical graph digest and states.
Changing graph parameter, boundary, frequency or source changes the appropriate identity.
Two fresh runs produce byte-identical evidence on same runtime; no output-directory overwrite.

## Singular fixture
All three tubes L=.08m, equal areas, B/C pressure release at f=c/(2L)=2143.75Hz.
This ideal network has an internal branch degeneracy. condition>1e8 or rank loss must
return NUMERICALLY_UNRESOLVED without finite fabricated output. Record it separately
from nominal finite fixtures. No claim that all lossless resonance values are finite.

## Scientific/software decisions
Numeric gate pass -> PROVISIONAL_NUMERICAL_PASS only.
Failure at eligible finite fixture -> FAILED; conditioning/solve failure -> NUMERICALLY_UNRESOLVED.
Independent code and physics reviews, OG-0 resolution and explicit decision are separate
requirements for SUPPORT_PASSIVE_THREE_PORT_BRANCH or later production promotion.
Keep Draft; do not merge automatically. Software/CI green is not independent approval.

## Evidence and delivery
Archive immutable graph JSON, protocol/source/oracle hashes, runtime and git revision,
all full-port complex states CSV, power/condition/oracle errors, negative controls, summary JSON,
and a labeled response comparison figure. Scientific runner recomputes actual physics.
CI executes all fixed nominal fixtures twice, checks gates/evidence, retains artifacts.
No edits to src/, contracts/, existing experiments or Studio.

## Sources
- Adopted docs/fidelity-0.md and acoustics/uniform_tube.py at pinned main above.
- Smith, Physical Audio Signal Processing, Lossless Scattering:
  https://www.dsprelated.com/freebooks/pasp/Lossless_Scattering.html
- OG-0 design #90 and review #93: claims still provisional.
