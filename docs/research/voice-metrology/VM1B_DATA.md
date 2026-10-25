# VM-1B research data and units

**Status: candidate instrumentation schema, NOT an adopted public model or Character Creator contract.**

```text
VM1BReport {
  schema_version: "voice-metrology-loaded-transfer/vm1b"
  scope: "RESEARCH_ONLY"
  physical_quality: "INDETERMINATE_REAL_RADIATION"
  voice_quality: "VOICE_NO_GO_UNCHANGED"
  frozen_exp028_blob_sha1: exact Git blob SHA1
  frozen_exp028_content_sha256: exact bytes SHA256
  source: {volume_m3, native_clock_rule, pulse_position_tick}
  parameters: {rho_kg_m3,c_m_s,cells_per_section}
  analytic: {case,body,termination,freq_hz,complex HpU [Pa s/m3],
             complex Zin [Pa s/m3],complex HU [1],
             load_Y_s_m3_per_Pa}
  native: {case,body,termination,native_clock_hz,dt_s,N,duration_s,
           source_digest_sha256, geometry_digest_sha256,
           freq_actual_hz, bin, each complex FFT p/U}
  comparison: {case, each complex rel_err, per-port gate,
               exact finite-record vs infinite-response flag}
  refinement: {model,frequency,cells=2/4/8,continuous_reference,
               convergence_errors}
  negative_controls: {silence,body_mismatch,wrong_load,nonfinite}
  limitations: {no real-radiation validation, no wall, no oscillator,
                no receiver, no quality adoption}
}
```

- Anatomy identity: independent loaded transfer rereads original immutable Experiment028 and checks byte-exact Git blob SHA1 `7810dfbb72cb6c41af007db6e9d51c58cad9a522`. Never copy the section-area numeric fixture into this document or repair mismatch.
- Explicit SI quantities: p [Pa], U [m3/s], Z=pressure/volume flow [Pa s/m3], Y=volume flow/pressure [m3/(Pa s)], frequency [Hz], dt [s], stored energy [J]. B0 `m` has [Pa s²/m3], `R` [Pa s/m3].
- Data `H_pU` means boundary **pressure** transfer, `H_U` boundary **volume-flow** transfer, `Z_in` input impedance. Never substitute particle velocity or radiated pressure.
- DFT complex values stored with real/imag components, actual target-nearest bin, rather than amplitude and 'formant' alone. Case labels are historical frozen body/termination references, not user-local Take UUID mappings.
- Physics state, body blueprint, prepared rest state, analysis output, Take and Studio UI selection are separately owned. This instrument reads the original Core physical waveguide; nothing in this report owns Studio panels or data.


## Executed-code identity amendment (2026-10-26; Codex P2 remediation)

The original candidate report did not disclose the **actual** checkout that executed the physics. The implementation now emits:

```text
execution_provenance:
  executed_checkout_git_sha: 40-hex exact `git rev-parse HEAD`
  executed_git_tree_sha: 40-hex exact tree
  executed_commit_parents: [] or [parents] (PR Actions often check out a synthetic merge commit)
  tracked_tree_clean: true (refuse dirty tracked worktree)
  is_pull_request_merge_commit: boolean
  executed_implementation_files_sha256:
    tools/vm1b_loaded_reference.py
    tests/test_vm1b_loaded_reference.py
    src/morphoacoustics_waveguide/passive_waveguide.py
    src/morphoacoustics_waveguide/__init__.py
    src/morphoacoustics/physical/tract1d.py
    src/morphoacoustics/physical/__init__.py
    .github/workflows/vm1b-loaded-reference.yml
    pyproject.toml
historical_base_main_sha_not_executed_sha: fixed historical reference only
```

The run refuses a non-identifiable git checkout, dirty tracked files, or a mismatch between actual `git HEAD` and GitHub Actions `GITHUB_SHA` (if supplied). **The merge checkout SHA is not automatically the feature-branch HEAD**; preserve exact evidence coordinates instead of mislabeling them. This is traceability of the executed code, not proof of biological validity.

The CI now uploads whatever JSON is present **even if previous numerical steps failed**, and produces a separately labeled `SYNTHETIC_FAILED_GATE_ARTIFACT_CONTROL` JSON after an intentionally failing CI step. Synthetic controls must never be counted as physical measurements, scientific PASS or genuine measured failures. The ordinary full report still has unchanged measured physics ports and gate outcomes; the negative-control file is explicitly annotated.
