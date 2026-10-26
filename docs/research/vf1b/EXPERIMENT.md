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


## Implementation authorization amendment (2026-10-26)
Creator delegated technical experiments and research PR management. This is the **VF-1B1** independent modal-work audit only; underlying VF-1A equations remain byte-for-byte unchanged. The first comparison is the exact symmetric tissue parameters and equal pressure areas of VF-1A; symmetric and antisymmetric modal coordinates use orthonormal unit vectors. Discrete per-step modal work and damping are compared to stored mechanical energy, plus the exact damped midpoint recurrence for the antisymmetric homogeneous mode. Later intraglottal pressure laws remain **outside scope** pending this evidence. New numeric tests/measurements follow this pre-source amendment. Source parent: VF-1A candidate 2b33bc69835170639fb9127c01dab7b523eff4f3; scientific results not yet run.


## Executed numerical pilot 2026-10-26 (append-only evidence)
**CI history:** Initial [Actions #40323432573](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40323432573) **FAIL**: 5 full experiment cases succeeded but one adversarial test loaded the *prior VF-1A runner module* via an ambiguous Python name `run`; it failed with AttributeError. The scientific receipt correctly remained `NUMERICALLY_UNRESOLVED`; historical RED artifact preserved. Fixed only the test import to use exact file path in commit `a4dd650` and added stored-energy/refinement diagnostics in `ba7bede`. No force/solver/threshold change.

**Verified exact code head:** `ba7bededaa5baba5fd407b1b88dc8af202639d51`, dedicated science [CI #40323754160](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40323754160) SUCCESS with VF-1A plus VF-1B1 pytest and runner, general tests [#40323754127](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40323754127) SUCCESS. Scientific receipt `MODAL_WORK_NUMERICAL_PASS_NOT_A_PHONATOR`; stored evidence artifact id `12650042231`, expiration 2027-01-24. Independent Codex exact-head review requested but NOT completed at this entry.

**Measured SI results:** 0.5s, uniform 800Pa 48k, pressure work to + mode `6.600578070316079e-6 J`, tissue damping + `2.9000250532126776e-6 J`, pressure work to − `0.0 J`, tissue damping − `1.839999999999692e-8 J`. Work minus damping for + is `3.7005530171034016e-6 J`: chiefly accumulated deformation energy at long time rather than persistent oscillatory amplitude. In 100ms demeaned + displacement RMS, `0.10–0.20s = 2.23005965e-6 m` falls to `0.40–0.50s = 1.24382853e-11 m`. Antisymmetric 0.10–0.20s RMS = `2.82262069e-7 m` falls to `1.28573484e-11 m` by 0.40–0.50s. The anti mode follows independent damped midpoint recurrence at every step; largest accumulated comparison error at 48k is `1.4146231e-13` in the mixed-position/velocity norm (different units; **not** a physical metric). No biological voice/onset claim.

**Load and resolution controls:** 800Pa 48k constricted + work `6.63051976934795e-6 J`, anti work 0 J. Zero-pressure at 48k yields + work numerically ~0 and anti work exactly 0 J. Uniform + work at 24k / 48k / 96k respectively `6.600568496127396e-6` / `6.600578070316079e-6` / `6.600580465382849e-6 J`; successive difference ratio ~0.25016. This ratio is an **observed convergence diagnostic**, not a post-hoc new PASS threshold. These tests show one model family and one state trajectory, not physiological generality.

**Decision:** VF-1B1 symmetric modal split and pressure-work audit `NUMERICALLY_SUPPORTED_LIMITED`, physiological validity `INDETERMINATE`, sustained self-oscillation `NOT_ESTABLISHED`, audio/Studio `NO-GO`. A later VF-1B2 pressure distribution proposal requires a **separately preregistered, work-conjugate force law and independent physical reference**; changing spring or audio gain is not acceptable.


### Dimensional audit follow-up — verified 2026-10-26
A separate measurement-science self-audit identified a **units defect in an auxiliary oracle diagnostic**: the L2 norm of displacement [m] plus velocity [m/s] was not a legitimate SI-valued error. Existing numeric pass already relied on the physically separate energy equations; nonetheless the mixed metric is retired rather than silently relabeled. Source `modal.py`, `run.py`, tests were corrected in `510a0b6`, `629da03`, `2c021b2`. No pressure/tissue/flow equations or numerical acceptance threshold were changed. [Dedicated CI #40324496663](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40324496663) and general tests SUCCESS at `2c021b2b0978d4945bf23c27083fd3ea02e94811`. At 800Pa 48k, maximum trajectory analytic positional error = `2.2803515280025874e-16 m`; velocity error = `1.4146230844711005e-13 m/s`. Both replace the formerly misleading mixed-unit norm. Original failed tests, initial valid-physics traces and corrected archived evidence remain visible. Scientific disposition unchanged: symmetric model numerical measurement SUPPORTED_LIMITED; biology INDETERMINATE; sustained self-oscillation NOT ESTABLISHED; creator voice NO-GO.
