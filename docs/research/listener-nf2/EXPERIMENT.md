# EL-NF2 — reproduction and evidence

Execution plan (WSL2/Linux, Python 3.11+):

1. Freeze this directory's PREREGISTRATION.md in a dedicated Git commit, record that SHA in subsequent reports.
2. Add standalone experiment Python runner, synthetic tests, evidence auditor, GitHub Actions workflow. Do not borrow unmerged #252 implementation.
3. Download original Zenodo 7316545 `NF_LIB_HRTF_measured.sofa` in CI, require exact original MD5, store measured SHA256 in result. No vendoring.
4. Score validation-only directions while model implementations are checked. Do not inspect final test directions until code/choices fixed.
5. Run final held-out directions exactly once for model selection (no after-the-fact tuning), archive JSON evidence as Actions artifact; arithmetic-audit every record and no-leak split.
6. Document all numerical failures, supported directional coverage, model selection and claim ceilings in RESULTS.md / DECISIONS.md.

Expected command after implementation: `python experiments/046_el_nf2_spatial/run.py --sofa /tmp/NF_LIB_HRTF_measured.sofa --output /tmp/el-nf2/evidence.json`. Required environment `pip install -e '.[dev]' scipy h5py`.

Synthetic tests verify identity reconstruction, identical left/right, known geometric delays, heldout-direction non-leakage, invalid/out-of-domain geometry, and evidence mutations. Synthetic tests do not constitute measurement accuracy or perceptual validation.

Runner should make a finite JSON evidence even for a numerical `REVISE_OR_REJECT` and CI should fail for invalid metadata, SHA mismatch or evidence arithmetic inconsistency. No auto merge.
