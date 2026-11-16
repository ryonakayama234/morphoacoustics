# EL-NF5 G0-A — desk audit outcome (non-acoustic)

**2026-11-01 JST. Public publisher metadata audited; no original HRIR obtained; no G0-B/G1–G5 executed.**

| Candidate | Source existence | Dataset-rights evidence | Scientific/physical adequacy | G0 verdict |
| --- | --- | --- | --- | --- |
| TH Köln KU100 near-field K1 | Primary listing + Zenodo ZIP + individual SOFA index confirmed *at listing level* | **Publisher's 2016 paper explicitly identifies the near-field SOFA+miro set as CC BY-SA 4.0**; per-original-file notices/compliance and derivatives NOT audited | 48-kHz 128-tap postprocessed; distances/grids documented; absolute arrival origin, measured receiver plane, normalization, robot-arm rear shadow and effective independent blocks remain unresolved | **BLOCKED_PENDING_ORIGINAL_AUDIT** |
| NHK 2026 HATS N1 | Technical paper confirmed; no published original IR archive verified | CC BY-ND is **paper-only**; data terms unknown | Reported 27 radii ×865 upper-hemisphere directions; no SOFA details, microphone plane, file hashes or split audit | **BLOCKED_NO_VERIFIED_ORIGINAL_DATA** |
| Aalto/KEMAR/SCUT prior | Existing original final acoustic targets already used in NF1–NF4 | Existing source-specific terms | Only historical development/retrospective diagnostics; no fresh blinded NF5 final | **EXCLUDED_AS_NEW_G3B** |

### Important observation that changes technical risk
The K1 source is a **postprocessed measured-channel surrogate**, not raw distance-dependent free-field/ear pressure. The authors used low-frequency extension and source magnitude+phase correction and truncated responses to 128 taps. The original absolute acoustic time-of-flight may therefore not be recoverable. NF5's H1 arrival time must pass a **measurand viability decision** before it can claim physical absolute arrival timing. Interaural timing may still be evaluable. Published normalization warning is a separate issue for radius-aware level claims. The publisher also flags back-angle support-arm shadow; count it as an instrument/system artifact, not an authentic anatomical cue.

### What was NOT observed
No original file, file header, recording endpoint, channel identity, calibration value, acoustic response, SHA256, measured gain/time factor, effective spatial block count, split hash, support curve, HRIR model prediction, code test, human listening, external science review or rights counsel result.

### Gate state
- G0-A public metadata audit: **DOCUMENTED**.
- G0-A original source qualification: **INCOMPLETE / BLOCKED**, not PASS.
- G0-B geometry-only amendment: **NOT_RUN / NOT_AUTHORIZED**.
- G1/G2 technical code: **NOT_RUN / NOT_AUTHORIZED**.
- G3a development: **NOT_RUN**.
- G3b independent final: **BLOCKED**.
- G4/G5, component validation, optional adapter adoption/Studio: **NOT_RUN / NOT_ADOPTED**.

Only if the owner separately authorizes acquisition/legal/metrology assessment should KU100 proceed to the next G0-A subgate. A candidate that cannot preserve a valid physical timing or plane claim may be limited to ILD/spectral-only model evaluation or be rejected; **reframing requires a prospective documented decision before final truth**.
