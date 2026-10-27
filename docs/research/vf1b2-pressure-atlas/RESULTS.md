# VF-1B2 Pressure Atlas / RESULTS — initial Gate-0 evidence, 2026-10-27
Status: LIMITATION IDENTIFIED / NO PRESSURE PHYSICS ADOPTION.

## Reproducible first run
- Research Draft [PR #218](https://github.com/ryonakayama234/morphoacoustics/pull/218); base Core main `e05e3274ad69bfb9202816049f6661a18ba39ec0`.
- [Dedicated first Actions run 40454842893](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40454842893) completed SUCCESS. Run logs explicitly show **13/13 standard-library unittests passed** and the emitted inventory receipt.
- First run was a **pull_request synthetic merge checkout**, with artifact `pressure-atlas-gate0-d49f5a87e566304b3ef3d26d6edfeab0c6e9d042`, ID `12711423367`. This demonstrates checks on GitHub's merge target but is **not** accepted as proof of testing the actual PR source HEAD.
- The workflow was repaired at commit `c91079bdef551aa08e5800a55a72b3dd8f63a798` to explicitly checkout and assert the PR **source** SHA, rather than treat `github.sha` (synthetic merge) as the research HEAD. See [revalidation run 40455098168](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40455098168); check its final conclusion, source HEAD, steps and artifact before claiming exact-head verification. No result from that run is fabricated here.

## Actual research observation from Gate-0 output
The 3 source inventories represent **M5 uniform axial**, **M6 transverse 3D**, and **M5 hemilarynx axial/opposing-wall** literature. At this initial stage the archive contains **zero measured numeric pressure-tap samples**, no paper-verified complete coordinate map and no qualified uncertainty budget or matched boundary-to-solver evidence for any of the 3 candidates. Each returned:
`HOLD_NO_NUMERIC_MEASURED_PRESSURE_PROFILE`.
Top-level outcomes:
- `gate0=SOURCE_INVENTORY_ONLY`
- `g2=INDETERMINATE_NO_INDEPENDENT_PRESSURE_MODEL_COMPARISON`
- `g3=NOT_APPLICABLE_NO_MOVING_WALL`
- `g4=VOICE_NO_GO`

**Positive science result:** the repository now reports missing prerequisites instead of treating a source citation, flow table or plotted curve as a validated pressure field. **NOT achieved:** quantitative intraglottal p(z), matched geometry, pressure-to-wall force, moving-wall FSI, any biological or natural sounding voice.

## Traceability correction during development
The M5 hemilarynx article DOI was initially mistyped as a different Journal of Voice article. Checked against [PubMed 18538986](https://pubmed.ncbi.nlm.nih.gov/18538986/), then corrected to `10.1016/j.jvoice.2008.02.005` in both source inventory and guarded evaluator **before** running initial CI. Its journal issue is Jan 2010 (the underlying article appeared online in 2008).

## Scientific next action (NOT yet executed)
Acquire source numeric p(tap), or independently digitize **one predeclared M5 uniform Fig.2 condition**, audit axes/calibration, measurement uncertainty and digitization uncertainty, then match its geometry and boundary conditions to an independently selected pressure model. Retain M6's 3D cross-width pressure and measured-Q discrepancy as a separate model-generalization challenge. Do not promote G2 by fitting Cd / separation thresholds. Future moving-wall power closure requires its own derivation and independent review.

## Product / causal impact
No Core runtime/OrganGraph/Performance API, Studio approved V2 UI/panel, immutable Take, ASMR or SMC change. The future place for such a source-quality receipt is **existing `research.drawer`** only; physical character audition remains blocked until actual source and acoustic quality gates. Draft PR #218 is not authorized for auto-merge.
