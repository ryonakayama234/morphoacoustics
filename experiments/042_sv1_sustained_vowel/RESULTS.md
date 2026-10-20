# SV-1 results — 2026-10-20

**Current engineering verdict: SUPPORT_DURATION_CONTROL (limited numerical/causal), NOT ADOPTED.**
**Creator pilot Gate (N=1): 0.50s B perceived as one desired long あーー; 0.25s A heard as あ,あ,あ (single-onset perception NOT confirmed); C diagnostic splice heard as bumpy, not clearly two natural syllables. Independent exact-HEAD review Gate: NOT YET APPROVED.**
Issue: [#124](https://github.com/ryonakayama234/morphoacoustics/issues/124); Draft PR: [#125](https://github.com/ryonakayama234/morphoacoustics/pull/125). Claim applies ONLY to frozen CC-A2 M0@1 rest /a/-like, LF 100Hz / Rd1.0, 48kHz, with a prescribed periodic glottal-flow source, not self-sustaining biological vocal-fold vibrations.

## Preregistration provenance

Prior to SV-1 execution, Issue #124 fixed experiment conditions and acceptance distinctions. Its initial static /a/ oracle was **wrongly identified** as 275/2101.75 Hz (the dynamically realized /i/-like endpoint). A **pre-execution** [science correction comment](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6282550015) restored the already adopted frozen Wolfram M0 /a/ rest P1=720.25Hz, P2=1288.50Hz (+/-0.25Hz), per [Experiment028 RESULTS](../028_task_field_morphology_transfer/RESULTS.md). We did not re-fit these peaks to SV-1 WAV.

## Actual execution and engineering correction

Initial CI [run 39364241010](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39364241010) **FAILED** 2/4 SV-1 tests while maintaining exact A/B equal-time float64 source-sample invariance. Independent per-file peak normalization in Experiment013 produces tiny duration-dependent scale differences in overlapping central sample values. This is a confounding extra variable, NOT evidence that the body changes.

The [repair was recorded on Issue #124](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6282636336) after this first exploratory run. Commit [178661f](https://github.com/ryonakayama234/morphoacoustics/commit/178661ff8b0f35e3081902d6eb747b2ba81860bc) derives **one common LF source normalization from the adopted 0.50-second reference** and uses the fixed gain on fresh 0.25-second source and the unchanged 0.50-second source. The preregistered strict bitwise equal-center-source and exact 0.5s legacy LF source gates were **not weakened**. Previously failed CI remains permanently a failure and the new run is post-fix engineering evidence, not prospective independent confirmation.

## First repaired exact-code execution (historical; C diagnostic implementation later strengthened)

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
- No Studio UX integration or local Windows/WSL2 manual end-to-end Studio playback was carried out. Creator listened to the generated WAV files in Windows and provided the qualitative N=1 report below; no formal multiple-listener hearing validation occurred.
- Keep Draft PR #125 open and **do not merge before independent review and explicit GO_LIMITED adoption**. The creator delegated the adoption decision provided blockers are fixed and perception limits are recorded; the independent current-HEAD reviewer must still finish.

Scientific limits: static prescribed tract source/filter model, quasi-stationary overlapping FFT time windows; no self-oscillation, respiration/lung dynamics, articulator inertia, connected /a/-to-/i/ coarticulation, arbitrary vowel duration or universal text-to-speech. Duration is bounded to two exact values.

## Second engineering audit: C must contain two independently rendered source/pressure calls

The first passing artifact at 178661f created diagnostic C by duplicating the A PCM buffer; while it was a valid **audio splice negative control**, it did **not** satisfy Issue #124's stronger preregistered wording of two independently calculated short voice performances. This discrepancy was disclosed on [Issue #124](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6282712034), not silently reclassified as a scientific success.

Correction: [commit ca3e92b](https://github.com/ryonakayama234/morphoacoustics/commit/ca3e92bc21e6615b2fa5003b4ab83181ae5b9816) creates a NEW 0.25s LF source and a NEW static-tract pressure rendering as component C_second. Its source, raw pressure Pa, WAV and trace are archived separately. Frozen deterministic matching with component A is an explicit hard gate, after which the distinct PCM payloads are concatenated for **C diagnostics ONLY**. The combined C waveform is still **not** a single physical speech act. [Test update 1918ef4](https://github.com/ryonakayama234/morphoacoustics/commit/1918ef4f33d17d106032cda835022e35f022e8c2) requires C_second actual source and pressure arrays and concatenation bytes.

[Corrected real-physics CI run 39365052298](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39365052298) at source/test commit 1918ef4: PASS. Dedicated normal/core regression and full reproducibility re-run; this supersedes the earlier 178661f artifact as the most scientifically complete SV-1 research realization.

- [Corrected blind listening ZIP artifact 12239062649](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39365052298/artifacts/12239062649), sha256:55a6bd4cf8d8fd2eed11820bbc3754fd75d4bb40a4ca594479444cd1c8ccd668.
- [Corrected raw research ZIP artifact 12239420270](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39365052298/artifacts/12239420270), sha256:66dbb3fe4dd055d51f1148286ac775305b67f4f33d5eb78173854153000469c8; includes C_second physical arrays and receipt.

**Source and output physical claims remain frozen**, no retuning of resonance thresholds, source family, body, geometry, F0, Rd, duration or strict common-source center inequality gate. All changes here are repair of implementation/evidence fidelity before adoption; independent reviewer and human listener still pending. Any newer exact-final-HEAD CI status belongs in the Issue #124 acceptance receipts and must be examined before accepting this Draft PR.


## Independent review disposition and hardened research infrastructure (2026-10-20)

After the new two-render diagnostic correction, independent Codex reviews were requested on [PR #125](https://github.com/ryonakayama234/morphoacoustics/pull/125). The first two reviewed commits c7449c5 and a48595d were **subsequently superseded**, so their reviews cannot be treated as final exact-HEAD approval. Their actionable findings informed the following repairs; retain the original threads, do not mark review PASS by developer self-assessment:

1. **P1 transitive physics trigger**, [review thread](https://github.com/ryonakayama234/morphoacoustics/pull/125#discussion_r4321198497): Removed push/PR path filters from the SV-1 evidence workflow. Changing any dependency source, including Exp009/012/026/027, now triggers a real pinned physical refusal/output gate. Generic tests alone are not this gate.
2. **P1 mutable GitHub Action tags**, [review thread](https://github.com/ryonakayama234/morphoacoustics/pull/125#discussion_r4321198502): Pinned checkout (11d5960a...), setup-python (a26af69b...), upload-artifact (ea165f8d...) to full SHA values verified via official GitHub refs before modification.
3. **P2 directory symlink/rename race**, [review thread](https://github.com/ryonakayama234/morphoacoustics/pull/125#discussion_r4321198499): Artifact writes now use directory-file-descriptor anchoring with O_NOFOLLOW and O_EXCL to prevent pathname swaps from truncating arbitrary existing files. A negative unit test swaps the pathname to a symlink and asserts the target remains unchanged. Trusted local/CI runner still required; not a multi-tenant sandbox.
4. **P2 partial manifest falsely signifying completion**, [review thread](https://github.com/ryonakayama234/morphoacoustics/pull/125#discussion_r4321217353): Complete canonical manifest is first written, flushed and fsynced to an exclusive staged file; exclusive atomic hard link creates manifest.json only after completion. Missing manifest always means the bundle is unaccepted.
5. **P2 drifting Python dependencies**, [review thread](https://github.com/ryonakayama234/morphoacoustics/pull/125#discussion_r4321198504): Generated and committed reviewed Python3.11 LF evidence lock 'requirements/sv1-physical-py311.lock.txt' with 14 exact distributions and 224 SHA256 wheel/sdist hashes. Dedicated CI installs with pip --only-binary=:all: --require-hashes, followed by --no-deps --no-build-isolation package installation, Python package integrity check, and prints installed versions. This is independent of general Core development tooling.
6. **P2 receipt authentication**, [review thread](https://github.com/ryonakayama234/morphoacoustics/pull/125#discussion_r4321198506): Manifest self-hashes cannot cryptographically authenticate a maliciously repacked offline bundle. All authoritative artifacts should be retrieved from the exact GitHub-hosted run; externally recorded GitHub artifact ZIP digest, Git commit and job receipt are the public verification authority. Offline signature/attestation **not implemented and explicitly out of current limited-scope trust boundary**. This is a residual finding requiring reviewer acceptance or a separately bounded attestation task before unrestricted artifact distribution.

Hash-locked [physical run 39365984818](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39365984818) succeeded with three fresh acoustic calculations per evidence bundle and all dedicated tests. Any subsequent documentation/head updates must still pass the same exact-HEAD CI. Keep the PR Draft, request final review at that exact HEAD, do not adopt or merge from past-success evidence. Human creator hearing remains NOT RUN.


## Creator blind listening: post-stimulus pilot report (2026-10-20)

User's *unprompted response before key disclosure* preserved verbatim in [Core #124 comment](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6287125130). The [subsequent key-checked adjudication](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6287167862) does NOT assert population naturalness, and this new written finding cannot retroactively change the earlier source/physics test thresholds.

| Blinded file | Frozen experimental condition | Creator's own perception | Gate |
| --- | --- | --- | --- |
| trial_01.wav | B; **fresh one-excitation one-render** static /a/-like 0.50s | "一番自然な『一度の長い『あーー』』" and close to what was imagined | **SUPPORTED: B single prolonged sound in this N=1 creator pilot** |
| trial_02.wav | C; separate short 0.25s physical renders A and C_second, then diagnostic-only *PCM concatenation* | "あー(ぁ)ー", bumpy / strange | **Distinct from B but NOT cleanly recognized as exactly two syllables** |
| trial_03.wav | A; **fresh one-excitation one-render** static /a/-like 0.25s | "あ,あ,あ" and three perceived restarted events, albeit artistically not bad | **NOT CONFIRMED: A perceptual single onset; no evidence of physical LF phase restarts** |

**Decision semantics:** Core duration generation can meet a scoped \`SUPPORT_DURATION_CONTROL\` while perceptual \`SINGLE_SUSTAIN_PERCEPT_CONFIRMED_PILOT\` is true **only for B (0.50s)**, **not for all conditions**. The diagnostic C splice is not a physical single-run result, and its audible roughness does not establish two distinct natural vocal onsets. A physical single run is not necessarily perceived as one voiced event. The two phenomena must be stored as separate observations; neither a length-dependent normalization hack nor an unreviewed vowel/voice perturbation may erase the discrepancy.

**Creative milestone:** the 0.50s material delivers a usable "one held /a/-like sound" to this creator. **Research limit:** the present 0.25s condition is not established to be one clean short vowel. This is future research into time-domain perceptual onset, source/renderer windowing, amplitude envelope and phonation-event model. The new work must use a separate frozen hypothesis and control, not silently rewrite SV-1's accepted G1 evidence.

## Current final review repair before any merge

Independent Codex review of [commit 557f43f](https://github.com/ryonakayama234/morphoacoustics/commit/557f43f3511769fd837483acbfd32149fb1da6b7) yielded a new **P2 incomplete crash-durability** concern: fsyncing raw files and the top-level output folder does not fsync nested listening directory entries; a completed marker could survive a power loss without all nested files. [Review thread](https://github.com/ryonakayama234/morphoacoustics/pull/125#discussion_r4321288549). Code fix [221eeb0](https://github.com/ryonakayama234/morphoacoustics/commit/221eeb0b6f58aecefdc68a5ec9fb49a4398fa5f3) flushes nested evidence directories in deepest-first order before the fsynced atomic manifest; test [6dba76d](https://github.com/ryonakayama234/morphoacoustics/commit/6dba76d602679689272ad979fbd10e459b9ae539) explicitly checks fsync-before-marker ordering. New exact-HEAD CI and independent review are release gates. Offline copies remain unauthenticated without external GitHub run/artifact evidence; do not claim general adversarial provenance.

**No modification to existing acoustic computations, source scale, static vowel geometry, sample duration or trial mapping was made by these provenance/crash-integrity repairs.** Source paths are still tracked via GitHub run HEAD.
