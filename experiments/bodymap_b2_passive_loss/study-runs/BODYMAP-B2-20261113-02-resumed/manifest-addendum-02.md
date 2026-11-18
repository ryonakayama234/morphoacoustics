# BODYMAP-B2-RUNMANIFEST-20261113-01 — ADDENDUM-02 (executor)

This is the before-results execution-package freeze, following supervisor ADDENDUM-01 at commit `27b37acbe1950529b04f68c5e77a168dbc519152`. No scientific conditions, numerical tolerances, caps, or scientific module bytes change.

- Exact clean execution checkout: `0bb60cc227d231ec1cb67b701a849172ed92164b`. The package lives OUTSIDE that checkout during execution.
- Runner: `study_runner.py`, SHA-256 `5c7f69b3167b24a38945a36cf5db1a2009adc7abf29d045e92b699f220ef9fa6`. `runner-freeze.json` fixes all input/audit/runner files before any engineering replay or scientific evaluation. Runner uses pinned scientific functions directly; it does not change the CLI, scientific authorization constant, candidate or oracle.
- Original manifest / auxiliary lock / supervisor addendum SHA-256 all matched (`e662141d…`, `884ca8de…`, `6214dba2532d1b567ac1876cabbf84429ffdc42bed26fecf5ef5ef21fffb581f`). Original prereg snapshot is byte-matched at `9a022469…`.
- New Python 3.11.18 venv: both locks installed with `--require-hashes --only-binary=:all:`; exact 14 distributions verified. OS/arch/build configuration and every version are in `preflight-receipt.json`. PYTHONPATH points to Core `src`; repository root is added for research imports.
- Audited OD2 M0 readback succeeded: digest `a98d484f…`, all 16 diameters and lengths matched. Source consumed buffer SHA-256 `724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc`; rfft buffer SHA-256 `a33c54be89317bbd09bd7e07a85f4306260d7a13623318fff2054a54630076d1`.
- Source claims remain RECOMPUTED; same-run input bytes/DFT/output are saved for the supervisor to attest. ACTUAL_RUN_ATTESTED is not asserted by the executor; full_verified_source_state stays UNKNOWN.

## Fixed execution sequence

1. Eight separate known engineering replay workers: U6 all four lambda, U19 0/1, M0 0/1. Full candidate grids, power diagnostics, Muse's unchanged oracle (bulk, as supervisor accepted), all 351 coefficient/primary comparisons and all 24000 samples via direct sum. Rounded supervisor acceptance numbers are reference values, not new thresholds. Only FZ-T1 thresholds gate execution. The accepted oracle's own 400/450-digit certification remains the supervisor's prior engineering evidence; no new independent certification is claimed here.
2. Only if all eight pass: 12 scientific workers in M0/U6/U19 order, each lambda 0/1e-6/.5/1; then three lambda=0 independent-process repeats in M0/U6/U19 order. Exactly one full candidate solve per worker. Engineering arrays are never reused as scientific arrays.
3. One invocation each of the nine pinned candidate mutation probes, all on nonuniform M0 (avoids the known uniform reversal identity). No extra candidate evaluation. These are the engineering-accepted diagnostic probes; independent mutation adjudication, including whether their perturbations fully meet FZ-N1, remains with the supervisor after submission. They must not establish conformance by themselves.
4. Candidate-only near-null/repeat/effect-floor comparisons and fresh-process pack readback. No study oracle or final result adjudication. Formal two axes remain UNRESOLVED × UNKNOWN until the supervisor's next-stage work.

One invocation of this package; no retry with partial results. Wall clock cap 3600 seconds covers orchestration, engineering replay, candidate evaluation and self-checks. Every started worker, exit status, stdout/stderr, partial output and refusal is preserved. All evidence writes are exclusive; no unlinking or overwritten packs. Output source/raw are native little-endian float64, complex arrays in NPZ include explicit HU/Zin/Hp Re/Im. Units and shapes are recorded in packs and the README. No preview gain or WAV is generated.

The old acceptance runner is not executed: its preflight bypass, uniform-port reversal fixture, and unconditional pack unlink were already reported on PR #294. This new orchestration adds guards and uses nonuniform M0, without editing any pinned scientific function.

## Input-audit transparency

The first new input-audit invocation stopped BEFORE any input loader, candidate, or oracle because the audit compared the distribution name `typing_extensions` literally with `typing-extensions`. The installed version was already correct (4.16.0); standard underscore-to-hyphen name normalization fixed the audit. Original traceback is preserved in `preflight-audit-normalization-error.log`. This was an executor audit-script defect, not a mismatch in the frozen environment, geometry, source, or supervisor files; numerical evaluation count at the fix was zero.

This freeze is published on a new Draft PR before starting any numerical replay. No result is yet claimed. Existing STOP evidence in PR #295 is retained unchanged.
