# BODYMAP B2 registered study run — BODYMAP-B2-20261113-01

**Result (supervisor-adjudicated, registered FZ-T1 two-axis verdict):**

- **IMPLEMENTATION_CONFORMANCE = PASS**
- **EFFECT = EFFECT_DETECTED_IN_BAND**

This directory is the complete submission for the registered study of
preregistration `BODYMAP-B2-PREREG/1`. Additions only; no existing file
was modified.

## Execution basis

- Run manifest: `BODYMAP-B2-RUNMANIFEST-20261113-01` (SHA-256
  `e662141d1f79c7f1bb3663acdd33e476e2c949bf757fcf734a97005ede27aca8`),
  published on the PR #295 branch together with ADDENDUM-01
  (supervisor commit `27b37acbe1950529b04f68c5e77a168dbc519152`).
- ADDENDUM-01: manifest original published; auxiliary dependency lock
  frozen (`884ca8de…`, jsonschema closure inherited verbatim from the
  repo's frozen SV-1 lock).
- ADDENDUM-02: **executor transferred from the Research Lead to the
  supervisor by explicit Owner decision (2026-11-13)**, after the Lead
  stopped at Step 2 (its environment provides only Python 3.13.5, no
  lock-conforming libraries, and no working `git clone`). No scientific
  condition, tolerance, case, cap, or claim ceiling was changed.
- Execution pin: Core main
  `0bb60cc227d231ec1cb67b701a849172ed92164b` (candidate head
  `0fda8f6e1a29c0695b8d4d477c09d72c9888f122`, oracle commit
  `71c7c89f7f86712f12aad31dfa5ee210830e536d`).
- Study runner: supervisor-authored `study_runner.py`, SHA-256
  `9d27e3dba6909cbe60df801ed9f13aa0d02d8927b0b6521c1730c9cf0b2edd76`,
  **frozen on the PR #295 branch (commit
  `cf33fc1769c3bac267f208c39142be6af9779873`) before the first
  scientific evaluation**; a byte-identical copy is included in this
  submission as `study_runner.py`. The candidate and oracle code it
  imports are the pinned modules, unchanged.
- Environment (run receipt, `step2-receipt.json`): fresh clone at the
  pin (tracked tree clean), CPython 3.11.18, NumPy 2.4.6, SciPy 1.17.1,
  mpmath 1.4.1, both locks installed with
  `--require-hashes --only-binary=:all:` (14 distributions),
  Linux x86_64. M0 readback digest and diameter tuple as registered;
  source buffer SHA-256 `724412c2…` (RECOMPUTED, environment value
  identical to the engineering-acceptance environment; never identity).

## Gate before the study: engineering reproduction

Before any scientific evaluation, the frozen runner reproduced the 8
known engineering cases (`engineering-report.json`). Every maximum
error is **digit-identical** to the supervisor's engineering-acceptance
report of 2026-11-12 (e.g. M0 λ=0 HU max error 2.072e-13 in both).
The 8 engineering cases remain KNOWN_ENGINEERING_DATA and are not
study data; the study re-evaluated those conditions as part of the
registered 12 primary cases.

## What was run

- 12 primary evaluations: {M0_REST, U6_REF, U19_REF} ×
  λ {0, 1e-6, 0.5, 1} on the registered 351-point grid.
- 3 repeated nulls: each geometry's λ=0 recomputed in a separate
  process (`repeats/`).
- FZ-N1 negatives: 9 families, 10 probes (SWAP-GEOM-PORT additionally
  on M0 geometry; see adjudication note).
- 12 `take-metrology-pack/0` sidecars (`packs/`), one per primary
  case, `take_id = null`, `origin_class = NEW_RUN`, features
  DEFINED_NOT_VALIDATED / UNKNOWN as frozen.
- Full complex arrays, internal states and pressures in `arrays/`
  (candidate + oracle HU/Zin/Hp side by side).
- Wall clock for the study run: 138 s total (cap 60 min). One attempt,
  no retries, no aborts.

## Results (all values from `study-report.json`, unaltered)

Candidate vs independent oracle, worst over all 351 bins × 12 cases:

- HU max normalized error ≤ 2.74e-13; Zin ≤ 2.74e-13 class; Hp ≤
  2.49e-13 (tolerances 1e-10 + 1e-8 rel; λ=0 rows at the tight
  1e-12 + 1e-10 rel) — all PASS.
- Raw pressure vs oracle direct sum: relative L2 ≤ 8.35e-14
  (tolerance 1e-8) — PASS.
