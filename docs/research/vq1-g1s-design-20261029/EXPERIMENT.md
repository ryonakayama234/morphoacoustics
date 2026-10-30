# VQ-1 / G1-S — Falsifiable experimental programme FINAL DECISION (EXPERIMENT)

**Date/version:** 2026-10-29 v1.0. **Design before additional work; no experiment or new source digitization has been executed by this PR.** Controlled objective: certify what measured pressure data can support, and issue explicit HOLD where force inference is impossible.

## Primary case and measurement endpoints

- **Anchor source:** Fulcher/Scherer/Powell (2011), rigid M5 **uniform** glottis, **Figure 2B**, life-size `d=0.02 cm`, reported transglottal drive **10 cmH2O**. Tap0 is tracheal reference; glottal entrance tap6 `z=0.211 cm`, straight portion includes tap11 `z=0.413 cm`, exit tap13 `z=0.511 cm`. Confirm every coordinate and pressure-axis endpoint from actual publication at source gate, not from memory or code.
- **Raw observable:** `D_{i,s}=p0-p_{i,s}` at source-resolvable taps, separate attachment labels FW/NFW **or AMBIGUOUS** if overlapped. Outcomes include per-tap Pa intervals, source support, axial position interval, explicit missingness; no continuous curve automatically.
- **Independent consistency context, NOT force/pressure fitting:** same-paper Table I `Q=64.7 cm³/s` and `k_ent=1.447` for the selected case (per prior [#220](https://github.com/ryonakayama234/morphoacoustics/pull/220)); verify column and units again at transcription. A derived exit coefficient or flow rate is not a tap pressure.
- **Optional discriminating challenge:** Figure 2C, d=0.16 cm, with independently verified drive/case and distinct FW/NFW markers, strictly separate source case and held-out pressure asymmetry test. Never mix its wall labels/values with Figure 2B.
- **Future independent dynamic reference (NOT this gate):** 2025 JASA [M5 moving-angle pressure abstract](https://doi.org/10.1121/10.0041540), plus 2026 Japanese conference [intraglottal pressure/hysteresis presentation](https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=202602236415458121). Neither supplies qualified numerical whole-cycle dynamic input in this project.

## Frozen research hypotheses and paired refutations

| ID | Hypothesis | Primary measurable outcome / oracle | Counterexample and result if unsupported |
| --- | --- | --- | --- |
| H-SOURCE | One precisely identified figure condition yields independently auditable pressure drop points. | immutable figure hash, two independent coordinate/pixel calibrations, source-case match, per-tap units and bounds | unreadable/occluded symbols or mismatched figure: PARTIAL or S0 HOLD, not interpolated evidence |
| H-REF | Recover `D` without external tissue pressure, but cannot recover absolute trans-wall `P` without independent `p0-p_back`. | algebraic identifiability / alternate `p_back` worlds produce same `D` and different `P` | if available source only gives trachea-to-downstream transglottal drive, S2 HOLD_REFERENCE |
| H-WALL | FW/NFW source categories and physical left/right IDs are distinct. | attachment class trace, independent wall/jet mapping and side marker visibility | swapping adhesion class with physical wall or averaging overlapping symbols falsely: REFUSE |
| H-COORD | A signed generalized load depends on the chosen motion coordinate. | synthetic: same two walls, `P=100 Pa`, `A=0.01m²` each => `Q_gap=1 N`, `Q_center=0 N` | interpreting cancellation as zero opening load: REFUSE; original #239 synthetic algebra still valid in its own limited semantics |
| H-MAP | Tap points do not uniquely specify full-surface pressure force. | two different pressure fields agree at all sampled taps but differ between them, and produce different `Q_q` | if no independently bounded interpolation/coverage => S3 HOLD_COVERAGE |
| H-UNC | Shared references and geometric uncertainty are essential to reliable signs and bounds. | interval perturbations of common primitive sensors **and independently variable backside pressure on two walls**, mapping and area/normals, sign stability interval; adversarial translation-mode counterexample must yield nonzero uncertainty when backsides differ | treating shared p0 as independent tap noise or reporting pressure-only half-width as total: REFUSE |
| H-STATIC | Static M5 cannot demonstrate positive cycle-integrated aerodynamic energy transfer or self-excitation. | no time-varying wall motion, no `Q_q(t)qdot(t)` paired measurement | any oscillator / audible voice quality / physiological dynamic claim: G1-D HOLD and VOICE NO-GO |

## Locked execution order and gates

**Gate 0 — archive and case integrity.** Acquire a citable source copy whose permitted figure bytes can be hashed; crosscheck publication identifier, panels, pressure endpoints, scaling, source labels, tap coordinate map and same-case table context. Fail-closed on missing original file, mixed d/drive, untraceable units, incorrect tap0 meaning. No numerical extraction until this ledger passes.

**Gate 1 — pressure atlas (next preferred executable task).** Two independent digitizers, ideally different extraction methods, mark each **visible** plotted symbol and two or more axis ticks, preserving raw pixel coordinates and calibrated mapping. Register FW/NFW class only if symbol independently distinguishable; `AMBIGUOUS` otherwise. Derive uncertainty from figure line thickness/resolution, calibration and any published error indications. Use union/enclosure of independently defensible digitization intervals; if reads disagree beyond documented image/paper resolution, adjudicate from source or classify unresolved. Never fit or smooth the source to a solver. Audit pressure-drop direction and printed units. Publish a raw-first atlas or `S1_PARTIAL`, keeping all RED evidence.

**Gate 2 — independent reference and surface admissibility.** Prove or reject an independent `p0-p_back` boundary relationship; qualify each physical wall map, wetted area, normal, scaling, `q_gap/q_center` mode, and the mapping from local tap pressure to each claimed surface support. A full-integral result requires **all reported region supports accounted for** and defensible bounds over unmeasured area; if not, limit to source-supported patches, keep full-force HOLD. No rebranding of plastic rigid M5 as vibrating living tissue. Geometry and coordinate sources must not be constructed by tuning to desired force sign or sound quality.

**Gate 3 — conditional force and adversarial analysis.** For admissible source-supported region, report both `Q_gap` and `Q_center` in N with explicit sign convention and uncertainty ledger; if physical wall identity is unknown, report **only possible assignment/coordinate-dependent bounds**, not a unique signed loading. Try alternative independently defensible spatial maps and geometries. Force sign is not accepted as robust if the interval includes zero; do not narrow uncertainties by selecting an attractive result. Test pressure-only vs total-mapping interval separately.

**Gate 4 — independent model predictive check (new task only).** If a fluid model is proposed, freeze model/parameters before comparing held-out M5 pressure taps and a non-fitted separate d/case; compare signed pressure-drop residuals/interval overlap rather than same-study flow-derived coefficients as independent measurements. A successful pressure prediction remains static rigid validation only. Subsequent G1-D needs moving-wall pressure, synchronized displacement/velocity, cycle work, energy-stable two-way coupling, independent tissue response and no imposed frequency masquerading as self-excitation.

## Exact software oracle and acceptance policy

- Algebra oracle (currently #239): pressure-gauge shift invariance, sign reversal, two different `q` modes, explicit Pa*m²=N, robust edge cases, shared uncertainty cancellation when justified by primitive provenance; compare simple closed-form synthetic controls to tight floating-point tolerance (e.g. `atol <= 1e-12 N` at non-pathological scales). This threshold is **not** a scientific pressure accuracy target.
- Source qualification: no arbitrary `MAE<foo` or `R²>foo` that can be passed by forged curves. A case passes only with complete audit trail and original-figure-resolution-based finite bounds; missing points are explicit. A small set of qualified points is an honest partial scientific achievement.
- Observation/source gates are separate from inference and voice gates. Synthetic tests can PASS while S1/S2/S3/S4 are HOLD. A future pressure prediction only passes a predeclared held-out observed interval criterion, not fitted synthetic data.
- Repeatability: immutable source reference and SHA, independent annotation IDs, exact code SHA / CI source, signed SI values and raw errors, per-status receipts. RED tests must still produce a STOP receipt (except proven unwriteable filesystem) and CI must not paint failure as PASS. Distinguish code review from independent source audit and expert scientific appraisal.

## Exit conditions and authorized next handoff

**Present state:** #239 latest exact-head [research CI success](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40710433629), source figure numeric atlas **not yet qualified**; real backside reference **not qualified**; full wetted area/physical-wall map **not qualified**; real force **not qualified**; G1-D **HOLD**; creator sound **NO-GO**.

**Next work package:** independently source-qualify the #220 M5 Figure 2B pressure points and report the resulting status/coverage. Implement no production Core source, no G1-D oscillator, no Studio UI. A negative identifiability result is a valid research outcome, and should redirect the next experiment to additional measurements or more suitable independently available datasets instead of fabricated in-between pressure.

**No implementation in this PR; no permission to merge an older draft.**