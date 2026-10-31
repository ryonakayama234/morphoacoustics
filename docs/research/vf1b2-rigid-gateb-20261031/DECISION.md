# VF-1B2 Gate B0 — bounded reference-control decision (2026-10-31)
**Decision: REFERENCE_ANALYTIC_CONTROL_V1 (research only).**
**NOT** an adopted phonator, biological vocal-organ solver, source–tract FSI, waveform renderer, Studio capability or Core public ABI. Keep Draft PR #262 unmerged; source remains explicitly research-only.

## Immutable qualification references
- Prospective preregistration frozen before code at `7cd56559b0dd106503980a559daffcf49a9505e7`.
- First reviewed code HEAD: `c7c323b4dead54bfe2bc00524e0e74f9cb5a0275` (Core main based, research branch); report-only subsequent commits DO NOT retroactively alter these tests.
- Fully successful exact-code GitHub Actions: https://github.com/ryonakayama234/morphoacoustics/actions/runs/41206377766 (Python 3.11/3.12/3.13).
- Regression workflows `tests`, `og3-gate-b`, `og4-gate-b`, `sv1-sustained-vowel-physical`: SUCCESS at exact code HEAD.
- Earlier 48-case record archive from https://github.com/ryonakayama234/morphoacoustics/actions/runs/41206091892 had the same outputs on three Python versions; `records.json` SHA-256 `202a8329648c43c29384ba767e3be822bd0a174cde88fd6a5055537d4093bc0f`, **before** per-cell receipt tightening (candidate physical results unchanged). New archive hash is not presumed identical without inspecting it.
- Initial Codex P2 on sum-preserving record corruption was fixed by a per-cell pressure-work identity plus explicit adverse controls. The latest exact-code Codex review returned `completed / no findings / no unresolved findings`; this is an independent *automated code audit*, not an external physical validation or guarantee against undiscovered defects.

## What this v1 control establishes
Within the declared slender low-Re fixed-wall Stokes/lubrication limits, a midpoint numerical discretization converges against the analytically integrated taper solution, maintains signed passive pressure/drop/power identities, and rejects unsupported inputs (including 800Pa). Two opposite taper orientations can share total flow and differ internally in pressure load; virtual forces are calculated as diagnostics only, never as verified moving-wall force/work.

The public exact fixture remains `L=.01m; w=.01m; h0=.00012m; mu=1.81e-5Pa s; rho=1.21 kg/m3; c=343m/s; s=-.2/0/.2; DeltaP=0/.1/.2/.4Pa; N=4/8/16/32`. H0-H5 and thresholds are frozen in EXPERIMENT.md.

## Scientific gate labels (distinct)
- G0 integrity + CI: PASS_LIMITED_EXACT_CODE.
- G1 low-Re rigid mathematical control: PASS_LIMITED.
- G2 measured geometry-matched intraglottal pressure / biological validity: INDETERMINATE.
- G3 autonomous self-sustained moving-wall phonation: NOT_APPLICABLE.
- G4 received audio / creator quality: NOT_EVALUATED_NO_GO.

## Nontransferability / no extrapolation
The observed algebraic power closure is partially constructed from cell resistance, so it does **not** prove an independently measured pressure field, loss/separation model, moving-wall conservation law, self-oscillation, or a human-like source. High-pressure vocal flow at 400/800/1200 Pa is outside this tested narrow model. M5/M6 rigid measured reference issues #215/#249 and related drafts remain independent evidence gates.

## Next research decision
Proceed ONLY with **B2a design-level moving-wall energy/port audit** on the separate PR #259: derive compressible mass, axial momentum, total advective enthalpy flux, wall force/work, SFI mean-flow vs acoustic-perturbation port, and an independently defensible pressure-loss/separation reference. If those cannot be reconciled, hold B2c. Do not tune pressure law, oscillator damping, F0 or downstream waveform to achieve a desired sound. Do not merge #262 to main or modify Studio/UI/SMC/ASMR; future contract/adoption requires a separate approved decision.
