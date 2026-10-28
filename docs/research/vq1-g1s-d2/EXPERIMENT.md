# VQ-1 G1-S D2 — EXPERIMENT: falsifiable prospective metrology and identifiability gates

**Date:** 2026-10-29 JST | **Status:** protocol/design only, no source digitization or test execution in this PR. This is the next work package **after separate creator agreement**; maintain historical experiments and PR #220's frozen case unchanged. Objective: make the value of partial or negative evidence explicit, without an incentive to fabricate a force or sound.

## Scientific question and preregistered primary endpoint

**Primary endpoint P0:** Can original **measured-marker** Figure 2B pressure-drop values for the preselected M5 uniform d=0.02cm, 10cmH2O condition be reconstructed at real FW-side taps 6..13 with source-verifiable tap identity, correct units/sign/scale and defensible intervals by two independent readings? If the figure is inadequate, return the best identifiable **partial** profile and explicitly classify its limitations, never fill missing taps.

**Secondary endpoint P1:** On the **recovered observations only**, are `D11-D6 > 0` (straight-section pressure drop) and `D11-D13 > 0` (exit pressure recovery) resolved by conservative uncertainty intervals? This tests observation-level features, **not** a force model.

**Secondary endpoint P2:** Under a separately frozen and independently evidenced surface/quadrature and gauge model, is any **specified static generalized force functional** uniquely identifiable or at least finitely bounded from the measured taps? If no admissible surface model exists, P2 MUST return `STATIC_FORCE_NOT_IDENTIFIABLE/NO_GEOMETRY`, not a fabricated value.

**Prohibited endpoints:** G1-D self-oscillation, physical tissue-work certification, human voice, naturalness, neural timbre, Character Creator controls, listening tests or new Studio panel.

## Hypotheses, nulls and admissible interpretations

| Hypothesis | Claim being tested | Null / decisive test | What does NOT follow |
| --- | --- | --- | --- |
| H-SRC | Authentic Figure 2B measured markers and exact case are separately identifiable from curves/lines and symbols | No valid original panel/tap/side/case => SOURCE_ONLY or PARTIAL; invented points prohibited | Physical force |
| H-AXIAL | On primary FW side, `D11-D6>0` | Lower bound `>0` SUPPORT; upper bound `<0` CONTRADICT; else INDETERMINATE | Dynamic viscosity law |
| H-RECOVERY | FW `D11-D13>0` in d=.02 case | Same interval criteria, no a posteriori tolerance | Universal pressure recovery |
| H-SIDE | FW and NFW are not automatically equivalent | Side overlap yields `AMBIGUOUS`; independently resolved differences may be reported; neither equality nor difference fabricated | Fixed anatomical laterality |
| H-IDENT | A particular `w^T d` is reconstructible from measured points `y=Hd` | Find any `v in ker(H)` with `w^Tv != 0` => structural nonidentifiability; unknown `H,w` => NOT_TESTABLE | An in-vivo vocal-fold force |
| H-GAUGE | Common pressure reference is necessary only where target fails to cancel it | Gauge-shift invariance when sum(w)=0; changed noncancelling target without measured p0-p_ext => HOLD | Source of pressure from acoustic inlet |
| H-UNC | Conservative pressure intervals cover stated plausible common calibration + local errors | Inject correlated axis offset, side ambiguities, positive/negative true values within frozen bounds; any exclusion => REVISE | Full geometry/tissue uncertainty |
| H-CAUSAL | A source-qualified static profile cannot imply moving-wall power or voice | Force/pass flags attempting to set G1-D/G4 GO must fail scientific audit | Production adoption |

For interval comparisons use exact predeclared decision function: `lower(contrast)>0` supports; `upper(contrast)<0` contradicts; `0 in interval` is indeterminate. A zero endpoint with interval touching zero is NOT support. The interval must include shared calibration correlations; do not compute it by independent per-point error RSS without justification.

