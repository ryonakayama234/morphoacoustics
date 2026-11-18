# C1-Open RESULTS — local original measured pilot and scope
Date 2026-11-04 JST. **Scientific verdict: STOP_NUMERICALLY_UNRESOLVED_REFINED_GRID**. Local Python 3.13.5 / NumPy 2.3.5; GitHub exact-HEAD CI is a separate gate; no physiological nor audible verification.

| Case, 0.30 ms | Independent full-step energy residual [J] | Independent mass residual [kg] | Tissue final xL,xU [m] | Outcome |
| --- | ---: | ---: | --- | --- |
| N8, Δp=0 | +1.00409e-16 | +3.79492e-22 | (-3.02477e-19, 5.08241e-20) | admitted stationary numerical control |
| N8, Δp=10 Pa | +3.05605e-18 | -6.63037e-24 | (2.25286878e-7, 1.02912161e-7) | admitted bounded numerical control |
| N16, Δp=0 | +9.63852e-17 | +3.47554e-22 | (-8.56363e-20, 2.86709e-20) | admitted stationary numerical control |
| N16, Δp=10 Pa | -1.94818e-18 | -2.76782e-23 | (2.44558677e-7, 1.13859190e-7) | admitted bounded numerical control |

**Blocking negative result:** N32, Δp=10 Pa, mobile wall stopped at 14.3811 microseconds; last accepted outlet characteristic velocity approximately -9.87896e-5 m/s, and a proposed next RK stage crosses the implemented -1e-4 m/s refusal. N64 stopped at 14.0170 microseconds; last accepted outlet approximately -9.77189e-5 m/s. Under same rightward reservoir delta, **locked-wall** N32 control does not show this stop over the corresponding short window. The difference therefore correlates with moving-wall-induced transient at the outflow, not merely a rigid-flow solver explosion. The physical meaning/accuracy of reverse-outlet speed and exact boundary wave interaction remains unqualified.

**Interpretation:** energy cancellation at N8/N16 strongly supports implementation-local accounting under admitted cases, **not grid-independent C1 physical ability**. Tissue x differs between N8 and N16 and the refined cases are rejected; cannot give convergence verdict or a globally valid power-balanced phonator. The microreverse may be a legitimate coupled acoustic transient or boundary/numeric discrepancy; cannot choose between them from these tests. Hidden clipping or reclassifying reverse as admissible post hoc would break A3. 7/7 dedicated `unittest` methods PASS locally, including the *expected scientific STOP* test. No WAV, F0, self-excitation, Studio Take, biology or perceptual quality claim.

The command `run.py` creates actual per-stage raw trace JSON, SHA256 files and failure histories. Consult exact SHA of CI artifacts and workflow runs before promoting local evidence to reproducible branch-head result.
