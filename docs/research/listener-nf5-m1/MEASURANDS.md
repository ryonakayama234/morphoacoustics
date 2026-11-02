# MEASURANDS — what is actually observed
## Formal object
At stationary identified artificial head H and measured source coordinate q=(r,az,el), define `h_e[n|q,H,C]` per measured channel e∈{L,R}, recording convention C, original sample rate Fs=48000 and FIR length N=128. The observable is the **published postprocessed measurement-plane channel response**. It is not eardrum pressure or absolute source-to-ear Green's function.
## Qualification questions and evidence
| ID | Measurand | Current evidence | Required to assert |
|---|---|---|---|
| Q1 | physical TOF, stored FIR origin, ITD | [270] Data.Delay shape (1,2) shared across positions; 128 samples = 2.66667ms vs 1.5m/c=4.373ms, publisher postprocessing | original pre/postprocessing timeline and calibrated reference, independently reviewable; unknown common shift does not automatically invalidate interaural lag |
| Q2 | L/R channel identity and measured plane | ReceiverPosition [2,3,1] cartesian metre; SOFA defaults not proof of actual KU100 mic plane | edition-specific publisher recording geometry and channel wiring; independent review of any channel-specific processing |
| Q3 | distance gain and reference | publisher factors at r=[0.25,0.50,0.75,1.00,1.50] m [1,.33,.25,.16,.095], relative and rounded | exact edition and precedence of gains, preamps/equalization; no Pa absolute interpretation without calibration |
| Q4 | 500–8000Hz spectral validity | 48k/128=375Hz native DFT spacing; 500–1000Hz has one native bin (750Hz); 200Hz bass extension | scientifically justified 500–1000Hz uncertainty and source/equalization/window study; zero-padding is not information gain |
| Q5 | genuinely new sealed independent geometry | original KU100 four shells and 2702 directions each | geometry-only bounded split + buffers, >=8 effective final blocks per S1/S2; same HATS ≠ new humans |
| Q6 | rights: research / redistribution / derivatives / commercial | paper CC BY-SA 4.0, embedded original SOFA CC 3.0 BY-SA mismatch confirmed in [270] | edition-specific interpretation and independent rights review; scientific viability ≠ commercial permission |
## Quantities and sign
`tau_c=(tau_L+tau_R)/2`; `delta_tau=tau_R-tau_L` (positive = right later). No physical absolute travel-time claim unless Q1 PASS. Measured ITD is a particular preregistered signal estimator with finite temporal uncertainty, not an assumed anatomical distance.
`m=.5(ln|H_L|+ln|H_R|)`, `ell=ln|H_L|-ln|H_R|`; `ILD=(20/ln 10) ell` for per-frequency amplitudes; band integrated `ILD_b=10 log10[(E_L,b+eps)/(E_R,b+eps)]`, with common mask and training-only eps. Common gain cancels from ideal ILD, ear-specific gain does not. Common time shift cancels ideal relative ITD, ear-specific delay does not.
A finite 128-tap measured HRIR may have an arbitrary analysis origin and endpoint; a real/causal reconstruction is relative to that declared window. A bare FFT round-trip does not establish physical causality, passivity, eardrum calibration or minimum phase.
## Status
Q1–Q4 unresolved for physical claims; Q5 needs original-geometry-only job; Q6 RIGHTS_CONFLICT_REVIEW_REQUIRED. Conditional limited *relative stored-channel* modeling remains a hypothesis, not a new qualification verdict. Prior G0-A2's structural validation remains valid.
