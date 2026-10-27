# SMC-6 Gate B — append-only result ledger

Research Issue [#219](https://github.com/ryonakayama234/morphoacoustics/issues/219), Design Draft [#221](https://github.com/ryonakayama234/morphoacoustics/pull/221), implementation Draft [#225](https://github.com/ryonakayama234/morphoacoustics/pull/225).
**NOT a public API / speech-naturalness result / Core physics / Studio UI change / main merge.** Every gate refers to exact code and test SHA.

## 2026-10-27 — inheritance, preregistration, and test-first RED
- SMC5 verified research input `894d2f0d68169e7f794d78be729057b3b31d6017` (limited symbolic software GO only), A0 design HEAD `23134784a96a08ad899bf711bf70702f6159508b`. Source includes unmerged SMC4 B-R Draft #189; research output is explicitly stacked.
- Protocol-first commit **`5ee24e89cf4ca149bea1385d778aaeb3e80a9021`** froze scope, exact mathematical T01–T15, falsifiers and remaining A0 D09 resolutions. No new test or source in this commit.
- Test-only commit **`7084b33906eb10b41a3087895c2edfed5b146aa8`** introduced `tests/test_smc6_stn_preregistered.py` importing the absent module; no `temporal_stn.py` existed.
- **Observed RED, not merely predicted:** GitHub isolated SMC workflow [40501281186](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40501281186), Python 3.11 job 122179296140, completed FAILURE during pytest collection with `ModuleNotFoundError: No module named 'morphoacoustics_smc.temporal_stn'`. Other matrix jobs may have been canceled due workflow concurrency; do not interpret as separate observed red.

## 2026-10-27 — first implementation, observed type-check failure and narrow repair
- First source implementation **`28b996c2f6c5e97fdb721eda2606f6f927c2eb1a`**, only `src/morphoacoustics_smc/temporal_stn.py` added. Existing SMC-3/5 source/public exports and physical Core/Studio unchanged.
- **Observed failing strict mypy:** isolated SMC run [40501595882](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40501595882), Python 3.12 job 122180369294, six errors: nullable diagonal comparison, abstract `object` canonical tuple indexing, and reused name `a` typed as EventAnchor instead of task-id str. Preserve this RED code snapshot. It did NOT establish mathematical solver invalidity.
- Repair commit **`21ef0748f9c30b97190efbdfcc796641c144994e`** only fixes those precise typing/aliasing defects; does not weaken preregistered tests or change mathematical semantics.
- Exact repaired-source SHA CI: isolated SMC, root matrix/typecheck and bounded SV1 **all SUCCESS** (see e.g. workflow [40501605241](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40501605241), isolated [40501605134](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40501605134)). Python 3.11, 3.12 and 3.13 package checks are green. This is limited software/nonregression evidence only.

## 2026-10-27 — independent mathematical oracle
- Additive independent test commit **`a2622da1c2a5e3683b9dc673356cb552dd253375`** adds 8 deterministic small exact 1/20s-grid temporal scenarios. Reference enumerates admissible onset/offset assignments without calling graph code; matches event windows and jointly possible overlap minima/maxima. This is a bounded independent reference, not a biological corpus or proof for all mathematical networks.
- Exact SHA `a2622da1c2a5e3683b9dc673356cb552dd253375`: isolated SMC [40501907561](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40501907561) **SUCCESS**, root tests/typecheck [40501907326](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40501907326) **SUCCESS**, bounded SV1 [40501907394](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40501907394) **SUCCESS**. Duplicate push/PR workflow set also succeeded. Python 3.11/3.12/3.13 SMC package jobs, strict mypy, root tests and physical regression completed successfully.
- T01–T15 preregistered synthetic assertions and additional independent reference cases are encompassed by the package pytest run. Specifically: expected [80,120]ms G1/G2 overlap in T01, extrema pinned in T02/T03, sequential zero in T04, contradictions rejected without witness in T05/T06, authenticated SMC5 exact compatibility in T07/T08, override provenance in T09, permutation in T10, sharing in T11, refusal cases T12/T13, monotonicity T14, direct hand oracle T15.
- **No new SMC phonetic/real-body/audio data**. Run result supports only exact small-scale synthetic temporal reasoning. A green SV1 is a regression check; it is not evidence of new voice quality.

## Final software review / adoption gate
**PENDING exact final documentation HEAD CI and independent GitHub `@codex review`** as of this entry. Status **MORE_DATA_REVIEW**. Do not silently promote to GO based on self-authored tests or previous SMC5's review. If an issue is found, add a separate preregistered counterexample and repair commit; preserve rejected receipts.

## Technical boundaries retained
- Caller submits bounded SMC5 bytes, which are recompiled through its canonical ingress; direct forged symbolic plans/receipts are not trusted.
- COMPATIBILITY imports original hard exact events, anchors and couplings. RESEARCH_OVERRIDE requires conspicuous timing replacement policy and reason, preserving original candidate/timing digest. Both are research alternatives, never indistinguishable.
- Task occurrence identity, TaskGoal source and selected pronunciation are preserved; Task ONSET/OFFSET are symbolic, not muscle onset or audible boundaries.
- Exact Fraction difference-bound consistency, source hash, finite horizon, positive duration, deterministic witness and analytic actual negative-cycle trace are checked.
- Joint overlap min/max uses feasible start/end ordering partitions, not independent marginal bound arithmetic.
- Not supplied: natural language reading, empirical phonetic timing, task-dynamic physical trajectories, oscillator phase, biomechanics, acoustics, listening, MotorScore product ABI or new Studio controls.

## Measurement handoff / next stage
L0 formal graph soundness is an observable here. L1 phonetic gesture data, L2 physical task execution and L3 radiated signal/listening require independent future methods, calibrated instruments, uncertainty and creator acceptance. If software gate passes, next decision should weigh prosodic/phase constraint semantics vs script reading/motor lexicon coverage; neither follows automatically from faster solver development.
