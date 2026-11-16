# HYPOTHESES — preregistered claims and counterclaims

D0 2026-11-04, before RP1 evaluator implementation.

### H1 — operation-specific type safety
A discriminated evidence union and explicit measurement and acoustic references detects incomplete or contradictory data before any counterfactual solver call.
**Falsifier:** an uncalibrated pressure-only HRTF receives changed-load permission, a measurement-plane mismatch passes, or unknown rights passes a requested distribution gate.

### H2 — intrinsic pressure-only nonidentifiability
For a one-port Thevenin source with pL=ps ZL/(Zs+ZL), a single pressure measurement under known ZL does not generally identify (ps,Zs). Fix the **dimensionless analytic** fixture:
- A: ps=1, Zs=0; B: ps=2, Zs=1.
- At baseline ZL=1: pL_A=pL_B=1.
- At unseen ZL=2: pL_A=1, pL_B=4/3.
No complex frequency dependence, HRTF inference or human-ear measurement is claimed.
**Falsifier:** under these identical equations and declared fixtures, both counterfactual predictions are forced equal. Numerical implementation error is not falsification of the mathematical derivation.

### H3 — bounded synthetic coupling
Given a complete passive Thevenin source/load and unchanged Core 1D transfer matrix, a conditional coupling algorithm predicts source, entrance and terminal complex ports and positive-frequency powers consistently.
**Falsifier:** independent traveling-wave reference, source/load boundary, passivity or power identities disagree beyond registered tolerances.

### H4 — reference-plane invariance
An identical lossless uniform tube represented as one length L or as two same-area serial segments L1,L2 (L1+L2=L) yields the same physical source and terminal fields after appropriate ordered T1*T2 composition.
**Falsifier:** nonzero end-port discrepancy beyond registered tolerance with identical source/load parameters and ordering.

### H5 — measured generalizability (future, NOT Gate A/B)
With genuinely calibrated equivalent acoustic port measurements and preselected unseen load conditions, the calibrated boundary-aware model can predict counterfactual complex end-port responses within metrological uncertainty better than a fixed-response baseline.
**Falsifier:** no prespecified improvement, loss of coverage, power/causality violations, or uncertainty-dominated effect. No fixed dB margin without prior measurement uncertainty and registered study design.

## Separation rule
A pass on H1/H2/H3/H4 yields only a synthetically qualified reference. H5 is a separate new-data study; neither NF5 sealed truth nor source-uncalibrated HRTFs may be treated as H5 evidence.
