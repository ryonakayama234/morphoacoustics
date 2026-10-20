# SV-1 results — 2026-10-20

**Current engineering verdict: SUPPORT_DURATION_CONTROL (limited numerical/causal), NOT ADOPTED.**
**Creator perceptual Gate: NOT RUN. Independent reviewer Gate: NOT YET APPROVED.**
Issue: [#124](https://github.com/ryonakayama234/morphoacoustics/issues/124); Draft PR: [#125](https://github.com/ryonakayama234/morphoacoustics/pull/125). Claim applies ONLY to frozen CC-A2 M0@1 rest /a/-like, LF 100Hz / Rd1.0, 48kHz, with a prescribed periodic glottal-flow source, not self-sustaining biological vocal-fold vibrations.

## Preregistration provenance

Prior to SV-1 execution, Issue #124 fixed experiment conditions and acceptance distinctions. Its initial static /a/ oracle was **wrongly identified** as 275/2101.75 Hz (the dynamically realized /i/-like endpoint). A **pre-execution** [science correction comment](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6282550015) restored the already adopted frozen Wolfram M0 /a/ rest P1=720.25Hz, P2=1288.50Hz (+/-0.25Hz), per [Experiment028 RESULTS](../028_task_field_morphology_transfer/RESULTS.md). We did not re-fit these peaks to SV-1 WAV.

## Actual execution and engineering correction

Initial CI [run 39364241010](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39364241010) **FAILED** 2/4 SV-1 tests while maintaining exact A/B equal-time float64 source-sample invariance. Independent per-file peak normalization in Experiment013 produces tiny duration-dependent scale differences in overlapping central sample values. This is a confounding extra variable, NOT evidence that the body changes.

The [repair was recorded on Issue #124](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6282636336) after this first exploratory run. Commit [178661f](https://github.com/ryonakayama234/morphoacoustics/commit/178661ff8b0f35e3081902d6eb747b2ba81860bc) derives **one common LF source normalization from the adopted 0.50-second reference** and uses the fixed gain on fresh 0.25-second source and the unchanged 0.50-second source. The preregistered strict bitwise equal-center-source and exact 0.5s legacy LF source gates were **not weakened**. Previously failed CI remains permanently a failure and the new run is post-fix engineering evidence, not prospective independent confirmation.

## Successful exact-code execution

[Dedicated pinned real-physics CI run 39364415813](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39364415813), actual source SHA 178661ff8b0f35e3081902d6eb747b2ba81860bc, Python 3.11 and NumPy 2.4.6:

- SV-1: 4/4 tests PASS, including both true fresh pressure renderings, data/format/sha checks, strict common-center identical source, exact 0.50s old LF source, second deterministic byte-for-byte run and invalid/unknown/symlink/refusal.
- CC-A2: 7/7 real-physics regression tests PASS; adopted physical M0/M1 body, oracle, no audio fallback unchanged.
- CLI: independently recomputed fresh pressure on exact commit; A 12,000 mono PCM16 frames, B 24,000 frames, C 24,000 diagnostic concatenation; all payload SHA-256 confirmed by a separate CI verification step, with one final manifest.json.
- Explicit status in the produced receipt: NUMERIC_GATE_PASS_CANDIDATE_NOT_ADOPTED; listening_gate=NOT_RUN_CREATOR_LISTENING_PENDING; independent_review=PENDING.
- Frozen static /a/ P1/P2 before generation 720.25/1288.5 Hz. The test geometry is exactly CC-A2 prepared M0 rest state, not its task-conditioned /i/-like endpoint. No geometry change between A and B.
- Listening WAV peak normalization is for listening only; raw Pa NPY preserves pressure. C is falsely continuous if presented as an adopted physical run and is explicitly segregated as a diagnostic.

### Archived artifacts (GitHub Actions)

- [Anonymized blind trial ZIP, ID 12238801340](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39364415813/artifacts/12238801340): files trial_01.wav, trial_02.wav and trial_03.wav **without the key**. Archive digest sha256:4e2c287d34de5b0211c6665dd9a2628fd4ae8129171da178e58fe0e220cbc4af.
- [Full raw audit ZIP, ID 12239260316](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39364415813/artifacts/12239260316): source flow, raw Pa arrays, source/geometry trace, normalized WAVs, C diagnostic, full receipt, checksum inventory and answer key. Archive digest sha256:251aba2164a86b0367b0939f277f36aded3f89629c36df649695e3869863d945.

Created 2026-10-20, artifact expiry recorded by GitHub as 2027-01-18. Do not claim the external CI binary files are committed permanently into git; the **runbook, manifest schema, code, quantitative evidence and CI links** are durable while downloadable archive retention is bounded.

## Human test still required

1. Download **only** sv1-blind-listening-trials. Listen without viewing the full audit package or the answer key.
2. For each trial, record unrestricted heard kana/quality first, then whether one sustained onset, two distinct onsets or unknown; note discontinuities, buzziness, perceived naturalness and usefulness.
3. Freeze the responses before revealing trial roles. This is one creator's engineering listening pilot (N=1), **not** population-level vowel identity, naturalness or biomechanical validation.
4. Never mark SINGLE_SUSTAIN_PERCEPT_CONFIRMED_PILOT without an actual report. Existing V4-A creator listening did perceive unwanted segmentation despite its one-run physical implementation, so this Gate is substantial.

## Review and merge blockers

- Get independent review of exact final diff: numerical causality (fixed source scaling vs end-envelope), static vs dynamic claim separation, source/output checksum proof, negative controls, code and output-path integrity, and CI evidence identity.
- Run standard GitHub tests and verify full exact final HEAD (not just the initially passing code SHA). If docs are edited, scientific source/digest remains pinned to exact code; CI must report final HEAD.
- No Studio UX integration or local Windows/WSL2 manual playback was carried out in SV-1. Anonymized WAV files can be downloaded and played by the user, but the human perception evaluation has not yet occurred.
- Keep Draft PR #125 open and **do not merge before independent review and explicit GO_LIMITED adoption**.

Scientific limits: static prescribed tract source/filter model, quasi-stationary overlapping FFT time windows; no self-oscillation, respiration/lung dynamics, articulator inertia, connected /a/-to-/i/ coarticulation, arbitrary vowel duration or universal text-to-speech. Duration is bounded to two exact values.
