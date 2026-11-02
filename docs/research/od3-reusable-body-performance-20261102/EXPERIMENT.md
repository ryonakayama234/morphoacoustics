# OD-3 EXPERIMENT — A0 frozen prospective protocol (before OD-3 executable source)
Date 2026-11-02 JST. Commit containing this document must precede any OD-3 code and any new OD-3 physics execution; known OD-2 and Exp027 results are prior knowledge, not blind discovery.

## Scope and factors
Primary factorial: B0 (M0 c4,r1.00), B1 (c4,r1.10) × G0/G1. Additional preselected B2 (c8,r0.90) × G0/G1 for different shape site. Six genuine physical conditions, 0.5sec each, fixed LH100? **source is LF100 only** (frozen `lf_fixed`), 48000 Hz, 24000 samples, Python3.11 NumPy2.4.6.
G0: original 3 task locations/degrees/kinds, all onset 0.150s offset 0.350s, sampled activation interpolation with control_step_s=0.005.
G1: only task index1 onset 0.170s offset 0.370s, identical task target/location/degree, original 0.005s sampling; two other tasks 0.150–0.350. Same solver, source, output observer/load/frame rendering. Neither is a new phonetic utterance nor MotorPersona.
Nominal scientific probes at t = 0.00, 0.20, 0.27, 0.35, 0.40, 0.50 s. G0/G1 should coincide at t0 and t>=0.40; at t=0.20 task1 activations differ; both complete at t=0.4. Expect same endpoint geometry at t>=.4. For known log-area realization, `log A(B,G,t)=log A_rest(B)+2 sum alpha_k(t)*d_k`; geometric body/schedule cross-contrast identically zero within floating point when both use same task fields. Acoustic interaction may or may not be nonzero.

## Measurements (units and observational meaning)
1. 16-section resting and timed areas [m²], lengths [m], V=sum L*A [m³], min/max area, actual physical geometry at probes; do NOT echo requested values as measured.
2. 3 task activations dimensionless; onset/offset seconds; precomputed nominal G0/G1 differences, null at .40s; dynamic log-area difference max norm.
3. Original source volume velocity [m³/s] hash and source id; native model pressure proxy [Pa] at 0.2m from inherited 1D resistive outlet/monopole, raw SHA256; 102 calls current renderer. No ear-pressure or calibrated absolute SPL. One common preview gain per archive, no gain intervention.
4. Same-body `D_G(B)=||p_B,G1-p_B,G0||2/||p_B,G0||2`; same-G0 body contrast and waveform difference-in-differences for B0/B1 (descriptive only).
5. Exact identity/provenance, finite waveform, saved NPY/WAV byte mapping, full recomputation from receipt, failure record.

## Prespecified falsifiers
H0 exact G0 model regression: native G0 Pa against inherited `Exp029.evaluate_condition` with replay L2 <=1e-12 in pinned environment, zero drift in bodies. Do not loosen after seeing new data.
H1 timing: G0/G1 activations equal for tasks0&2 at probes; task1 differs at .2 and identical at .4; no material/shape/source mutation. Expected endpoint equality. Numeric geometry log-area formula residual <=1e-10.
H2 geometry: no new organ, source length or rest geometry; identity and preparation digests rederived under OD-2; valid positive 16 areas; rest log-area shape oracle unchanged.
H3 physics: G1 real frame-rendered Pa from freshly realized time-varying geometry, not shifted or relabeled G0; acoustic call count=102; finite 24000 samples; G1-G0 raw Pa difference > max(1e-8,10× G0 deterministic replay floor). A floor too uncertain gives MORE_DATA, not manufactured success.
H4 same old G0: B0 matches previous frozen M0 source pressure oracle, B1/B2 G0 match the previously OD-2 recomputed reference. Existing OD2 source hashes must still verify.
H5 immutable archive: archive hashes and full physical replay all 6 or all selected paired cases, absent/extra bytes and partial writes rejected; never overwrite; load from fresh process succeeds; reject coordinated forged Pa/WAV/manifest.
H6 null/invalid: invalid center/ratio/schedule, NaN/Inf, modified body receipt, changed G0 schedule, symlink and wrong body reference refuse before success. A valid yet physically unsupported task yields UNSUPPORTED/INFEASIBLE according to actually executed validation, not fabricated state.
H7 audio discipline: one common playback gain for all WAVs in one experiment; PCM exact recomputation from raw Pa; no EQ, pitch edits, reverb, per-condition normalization or creative neural corrections.

## Numeric error and scientific gates
Geometry analytical identity tolerance max abs log area <=1e-10; task sampled-activation exact same computation; model raw Pa replay <=1e-12 (L2 relative, pinned Python3.11/NumPy2.4.6); audio exact bytes; 102 acoustic calls (existing frame_count). Failure or new inferred constraints must be documented as a prospective amendment before rerun. Secondary robustness check under half hop-size where available is exploratory and never substituted for primary frozen reference. A/B difference is *not* auditory discrimination: user/creator voice quality remains NOT_TESTED without controlled evidence.
Outcomes: FAIL if contradicted verified invariants, NOT_TESTABLE for backend unsupported, MORE_DATA if numerical floor unresolved, GO_LIMITED_RESEARCH only after actual physics + adversarial CI + recorded run evidence + code review. No naturalness, speech intelligibility or full physical voice fidelity claim.

## Review/audit
First docs-only freeze commit; THEN isolated implementation commit(s), and CI run artifacts. Record every known failing intermediate run in append-only RESULTS; retain native raw and decision conditions. CI may skip expensive physics in generic Python matrices but dedicated Python3.11/NumPy2.4.6 workflow MUST actually generate and verify new pressure, and upload artifacts. Pinned known model claims explicitly separated from novel timing results.
