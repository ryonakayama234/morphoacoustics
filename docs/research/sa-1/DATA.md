# SA-1 — DATA contract (proposed only)

STATUS: NOT_RUN. Do not invent measured port traces.

Source: frozen 48,000 samples/s, 24,000 samples (0.5 seconds), exact adopted prepared M0 rest geometry and full 16-section body digest. Exact JET source provenance: 9a79fa616e280de24daab5bfbe3cce57fda92256; preserve original 2026-10-23 failure artifact digest e407612b7706d761e4161633156fa69f3f1c7fe92c18738cd979e91cdbdc259b. A second body is only used when an independently verified prepared M1 binding exists; otherwise mark UNAVAILABLE, not an invented tube.

A future experiment-only manifest should contain exact git SHA, actual CI run, Python/NumPy versions, geometry/section dimensions, density, sound speed, load-impedance model, source controls/seed/flow, experiment code SHA, window/hop/edge settings, diagnosis status, and SHA256 per artifact. A source_head placeholder is NOT provenance.

## Physical data definitions
| Field | Units | Status/meaning |
|---|---|---|
| inlet_glottal_U | m3/s | real source time series |
| residual_noise_U | m3/s | generated source-local perturbation |
| T_U and Zin | dimensioned | reconstructed from fixed transfer matrix |
| U_lips | m3/s | analytical port reconstruction, not a direct CFD flow |
| p_g and p_lips | Pa | analytical port reconstructions |
| radiation_to_observer | Pa s/m3 | declared ideal observer surrogate |
| observer_pressure | Pa | real Core frame_render output |
| listening_pcm | PCM | one frozen common gain, OPTIONAL, not physical authority |

Compare 0–0.50s full-file and 0.05–0.45s steady intervals; freeze taper and bins in the manifest. Record raw RMS in each native unit, source/lip/observer squared-energy ratio >=2kHz, complex gain and phase, hop sensitivity, port power (only when pressure+flow share the SAME port), zero-input output, and superposition error. Source-frequency bins with negligible input are masked and reported; never divide by a tiny FFT value and call resulting spikes a physical transfer.

The JET-P0 <20% observer pressure high-band screen remains a FAILED historical source-candidate criterion, NOT a general physical validity rule. The new SA-1 ratios are diagnostic only. Do not change previous acceptance bounds or normalize conditions independently.
