# B2-A prospective gate — physical anatomy / local junctions
Date: 2026-10-25. FROZEN BEFORE B2-A solver implementation.

## Scope
Generalize B1b's one common passive bidirectional traveling-wave solver to serial, stationary, rigid, lossless 1D area-varying ducts. Preserve existing prepared-body identity and immutable M0/M1 section arrays. No dynamic geometry, glottal FSI, 48 kHz coupled source, microphone, Studio integration, or Core production cutover.

## Frozen test bodies
- Exact Experiment 028 frozen_reference.json M0 /a/ and /i/: 16 sections each 0.010 m; compare both different area functions.
- CC-A2 prepared M1 /a/: same M0 /a/ area array, 16 sections each 0.011 m, total 0.176 m vs M0 0.160 m.
- Uniform-body reduction with 16 equal sections and B1b identical physics and mouth.
- Two-section area steps, including reverse ordering and equal-area identity.

## Physical contract
- Acoustic p in Pa, U in m^3/s, Z=rho*c/S, signed boundary power p*U.
- At each stationary junction enforce common pressure and conserved outward volume flow. Incoming traveling pressure a from left, b from right; junction pressure p=2*(a/Z_left+b/Z_right)/(1/Z_left+1/Z_right); outgoing waves left=p-a and right=p-b. This must reduce to identity for equal areas and produce pressure reflection (Z_right-Z_left)/(Z_right+Z_left) for incidence from left.
- At fixed geometry, junction power is exactly conserved: a^2/Z_left+b^2/Z_right = (p-a)^2/Z_left+(p-b)^2/Z_right. No gain, post-WAV EQ, fitted damping or invented source.
- Wave travel in each segment must retain physical length/c without rounding to 48k. For B2-A's equal-length-per-section bodies, permit per-body physics clock c/(section_length/n) with integer n=2,4,8 cells per anatomical section; no claim that arbitrary unequal-length section arrays are supported. Fail explicitly on unsupported lengths.
- Original B0 physical radiation one-port, instantiated using the body's actual lip area; do not change its physical constitutive law. Separate controls: matched, closed, pressure-release.
- Total stored energy includes traveling wave FIFO energy and B0 inertial state. Signed source work and passive outlet loss must balance per tick and cumulatively.

## Independent scientific acceptance
1. Equal-area 16-section B2-A reproduces B1b's exact wavefront, phase/group delay, p/U and energy at each tested refinement, with no pre-arrival wave.
2. Two-section step: reflection/transmission signs and amplitudes agree with independently derived continuum formulas, including reverse direction; junction energy error <= 1e-11 of a clearly stated nonzero incoming power scale.
3. M0 /a/, M0 /i/, M1 /a/: actual frozen geometry and prepared-body identity checked, no hardcoded fabricated area values. Physical first mouth arrival L/c (32/64/128 internal ticks) and no earlier response. M1 physical arrival is 1.1x M0 at same c.
4. Frequency-domain independent 2x2 cascade using exact lengths, areas and identical analog B0 load is the oracle for time-domain complex transfer over 200,400,600,1000,2600 Hz (B0 ka <= 0.8 only). Require <= 0.5% complex relative error at n=2 except at near-null/ill-conditioned frequencies (then predeclare absolute and reference-normalized metrics), and errors to decrease monotonically with refinement n=2,4,8, preferably <= 0.35 each halving of dt. If actual M0 sharp junctions cause a legitimate numerical deviation, record HOLD and independently diagnose; do not weaken gate retroactively.
5. Every termination passes signed per-step and integrated energy identity; passivity from nonzero seeded initial states and both positive/negative source pulses. Record raw p/U, incoming/outgoing wave, B0 q, energy/work/dissipation, SHA256 manifests and exact CI source/ref. Independently audit raw files without importing the solver.
6. Negative controls: reversed junction reflection sign, replacing all areas by lip area, 48k integer-rounded section delays, omission of B0 stored energy must be caught.
7. Both source-branch and PR CI, plus optional @codex review requested on GitHub if supported. No assertion of third-party review until a real review appears.

## Disposition
Only if all frozen scientific tests pass: B2A_STATIC_ANATOMICAL_WAVEGUIDE_VERIFIED (research only). Otherwise B2A_HOLD with exact failed evidence. Dynamic B2-B, cross-clock and production remain unverified. Keep stacked draft PR; no merge into main.