## Frozen primary source / exclusion

- Original article Fulcher/Scherer/Powell 2011 DOI 10.1121/1.3514424. Original Figure 1B geometry and Figure 2B **measured** FW filled circles at d=.02 cm, transglottal 10 cmH2O only. NFW open triangles logged separately only if independently visible.
- Reference `D_i=p_tap0-p_i` with source tracheal tap 0; tap 6/11/13 source-verified axial anchors. Other positions must come from genuine published geometry or retain UNKNOWN. Published 7.5 scale handled explicitly after axis/source identity, not assumed from display pixel appearance.
- Same-case Table I `Q=64.7cm3/s`, `k_ent=1.447` are contextual checks only; no fit or synthesized `D_i` from Q/k. The paper's computed Figure 4/Eqs.4–6 pressure curves, other Fig2 panels and other transglottal pressure curves are excluded from primary observed sample array.
- M6 3D rows and hemilarynx observations are **separate** cases. No transfers of their tap coordinates/side to M5 primary.

## Scientific order and frozen gate definition

**Gate A — source archive and figure identity.** Acquire stable original source/panel (respect rights), record hash/URI, resolution, 1B/2B correspondence and the actual plotted pressures; distinguish measured symbols from mathematical curves. If inaccessible or non-legible: SOURCE_ONLY, with audit evidence.

**Gate B — calibration/tap map BEFORE point values.** Record both axes, physical tick labels, >=2 genuine anchors per axis, crop transform, sign, unit, life-size/rig scaling, marker sizes, source tap positions and unresolvable coordinates. If wrong case/axis/legend: HOLD. Calibration must be frozen before the force model sees numbers.

**Gate C — two independent marker passes.** Independently read raw measured marker centers and side identities from the **same archived original image** using distinct analysts/methods with no second-read copying; store raw picks, not just averages. Missing marks are `MISSING`, overlaps `AMBIGUOUS`. Do not silently select the read that improves hypothesis agreement. These are **replications of digitization**, not independent pressure measurements.

**Gate D — uncertainty and reconciliation.** Separate paper instrument bound, figure/calibration correlated errors, symbol width, pixel/axis read errors, positions, scale and between-read discrepancy. Construct conservative joint feasible intervals/sets with clearly documented assumptions. If independent read interval sets do not intersect or shared calibration is non-identifiable: `DISAGREEMENT_HOLD`. No retrospective widening only to secure an expected sign.

**Gate E — measured-profile and feature decision.** Full `SOURCE_QUALIFIED_FOR_PROFILE_COMPARISON` requires independently reconciled **all eight** FW tap 6..13 identities/positions/intervals and independent source audit as #220 predefines. Otherwise `PARTIAL_PRESSURE_REFERENCE`, with any independently resolvable local contrasts assessed ONLY when their exact taps are eligible. The descriptive 2 contrasts are assessed after Gate D; numerical results remain DATA, not validated physics law.

**Gate F — separate identifiability audit, NOT automatic from E.** Before any force evaluation freeze target generalized coordinate, actual source-derived 3D wetted surface, normals, quadrature reconstruction error, outside gauge and complete patch coverage. Derive measurement operator H and weight w from **independent source/geometry**, not from desired F. Check `ker(H)` and `w`, and shared gauge. If independent geometry/pressure coverage is missing, publish `STATIC_FORCE_NOT_IDENTIFIABLE` (a legitimate result). **No new force-model fitting to Figure 2B; no actual Force GO without separate held-out reference and geometry audit.**

**Gate G — independent source-science audit + exact-head CI.** Source audit by reviewer separate from digitization/model author; check original Figure vs every marker and tap/side, scale, uncertainty bounds, source byte fingerprint. Run negative/tamper controls and retain failure evidence. A software CI PASS is not proof of experimental accuracy. Never automatically merge the research PR.

## Predeclared adversarial and null controls

