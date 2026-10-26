# VF-1B EXPERIMENT — proposed Gate A; NOT RUN
**Scope:** design/research preregistration proposal, not an adopted self-exciting vocal fold. [Issue #212](https://github.com/ryonakayama234/morphoacoustics/issues/212). This document intentionally contains no fabricated results. Freeze thresholds and independent controls in an amendment **before any experiment code**, without rewriting failures.

## Observed baseline (previous VF-1A, NOT VF-1B results)
At exact head `2b33bc69835170639fb9127c01dab7b523eff4f3` and [CI 40317639558](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40317639558): 13 independent/adversarial pytest tests and experiment runner succeeded, artifact `vf1a-research-evidence`; runner verdict `RESEARCH_NUMERICAL_PASS_NOT_A_PHONATOR`. For 800Pa uniform tract, pressure work in 0–20/20–40/40–60ms = 10.0009369/−4.5818148/+1.5186957 µJ; damping 2.2961134/0.4929172/0.1038317 µJ. 40–60 / 20–40ms mean-removed x1 RMS = 0.377485. This neither proves nor disproves long-term self-excitation; review thread P2 is outdated, still formally unresolved, and later exact-head re-review not established.

## Primary falsifiable question VF-1B1 (no new force law)
H0: pressure work and damping do **not** produce reproducible growth of an independently defined oscillatory mode. H1: a named oscillatory mode receives robust phase-coherent positive cycle work under steady respiratory drive.
- Frozen same pressure/tissue/tract/initial perturbation as VF-1A for first comparison; extend simulation into a declared long duration (candidate >=0.5s, subject to stability) at native dt=1/48k, also dt=1/96k. Include Psub=0 negative control, other pressures only with preregistered ranges.
- Measure signed full tissue/aero/acoustic power and stored mechanical energy, and independently reconstructed full work ledger; estimate equilibrium only using a disclosed reproducible procedure.
- Report separate x1/x2 amplitude envelopes, phase with p and force, normal-mode projection where valid, and per-cycle work only if cycle timing is identifiable. Reconcile positive late-window full work with decreasing mean-removed displacement; if not reconcilable label UNRESOLVED.
- Verify no 'self oscillation' from initial transient, forcing harmonics, numerical aliasing, sign convention error, hidden imposed periodic area, unstable negative damping, or false PASS after failed tests.

## Conditional follow-up VF-1B2 (new law only if mechanism needs it; separately registered)
H0: current simplified intraglottal pressure law suffices to transfer sustainable oscillatory energy. H1: physically justified lower/upper pressure distribution and flow separation alters the phase-related work enough to change onset, without breaking power accounting.
- Only one law/assumption changes; same mass/damping/source/tract/outlet, independent analytic or experimentally grounded pressure/flow reference, explicit loss/work terms and signed port orientations.
- Compare current-law, candidate-law, no-drive, load-only and invalid-sign/missing-energy negative controls.
- If no credible independent reference or solver convergence: stop, label PHYSICAL_MODEL_INDETERMINATE.

## Decision matrix, no proxy-quality shortcuts
G0 EVIDENCE: hashes, SI trace, signed measurement port, raw/failed archives.
G1 NUMERIC: independent model checks, convergence, work-closure, adversarial controls.
G2 PHYSICAL/BIO: independent aerodynamic reference; otherwise INDETERMINATE.
G3 PHONATION: nondecaying self-driven cycle and response to drive/load intervention; currently NOT ESTABLISHED.
G4 CREATOR: NO-GO; no ear-point WAV, speech intelligibility, timbre or Studio decision asserted.

## Workflow
After creator agreement on this model family, separate science implementation Draft (not main) must update this EXPERIMENT record and sibling SYSTEM/DATA together at each meaningful change; use independent @codex review, exact-head CI and preserved artifacts, then decide ADOPT_LIMITED / REVISE / INDETERMINATE / REJECT. No main/Studio/SMC/ASMR merge as part of this proposal.
