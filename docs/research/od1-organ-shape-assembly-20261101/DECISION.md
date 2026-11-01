# OD-1 DECISION v1 — 器官形状を物理的な身体へ変える
Status: DESIGN_GRADE_CANDIDATE; NOT_EXECUTED; NOT_A3_FROZEN.

## Objective
Creator changes a *body*; Core produces the same motor request through a different prepared geometry, which causes a physically explained acoustic observation. Exact old body and old Takes remain immutable. Success is not equivalent to high-quality human voice.

## Audit corrections
- Studio PR #27 is MERGED (2026-10-23). It already supplies local private CC-B1: exact M0/r1 zero-based index8 rest-area ×{0.90,1.10}, a pinned unmerged Core physical performer, fresh paired common-gain raw-derived WAVs, Core-authored revisions, local reload. Therefore DO NOT implement an identical slider again.
- Core PR #166 is still DRAFT and stacked on other unmerged Gate-C work; Studio main uses an exact pinned Core checkout, not a stable Core/main import. Full general organ/body editor does not exist.
- Section0 ±10% changed raw Pa L2 roughly 3%, but creator informally could not hear the difference. Later site4 was heard as a slight change without blinded test. Prior all-site sensitivity scans are exploratory, not prospective human discrimination evidence.
- Core Exp019 material-conditioned realization is a reduced mathematics test, not an anatomically calibrated material law. Current OG-3 graph represents passive fixed acoustic tubes, not active organ and tissue mechanics.
- SV-1 was adopted only for a narrowly prescribed-source /a/-like output. Studio WG2 quality NO-GO and Exp025 buzzer-like quality remain relevant.

## Choice between implementations
| Alternative | Benefit | Limitation | Selection |
|---|---|---|---|
| Repeat existing site8 single-cell edit | easy | already works privately; adds no new capacity | NO |
| 16 independent raw cross-section sliders | large edit space | ill-conditioned, sharp arbitrary junctions, poor semantics | DEFER |
| **One bounded five-section logarithmic shape basis** | interpretable minimal organ form, analytic geometry/impedance oracle, positive areas, independent tests | restricted 1D model and not genuine tissue | **SELECT** |
| 3D mesh + XPBD/FEM/FSI now | flexible physical anatomy | unqualified material/actuation/contact model; large causality ambiguity | DEFER |
| Direct formant/pitch/timbre adjustment called a body | immediate audible change | physical causality fabrication | REJECT |

## Exact selected family (design frozen)
- Base: existing vetted CC-A2 M0 16×10mm rest vocal tract (0.16m), the unchanged inherited LF 100Hz source and fixed three-task /a/→/i/-like timecourse; exact versions to be frozen at A3.
- Spatial centers c∈{4,8} (zero-based glottis→lips). Ratios r∈{0.90,1.00,1.10}. Shape basis weights w at indices c-2..c+2 = (1/4,1/2,1,1/2,1/4); elsewhere 0.
- Rest area A_i(new)=A_i(base)*r^(w_i), not changing length, medium, source, motor, output gain or solver. Ratio 1 is null. Two known centers are NOT novel blind site selections; the new five-section basis is the prospective model-family intervention.
- Preserve old single-cell site8/body revision as a **distinct family** and identity. Never reinterpret its revision as five-cell geometry.
- No generic 3D organ type, arbitrary port, tissue material, self-excited fold, acoustically targeted edit or human-specific character label promoted in this scope.

## Release and baseline policy
BASELINE_PINNED (existing limited CC-A2/SV1 and private PR #27 source pins) -> G1_SHAPE_VALIDATED -> G2_ACOUSTIC_MODEL_VALIDATED -> G3_CREATOR_LOOP_VALIDATED -> G4_VOICE_DISCOVERY_SUPPORTED. Each is separately judged GO_LIMITED, REVISE, MORE_DATA or REJECT with SHA and test evidence; success at one never promotes the next. G1 validates within 1D numerical geometry; G2 within inherited acoustic backend, not human anatomy; G3 includes historical Takes and app gate; G4 requires controlled audibility and naturalness evaluated separately.

## Hard boundaries
Core source is the authority on physical legality and new BodyRevision. Studio V2 slots remain exactly: Character canvas, Motion canvas, Scene canvas, one contextual Inspector, left Library, fixed Take dock, optional Research drawer. Its accepted UI decision explicitly requires separate approval before panel code edits. Core current OG-3 acoustic.p_u ports cannot be treated as arbitrary force, momentum or FSI ports. VF-1B2a C1/C2, speech-motor-compiler, ASMR and broad material mechanics are independent future capabilities. Old Performance Contracts v0/v1 and source pin semantics stay untouched.

## Separate accepted precedent vs external science
Project evidence: Core #141 / PRs #143,144,149,150,166; Studio #25/#27 and fixed Workspace V2; Exp019,025,027–029,042.
Independent theory only: https://vocaltractlab.de/index.php?page=background describes articulatory geometry→area function→acoustic modeling; https://musicweb.ucsd.edu/~trsmyth/pubs/smc21.pdf develops piecewise waveguide transfer formulations. Neither independently validates MORPHO's particular model, a new sound or a character voice.
