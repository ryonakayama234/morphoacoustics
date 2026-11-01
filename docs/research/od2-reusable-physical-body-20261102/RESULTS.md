# OD-2 / Gate B RESULT — bounded five-cell revision and real physical replay

**Date:** 2026-11-02 JST (CI event timestamp 2026-11-01 UTC).  
**Authoritative implementation evidence commit:** \`5003ab497e43ba09ad93ca1f34d3d84e9313b4f9\` (before this results document).  
**Study outcome:** \`GO_LIMITED_OD2_RESEARCH_REVISION_REPLAY\` for the strictly scoped inherited 1D physics and content-addressed body archive. **NO** adoption of a published stable Core ABI, generalized editable OrganGraph, Studio UI, BodyRevision production registry, natural voice, or human-audible speaker individuality.  
**Tracking:** Core Issue #271, design Draft PR #272, implementation Draft PR #273.  
**Exact SHA machine evidence:** [OD-2 Actions run #41323893539](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41323893539) — SUCCESS.  
**14 original artifacts:** [evidence archive #13090651293](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41323893539/artifacts/13090651293) — 6 float64 native raw Pa NPY + 6 common-gain PCM16 WAV + physical decision.json + derived-revision manifest.json (ZIP ID 13090651293, uploaded size 1,301,895 bytes). Preview WAVs are not calibrated ear pressures.

## What was genuinely executed
1. Frozen source/code inventory checked, including OD-1 run.py, oracle.py, production BodyPresetRegistry and CC-A2 adapter; older LF, task, solver, and observer pins are checked through OD-1 and inherited frozen live adapter. NumPy **2.4.6** pinned for this research.
2. Reconstructed exact Core CC-A2 M0 body using \`BodyPresetRegistry\`, with the authoritative parent preparation digest:
   \`sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de\`.
3. Derived four immutable content-based \`tract1d.local-log-area-5.v1\` body receipts for centers 4/8, ratios 0.90/1.10. Repeated derivation returned byte-stable recipes and identities. c=4/8 at r=1.00 aliased the **same original parent** and minted no additional body.
4. Produced **six fresh** model pressure WAV cases (48kHz, 24000 samples, fixed LF100 Hz and fixed three-task gesture, 102 inherited acoustic calculations per case), with geometry/shape and matched-load acoustic oracle checked by the unchanged OD-1 research model.
5. Wrote receipts and artifact SHA256 manifest only after the physical artifacts were generated. Reopened the archive, re-derived each receipt from the trusted parent, independently rechecked shape, pinned source and task IDs, raw pressure hashes, shared-gain WAV bytes and historical M0 quantized hash.
6. Ran negative tests for revised manifests, changed geometric area/identity, raw pressure corruption, WAV corruption, changed decision, symlink and coordinated WAV+decision+manifest SHA forgery. All relevant negative cases **refused**.

## Actual measured physical data
Reference model: 16 × 0.010 m sections, SI area fields, resistive terminal Zload=0.05*rho*c/A_last, 0.20 m monopole pressure proxy (Pa), source prescribed (not self-oscillating). Raw pressure relative L2 against an independent same-run M0 null is a waveform norm, *not a dB or a perceptual threshold*.

| Zero-based shape center | Rest area ratio | Raw Pa relative L2 | Revision meaning |
|---|---:|---:|---|
| 4 | 0.90 | 0.05627127292070631 (5.6271%) | new validated recipe |
| 4 | 1.00 | 0.00000000000000000 | original M0 null alias |
| 4 | 1.10 | 0.05680526299910064 (5.6805%) | new validated recipe |
| 8 | 0.90 | 0.02659999178612523 (2.6600%) | new validated recipe |
| 8 | 1.00 | 0.00000000000000000 | original M0 null alias |
| 8 | 1.10 | 0.027079007843954235 (2.7079%) | new validated recipe |

**Interpretation:** These are **not newly discovered shape effects**. They reproduce prior OD-1 results exactly at the reported precision in the same inherited physics model. The OD-2 result is that those existing physical effects now carry Core-authored distinguishable, reproducible body receipts, with archive replay and refusal evidence. A 5.6% L2 signal difference does not imply a 5.6% loudness or reliable perceptual difference.

**Source evidence from live command output:**
- \`source_id=lf_fixed\`.
- \`source_sha256_le_f64=4d075fd89958ff481507661ea43e4602ed5fe72b0104bc897685b1f696abf529\`.
- \`gesture_plan_sha256=17148dea27e59abfb626b149beebcc7893d4ff9ba04ce4cf3af9ad408ce8a7bf\`.
- \`verified_revisions=4\`, \`verified_null_aliases=2\`.
- Two examples of stable Core-authored exact identity:
  - c4/r1.10: \`od2-7c2663189d907111665544c67def56c885576f5394e4220ec12251e0ca5ebf67\`, prepared \`sha256:f2778205243970d43ca3ea0151b91286fd9c46fb85b8867a8efbb7b811e6da0a\`.
  - c8/r0.90: \`od2-d722dfb9595672f0d19c46a8780c610c9d41fc3a8935b93d3d01a5d68aab4084\`, prepared \`sha256:4b4300f05d0ea98d2edc3e6c17d8075fd29a51c8de91af599a94fa663b602375\`.
  - These are not source-authenticating digital signatures. Their meaning depends on a trusted checkout and local filesystem.

## CI verification ledger
**At implementation SHA \`5003ab497e43ba09ad93ca1f34d3d84e9313b4f9\`:**
- Dedicated OD-2 [run #41323893539](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41323893539): SUCCESS, including real physics, archive verification, adversarial replay test and adopted CC-A2 physical regression.
- Frozen direct OD-2 + OD-1 + BodyPreset test selection: **16 passed, 1 skipped** (the single skipped case is opt-in physical archive negative test, subsequently run explicitly under OD2_REAL_PHYSICS).
- Real physical replay/adversarial cases: **6 passed** including the actual audio archive test.
- Generic Python test matrix: [run #41323893593](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41323893593) SUCCESS, typecheck and Python 3.11/3.12/3.13. The OD-2 physics tests are **skipped** in non-frozen NumPy environments rather than disabling the physical source version check. They run fully under pinned 3.11/NumPy 2.4.6 in the dedicated OD-2 workflow.
- OG3 [run #41323893663](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41323893663), OG4 [run #41323893687](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41323893687), SV1 [run #41323893613](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41323893613): SUCCESS.
- Initial generic-matrix failures (before SHA \`56cecaa...\`) exposed frozen NumPy 2.4.6 vs generic 2.5.4. This was an integration test-scoping error, **not** a physical source result. Corrected by skipping OD-2 tests only outside the pinned scientific runtime. Physics version checks remain strict.
- The first positive run preceded an additional **post-first-run audit hardening**: re-derive pinned source/task and reconstruct identical WAV bytes from native Pa and one computed shared gain; then coordinated fake WAV+manifest hash test. This was added without changing source physics, shape family or thresholds. Its success is confirmed at implementation SHA \`5003ab4...\` and must not be represented as frozen before the first experiment.

## Design and model quality judgement
- **G0 provenance and source pins:** GO_LIMITED, exact physical runtime only.
- **G1 rest geometry and immutable revision identity:** GO_LIMITED, fixed 16-section and four nonnull edits, no generalized anatomy.
- **G2 inherited acoustic run and independent same-model oracle:** GO_LIMITED, same 1D mathematical physics as OD-1; no human biological calibration.
- **G3 reusable local replay archive:** GO_LIMITED **RESEARCH ONLY**. One source-checkout CLI, exact snapshot derivation and verified immutable directory; no general durable Core production registry or adopted public API. Neither #166 old private mutable registry nor its entire stacked PR ancestry was automatically merged.
- **G4 Studio V2 integration:** NOT_IMPLEMENTED. Studio frozen panel registry untouched, existing CC-B1 site08 and historical Takes unaffected.
- **G5 audible identity / naturalness / speech quality:** NOT_TESTED. Existing unpleasant buzzer/tonal voice-quality NO-GO is unchanged.
- **SMC/ASMR/VF1B2/multi-organ material/FSI:** untouched, NOT_CLAIMED.

**Current defensible decision:** \`GO_LIMITED_OD2_RESEARCH_REVISION_REPLAY\` — proof that a validated body variation can be re-identified and replay-verified while preserving original physical causal computation. **Not** \`CORE_PUBLIC_API_ADOPTED\`, **not** \`CHARACTER_CREATOR_COMPLETE\`.

## Next gates (NOT claimed complete)
1. Review the exact model/identity protocol and no-duplicate-registry reconciliation against unmerged #145→#166. Select whether a single stable local Core CLI should be promoted, with source-inventory compatibility and complete negative-case acceptance.
2. Add individually selected and reused character-body execution (rather than current entire six-case research suite), an approved persistent Core revision authority and new historical-Take lifecycle. Scope strictly to the proven family; no generic anatomy until separately validated.
3. Propose one concrete Studio V2 Character selection/Inspector/Take Dock change and seek creator approval under its STOP-AND-PROPOSE rule. Do not merge the existing unmerged Workspace V2 preview as a side effect.
4. Independently address voice quality: acoustically validated anatomical variation is not yet a usable natural Speaker voice. Controlled listening must separately assess discrimination, voice likeness and creator utility. Do not make the physics sound better through artificial waveform manipulation.

## Source documents
- [OD-1 prereg/results](../od1-organ-shape-assembly-20261101/RESULTS.md).
- [OD-2 A3 pre-code freeze](A3_FREEZE_20261102.md), [SYSTEM](SYSTEM.md), [DATA](DATA.md), [EXPERIMENT](EXPERIMENT.md), [DECISION](DECISION.md).
- [Studio Workspace V2 fixed UI contract](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md).


---

## Subsequent R1/R2 direct physical replay and Codex P2 remediation (append-only)

**New reviewed-issue source:** [PR #273 automated review](https://github.com/ryonakayama234/morphoacoustics/pull/273) against earlier docs-only SHA dde93031b24e9d4ff42b9539b273ef61c3c61ef6 identified two P2 correctness holes: (1) forged nonnull pressure could preserve relative L2 while changing all waveform/hash receipts together; (2) archived scientific shape/oracle scores were insufficiently revalidated. The prior success run remains historical; it is not the final acceptance evidence.

**Pre-implementation remediation chronology:** [R1 direct execution freeze](R1_DIRECT_REPLAY_FREEZE_20261102.md), followed by [R2 Codex review remediation plan](R2_REVIEW_REMEDIATION_20261102.md), then code/tests. One intermediate CI [run #41324849433](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41324849433) generated and verified model pressure successfully but failed its extra command on a refactor-introduced NameError in the CLI's returned \`acoustic_calls\` field. This was corrected without altering the physical solver, reference model or numerical gate. Failures remain in the GitHub history.

**Final independently executed post-remediation evidence at code SHA \`e358402d4373cc71dbbe38f6076de55c85d967cd\`:**
- [OD-2 all-gates Actions run #41324965684](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41324965684): **SUCCESS**, frozen structural/negative 16 passed 1 skipped; real physical/adversarial 6 passed; inherited adopted CC-A2 physics regression SUCCESS.
- [Exact output ZIP artifact #13090413183](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41324965684/artifacts/13090413183): 6 native f64 Pa NPY + 6 WAV + decision + verified body manifest, 14 files.
- [Python 3.11/3.12/3.13 + typecheck run #41324965755](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41324965755): SUCCESS. [OG3 #41324965726](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41324965726), [OG4 #41324965722](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41324965722), [SV1 #41324965689](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41324965689): SUCCESS.

### Full physics re-execution and direct R1 command
At archive verification, **all six** model raw pressure traces are now recomputed by Core from the saved verified body receipt: its 16 section area/length hexadecimal values are decoded, bound via \`prepare_tract1d\`, given the same LF100 source and three-task, and passed to \`exp.evaluate_condition\` (102 acoustic calls each). Reexecuted full waveforms are compared directly to the archived native pressure with predeclared same-runtime relative L2 <=1e-12. Hence a sign-flipped body response retaining the same baseline-relative L2 cannot qualify.

The CLI's separately selected direct replay was executed for:
- c4/r1.10, revision \`od2-7c2663189d907111665544c67def56c885576f5394e4220ec12251e0ca5ebf67\`: **fresh raw L2 replay error = 0.0**, 102 acoustic calls, fresh and archive f64 SHA \`351f2732e802bf9861b071de57774ef1c5da6a96d23764dadbdb3119c5e1d1b0\`.
- c8/r0.90, revision \`od2-d722dfb9595672f0d19c46a8780c610c9d41fc3a8935b93d3d01a5d68aab4084\`: **fresh raw L2 replay error = 0.0**, 102 acoustic calls, f64 SHA \`2b42192c4c4e667d403f6e8f6d906dad93e67f97f782087c8f6b6575f848f6f6\`.

These are *zero differences in the declared pinned run*, not a claim of portable byte equality on every CPU.

### Explicit scientific evidence replay
For each receipt, verifier also reconstructs the SI rest shape and compares stored: shape log residual, rest volume and dV/dtheta, model-pinned rest harmonic transfer, and independent actual-loaded complex transfer at both rest and terminal states. All must be finite, complete and within frozen tolerances; a saved successful status and a changed manifest hash are not sufficient. New negative test confirms that changing stored grid complex error to 1.0 and updating the enclosing SHA is refused.

### Coordinated false-audio mutation rejection
New negative test replaces one nonnull pressure waveform by \`2*p_null - p_original\`, preserving its difference magnitude while inverting the intervention's waveform effect. It reconstructs the common monitoring gain and **all six WAVs**, updates the altered raw Pa SHAs, all preview WAV SHAs, decision.json and manifest SHA. Despite the internally consistent artifact receipt and retained L2 statistic, **the verifier refuses the forged result** on fresh body-driven waveform mismatch. This directly resolves the first P2 mechanism. Source and output are still a physically qualified simplified 1D model, not biological truth.

### Meaning of revised result
**R1:** the versioned body receipt is not merely a label attached to old pressure: a Core body reconstructed from it physically executes and reproduces the source+geometry-specific waveform.
**R2:** replay qualification rechecks full physical waveform and model measurements rather than only hashes/aggregate signal norms.
**No change** to Studio UI, production registry, Core package source, FFT/EQ/audio coloring, human perception, actual tissue mechanics, SMC/ASMR or published stable ABI.

**Final disposition remains \`GO_LIMITED_OD2_RESEARCH_REVISION_REPLAY\`**, with a stronger engineering basis and the same narrow model/sound-quality claim. Automated code-review signoff and main merge decisions are independently tracked on PR #273; do not interpret passing CI alone as creator acceptance of sound quality.
