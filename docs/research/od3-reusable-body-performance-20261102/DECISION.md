# OD-3 DECISION — reusable BodyRevision × bounded motor coordination (prospective)
Date: 2026-11-02 JST. **A0 scientific/design freeze BEFORE OD-3 implementation and novel OD-3 pressure inspection.**
Base Core main: `3131f4bf4c0466d54c5822add54d1ee13b7c322f`. Parent: OD-2 merged PR #273, limited result `GO_LIMITED_OD2_RESEARCH_REVISION_REPLAY`.
**Scope:** research-local executable, physically derived single- and multi-body performance from EXACT inherited OD-2 1D body receipts. No general phonetic TTS, material constitutive model, self-oscillating folds, full OrganGraph, production persistent registry, public stable API, Studio UI, SMC/ASMR import, or claim of natural voice. No waveform modification to fabricate physics. Existing source, old Takes and source-pins unchanged.

## Decision
Choose a *separate parameterized coordination-schedule adapter* (experiment local), using inherited Exp027 3-tasks' spatial log-diameter fields, Exp029 real 1D acoustic transfer/frame renderer, OD-2 canonical BodyRevision receipt/identity and existing BodyPresetRegistry/preparation. Keep source and acoustic observer the same as OD-2; no duplicate graph or body registry. Preserve G0 path by exact numerical regression to inherited evaluate_condition. G1 changes the onset/offset ONLY for T1 (middle constriction) by +0.020 seconds; spatial targets/degrees/three task kinds/drive/source stay fixed. The 3-task endpoints are the same by t=0.40s.

**Chosen research bodies:** B0: (c4,r1.00), exact M0 parent alias; B1: (c4,r1.10), nonnull OD-2 revision; B2: (c8,r0.90), another OD-2 revision. Two schedules each: G0 and G1. Two-body factorial B0/B1 primary; B2 confirms distinct site. This is not novel validation of shape physiology or human voice.

## Choices rejected
- Altering frozen Exp027/029 or OD-2 source code (invalidates source and provenance pins).
- Reusing, pitch-changing, splicing, EQing or time-stretching archived WAV (counterfeit causal mechanism).
- Introducing an independent mutable BodyRevision registry or public production ABI before evidenced interface.
- Building a new biological motor/FSI solver or neural generator in the timing study.
- Changing the Studio V2 approved panel layout. Studio ADR #34 requires separately authorized UI delta; preview PR #33 remains on hold.

## Prior evidence and claims
OD-2: exact six-case model pressure replay, identity and tamper rejection in pinned Python 3.11/NumPy 2.4.6; not an audible quality endorsement. Exp027: independent three-task task-field activations and 16-cell log-area model; Exp029: capability reporting and real finite acoustic observer. The frame-rendered pressure is a model-specific pressure proxy at 0.20m with resistive terminal load, **not listener-ear calibrated Pa**, nor guaranteed continuous-time energy-conserving FSI. The LF100Hz source is prescribed, not self-oscillation.

## Advancement rule
A0: freeze this system/data/experiment contract, source main, hypotheses and guards before implementing.
B1: code isolated and G0 regression matches OD-2 same physics within frozen-environment relative L2 <= 1e-12.
B2: genuine newly computed 3×2 raw Pa/trace and single common-gain WAVs; adversarial artifact mutation fails fresh recomputation; negative/null cases pass; commit and archive run evidence.
B3: one selected body reused in a bounded G0/G1 pair, immutable archive and reverify, no public ABI claim.
C: Studio V2 interface **proposal only**, prior approval separately required. No Studio runtime or UI edit here.
Result labels distinguish `GO_LIMITED_OD3_RESEARCH_EXECUTION` (physical reproducible), `NOT_TESTABLE_BACKEND_CAPABILITY`, `MORE_DATA`, `REVISE_OR_REJECT`, and `NOT_STUDIO_ADOPTED`.
Do not merge solely on passing software CI; require pinned actual physical run and verified evidence with review. No preference gate for the physics. Creator voice-likeness remains separately untested.