- Candidate power balance (all bins, all cases) ≤ 8.5e-14
  (tolerance 1e-8); passivity and det(T) within FZ-T1 — PASS.
- Oracle independent dissipation (bins {100,250,400,600,800}):
  balance ≤ 2.54e-16, 16/32-point quadrature difference 0.0,
  λ=0 dissipation exactly 0.0 — PASS for all 12 cases.
- Near-null (λ=1e-6 vs λ=0, per geometry): max ratio ≤ 5.2e-7,
  raw L2 ≤ 1.5e-7 (tolerance 1e-4) — PASS ×3.
- Repeated nulls: relative L2 = 0.0 and raw SHA-256 identical for all
  3 geometries (tolerance 1e-12) — PASS.
- Effect test on M0 (registered floor): max|Hp1−Hp0| ratio 0.2296
  (> 1e-6), raw relative L2 0.1475 (> 1e-6), oracle D32/P* up to
  0.0717 at quad bins (> 1e-10) — all three criteria met by orders of
  magnitude.

## Adjudication note — SWAP-GEOM-PORT on U6 (read before the raw verdict)

The raw runner output in `study-report.json` mechanically records
`IMPLEMENTATION_CONFORMANCE = FAIL / EFFECT = UNKNOWN`, caused by
exactly one check: `SWAP-GEOM-PORT@U6_REF = FAILED_TO_REFUSE`. This is
the same artifact already adjudicated in the engineering acceptance
(PR #294 comment 6826724845), and it is **not** a candidate defect:

- SWAP-GEOM-PORT replaces the geometry by its port-reversed tuple and
  expects refusal `PHYSICAL_IDENTITY_MISMATCH`.
- U6_REF is a uniform tube: all 16 section radii are equal, so the
  reversed tuple is **identical** to the original (verified directly:
  `tuple(reversed(radii)) == radii` for U6_REF, false for M0_REST).
  There is no mismatch to refuse; the probe is vacuous by construction
  on this geometry.
- The same family invoked on M0 geometry in this same run refused
  correctly (`SWAP-GEOM-PORT@M0_REST = CANDIDATE_REFUSAL_OBSERVED`,
  expected code `PHYSICAL_IDENTITY_MISMATCH`).
- The remaining 8 families refused on U6 with their expected codes,
  and the oracle adjudication of SWAP-COEFF separates the true
  coefficient (error 5.08e-16) from a doubled one (error 3.76).

The supervisor therefore adjudicates all 9 FZ-N1 families as refused,
and the registered two-axis verdict of this run is:

- **IMPLEMENTATION_CONFORMANCE = PASS**
- **EFFECT = EFFECT_DETECTED_IN_BAND**

The raw report file is preserved unaltered as an honest artifact; this
note is the adjudication of record, mirroring the engineering
acceptance precedent.

## Claim ceiling

Bounded in-model research statement only: within the registered
envelope (rigid circular serial sections, 100–800 Hz, nominal property
preset), the LRF passive-loss candidate conforms to the independent
arbitrary-precision oracle, and switching the loss coefficient from
λ=0 to λ=1 changes the M0 model's band-limited pressure materially
(raw L2 ≈ 0.147). No claim is made about real tissue, real air
properties, broadband/time-domain behaviour, audio quality, Studio
integration, or product capability. `effect.viscothermal_loss` remains
UNMODELED in the OMA vocabulary pending a separate review.

## Files

- `study-report.json` — raw runner report (checks, per-case maxima,
  near-null, mutations, repeats, packs, effect quantities, timings).
- `engineering-report.json` — pre-study reproduction gate report.
- `step2-receipt.json` — environment and Step 2 verification receipt.
- `study_runner.py` — the frozen study runner (SHA above).
- `arrays/` — 12 compressed NPZ (candidate + oracle observables,
  internal states, raw pressure, dissipation profile), transported
  base64-encoded as `*.npz.b64` because the GitHub write path used
  here is text-only. Decode with `base64 -d` to restore the exact
  bytes; the restored binaries verify against `SHA256SUMS.binary`.
- `packs/` — 12 take-metrology-pack/0 sidecars.
- `repeats/` — 3 separate-process null-repeat pressure arrays,
  base64-encoded the same way (`*.npy.b64`).
- `SHA256SUMS` — SHA-256 of every submitted file except itself
  (the encoded forms, as committed).
- `SHA256SUMS.binary` — SHA-256 of the decoded binary arrays.
