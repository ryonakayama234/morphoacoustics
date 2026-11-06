# OMA-R-20261106-01 — Response to Muse: D1 minimal Organ Design vocabulary and non-destructive legacy view

**STATUS: D1 RESPONSE PROPOSAL / NOT ADOPTED / NOT IMPLEMENTED / NOT A RELEASED SCHEMA / NO EXPERIMENT RUN.**  
Respondent: ChatGPT (Core design adviser). Date: 2026-11-06 JST. Question: Muse `OMA-Q-20261106-01`, Draft PR #289, `docs/research/oma-1-vocabulary-questions-20261106.md`. Tracking Issue #288. Proposed against Core `main` `34dfcd693bad979590919204ed168a61c77f6e08`. This answer is for Muse **AGREE / REVISE / DISAGREE** review and subsequent **Owner** decision; it is not a self-executing freeze or authorization. One Markdown document only; no executable code, schema files, tests, Studio, SMC/ASMR, experiments, or merge.

## 0. Direct answer, scientific boundary, source audit

**Recommendation: CONDITIONAL D1 DESIGN GO** to freeze a *closed vocabulary of bounded capabilities*, preserving D0, **not** a general OrganGraph implementation. Adopt Muse's PV1–PV6 **with qualifications**: `ideal.branch3.p_u` is already an OG-4 *limited* adopted law; keep all six future port names solely as explicitly non-executable design-intent reservations (two are not energy ports); use I7 category + proposed reason code + non-identity diagnostic; preserve preexisting versioned ABI identifiers; require independent evidence and Owner action for promotion; never silently mutate a frozen version. **All entries in this response are proposed D1 entries; the evidence-backed executable meanings already existing on main are not new D1 implementation approvals.**

**New refinement (hypothesis, not adopted): capability is a scoped relation, not a Boolean attached to a word.** A physical operation is eligible only when `(port/law, named adopted backend, exact topology/fixture, numerical and task envelope, excitation/load/observable, evidence)` all match. `EXECUTABLE_LIMITED` means there **exists** a specifically evidenced supported context, not that the vocabulary ID may be used in any graph. `MODELED_LIMITED` has the same context dependence for ideal material/boundary declarations. A `UNMODELED` reservation can be displayed and preserved in an **offline intent draft** but cannot be silently dropped, fed into physical digest authority, or returned as a successful physical result. The five objects remain separate: semantic `CreatureSpec` → editable intended Blueprint → immutable prepared rest binding → physical state → observation; loads/source/receiver are supplied by *evaluation request*, not anatomical body identity. Some historical OG-3 metadata retains its prior hashing semantics, by explicit D0 exception.

