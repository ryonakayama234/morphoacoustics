# CORE-WG-1 Gate A — static passive time-domain waveguide candidate

Status: **PREREGISTERED BEFORE IMPLEMENTATION** (2026-10-25 JST). Candidate only. Do not merge on these words alone.

## Motivation, exact source boundary
Research B0 (PR #176), B1b (PR #181), B2-A (PR #184, exact tested SHA `49d56f581036286e534e14835bede895a06327d6`) have research PASS, not Core adoption. Original B1 (PR #178) is an archived finite-support HOLD; do not bring it into the production acoustic engine. Preserve independent research code, raw data, negative CI and Codex review history. This new main-based branch ports the *physical method*, not a claim to a new scientific discovery.

## Pre-code hypothesis
H1: A self-contained, unchanged static 1D serial plane-wave scattering kernel can be expressed under `morphoacoustics.acoustics` without importing experiment code, without touching the source/gesture realization/Studio runtime and without introducing nonlocal influence or energy creation.

H2: Explicit section geometry determines the wave impedance, physical step and B0 passive outlet. The physics clock is `c*n/section_length`, never rounded to 48 kHz. Only uniform section LENGTHS within a body are supported; areas can vary arbitrarily (positive finite). The user receives a failure for unsupported geometry rather than a retuned approximation.

H3: The transplanted implementation is equivalent to B2-A on identical input/state and anatomy. The core candidate is a shadow API, NOT a new voice generator or naturalness claim.

## Frozen model and cases
- Fixed static rigid serial 1D lossless plane waves, real SI units, `rho=1.21 kg/m^3`, `c=343 m/s`.
- Local pressure-wave junction: `r=(Z_R-Z_L)/(Z_R+Z_L)`, left outgoing `r*a_L+(1-r)*b_R`, right outgoing `(1+r)*a_L-r*b_R`, `Z=rho*c/A`.
- Exactly `n=2,4,8` cells/section, FIFO shift one cell/tick. Inlet prescribed signed volume flow, explicitly named as a *driven boundary*, not a glottal oscillator.
- Terminations: closed `b=a`, pressure-release `b=-a`, matched `b=0`, B0 physically derived passive RL circuit with lip area from last actual section (research B0 equations, no EQ). Frozen research B0: `M=8*rho*a/(3*pi*A)`, `tau=3*pi*a/(16*c)`, `R=M/tau`, `a=sqrt(A/pi)`.
- SI per-step energy: `E_wave=h*sum((f^2+b^2)/Z)` over every FIFO element plus `M*q^2/2` B0 storage; `W_source=h*p_in*U_in`; `D_b0=h*p_mid^2/R`, matched `h*a_lip^2/Z_lip`, reflective 0. Residual `Delta(E)-W+D`.
- Zero input from empty state must be exactly silent; physical propagation must have no lip event before `N_sections*n` ticks. Equal areas reduce to uniform tube. M0 length 0.16 m, M1 length 0.176 m yields 1.1 transit ratio.
- Invalid/nonfinite geometry/input and unequal section lengths must fail *before* modifying state.

## Acceptance gates (fixed before code)
1. Physical clock/first arrival for 16x10 mm and 16x11 mm examples exactly 32 ticks at n=2 (within floating-time tolerance 1e-13 s), with zero earlier samples.
2. Independent static junction continuity and power conservation (signed bidirectional cases) at relative tolerance 1e-12.
3. All four termination energy residuals over nonzero inlet stimulus: `|residual| <= max(1e-9*max(|Delta E|,|W|,D,1e-20), 1e-12*max(Eold,Enew,1e-20))` per tick.
4. B0 pressure/reflection/state and wave traces match research equations on identical initial state/inputs within floating arithmetic limits (target relative <=1e-12). No arbitrary outlet gain, no wave postfilter.
5. CI on the new branch checks full existing Core pytest, new focused tests and static typing. Independent review must focus on mathematical port, boundary conditions and regression. Failed gates stay recorded; no retroactive threshold adjustment.
6. Documentation `INDEX/SYSTEM/DATA/EXPERIMENT` updated with actual result, commit, negative controls, separate scientific and audible verdicts. **No main merge**, Studio backend switch, 48k sound-quality claim, B2-B moving wall, self-oscillation, turbulence, neural, SMC or ASMR changes until evidence and review gates pass.

## Separate future gates
- CORE-WG-2: run exact B2-A M0/M1 prepared registry fixtures, independent continuum transfer oracle, raw state audit, 48k observation/source-port *physical coupling*.
- B2-B: time-varying wall work + conservation, must reduce to this model in static limit.
- Source/voice gate: physically coupled glottal source and human listening voice-like ratings are **separate**, not implied by transmission-line passivity.
