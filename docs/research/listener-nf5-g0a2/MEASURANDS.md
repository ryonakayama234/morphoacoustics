# Measurands and falsifiable qualification rules Q1–Q6

| ID | Physical claim at issue | Admissible evidence | STOP / bounded conclusion |
|---|---|---|---|
| Q1 TIME | physical propagation arrival, absolute zero and stored/common delay | publisher processing chain; SOFA Delay semantics; independent reference-plane/clock audit | Presence of `Data.Delay` proves no absolute arrival. If phase compensation/trimming removes origin, absolute arrival UNSUPPORTED; ITD separate |
| Q2 BILATERAL | measured-relative L/R, ITD, ILD | receiver plane, orientation, channel identities, channel-specific normalization | Unknown L/R or independent corrections -> BLOCKED. Symmetry/shape alone does not prove channel labeling |
| Q3 LEVEL | distance gain and pressure ratio | exact publisher gain note + capture/preamp/equalization records, edition-specific file provenance | Gains are relative to the dataset's 0.25-m reference, NOT absolute Pa calibration |
| Q4 WINDOW | 128-tap 48-kHz response adequacy for registered 500–8000 Hz band errors | processing/window method, effective time aperture and low-frequency replacement, independent metrology | Zero padding creates FFT samples, not new independent information; metadata only cannot PASS spectral fidelity |
| Q5 SPLIT | new independent held-out angular/radial data | dataset identity; *later* G0-B geometry-only manifest with blocked regions, buffers, >=8 independent accepted spatial blocks per S1/S2 | G0-A2 cannot seal geometry or claim independence of many positions as multiple heads |
| Q6 RIGHTS | right to inspect vs redistribute source, coefficients and use commercially | 2016 publisher explicit dataset CC BY-SA 4.0, edition/file notices, attribution/ShareAlike and derivative rights review | Publisher declaration supports scoped research intake, not blanket commercial/API adoption. Independent legal review pending |

## Measurand hierarchy
- `PHYSICAL_TOF`: difference between physical propagation time and calibrated recording-origin time; **NOT QUALIFIED**.
- `STORED_FIR_TIME`: 128-tap array local origin; not equivalent to `PHYSICAL_TOF`.
- `ITD`: right-minus-left lag under a preregistered estimator; may remain evaluable after common corrections but not guaranteed.
- `ILD`: log spectral energy difference between L/R; a common gain cancels but independently modified L/R does not.
- `RADIUS_GAIN`: publisher-provided restoration factors differ by radius; not an absolute sound pressure measurement.
- `RECEIVER_PLANE`: source-to-ear-entrance laser alignment reported; not proof that SOFA numerical origin equals ear canal entrance or an ear-drum measurement.

## Numeric dimensional audit (analytic, not measured response)
At `Fs=48000`, `N=128`, duration `N/Fs = 2.6666667 ms`, native DFT spacing `Fs/N = 375 Hz`. Free-space 1.5 m / 343 m/s is 4.37318 ms, which exceeds the stored local FIR window; this does **not** prove loss of delay when separate metadata or preprocessing may encode it. The original 500–1000 Hz band includes one native 128-point DFT bin (750 Hz); integrals/dense FFT samples can be calculated but cannot manufacture independent information. The band fidelity must be evaluated scientifically, not deduced as false from the spacing alone.

## Model-facing consequences (future, not implemented)
If Q1 fails but Q2 is qualified, a prospectively amended NF5 claim could be limited to relative ITD. If Q3 fails, no distance-dependent absolute SPL. If Q4 cannot pass, no confirmed quantitative 500–1000 Hz claim. If Q5 fails, no independent G3b. No reinterpretation after final acoustic-truth exposure. Existing D0 primary B0/B*, 15% ILD improvement, 80% per S1/S2 coverage, block/bootstrap, time/spectrum guards remain unchanged until separately reviewed prospective amendments.