**Frozen D0 authority:** `docs/research/oma-0-organ-design-contract-response-20261105.md` (OMA-R-20261105-01, adopted paper contract after the supervisor's QO3/QO6 revisions; PR #285/#287 merged, Issue #286 closed). I7/I8 and preparation semantics: `docs/invariants.md`, `docs/architecture.md`, `docs/fidelity-0.md`, `README.md`. Existing adopted **bounded** physics, not general anatomy:
- `src/morphoacoustics_graph/model.py`: `SCHEMA="og3.passive.fixed2.v1"`, `PORT_KIND="acoustic.p_u"`, `SERIES_LAW="ideal.series.p_u"`, `BRANCH_LAW="ideal.branch3.p_u"`. `docs/research/og3-gate-c-limited-adoption.md`: OG-3 fixed two passive tubes only, #104 merged, no loaded speech claim.
- `src/morphoacoustics_graph/branch3.py`: `SCHEMA="og4.passive.branch3.v1"`, `BACKEND_ID="og4.fixed.passive.branch3.pu.v1"`; OG-4 Gate C `GO_LIMITED_CORE_FIXED_3PORT`, PR #108 merged (2026-10-16), *exact fixed three-tube/one passive junction* scope. `docs/research/og4-branch3-api-v1.md`, `docs/research/og4-gate-c-review.md` record the normative and review boundaries; older "NOT ADOPTED" headings in those historical documents do **not** undo PR #108's later, scoped adoption.
- `src/morphoacoustics/domain/creature.py` defines semantic `CavitySpec`, `CavityConnection`, `SourceOrganSpec`, `ArticulatorSpec`, `CreatureSpec` (not general physical graph nodes/laws). `src/morphoacoustics/preparation/tract1d.py`, `src/morphoacoustics/physical/tract1d.py`, `src/morphoacoustics/integration/body_presets.py` and `docs/fidelity-0.md`: backend-specific, *source-free, waveform-free* Fidelity-0 plus exact existing body-selection authority.
- `docs/research/cc-a2-two-body-live.md`: exact `v3b-axial-M0@1` / `v3b-axial-M1@1`, CC-A2 adopted limited. `docs/research/od2-reusable-physical-body-20261102/{DECISION,RESULTS,A3_FREEZE_20261102}.md`: OD-2 `tract1d.local-log-area-5.v1`, bounded research-only BodyRevision and physical replay (#273 merged). `docs/research/od3-reusable-body-performance-20261102/{DECISION,RESULTS}.md`: limited coordination/performance research (#277 merged), not a public general controller.
- `docs/research/organ-graph-data-candidate.md` is a **general graph proposal, NOT ADOPTED**. `experiments/025_smooth_source_spectrum_vowel_cue/RESULTS.md` distinguishes closed-set cue success (29/29 answered) from an incomplete 30-trial human gate and failed qualitative voice-likeness. Do not turn acoustic model evidence into human speech/receiver/quality evidence.

**External methodological rationale, not project-specific qualification:** VocalTractLab's [articulatory simulation overview](https://www.vocaltractlab.de/index.php?page=background) distinguishes anatomical geometry, its discretized area function, motion and acoustic calculation. NIST's [VVUQ/metrology report, 2026-10-05](https://www.nist.gov/publications/methods-uncertainty-quantification-computational-modeling-and-simulation-harmonizing) and [FDA/ASME V&V 40 credibility framing](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/assessing-credibility-computational-modeling-and-simulation-medical-device-submissions) motivate claim envelopes and evidence proportional to intended use; **no regulatory compliance is claimed**.

## QD1 — Organ-kind vocabulary

**Recommendation.** Freeze exactly **two descriptive design kinds**; each maps to an existing *different* bounded backend lineage and is **not itself a new executable API**.

| Proposed vocabulary ID | Status and supported evidence | Exact meaning and limitation |
| --- | --- | --- |
| `organ.tract.serial1d` | `EXECUTABLE_LIMITED` *as a view* of existing Fidelity-0/CC-A2/OD-2 bounds; `docs/fidelity-0.md`; `docs/research/cc-a2-two-body-live.md`; OD-2 `DECISION.md`, `RESULTS.md` | One functionally persistent vocal-tract organ; 16 ordered cells are the numerical rest discretization and remain in its exact receipts. OD-2's five-cell local edit kernel changes this **same** tract, not five organs. `prepare_tract1d()` is **not** an `acoustic.p_u` graph API and this entry does not imply such interoperability. |
| `organ.passive_tube.uniform1d` | `EXECUTABLE_LIMITED` only through OG-3 fixed2 `og3.passive.fixed2.v1` or OG-4 branch3 `og4.passive.branch3.v1` adopted fixtures; `src/morphoacoustics_graph/{model,branch3}.py` | A uniform passive two-ended **graph component**, individually named in OG-3/OG-4. It is not proof of an anatomically independent tube organ; arbitrary tube counts/areas, moving tissue or source/tract coupling are unsupported. |

The **organ-vs-discretization rule** is persistent independent anatomical/functional ownership **plus** intended interfaces/actuation/material scope, *not* the presence of a mesh cell or a software class. The tract is a **kind**, not a composition of 16 tube-organ instances; OG-3's two `PassiveTubeOrgan`s remain two passive *components* with separate historical identity. Do not merge the two classes just because they share 1D transmission-line mathematics.

**Two-level semantic rule:** `CavityKind`/`CavitySpec` (oral, nasal, etc.), `SourceOrganSpec`, `ArticulatorSpec` and `CavityConnection` in `src/morphoacoustics/domain/creature.py` are semantic morphology assertions, **not** a namespace of executable design-organ kinds, numerical rest states, validated ports, or junction laws. A future source with kind `phonator` cannot acquire physical capability by reusing a semantic `kind` string. It needs an independently versioned physical contract and a measured gate.

**No additional organ-kind reservations in v0.** A "branched path" belongs to topology/connection, not automatically a distinct organ kind; a "compliant-wall" is a constitutive effect, not an organ kind. Semantic source/articulator specs already allow non-executable expression without duplicating misleading physical names. A future nasal cavity or glottal source may enter a **new** vocabulary version after separate evidence, but OG-4's passive three-port proof does not confer nasal anatomy, and experiments 019–022 do not confer compliant tissue.

**Reject:** one organ per tract cell; calling OD-2's five edited cells five organs; equating `SourceOrganSpec.kind` with an executable organ-kind; collapsing OG-3 tube component IDs to a new tract digest; admitting `organ.compliant_wall` as working by name.

**Falsifier / STOP:** if a vocabulary mapper changes an inherited M0 16-cell rest state/receipt or `r=1.00` alias, marks a semantic source as executable, or exposes a general branch/soft-wall capability without a named adopted gate, reject this mapping. **QD1 NEW TYPES NOT ADOPTED / NOT IMPLEMENTED.**

## QD2 — Ports, laws, and naming

**Recommendation.** The **sole** executable port kind is `acoustic.p_u`, interpreted **by exact reference to adopted OG-3 and Fidelity-0 material** (`docs/research/og3-gate-c-limited-adoption.md`, `docs/fidelity-0.md`, `src/morphoacoustics_graph/model.py`) rather than by inventing a new convention: pressure `p` [Pa], **volume velocity** `U` [m³/s] (never particle velocity [m/s]), signed orientation at each port, complex peak phasors with `exp(+jωt)` where the frequency-domain APIs use them; power audit with oriented `1/2 Re(p U*)` for peak phasors. OG-3 serial transfer maps outlet `[p,U]` to inlet `[p,U]`. Port-type identity does **not** guarantee compatible fixture or common source/load/observer. Exact stage/canonical hashing remain as in existing respective APIs.

| Connection-law ID (existing source spelling; no renaming) | Status | Scope and mathematical meaning |
| --- | --- | --- |
| `ideal.series.p_u` | `EXECUTABLE_LIMITED` | OG-3 fixed2, also used where separately supported by OG-4. Common junction `p`, oriented signed volume-flow conservation; **not** arbitrary serial topology. `src/morphoacoustics_graph/model.py`, `docs/research/og3-gate-c-limited-adoption.md`. |
| `ideal.branch3.p_u` | `EXECUTABLE_LIMITED` | **Only** OG-4 `og4.passive.branch3.v1`, exact three passive tube organs, one A-out → B/C-in ideal junction, `p_A.out=p_B.in=p_C.in`, `U_A.out=U_B.in+U_C.in`, frozen medium, geometries, source/load choices and eight supported frequency anchors. `src/morphoacoustics_graph/branch3.py`, `docs/research/og4-branch3-api-v1.md`, merged PR #108. No nasal anatomy, arbitrary branches, active source coupling or generic graph solver. |

**Six `UNMODELED` reservations (all kept, PV2 with two critical corrections):**

| ID | Future missing physical/operator law or requirement | Why keep and what is forbidden now |
| --- | --- | --- |
| `airflow.pressure_flow` | Mean pressure–volume-flow and aerodynamic resistance/compressibility; conservation and operating point | Separates mean airflow from **small-signal** acoustic `p/U`; no glottal-flow computation from `acoustic.p_u` alone. |
| `mechanical.force_velocity` | Oriented force/velocity power exchange and lawful mechanical boundary coupling | Explicit transduction and unit-conjugate power model absent. |
| `tissue.contact` | Unilateral contact, gap/normal force, complementarity or contact constitutive law | No contact pressure, wet friction or closure solver is adopted. |
| `actuation.command` | Command-to-force/displacement/state dynamics and actuator limits (a **control** interface, not necessarily a power port) | A task string must not directly create physical pressure/audio. |
| `acoustic.radiation_interface` | Impedance/field radiation boundary operator in a specified exterior domain | Existing pressure-release or fixed resistive terminations are **not** anatomy-specific radiation models. |
| `receiver.observation` | Observation transfer/reference-plane/near-field measurement operator (a **read-only observation interface**, **not** an organ energy junction) | It must never be connected as an `acoustic.p_u` load or treated as a physical body port. |

A reserved entry has a mandatory recorded `UNMODELED` status, missing operator, provenance and no claimed energy connection. It is preserved only in non-executable **design intent**. A request that requires one to perform physics is `UNSUPPORTED` at the **earliest stage where its required numerical binding cannot exist**; if a coherent rest state is independently bindable, keep it and refuse missing runtime capability **at realization/evaluation**, per D0 QO3. Never silently discard a design-intent reservation while claiming a faithful executable projection.

**Naming rule (PV4 qualified):** Preserve all **pre-existing** ABI strings byte-for-byte, including `og3.passive.fixed2.v1`, `og4.passive.branch3.v1`, `tract1d.local-log-area-5.v1`, and both exact `ideal.*.p_u` law identifiers; they do not acquire a new trailing version merely because the vocabulary is versioned. **New D1 design IDs** are unversioned lowercase dotted/underscored descriptive names, and never claim to be registered runtime schemas. `*.v1` or `/v1` in a new *released* ID must be separately justified by an approved concrete physical/API contract; there is no automatic alias, and a reservation must not look like a versioned executable ABI. The vocabulary document itself is proposed as `oma-vocab/v0` (document label, **not** a solver ID). Existing `ideal.*` law IDs lack explicit suffixes and remain grandfathered, not renamed.

**Reject:** equating acoustic volume flow with particle velocity; listing OG-4 as unbounded; deleting all future port names; accepting future commands/receivers as power-conserving organ ports; changing original IDs to cosmetically regularize grammar.

**Falsifier / STOP:** an unequal-area junction uses particle velocity conservation; a non-OG-4 branch is accepted solely because `ideal.branch3.p_u` exists; any `UNMODELED` input changes a physical digest/result, or a read-only receiver becomes an organ energy port. **QD2 VOCABULARY NOT ADOPTED / NO NEW PORT OR LAW IMPLEMENTED.**

## QD3 — Constitutive declarations and missing effects

**Recommendation.** Freeze `rigid-wall` as the sole **effective descriptive physical assumption** at `MODELED_LIMITED`: ideal kinematic *zero normal wall velocity* at the rigid boundary, not a finite elastic modulus, not tissue mechanics, and not a new material law. It is effective only where the *actual adopted* Fidelity-0 serial rigid lossless tube, OG-3 fixed2 passive tubes or OG-4 fixed branch3 passive tubes already implement rigid walls (`docs/fidelity-0.md`; `docs/research/og3-gate-c-limited-adoption.md`; `src/morphoacoustics_graph/branch3.py`). The D0 string **`rigid-wall/v1` was a candidate descriptive label, not an existing ABI**: choose `rigid-wall` as the v0 **unversioned vocabulary ID** and record `rigid-wall/v1` as a *previous proposal, not an accepted alias*. Historical model/receipt bytes are untouched. A future formal versioned law may only be introduced separately, not inferred from this label.

**Exactly two declaration states (no third):**
- `MODELED_LIMITED`: a named adopted backend **actually enforces the specific idealization/effect** in its declared context of use; an effective declaration follows the adopted legacy physical authority's current identity/canonicalization, **not a new hash field**. Request outside that context → `UNSUPPORTED` at the lawful stage.
- `UNMODELED`: design intent, acknowledged missing physical law, **no physical effect and no adopted physical digest contribution**. Offline design may preserve it and its provenance, but use requiring that effect is refused `UNSUPPORTED`, with a reason and no counterfeit observation.

No third state "modeled elsewhere": a *physical law's availability is backend- and fixture-dependent*. The same declared effect may be `MODELED_LIMITED` in one named backend and `UNMODELED` for the selected backend without introducing an ambiguous global state. Record capability's evidence/scope separately from the two-value state, not as a "partially simulated" third status. Do **not** force a new `rigid-wall` field into legacy digest bytes.

**Closed v0 missing-effects catalogue** (all `UNMODELED`; names describe *missing physics*, not existing promises):

| Effect ID | Scientific model/operator required *before promotion* |
| --- | --- |
| `effect.viscothermal_loss` | Frequency-dependent lossy boundary-layer acoustics, passive dissipation checks, dimensional and frequency-domain validation against an independent reference. |
| `effect.wall_compliance` | Displacement/pressure mechanical interface, admissible stiffness/geometry law, coupling and independent validation. |
| `effect.wall_damping` | Material loss/viscoelasticity and a nonnegative dissipation/energy audit with identified parameters. |
| `effect.radiation_impedance` | Defined mouth/aperture exterior, complex load or field operator, measured/reference boundary-domain checks. |
| `effect.turbulence_noise` | Mean-flow regime, source/noise law, stochastic/provenance and reproducible measurement comparisons. |
| `effect.source_tract_coupling` | A bidirectional source–acoustic loading port law, stable causal coupling and negative-control/energy audits. |
| `effect.tissue_stress_strain` | Biomechanical constitutive relation (including strain, possible anisotropy), SI identification, calibration and solver verification. |

This is **closed within v0**, not a catch-all "other"; any genuinely new effect requires an explicit v1 amendment with rationale and evidence/status, so an unlisted effect cannot pass as modeled. The catalogue is a reminder of absence, **not** a mandate to implement every item and not an assertion that these models are already biologically validated. Effective-law promotion must separately establish named implemented backend and gate-qualified context of use. An omitted modeled phenomenon can be discussed narratively but is **not a valid v0 catalogue token**.

**Reject:** `rigid-wall/v1` as if deployed ABI; arbitrary `Youngs_modulus_Pa` or "soft" UI labels contributing to physical state; third "modeled somewhere" global state; extending v0 by silent insertion; allowing a rejected effect to perturb sound or body identity.

**Falsifier / STOP:** any v0 UNMODELED stiffness/damping/turbulence makes a measurable output difference, any rigid idealization falsely claims a physical tissue modulus, or an effective parameter changes without the *existing applicable* authority's identity tracking. **QD3 NEW DECLARATIONS NOT ADOPTED / NOT IMPLEMENTED.**

## QD4 — Stage vocabulary and reason codes

**Recommendation.** Freeze **four conceptual stages**: `design`, `assembly-binding`, `realization`, `evaluation`. These are distinct validation **responsibilities**, not a claim that legacy OG-3/OG-4 APIs have four identically named runtime methods. The successful *product* and failure boundary must be distinguished:

| Stage | Success product | Refusal/non-success product; important ordering |
| --- | --- | --- |
| `design` | Validated **non-authoritative** Blueprint intent; may contain explicitly UNMODELED reservations. No BodyRevision or physics. | `INVALID` + code/path; check malformed grammar, SI, duplicate/conflicting IDs, unknown refs. Offline UNMODELED is a visible state, **not** a successful physical binding. |
| `assembly-binding` | Immutable coherent **numerical rest binding** through existing authority (`PreparedMorphology`, OD-2 receipt, OG-3/OG-4 preparation as respectively scoped), even if selected backend cannot execute all morphology. | `INVALID` malformed/mismatched identity; **exceptional** `UNSUPPORTED` only if **no coherent bindable rest state at all**. Do not preempt later solver-capability refusal. |
| `realization` | Valid supported task leads to a **physical state**, labeled `FEASIBLE`; only now may actual physics be evaluated. | `INVALID` request/binding; `UNSUPPORTED` task/topology/law/backend; `INFEASIBLE` *only after support and valid task* for demonstrated body-specific reach. Numerical failure separately `NUMERICALLY_UNRESOLVED`. No state on I8 non-success. |
| `evaluation` | Actual computed observation/measurement and audit manifest, only from lawful physical computation. | `INVALID` observer/request; `UNSUPPORTED` receiver/observable operator; numerical `NUMERICALLY_UNRESOLVED` or infrastructure `FAILED` distinct from biological infeasibility. No observation/Take on non-success. |

**Proposed closed D1 reason-code table** (these are **new paper vocabulary**, not claims that Core runtime already returns these exact strings; existing OG-3/OG-4 and Performance/Body-binding codes stay unchanged). Stable `reason` is the pair `(stage, I7 category, reason_code)`; the `path`, message, SI values, backend fixture and diagnostics are **free-text/provenance**, never body identity. Existing backend statuses must be retained in an adapter's separate `legacy_status`/`legacy_code` view, not overwritten or falsely represented as wire compatibility.

| Stage | Category | Proposed stable reason code | Meaning / example |
| --- | --- | --- | --- |
| design | INVALID | `DESIGN_MALFORMED` | Broken Blueprint structural form, malformed required entry. |
| design | INVALID | `UNIT_VIOLATION` | Pressure vs volume-flow units, non-SI field where required. |
| design | INVALID | `REFERENCE_UNKNOWN` | Junction points to absent organ/port. |
| design | INVALID | `IDENTITY_CONFLICT` | Duplicate IDs or contradictory revision identity. |
| design | INVALID | `PORT_KIND_MISMATCH` | Incompatible or wrong-direction port kinds in claimed lawful connection. |
| design | INVALID | `PARAMETER_RANGE_INVALID` | Nonfinite, negative length/area, invalid number/range. |
| design | INVALID | `VOCABULARY_ENTRY_UNKNOWN` | Unrecognized token pretending to be in closed v0. |
| assembly-binding | INVALID | `BODY_REFERENCE_UNKNOWN` | No existing exact preset/receipt/graph authority. |
| assembly-binding | INVALID | `PREPARED_BINDING_MISMATCH` | Prepared geometry, version or provenance conflicts with actual body. |
| assembly-binding | INVALID | `IDENTITY_CONFLICT` | Two conflicting authorities/duplicate resolution for one proposed binding. |
| assembly-binding | UNSUPPORTED | `REST_BINDING_UNAVAILABLE` | No coherent numerical rest state can be bound, **not** simply "solver cannot run". |
| assembly-binding | UNSUPPORTED | `PORT_LAW_UNMODELED` | Required physical junction has no bindable law/rest relation at all. |
| assembly-binding | UNSUPPORTED | `MATERIAL_LAW_UNMODELED` | Required constitutive rest binding cannot exist; otherwise defer to realization. |
| realization | INVALID | `REQUEST_MALFORMED` | Invalid task parameters or malformed requested run. |
| realization | INVALID | `PREPARED_BINDING_MISMATCH` | Selected backend/physical binding not the validated one. |
| realization | UNSUPPORTED | `TASK_BACKEND_UNSUPPORTED` | Valid `PHONATE` on Fidelity-0, which is CONSTRICT-only. |
| realization | UNSUPPORTED | `TOPOLOGY_BACKEND_UNSUPPORTED` | Valid branch on serial-only realizer, with coherent prior rest binding. |
| realization | UNSUPPORTED | `PORT_LAW_UNMODELED` | Required currently unavailable physical port law at execution. |
| realization | UNSUPPORTED | `MATERIAL_LAW_UNMODELED` | Bindable geometry, but selected realization cannot simulate requested material effect. |
| realization | UNSUPPORTED | `PHYSICAL_MODEL_UNMODELED` | Required aeroacoustic/loss operator is absent and is neither a material nor port law. |
| realization | UNSUPPORTED | `BOUNDARY_BACKEND_UNSUPPORTED` | Valid imposed source/load outside current supported fixture. |
| realization | INFEASIBLE | `ARTICULATOR_REACH_EXCEEDED` | **Supported** constriction outside the real body's permitted interval. |
| evaluation | INVALID | `OBSERVATION_REQUEST_INVALID` | Bad observation grid/units/receiver reference. |
| evaluation | INVALID | `PREPARED_BINDING_MISMATCH` | Evaluation request names a mismatched computed state/body. |
| evaluation | UNSUPPORTED | `RECEIVER_MODEL_UNMODELED` | A true ear/near-field operator requested but not supported. |
| evaluation | UNSUPPORTED | `OBSERVABLE_BACKEND_UNSUPPORTED` | Waveform asked of source-free, waveform-free Fidelity-0. |

**Numerical and infrastructure failure are NOT a fourth I7 biological-capability category.** Existing OG-3/OG-4 already use `NUMERICALLY_UNRESOLVED` and must keep their exact exceptions and codes. A *prospective* adapter-level numerical reason vocabulary is `NUMERICAL_NONCONVERGENCE`, `NUMERICAL_SINGULARITY`, `NUMERICAL_NONFINITE` (category `NUMERICALLY_UNRESOLVED`, possible at physics realization or evaluation). External runtime/IO failures retain separate `FAILED` provenance, never `INFEASIBLE`. None of these candidates changes existing `GraphError` / `Branch3Error` wire codes or implies their existence on main.

**Reason grammar:** new paper codes are uppercase ASCII tokens `[A-Z0-9_]+`, one stable diagnostic reason per first decisive refusal, deterministic precedence **structural INVALID before support, support before physical reach, physical validation before observation**. A future stable interface must pin its own exact mapping and path conventions. The code is semantic and may not change meaning in v0; new codes, deprecation, or changed meanings require a new vocabulary version, with old codes accepted only as historical aliases and NEVER repurposed. `detail`/human-readable Japanese or English messages and `path` may gain context without minting new body versions; never hash those into authoritative physical identity.

**Reject:** treating unknown topology as `INFEASIBLE`; treating numerical singularity as anatomy; making every unsupported future effect fail preparation despite an existing bindable rest state; rewriting legacy error ABI; folding mutable messages into hashes.

**Falsifier / STOP:** supported-but-unreachable articulation is returned `UNSUPPORTED`, unsupported `PHONATE` is `INFEASIBLE`, any numerical failure returns successful observation, or a coherent branched semantic morphology is erased at preparation. **QD4 NEW REASON TABLE NOT ADOPTED / NOT IMPLEMENTED; NO TESTS RUN.**

## QD5 — Non-destructive legacy mapping (document-only)

**Recommendation.** The table below is a **reader/view** with no new authority. Map each existing exact ref to one or more design vocabulary descriptions; **do not** translate, rewrite, rehash, retarget, or issue a historical `BodyRevision`. For legacy OG-3 source/load metadata, retain original snapshot and digest semantics **byte-for-byte** despite future anatomical-vs-evaluation separation.

| Existing authority / exact asset | D1 description refs and evidence | Explicit **NOT CLAIMED** |
| --- | --- | --- |
| `BodyPresetRegistry`: `v3b-axial-M0@1`, `v3b-axial-M1@1` | `organ.tract.serial1d`, `rigid-wall`; `src/morphoacoustics/integration/body_presets.py`; `docs/research/cc-a2-two-body-live.md`. Distinct exact presets, 16 cells: M0 length 0.160 m, M1 length 0.176 m. | **NOT** arbitrary anatomy, semantically equal geometry, new shared physical-graph ABI, natural voice or an unpinned body override. |
| OD-2 `tract1d.local-log-area-5.v1` + existing BodyRevision receipts; `c4/r1.00` and `c8/r1.00` parent alias | `organ.tract.serial1d`, `rigid-wall`, **shape-edit kernel** (not organ kind). `docs/research/od2-reusable-physical-body-20261102/{DECISION,RESULTS,A3_FREEZE_20261102}.md`. c∈{4,8}, r∈{0.90,1.00,1.10}; both r=1.00 resolve to exact original M0 parent, no minted new body. | **NOT** five organs, continuous arbitrary edit, tissue mechanics, public general Core API, new digest or new r=1.00 revision. |
| OG-3 `OrganGraphBlueprint` / `PreparedPhysicalGraph` under `og3.passive.fixed2.v1`, `ideal.series.p_u` | `organ.passive_tube.uniform1d`, `acoustic.p_u`, `ideal.series.p_u`, `rigid-wall`; `src/morphoacoustics_graph/{model,preparation}.py`; `docs/research/og3-gate-c-limited-adoption.md`. Preserve original blueprint/preparation/observation digest authority incl. termination metadata. | **NOT** any novel terminal-load physical simulation, arbitrary graph, dynamic tract, new source, waveform or receiver; no retroactive reinterpretation of historical OG-3 digests. |
| Fidelity-0 `PreparedMorphology[Tract1DGeometry]` via `prepare_tract1d()`, `fidelity0.tract1d` | `organ.tract.serial1d`, `rigid-wall` as conceptual view; `src/morphoacoustics/preparation/tract1d.py`, `docs/fidelity-0.md`. `CreatureSpec` bound to exact manually supplied rest geometry; no inference of anatomy from semantics. | **NOT** an OrganGraph `AcousticPort`, not dynamic speech, no source, WAV or radiation, no claim all semantic cavities are supported by its realizer. |
| OD-3 coordination/performance outcomes (#277 merged) | **evaluation-side evidence** referencing `organ.tract.serial1d` and existing OD-2 bodies; `docs/research/od3-reusable-body-performance-20261102/{DECISION,RESULTS}.md`. B0 M0 alias, B1 c4/r1.10, B2 c8/r0.90, two schedules G0/G1. | **NOT** an organ kind, independent body authority, speaker behavior generalization, adopted Studio Take, human phonetic/voice-quality evidence. |
| Additional bounded OG-4 `og4.passive.branch3.v1`, PR #108 merged | `organ.passive_tube.uniform1d`, `acoustic.p_u`, `ideal.branch3.p_u`, `rigid-wall`; `src/morphoacoustics_graph/branch3.py`, `docs/research/og4-branch3-api-v1.md`. **Read-only extra source confirmation for QD2**, not a request to create a new body. | **NOT** an anatomically branching source–filter solver or a general three-port wiring license. |

**Document-only conceptual record fields** for each row: `legacy_asset_ref` (exact family/preset/revision/digest domain), `descriptive_vocabulary_ids`, `view_adapter_label_and_version` (proposed `oma-legacy-view/v0`, a **paper mapping label** only), `existing_authority_owner`, `evidence_ref` (main path + optional PR/SHA), `scope`, `not_claimed`, `provenance_note`, `historical_identity_rule`. Every row belongs **only here in `docs/research/oma-1-vocabulary-response-20261106.md`**; no registry entry, schema file, commit hook, new digest function, adapter implementation, or historical data rewrite. If an actual read-only adapter is later approved, its versioning must not impersonate legacy wire/physical identity.

**Reject:** issuing a new canonical body ID to unify OG-3 and OD-2; hashing a cosmetic label as if physical; converting M0 alias to new BodyRevision; making the view the source of Take truth.

**Falsifier / STOP:** any byte-different legacy JSON/Pa/WAV/receipt, changed OG-3 digest, missing OD-2 alias or a new unreviewed authority caused by the view. **QD5 VIEW NOT ADOPTED / NOT IMPLEMENTED; NO ASSET MODIFIED.**

## QD6 — Versioning, promotion and amendment

**Recommendation.** Version the **paper catalogue independently** from the frozen D0 architecture, each historical runtime ABI, the implementation/revision authority, evaluation protocol and archived Take. Proposed label `oma-vocab/v0` is an audit document identifier only; it must not overwrite `og3.passive.fixed2.v1`, `og4.passive.branch3.v1`, `tract1d.local-log-area-5.v1` or `v3b-axial-M0@1`. D0 cannot be changed in a D1 vocabulary edit; any contradiction is a **D0 deviation candidate** requiring separate Owner decision.

**Amendment classes — every one requires a **new versioned vocabulary document** after v0 freeze:**
1. New reserved name or new effects/stages/reason codes: v1 proposal, evidence of necessity and collision review; no silent appends to frozen v0.
2. Reservation → `EXECUTABLE_LIMITED` or `UNMODELED` effect → `MODELED_LIMITED`: **not** achieved merely by publishing v1. Require a separate evidence-gated implemented backend, precise law and admissibility scope, independent numeric/reference checks, negative controls, supervisor review and explicit Owner promotion decision (OG-3/OG-4 Gate C pattern).
3. Change effective meaning/scope/eligibility or deprecate an entry: new version and **explicit compatibility disposition**. Narrowing a previously accepted scope needs a migration/withdrawal decision; a simple new "status" cannot invalidate archived measurements.
4. Renames: **forbidden in-place**. Keep old ID permanently interpretable; if a genuinely improved label is wanted, introduce a new ID + explicit historical alias/redirect review, never retarget old receipts. No silent name normalization.

**Preserve identities:** v0→v1 changes only how new descriptions are read/evaluated under an explicitly chosen new catalogue. Old prepared bodies, OD-2 BodyRevisions, OG-3/OG-4 physical digests, source pins, and past Takes remain exactly referenced by their original runtimes and archive bytes. Old Take replay is original verified archive readback or exactly pinned original computation, not recomputation silently delegated to a newer solver. Historical v0 remains readable forever. A manifest hash of references, if ever accepted, is audit-only and cannot become a second body authority.

**Promotion rule:** require (i) a formal **context of use / measurand / units and signs**; (ii) an adopted constitutive/connection law and exact backend envelope; (iii) stable independent numerical/physical oracle, admissible errors and negative controls *preregistered before outputs*; (iv) stable identity/replay and regression; (v) supervisor critical review and **Owner** decision. E0/E1 G0/G1 remain future separately approved gates; their provisional ±2e-6 archived effect tolerance is **not yet frozen**, must be justified and frozen at preregistration, and is not a D1 acceptance threshold. Scientific PASS is determined by measured evidence; creator listening is a distinct final **binary adoption** decision, never an override.

**Reject:** a D1 document claiming G0/G1 PASS, in-place editing frozen v0, widening OG-4 via a label change, changing old Take interpretation, merging or executing new code based on the vocabulary alone.

**Falsifier / STOP:** any vocabulary amendment silently invalidates/recomputes an old Take or promotes a reservation without a separate approved evidence gate. **QD6 PROCEDURE PROPOSED / NOT ADOPTED / NOT IMPLEMENTED.**

## QD7 — Updated system diagram and exhaustive v0 data structure

**Recommendation.** Treat the vocabulary as an **auditable typed catalogue of declarations**, never a giant universal physics object. Each back-end has an independently evidenced *capability envelope*. The following updated diagram is **architecture intent only**, not an implemented runtime pipeline:

    Semantic CreatureSpec / CavitySpec / SourceOrganSpec / ArticulatorSpec
      (semantic anatomy; no port-law executable privilege)
                 |
                 v
    [DESIGN] Organ Blueprint intent
      organ kinds: tract.serial1d | passive_tube.uniform1d
      port: acoustic.p_u; six UNMODELED reservation labels
      law: ideal.series.p_u | ideal.branch3.p_u (bounded scopes)
      rigid-wall; seven UNMODELED effects; no physical digest on intent
                 | valid design / explicit UNMODELED annotations
                 v
    [ASSEMBLY-BINDING] exact authority-resolved numerical rest state
      BodyPresetRegistry ---- PreparedMorphology[Tract1DGeometry]
             |                        |
      OD-2 BodyRevision receipts       |  [existing Fidelity-0/CC-A2/OD-2]
             |                        |
      OG-3 fixed2 / OG-4 branch3 authoritative snapshots & digests
      (separate historical provenance; no universal new registry)
                 | coherent BOUND (not proof of all tasks)
                 v
    EvaluationRequest: task/source, imposed load, observer, clock, backend
                 |                    |
                 +----> [REALIZATION]  <---- exact backend capability envelope
                            | FEASIBLE physical state or typed refusal
                            v
                        [EVALUATION]
                          real observation / numeric failure / refusal
                            |
                            v
                   Measurement + audit-only manifest
                            |
                            v
      Future Studio: existing Character / Inspector / Take slots
      exact Core body refs, evidence-backed capability & UNMODELED labels only
      (no new panel, no raw solver state, no auto-Take, no Studio edits)

**Conceptual entry-record data structure (not JSON, not a machine-readable or adopted schema):**

| Record field | Meaning and rule |
| --- | --- |
| `id` | Exact vocabulary token. Existing ABI strings remain unchanged; new design tokens are not executable ABIs. |
| `class` | `organ_kind`, `port_kind`, `connection_law`, `constitutive_assumption`, `missing_effect`, `declaration_state`, `stage`, `failure_reason`, or `numeric_failure_reason`. |
| `status` | `EXECUTABLE_LIMITED`/`UNMODELED` for kinds/ports/laws; `MODELED_LIMITED`/`UNMODELED` for effects; `VOCABULARY_ONLY` for stage/state/reason description (**no newly implemented handler**). |
| `definition` | Precise semantics, including difference between body, control, receiver and an actual energy port. |
| `scope` | Exact **positive** admitted backend/fixture/observable/task envelope (or "offline design intent only"). Absence of scope means **no** executable claim. |
| `evidence_ref` | Main path and adopted bounded gate/PR for effective entries; `D0+QD* proposal` for words not deployed. |
| `failure_behavior` | Earliest legal refusal stage/category/code where required; offline declarations alone may be retained. |
| `aliases` | Explicit **accepted** alias only; `[]` for v0; rejected historical spelling is provenance not alias. |
| `introduced_in` | `oma-vocab/v0` **if Owner freezes it**; original ABI introduction is separately recorded under `evidence_ref`, not rewritten. |
| `not_claimed` | Explicit capability ceiling; prevents misleading user-facing status. |

**Complete proposed v0 ledger — the following rows *are* the data entries; detailed definitions, evidence, refusal precedence and non-claims in QD1–QD6 are incorporated by those referenced sections. Every row has `aliases=[]`, proposed `introduced_in=oma-vocab/v0`, and **is NOT ADOPTED as a D1 vocabulary until the Owner freezes it**.** In `Scope/ref` the source name designates a *particular historical adopted capability*, not generic deployment. In `Failure` `R` = refuse if physically required with the QD4 reason; `D` = descriptive only / no physical side effect; `A` = conditional bounded execution. All rows are paper declarations, not code.

| ID | Class / status | Definition; exact scope/ref | Failure / not-claimed |
| --- | --- | --- | --- |
| `organ.tract.serial1d` | organ / `EXECUTABLE_LIMITED` | One tract, not mesh cells; `docs/fidelity-0.md`, CC-A2, OD-2; QD1 | A; no OG general graph or tissue |
| `organ.passive_tube.uniform1d` | organ / `EXECUTABLE_LIMITED` | Passive graph component only; OG-3 #104 / OG-4 #108; QD1 | A; no anatomy/active solver |
| `acoustic.p_u` | port / `EXECUTABLE_LIMITED` | Pa, m³/s, signed, +jωt; OG-3/OG-4, Fidelity-0; QD2 | A; no free arbitrary coupling |
| `airflow.pressure_flow` | port / `UNMODELED` | Mean aerodynamic pressure/flow requirement; D0/QD2 | R `PORT_LAW_UNMODELED`; no flow solver |
| `mechanical.force_velocity` | port / `UNMODELED` | Mechanical power-law intent; D0/QD2 | R `PORT_LAW_UNMODELED`; no mechanics |
| `tissue.contact` | port / `UNMODELED` | Gap/contact complementarity; D0/QD2 | R `PORT_LAW_UNMODELED`; no contact |
| `actuation.command` | port / `UNMODELED` | Control-to-physical-realization interface; D0/QD2 | R `TASK_BACKEND_UNSUPPORTED`; not power port |
| `acoustic.radiation_interface` | port / `UNMODELED` | Exterior radiation operator; D0/QD2 | R `PORT_LAW_UNMODELED`; no true radiation |
| `receiver.observation` | port / `UNMODELED` | Read-only observer interface; D0/QD2 | R `RECEIVER_MODEL_UNMODELED`; not organ junction |
| `ideal.series.p_u` | law / `EXECUTABLE_LIMITED` | Existing series junction, OG-3 fixed2 and scoped OG-4; QD2 | A; not arbitrary series graph |
| `ideal.branch3.p_u` | law / `EXECUTABLE_LIMITED` | Existing OG-4 exact one passive junction, #108; QD2 | A; not anatomical nasal branch |
| `rigid-wall` | assumption / `MODELED_LIMITED` | Zero normal wall velocity idealization, Fidelity-0/OG-3/OG-4; QD3 | A; no tissue modulus |
| `effect.viscothermal_loss` | effect / `UNMODELED` | Dissipative boundary layers; QD3 | R `PHYSICAL_MODEL_UNMODELED`; no loss computed |
| `effect.wall_compliance` | effect / `UNMODELED` | Pressure/displacement wall law; QD3 | R `MATERIAL_LAW_UNMODELED`; no moving wall |
| `effect.wall_damping` | effect / `UNMODELED` | Constitutive dissipation; QD3 | R `MATERIAL_LAW_UNMODELED`; no damping |
| `effect.radiation_impedance` | effect / `UNMODELED` | External complex radiation; QD3 | R `PORT_LAW_UNMODELED`; no realistic radiation |
| `effect.turbulence_noise` | effect / `UNMODELED` | Aeroacoustic noise law; QD3 | R `PHYSICAL_MODEL_UNMODELED`; no noise model |
| `effect.source_tract_coupling` | effect / `UNMODELED` | Bidirectional source load; QD3 | R `PORT_LAW_UNMODELED`; no FSI/feedback |
| `effect.tissue_stress_strain` | effect / `UNMODELED` | Stress/strain constitutive law; QD3 | R `MATERIAL_LAW_UNMODELED`; no tissue physics |
| `MODELED_LIMITED` | state / `VOCABULARY_ONLY` | Effective only in named actual backend; QD3 | D; no generic promise |
| `UNMODELED` | state / `VOCABULARY_ONLY` | Offline intent only, no physical digest; QD3 | D; no silent computation |
| `design` | stage / `VOCABULARY_ONLY` | Validated nonauthoritative intent; QD4 | INVALID-only refusal; no body |
| `assembly-binding` | stage / `VOCABULARY_ONLY` | Coherent immutable rest state via old authority; QD4 | INVALID or narrow UNSUPPORTED |
| `realization` | stage / `VOCABULARY_ONLY` | Actual physical state or I7 refusal; QD4 | Only stage with INFEASIBLE |
| `evaluation` | stage / `VOCABULARY_ONLY` | Actual observation with evidence; QD4 | No invented audio |
| `DESIGN_MALFORMED` | reason / `VOCABULARY_ONLY` | design INVALID; QD4 | D; not legacy wire code |
| `UNIT_VIOLATION` | reason / `VOCABULARY_ONLY` | design INVALID, SI failure; QD4 | D; not legacy wire code |
| `REFERENCE_UNKNOWN` | reason / `VOCABULARY_ONLY` | design INVALID, dangling ref; QD4 | D; not legacy wire code |
| `IDENTITY_CONFLICT` | reason / `VOCABULARY_ONLY` | design/assembly INVALID, duplicate or conflict; QD4 | D; not legacy wire code |
| `PORT_KIND_MISMATCH` | reason / `VOCABULARY_ONLY` | design INVALID; QD4 | D; not legacy wire code |
| `PARAMETER_RANGE_INVALID` | reason / `VOCABULARY_ONLY` | design INVALID; QD4 | D; not legacy wire code |
| `VOCABULARY_ENTRY_UNKNOWN` | reason / `VOCABULARY_ONLY` | design INVALID, outside closed list; QD4 | D; not legacy wire code |
| `BODY_REFERENCE_UNKNOWN` | reason / `VOCABULARY_ONLY` | binding INVALID; QD4 | D; not legacy wire code |
| `PREPARED_BINDING_MISMATCH` | reason / `VOCABULARY_ONLY` | binding/realization/evaluation INVALID; QD4 | D; collision checked at adoption |
| `REST_BINDING_UNAVAILABLE` | reason / `VOCABULARY_ONLY` | binding UNSUPPORTED, no rest state; QD4 | D; never a solver shortcut |
| `PORT_LAW_UNMODELED` | reason / `VOCABULARY_ONLY` | binding (rare)/realization UNSUPPORTED; D0/QD4 | D; no fake port |
| `MATERIAL_LAW_UNMODELED` | reason / `VOCABULARY_ONLY` | binding (rare)/realization UNSUPPORTED; D0/QD4 | D; no fake material |
| `PHYSICAL_MODEL_UNMODELED` | reason / `VOCABULARY_ONLY` | realization UNSUPPORTED for other missing physical operators; QD4 | D; never a generic no-op |
| `REQUEST_MALFORMED` | reason / `VOCABULARY_ONLY` | realization INVALID; QD4 | D; not legacy wire code |
| `TASK_BACKEND_UNSUPPORTED` | reason / `VOCABULARY_ONLY` | realization UNSUPPORTED; QD4 | D; not INFEASIBLE |
| `TOPOLOGY_BACKEND_UNSUPPORTED` | reason / `VOCABULARY_ONLY` | realization UNSUPPORTED; QD4 | D; not anatomy |
| `BOUNDARY_BACKEND_UNSUPPORTED` | reason / `VOCABULARY_ONLY` | realization UNSUPPORTED; QD4 | D; request, not body change |
| `ARTICULATOR_REACH_EXCEEDED` | reason / `VOCABULARY_ONLY` | realization INFEASIBLE only, supported task; QD4 | D; physical no-go |
| `OBSERVATION_REQUEST_INVALID` | reason / `VOCABULARY_ONLY` | evaluation INVALID; QD4 | D; not legacy wire code |
| `RECEIVER_MODEL_UNMODELED` | reason / `VOCABULARY_ONLY` | evaluation UNSUPPORTED; D0/QD4 | D; no ear calibration |
| `OBSERVABLE_BACKEND_UNSUPPORTED` | reason / `VOCABULARY_ONLY` | evaluation UNSUPPORTED; QD4 | D; no synthetic WAV |
| `NUMERICAL_NONCONVERGENCE` | numeric reason / `VOCABULARY_ONLY` | physics/evaluation NUMERICALLY_UNRESOLVED; QD4 | D; never INFEASIBLE |
| `NUMERICAL_SINGULARITY` | numeric reason / `VOCABULARY_ONLY` | physics/evaluation NUMERICALLY_UNRESOLVED; QD4 | D; never INFEASIBLE |
| `NUMERICAL_NONFINITE` | numeric reason / `VOCABULARY_ONLY` | physics/evaluation NUMERICALLY_UNRESOLVED; QD4 | D; never INFEASIBLE |

Ledger class-specific statuses do **not** grant capability. Evidence links, alias/provenance and refusal fields are fully specified by the linked QD tables and the record defaults above; an eventual machine-readable registry requires a **separate authorized implementation/schema**. `PREPARED_BINDING_MISMATCH` may already exist *as a different scoped legacy code* in OG-4; spelling coincidence does not authorize new cross-backend error ABI.

**Future Studio Inspector, read-only principle:** a future already-approved existing-slot Inspector may show `display_name`, backend/fixture-scoped `available_limited` vs `UNMODELED`, original body/recipe reference and trusted evidence link. It does **not** list a reservation as a usable slider, infer speaker anatomy from tube sections, display acoustic WAV if no source exists, create revision/Take, or add UI panels. Core remains the capability and physical-evidence authority. This is **design intent only; NO STUDIO IMPLEMENTATION OR CHANGE.**

**Reject:** a single universal schema inferred from the table, Studio as physical authority, arbitrary graph rendering as an existing feature, or `UNMODELED` as a silently ignored no-op. **Falsifier / STOP:** any class lacks a bounded evidence scope/refusal condition, or the Studio reader could claim a newly executable ability from an unadopted token. **QD7 PROPOSAL / NOT ADOPTED / NOT IMPLEMENTED.**

## 8. Higher-resolution hypotheses and decision rationale (new, not frozen)

**H1 — Capability is a product of *law × backend × fixture × measurement*, not a bare token.** Proposed check for a future gate: a request citing `ideal.branch3.p_u` with a valid but non-OG-4 anatomy must report `UNSUPPORTED` (or be coherently prepared and then report it at realization), while the exact adopted OG-4 fixed fixture remains supported. If the broad case passes without a newly adopted backend/evidence gate, the vocabulary has concealed capability inflation. This is a *future test proposal*, **not an experiment executed**.

**H2 — Identity correctness is preserved by a mapping relation, not by content-hash unification.** The same creative tract can have a semantic one-organ view, a mesh-specific 16-cell body receipt and a time-dependent observation without replacing its existing digest. Conversely, two OG-3 passive components do not become one anatomical tube. A prospective G0 gate must show unchanged legacy identities/bytes and E0 equivalence; any altered historical ID is a STOP. This follows D0's one-authority architecture and OG-3/OD-2 lineage separation.

**H3 — Model credibility is conditional on observables and boundary conditions.** A mathematical passive p/U junction oracle can validate ideal power continuity, **not** speech audibility, biological tissue, listener-ear Pa or a near-field receiver. A future comparison must hold source/load/measurement plane and scope fixed. The unresolved VM-0 600 Hz dominant harmonic and Experiment-025 buzzer-like perception remain independent unresolved obligations. Do not fabricate a quality gate in D1.

**H4 — Better refusal taxonomy improves physical inference.** After syntax and capability validity, the *same* supported task on two exact bodies may legitimately produce feasible/infeasible results; `INFEASIBLE` must not be used to hide missing backend functionality. In a future scientific evaluation, comparing task outcomes can reveal body-specific constraints; this is a falsifiable intervention design and not present proof of biological realism.

**Technical selection consequence:** do *not* choose FEM/FSI, neural microtexture, a general topology solver or a new Core/Studio schema in D1. Retain existing specialized, scope-auditable backends and an evidence-indexed **documentary** design view. The selected architecture is **typed descriptive organs + scoped physical law candidates + existing authoritative preparation + explicit refusal + audit-only observation**. It protects the project thesis: the body and its actual physical solver, not a diagram or an audio postprocessor, determine what sound can occur. No threshold or new empirical claim is created here.

## 9. Reverse questions to Muse (3/4; supervisor answer requested)

**RQ-D1-1 — `rigid-wall` spelling vs ABI implication:** Do you **AGREE** that the D0 candidate string `rigid-wall/v1` remains *historical proposal provenance*, while the D1 descriptive token is unversioned `rigid-wall`, effective only through existing backend assumptions—and any later versioned constitutive ABI requires a new gate? If **REVISE**, specify exactly how a versioned label could avoid pretending an implemented/hashed law exists.

**RQ-D1-2 — non-power reservation taxonomy:** Do you **AGREE** with retaining all six PV2 names while explicitly typing `actuation.command` as a control interface and `receiver.observation` as a read-only measurement interface, *not* energy-conserving body junctions? If **REVISE**, say which belongs in a separate future vocabulary class and whether D0's no-executable-reservation rule remains intact.

**RQ-D1-3 — numerical status and historical error ABI:** Do you **AGREE** that D1 may freeze proposed stable reason words while `NUMERICALLY_UNRESOLVED` and infrastructure `FAILED` remain **outside** the I7 three-way biological/capability categories, and legacy OG-3/OG-4 codes are preserved in their own namespace? If **REVISE**, provide a lossless mapping that will not label singularity as `INFEASIBLE`.

No additional reverse questions are required. These are design agreement questions, **not authority to run a probe or change code**.

## 10. Requested supervisor and Owner disposition

Muse: record **AGREE / REVISE / DISAGREE** on **QD1–QD7**, with a concrete proposed replacement for any challenged ID, scope, failure code or missing-effect row. Please answer RQ-D1-1–3; verify the adopted OG-4 limited scope, legacy identity non-destruction, `assembly-binding` I7 precedence and full ledger exhaustiveness. Explicitly mark discrepancies against frozen D0 as **D0 deviation candidates**, not unilateral D1 amendments. The Owner may then approve/revise/reject **D1 paper vocabulary freeze**, separately from any later G0/G1/G2/G3/G4 authorization.

**Final state of this document: ANSWER SUBMITTED FOR SUPERVISOR REVIEW / VOCABULARY NOT ADOPTED / SCHEMA NOT ADOPTED / NO IMPLEMENTATION / NO EXPERIMENT / NO STUDIO CHANGE / NO MERGE.**
