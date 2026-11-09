# VF-1B2 Pressure Atlas Gate1 — decision record / design handoff

Date 2026-10-27. Research design only. No code, no measured p(z), no scientific model GO. Core Issue #215 and Gate0 Draft #218 are the parent tracks.

## The problem this design resolves
Previous rigid-flow work [Draft #217] reliably transcribed published M6 measured Q and detected mismatch to a deliberately NON-geometry-matched 1D surrogate. This cannot certify glottal pressure forces on tissue. [Draft #218] established honest source qualification: three named references, no measured p(tap) profile yet; 13 source-qualification tests pass and independent Codex exact-head review at dd2a945 reports no major issue. G2/G3/G4 remain not established.

A creator should ultimately be able to edit a physically modeled organ and HEAR a defensible difference. That requires actual fluid pressure/flow and moving organ properties to be linked, not a tone or EQ control given the appearance of physiology. The immediate prerequisite is to measure what the literature actually reports rather than choosing a hypothetical force law to get sustained oscillation.

## Final primary target choice
- Use Figure 2B of DOI 10.1121/1.3514424. Uniform M5 static rigid glottis, d=0.02 cm life size, 10 cmH2O transglottal pressure.
- Same-condition Table I: Q=64.7 cm3/s, entrance loss coefficient k_ent=1.447 (NOT 1.378, which belongs to the 15 cmH2O column). Figure2B measured marker values have NOT been digitized.
- The measured observable is pressure drop D(z,wall)=p0-p_wall(z), anchored to tracheal tap0; actual coordinates and distinct FW/NFW marker identities cannot be guessed. Tap6 z=0.211 cm; tap11 z=0.413 cm; tap13 z=0.511 cm life-size as source text.
- Primary complete-profile eligibility requires eight attributable FW taps (6..13), independent dual extraction, calibration and non-manufactured uncertainty; otherwise PARTIAL/HOLD. Record NFW where verifiably distinguishable and explicitly note occlusion. No side averaging for convenience.
- Why not M6 first? M6 3D sinusoidal transverse geometry and multiple lateral tap arrays are a much larger representation mismatch for the present 1D toy; mixing them with M5 axial measurements conceals model limits. M6 remains a later generalization stress test.
- Why not d=0.005 first? Tiny gap emphasizes viscous losses and may challenge figure resolution/meter applicability; d=0.02 supplies a published middle regime with flow, entrance loss, measured axial gradient and near-exit recovery. This is a pragmatic **measurement qualification pilot**, not a calibrated physiological operating point.

## Hypothesis hierarchy / what PASS would mean
- H-REF: quality-assured measured marker dataset can be reconstructed (software + scientific source quality).
- H-AXIAL, H-RECOVERY: directional observations may be resolved from pressure-drop uncertainties; no forced pass if intervals overlap.
- H-SIDE: potentially unresolvable FW/NFW overlap in this figure must be preserved instead of averaged as though two independent measurements existed.
- H-CAUSAL-LIMIT: even perfect source reconstruction cannot validate a candidate pressure law, estimate moving-wall tissue energy or produce a believable creature voice.
- Gate1 SOURCE_QUALIFIED_FOR_COMPARISON is **a reference dataset milestone only**. A separate, preregistered, geometry-matched model experiment and independent review are required for G2. Another derivation is required for G3. Listening and product GO are still independent G4.

## Decided responsibilities / interface non-changes
Core owns scientific model, physical law and legality. Figure observations and metrology live only in a research reference producer; no source runtime, public physics graph ABI or Performance Contract change.
Studio accepted workspace V2 is frozen. Character canvas = organ/typed ports; Motion = Script/Direction/Gesture; Scene = Speaker/Listener stage; Take transport = immutable generated audio; Research Drawer = future evidence/receipt reading. A source digitization is neither a playable Take nor a new panel. SMC/ASMR remain independent optional modules. No creator-action/UI semantics are changed by this research.

## Explicit trade-offs / risks
1. Figure 2B original resolution may not support reliable independent marker identification or uncertainty: fail closed and retain partial data; request original machine-readable measurements or better figure, do not fill with Eq.4–6.
2. FW/NFW symbols overlap, and side selection could bias pressure extraction: always preserve physical side provenance, report masked/unresolved sides.
3. Figure shows pressure DROP relative to trachea rather than absolute p_wall. Without absolute reference there is no mechanically meaningful pressure integral; future wall traction requires consistent gauge/reference on BOTH sides and appropriate geometry.
4. Paper uses scaled-up static rig. Converting life-size axes to model-scale numerical geometry without recording scaling and ambient conditions makes accidental force errors possible. The current research does not compute a wall force.
5. Published same-condition k_ent/Q are coupled to paper's own fit; they cannot be treated as independent holdout data proving a pressure closure.
6. Current 1D toy omits rounded outlets, wall asymmetry/jet attachment and validated separation dynamics; no amount of 'good-looking' p(z) can remove that without a matched-geometry audit.
7. Measurement error <1% quoted for specified taps is an upper-limit statement, not known Gaussian SD or an all-tap bound; digitization/correlation uncertainties can dominate.
8. For private development, focus on ONE figure/case and meaningful scientific evidence, not general data infrastructure, a dashboard or extra UI.

## GO / HOLD / REJECT decision before any next implementation
GO for narrowly bounded digitization experiment ONLY if this preregistered target/method and original figure usability are independently checked and user does not object to proceeding. Its success is research-source quality, never G2/G3/G4.
HOLD if figure markers/tap positions cannot be mapped, reference/sign or measurement uncertainty cannot be meaningfully quantified, or independent reads disagree beyond declared bounds.
REJECT any claim that a static flow plot establishes phonation, a new Character voice or permission to change frozen UI. Any public Core module ABI or Studio interaction must return to the user as a specific contract/UX proposal first.

## References
- Primary: https://pmc.ncbi.nlm.nih.gov/articles/PMC3078031/ (Fulcher et al., 2011, Fig1B/Fig2B/Table I).
- 3D challenge: https://pmc.ncbi.nlm.nih.gov/articles/PMC2933258/ (Scherer et al., 2010 M6).
- Opposing walls: https://pmc.ncbi.nlm.nih.gov/articles/PMC4804921/ (M5 hemilarynx; do not confuse computed FLUENT curves with measured symbols).
- Core science parent: https://github.com/ryonakayama234/morphoacoustics/issues/215
- First Gate0 Draft: https://github.com/ryonakayama234/morphoacoustics/pull/218
- Approved UI architecture: https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md
