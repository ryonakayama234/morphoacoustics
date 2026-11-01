# EL-NF5 G0-A — access/qualification controls

**G0-A evidence only.** No authorization to obtain the KU100 ZIP, individual SOFA, NHK IR, or acoustic truth, even if a publisher publicly offers downloads. The public publishers' textual pages/papers, indexed file lists and their listed MD5 values were inspected; these are *not* original HRIRs. This file defines future gates; it is NOT an authorization to run them.

## Present controls (effective for #265)
- No original measured HRIR/SOFA/raw audio download/open, no Data.IR, Data.Delay or signal extraction, no simulated file access, no SHA256 falsely represented as calculated.
- No geometry split generated from original files or finalized based on acoustic observations; **G0-B is separately gated**. A paper's grid count is not a verified SOFA coordinate manifest.
- No Core, SMC, `asmr/` adapter, Studio, experiments, tests or CI change; no model training, numerical scoring, listening or human-subject signal release.
- Use public publisher documentation and article statements only, with linkable evidence and explicit nulls for missing claims.
- Do not put restricted raw response/individual human traces, source SOFA, or reconstructive models in GitHub.
- Preserve prior NF4 failure and old final-data exposure. Repackaging a KU100 mirror as different corpus, or resplitting SCUT/KEMAR/Aalto opened final, is not independence.

## Next gate, not yet authorized
For any candidate K1/N1 to become `QUALIFIED_LIMITED`, issue a specific new scope authorization before obtaining original files. In an access-controlled, non-repo environment:

1. Resolve original publisher/file rights, version/identity, download and analysis authorization, explicit attribution/SA conditions, model/derivative distribution restrictions; independent rights reviewer signs off. CC BY-SA grants broad reuse subject to conditions; do not assume 'noncommercial' or 'unrestricted commercial Studio output'.
2. Record controlled location and file names, publish ONLY non-reconstructive receipt and locally **computed** original SHA256; if mirror compared, record cryptographic equivalence. Keep blind final truth inaccessible to model builders until prediction seal.
3. Audit SOFA coordinates, units, radii, listener/receiver physical plane, left/right, true `Data.Delay`/time-origin policy and sampling/FIR dimensions. The paper's measurement distance to *ear-canal entrance*, the 128-tap compensated response, 200-Hz replaced bass, equalization and inter-radius gain normalization require **special attention**. If physical propagation time was removed, limit H1 to qualified relative/ITD claims or stop the arrival-time claim; do not fabricate common-delay truth.
4. Address robot arm rear shadow and near-source interference prospectively. If excluding angular blocks by known setup geometry, register exact exclusions **without peeking at signal outcomes**; report exclusion count and reduced target scope.
5. Establish a truly new independently measured original vs NF1–NF4; distinct URL is not sufficient. Verify each condition's >=8 effective independent spatial blocks, angular buffers, radius bracketing and predicted support denominator without using acoustic data.
6. On **separate G0-B authorization**, seal deterministic geometry-only fit/selection/calibration/final roles, all query IDs and split hash before acoustic signal access. Final acoustic truth remains hidden through model selection, support calibration and prediction-hash sealing. Assess S1 (spatial angular holdout) and S2 (angular + interior radial shell) separately.
7. On further **separate** G1/G2 authorization, build/test algorithms using synthetic and prior-exposed development data; do not turn that into independent G3b. Apply the original D0 baseline B0, strongest B*, 15%/80% gates, paired bootstrap, safeguards unchanged.

A permission ambiguity, unclear absolute/relative measurand, missing original source, absent honest radial/angle split, or premature final acoustic access is a **STOP**, not a conditional numerical PASS. Independent science reviewer and owner approval remain necessary for any component freeze; production adoption requires its own optional versioned adapter authorization.

## Provenance and integrity semantics
- Published MD5 (e.g. Zenodo ZIP) is **publisher metadata**; it is **not** a checked `sha256`.
- A publicly visible download listing is not an acquired verified file.
- Original acoustic values cannot be said 'sealed' until access-control and verifiable prediction sealing are demonstrated.
- Research, redistribution and any Studio adoption rights are separate determinations.
