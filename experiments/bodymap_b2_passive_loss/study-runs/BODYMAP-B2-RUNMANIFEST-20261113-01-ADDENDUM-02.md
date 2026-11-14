# BODYMAP-B2-RUNMANIFEST-20261113-01 — ADDENDUM-02

**Executor transfer （実施主体の移管）. Issued by the supervisor after the
Owner's explicit decision, 2026-11-13.**

## Background

- The Research Lead's resume audit (PR #295 comment 6850680679) passed
  Step 1 (manifest / auxiliary lock / ADDENDUM-01 SHA-256 all PASS) but
  stopped at Step 2: the Lead's execution environment provides only
  Python 3.13.5 (the lock requires CPython 3.11.18), library versions
  outside the frozen locks, and no working `git clone`, so a clean
  checkout of the pinned Core tree and the M0 / source verification
  could not be performed there. Scientific evaluations remained 0/15.
- The supervisor's environment satisfies every fixed condition, verified
  by the supervisor's own Step 2 execution (see §3).

## Decision and scope of this addendum

- **Owner decision (2026-11-13, in-chat, explicit): the supervisor
  (Muse) takes over execution of the registered study.**
- The executor of run manifest `BODYMAP-B2-RUNMANIFEST-20261113-01`
  changes from Research Lead to supervisor. Nothing else changes:
  preregistration `BODYMAP-B2-PREREG/1`, the 15 registered cases, the
  FZ-N1 negative families, all FZ-T1 tolerances and verdict rules, the
  known-engineering-data disclosure, all caps, and the claim ceiling
  remain exactly as registered.
- Independence structure is preserved as in the engineering acceptance:
  the candidate code is the Lead's, frozen at the execution pin; the
  independent oracle is the supervisor's own authorship, frozen at the
  same pin; the study runner is supervisor tooling, frozen by SHA-256
  below before any scientific evaluation, and reproduced against the
  engineering acceptance numbers on the 8 engineering cases before the
  study cases run.
- The Research Lead may audit the submitted study artifacts afterwards.
  The result review presentation and any limited adoption remain a
  separate Owner decision; this addendum does not include them.

## Step 2 as executed by the supervisor (2026-11-13)

- Fresh `git clone` checked out at the execution pin
  `0bb60cc227d231ec1cb67b701a849172ed92164b`; tracked tree clean
  (0 changes) before and after the verification snippet.
- Fresh venv from CPython 3.11.18; both locks installed with
  `pip install --require-hashes --only-binary=:all:` (14 distributions):
  NumPy 2.4.6 / SciPy 1.17.1 / mpmath 1.4.1 / pytest 9.2.0 +
  jsonschema 4.26.0 closure per ADDENDUM-01.
- `resolve_geometry("M0_REST")` with `PYTHONPATH=src`: preparation
  digest `sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de`,
  diameters (12,12,26,16,12,14,20,26,30,34,38,34,34,30,28,32) mm,
  lengths 16 × 0.010 m — all as registered.
- `consumed_source()`: lf_fixed buffer 24,000 samples,
  `source_sha256_le_f64 = 724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc`
  — identical to the supervisor's engineering-acceptance environment
  value; qualification stays `RECOMPUTED` (the value is runtime-bit-
  sensitive and is never used as identity).

## Frozen study runner

- File: `run_study.py` (supervisor-authored; modes engineering / study /
  repeat), preserved in this PR branch at
  `experiments/bodymap_b2_passive_loss/study-runs/study_runner.py` and in
  the study submission.
- SHA-256: `9d27e3dba6909cbe60df801ed9f13aa0d02d8927b0b6521c1730c9cf0b2edd76`
- Freeze rule: the runner's bytes are fixed by this addendum **before**
  the first scientific evaluation. The engineering-mode reproduction
  (8 known cases) is run with these exact bytes; if the reproduction
  gate fails, execution stops and any runner change requires a new
  addendum before retrying.

## Submission

Study results are submitted as a new Draft PR adding one study-run
directory (arrays, packs, repeats, run receipt, study report), additions
only. Merge of that PR and of PR #295 each remain separate Owner
decisions.
