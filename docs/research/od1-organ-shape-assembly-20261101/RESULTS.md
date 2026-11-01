# OD-1 / Gate B RESULTS — local five-cell shape (2026-11-01)
Research-only prospective within the inherited 1D model. Explicitly NOT a Core public Organ Design API, general body editor, human-anatomical model, biological self-excited voice or Studio Take.

## Independent preregistration
Core freeze commit b3f0efd2dc88f5695eee14c51c2579a6fc1ca85a (before source code), blob b7ee5bb03cfbaffd29ffeff3fe73a8e20d4972bd. Family c=4/8 ×r=.90/1.00/1.10, fixed old CC-A2 M0 /a/-like 16×10mm, prescribed LF100Hz source and three-task timecourse, 48kHz×24000 samples, resistive outlet+monopole pressure proxy and numerical thresholds all selected prior to implementing B. Site choices were influenced by historical exploratory experiments and are NOT unbiased blind discovery. Two independently coded acoustic formulations test the same modeled equations, not real-world physiology.

## First real, archived physical run
Candidate code exact SHA f61237db1312e0967d65246164c0f1673535edb8
GitHub Actions od1-preregistered-shape-science run #41305284227: SUCCESS, all 4 initial independent/negative tests, 6 fresh physical outputs, six validations of 102 acoustic calls each, and adopted CC-A2 physics regression. Archived scientific artifact #13083475742 (six float64 native Pa NPY files, six pair-common-gain PCM16 WAVs, decision.json); CI log includes actual six-case measured L2. The later audit-strengthening changes on PR #268 include independently split oracle recurrence and explicit SHA guard/mutation tests and must receive their own exact-head CI confirmation.

| zero-based center | permanent rest area center ratio | measured native pressure relative L2 vs independently rendered r=1 null |
|---|---:|---:|
| 4 | .90 | 0.05627127292070631 |
| 4 | 1.00 | 0.00000000000000000 |
| 4 | 1.10 | 0.05680526299910064 |
| 8 | .90 | 0.02659999178612523 |
| 8 | 1.00 | 0.00000000000000000 |
| 8 | 1.10 | 0.027079007843954235 |

**Interpretation:** a five-section positive rest-area intervention modifies actual time-dependent model pressure by approximately 5.6% (center4) or 2.7% (center8) in full-duration relative waveform norm. Both effects are resolved above the prior 1e−4 relative numerical threshold; exact nulls remain zero; not one sample is painted, voice-converted, re-used or post-hoc EQ-corrected. This measure is neither a dB loudness difference, human threshold, natural-voice score nor evidence of different speaker identity. Location-specific waveform norm is not monotone in resonance shift or perceived pitch. Section0/2/4 and single site08 past studies use different intervention geometries and are not strict comparative efficacy studies.

## Other gate interpretations
- Geometry: pinned 1D SI rest body and independently reconstructed published diameter array; positive areas, fixed length and analytic log-area and rest-volume checks.
- Motor: same three-task/fixed source; 4 timed trace probes confirm separability of the five-cell rest shape and inherited task field within *this prescribed* model.
- Acoustics: actual complex resistive-load outlet-flow and 0.20m monopole pressure proxy cross-checked via two separate calculations. The model still uses an experimental lossy 1D transfer and quasi-stationary time rendering; it does not calculate tissue mechanics, self-oscillating VF-1B2a, calibrated lip radiation or listener ear pressure.
- Source continuity: adopted reference M0 quantized pressure SHA dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e required at both nulls.
- Creative perception: NO controlled human sound test for new family. Neither audible character difference, semantic Japanese speech, voice quality, independent material sensitivity nor more voices is certified.
- System: Studio PR #27 private single-site sound workflow and Workspace V2 remain unchanged; no new historic editable BodyRevision/Takes or general OG-3 ports were introduced.

## Technical acceptance boundary
Machine evidence currently supports a bounded **GO_LIMITED_RESEARCH_SHAPE_AND_INHERITED_1D_ACOUSTICS** from the first successful run, pending final exact-head verification of code hardening and critical technical review. This is a research-level reproducible reference, NOT Core public ABI, Studio feature adoption or main merge approval. A failed newer build supersedes any claim of the newer exact HEAD succeeding. Publish exact final HEAD workflow and unresolved tests as a final PR decision/comment rather than retroactively altering thresholds.

## Remaining uncertainties
No independent human physiological measurement; no numerical convergence study of an actual moving-wall tissue/fluid solver; no real calibrated vocal loudness; no sound quality or identity trial; no general structural Physical Assembly; no persistent new BodyRevision registration; no arbitrary script; no ASMR/SMC import; no 3D anatomy. A true next-generation voice engine remains separate research. Future gate C/D needs separate adopted contracts and Studio UI authorization.