1. Supply Figure 4 modeled curve as measured symbol; MUST reject.
2. Relabel 15cmH2O or d=.16 as the chosen 10/.02 source case; MUST reject.
3. Reverse `p_i-p0` sign; MUST reject; directional hypothesis flips in an independent synthetic control.
4. Use 7.5 scale twice/zero times or confuse rig and life-size pressure; MUST reject.
5. Reassign FW or NFW to left/right, average overlapping triangles, clone FW marker into hidden NFW; MUST reject.
6. Invent equally spaced `z7..z10` between published z6/z11 or use M6 tap map; MUST reject.
7. Change original file/crop/axis ticks after calibration without versioning; MUST reject.
8. Give two incompatible analyst readings; MUST output DISAGREEMENT_HOLD, not pick one.
9. Inject common axis offset with correlated errors; worst-case interval must still cover the declared true synthetic contrasts, or REVISE.
10. Two distinct spatial pressure vectors `d, d+v` with `Hv=0`, `w^Tv!=0` must produce `NOT_IDENTIFIABLE` rather than equal physical force.
11. Use identical pressure points but different physically plausible interpolations between taps without bounded reconstruction error; MUST refuse whole-wall force GO.
12. When `sum w !=0`, omit p0-p_ext: absolute-force result MUST refuse; when `sum w=0`, shared uniform gauge shift leaves the specific differential target invariant.
13. Claim a force from a 1D duct area profile without actual wetted surface normals/side/mode mapping; MUST refuse.
14. Attempt to classify any synthetic control, scalar k_ex, rigid-model data as vibratory pressure work/self-oscillation/Voice GO; MUST refuse.
15. Force a failing test to still emit PASS or lose its JSON receipt on calculation exception; MUST fail negative controls (independent from existing #239 P2 repair).

## Quantitative evaluation without arbitrary numerical cutoffs

No fixed percentage or pixel tolerance is invented before original figure quality is observed. **Freeze the acceptance logic now**, derive numerical uncertainty bounds from original axis ticks, instrument statement, image geometry and raw marker widths **before feature/model inspection**, retain all derived numbers and justifications. Use source-specified bound semantics, not a made-up 1-sigma. Formal exact-zero test identities can be exact algebraically; numerical float tolerances in any subsequent implementation must be independently justified in units and by rounding/conditioning, not by desired outcome.

## Decision table

| Evidence outcome | Allowed scientific result | Forbidden promotion |
| --- | --- | --- |
| No legible original source | `SOURCE_ONLY` / STOP | No fake points or force |
| Some attributable measured markers | `PARTIAL_PRESSURE_REFERENCE` with identities/intervals | No full 8-point profile |
| Complete source-qualified eight FW markers | `SOURCE_QUALIFIED_FOR_PROFILE_COMPARISON` | Not G2 pressure-model validity or force |
| Resolved two axial features | `FEATURE_SUPPORTED/CONTRADICTED` plus intervals | Not a full fluid constitutive law |
| No 3D geometry / pressure reconstruction bound / gauge | `STATIC_FORCE_NOT_IDENTIFIABLE` | No in-vivo or model-static force |
| Separate qualified fixture geometry + gauge + admissible pressure coverage | `STATIC_FORCE_CONDITIONAL_ONLY` **after new approval** | Not moving tissue physics |
| Even all above | `G1_D_HOLD; G4_VOICE_NO_GO` | No Studio voice quality claim |

## Experiment records and creator link

At execution, update `SYSTEM` (actual supported graph), `DATA` (source/observation schema, hashes and missing fields), `EXPERIMENT` (raw cases, failed hypotheses, exact numerical results, reviewer objections) **together**. No Studio UI modification or additional panel. A future capability may expose a verified receipt only inside the approved hidden research drawer after separate creator approval. This phase generates no WAV and has no meaningful auditory gate; later actually voiced Takes must pass sound physics, source-to-tract-to-ear provenance, and independent creator listening, while quantitative physics remains its own gate.
