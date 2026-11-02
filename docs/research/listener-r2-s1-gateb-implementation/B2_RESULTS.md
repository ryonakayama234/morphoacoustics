# B2 RESULTS — EL-R2-S1 prospective 24-case numerical audit

**2026-11-02 JST. Research-only scoped numerical decision: FROZEN_NUMERICAL_REFERENCE / LIMITED_SYNTHETIC_ONLY / INDEPENDENT_HUMAN_SCIENTIFIC_REVIEW_PENDING.**
No empirical listener, HRTF, time-domain waveform, perceptual ASMR or Studio capability is demonstrated or adopted.

## Provenance and temporal ordering

1. Prior frozen Gate A original [PR #158](https://github.com/ryonakayama234/morphoacoustics/pull/158), Git blob JSON `f89ccf20cb60019c4487873a13af678e983beb6b`, WL source `fa8c2112f36f2b7119d40e8125e4d979ba091eef`, unchanged. Gate B precursor [PR #233](https://github.com/ryonakayama234/morphoacoustics/pull/233), automated code audit findings and fixes already recorded there.
2. Prospective new E2 design fixed **before oracle generation** in [commit 79012a91b820f073251bdea042217145cde5b8e0](https://github.com/ryonakayama234/morphoacoustics/commit/79012a91b820f073251bdea042217145cde5b8e0). 2 areas × 3 lengths × 4 frequencies = 24 previously unused synthetic cases. This ordering does not produce human/empirical blinding.
3. Separate ECMAScript complex scattering calculation fixed 24 reference vectors in [commit 48c194017ebd0a799bcf6d3321ac3139ada2e449](https://github.com/ryonakayama234/morphoacoustics/commit/48c194017ebd0a799bcf6d3321ac3139ada2e449), authentic Git blob SHA `0c3476899de4d3cdeaad46816895b8318b43cde0`. The generator `rebuild_b2.mjs` contains the source of the independent algorithm; `verify_b2_generated.py` checks regenerated rows, metadata, identity and the actual pinned Git blob.
4. No modification to Core, existing 18-point oracle, original frozen acceptance conditions or Studio. This B2 research is a Draft PR stacked on existing Gate B #233, not on main.

## Exact numerical evidence

**Successfully executed at code head `68a0ab04fb5386b823385aa8ea14197d0976d726`** in [pull_request GitHub Actions run #41381928145](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41381928145) (Python 3.11 and 3.12, both SUCCESS). The matched push CI [#41381922316](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41381922316) also SUCCESS.

- Primary original Gate A: original 18/18 independent Wolfram JSON rows retained and tested; exact original JSON/WL pin verified by predecessor tests.
- Prospective B2: **24/24** extra conditions pass full complex pressure/volume-flow comparisons, four powers, two source/tube energy balances, and phase/linear-source scaling controls.
- Cross-language independent reference regeneration via Node.js: **PASS** both matrix versions; maximum pressure component deviation (rebuilt vs original JSON) `1.1102230246251565e-16 Pa`; scaled flow component deviation `3.43304769627883e-17 Pa`.
- Largest Python Core-matrix vs independently frozen ECMAScript-traveling-wave error over 24 B2 rows, both Python versions:
  - Pressure component: `7.771561172376096e-16 Pa` (preregistered ≤1e-11 Pa).
  - Volume-flow component after multiplying by reference Zc: `2.9180905418370057e-16 Pa` (≤1e-11 Pa).
  - Mean power: `2.9778502051908996e-23 W` (≤max(1e-13 W,1e-10×power scale)).
  - Source conservation residual: `6.617444900424222e-24 W` (≤1e-13 W here).
  - Tube conservation residual: `3.308722450212111e-24 W` (≤1e-13 W here).
- Both CI jobs uploaded exact 24 complex port observations and regenerated oracle JSON. See the workflow run artifact list for separately named Python 3.11/3.12 output.

### Physical interpretation, strictly synthetic

The 24 prescribed points vary A=40/80 mm², L=15/35/45 mm and f=750/2200/5100/7900 Hz at unchanged **absolute** source/terminal impedances. The complex entrance pressure is *solved*, not fixed. Independent analytic wave calculations show substantial geometry- and frequency-dependent terminal amplitude even with the same synthetic drive.

For 2200 Hz: with area 40 mm², terminal magnitudes by L 15/35/45 mm are approximately 0.636812/0.587081/0.589277 Pa; area 80 mm² gives approximately 0.490606/0.353640/0.357927 Pa. The range of |pL| over the entire 24-case numerical grid is approximately 0.353640–0.665053 Pa; the largest/smallest ratio is 1.88059, or 5.486 dB. **These are not perceived loudness differences, measured ears or real source pressure fields**. Changing geometry also changes source loading; the condition is a synthetic equivalent Thevenin fixture, not "same real free sound field".

Phase is retained as a complex phasor, so any replacement by pure magnitude, phase-only shortcut or naive filter concatenation is scientifically unauthorized. Energy conservation only holds because the studied tube is mathematically lossless; source internal resistance dissipates nonzero power and must be accounted separately.

### Adversarial tests

The suite tests nonfinite raw observation fields and mutation of output pL/uL, source-resistor dissipation, all-zero derived transfer triples, wrong port reference plane, source amplitude 0.5×/2× and phase rotation e^(i0.63) at three distinct fixtures, plus single-scalar mutations in the independent reference. Existing predecessor PR #233 includes the original 18-case source-match length/phase null, ideal source, fixed versus normalized load comparison, invalid/unsupported/numerically unresolved inputs and other mutation tests.

### Decision and limits

**Decision: GO_LIMITED_NUMERICAL for frozen, synthetic lossless 1D reference only**. This does not promote the candidate into the `morphoacoustics_asmr` runtime or Core public contract. Independent science/architecture **human** review remains outstanding, even after ordinary CI or automated code review. It is legitimate to use as a reproducible comparator for future experiments, not a verified ear model. Physical accuracy, near-field HRTF reference planes, calibration, viscothermal loss, ear geometry and perception require new preregistered gates and measured evidence.

Reproduction:
```bash
python -m pip install -e '.[dev]'
python -m pytest -q tests/test_experiment_el_r2_s1.py tests/test_experiment_el_r2_s1_b2.py tests/test_acoustics_uniform_tube.py
node experiments/044_el_r2_s1_source_load/rebuild_b2.mjs > /tmp/el-r2-s1-b2-rebuilt.json
python experiments/044_el_r2_s1_source_load/verify_b2_generated.py /tmp/el-r2-s1-b2-rebuilt.json
python experiments/044_el_r2_s1_source_load/run_b2.py /tmp/el-r2-s1-b2-results.json
```

Claim classification: synthetic computation and CI **observed PASS**; physiological/psychophysical validation **NOT TESTED**; public API **NOT ADOPTED**; production Studio **UNCHANGED**.

## Post-implementation independent automated code review (2026-11-02)

An automated Codex review of PR #275 at `f16a29e` found one **P2 fail-open audit defect** (see [discussion](https://github.com/ryonakayama234/morphoacoustics/pull/275#discussion_r4438615245)): `verify_b2_generated.py` compared arrays using `zip(left,right)` without verifying full row width; a regenerated row containing just A/L/f could be falsely accepted, because all scientific outputs were silently skipped. This is a verification **false positive**, not evidence that the underlying Core solver or 24 genuine results were numerically wrong.

**Remediation (not part of preregistered Gate A):**
- Commit [0d5e8c2](https://github.com/ryonakayama234/morphoacoustics/commit/0d5e8c23f3ca60ca156c2cbe72c6a7b0a40cb7cd): compare exact 15-column width and row type *before* zip, on both frozen and regenerated records.
- Commit [fc5040f](https://github.com/ryonakayama234/morphoacoustics/commit/fc5040f2e2982e8cb742822e17984ec264a1d30e): regression test that truncates every regenerated 24-row sample to just A/L/f and requires explicit failure. No relaxation of the immutable numerical tolerances.
- Initial acceptance at previous code head `68a0ab0` is historical; subsequent code changes need current-head CI. [Corrected-head push CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41382492216) reported SUCCESS, including Python 3.11/3.12, frozen 18 and 24, cross-language regeneration; separate [PR workflow](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41382499053) was triggered for corrected head. The latest head must be inspected after this document-only commit; no blanket CI claim is carried across SHAs.
- New guard also rejects malformed/nonfinite 24-row input and changed absolute source/load/air parameters in the 24-row audit (commit [2be6c6d](https://github.com/ryonakayama234/morphoacoustics/commit/2be6c6de63af62d4ff2d054e414fc8a174d509c9)). The prior original 18-row oracle has not changed.

**Audit interpretation:** the review identified a real quality-control vulnerability which the regression now reproduces and prevents. Any independent review still applies to this final amended code; automated Codex findings are not a substitute for independent physical auditory-science evaluation.
