# OD-2 SYSTEM — module ownership, physical derivation and callable boundaries

**DESIGN-ONLY: conceptual arrows are not claims of current executable APIs.**

## Fixed owner/UX architecture
~~~mermaid
flowchart TB
 L["Studio project.library: references only"] --> C["Studio character.canvas: select organ"]
 C --> I["selection.inspector: bounded shape intent"]
 I -. "separate UI approval" .-> A["Core: ShapeFamilyAdapter / validation"]
 B["Core BodyPresetRegistry: exact M0@1 binding"] --> A
 A --> R["Core: immutable BodyRevision / content identity"]
 R --> P["PreparedMorphology[Tract1DGeometry]"]
 M["Studio motion.canvas: Script / Direction"] -. "existing task or separate SMC gate" .-> G["Valid GestureScore"]
 G --> X["Core physical execution: inherited realizer + fixed LF source + acoustics"]
 P --> X
 X --> Q["Native physical pressure in Pa, timed geometry/trace, named observer"]
 Q --> V["Verified artifact manifest / genuine Take adapter"]
 V --> T["Studio take.transport: playback / A-B / historical references"]
 Q --> D["research.drawer: source, solver, metrics, hashes"]
 S["Studio scene.canvas: Speaker/Listener instances"] -. "future gated scene physics" .-> X
 A --> F["INVALID / UNSUPPORTED / REVISION_MISMATCH / INFEASIBLE / NUMERICALLY_UNRESOLVED"]
~~~

No actual module imports from Studio to Core internals. Existing performance contracts v0/v1 remain unchanged; define an opt-in adapter interface after Gate G3. No physical state is owned by the UI. No arbitrary OrganGraph topology or new 'Organ' panel.

## Three Core conceptual layers
**Organ Design** accepts a validated shape-family proposal over one existing vocal-tract rest geometry. This is an *area field*; it must not claim a 3D material constitutive law or active tissue motion.
**Physical Assembly** verifies exact parent identity, physical SI sections, positive/rest geometry, family/backend capability and provenance; gives a prepared body. Shape validation (INVALID) is different from unavailable capability (UNSUPPORTED); inability to execute a valid task is INFEASIBLE.
**Physical Execution** consumes PreparedMorphology + unchanged task + fixed LF source and observed load, then computes actual time-dependent states and pressure. It never receives desired F0, desired formants or a waveform target from a shape edit.

## Model and derivations (inherited 1D)
index i=0,...,15 from glottis to lips; c={4,8}; r={0.90,1,1.10}; theta=ln(r).
w_i(c)=1 (i=c), 0.5 (|i-c|=1), 0.25 (|i-c|=2), otherwise 0.
A_i^rest(c,r)=A_i^base*exp(theta*w_i).
L_i=0.010m, Ltotal=0.160m. V_rest=sum_i L_i A_i^rest.
dV/dtheta=sum_i L_i A_i^rest w_i.
For fixed air density rho and wave speed c_air, Z_i=rho*c_air/A_i, hence d ln(Z_i)/dtheta=-w_i.
This validates 16-area geometry and a *fixed* cavity, not general topology. Zero edit returns exact original object/geometry and does not create a new revision.

For existing Exp027/029 log-area realizer, the **testable separability** relation is
A_i(t;theta,G)=A_i^base*exp(theta*w_i + g_i(t;G)).
Only claim this after checking the pinned actual inherited code; a later nonseparable controller requires a new model, not a forced post-hoc addition.

## Acoustic observer and model assumptions
The OD-1 preregistration pins the actual 1D acoustic medium rho=1.21kg/m3, sound speed 343m/s, attenuation 0.4Np/m, resistive outlet Zload=0.05*rho*c_air/A_last, 0.20m monopole pressure proxy. Use this exact finite load and named proxy; do not compare ideal pressure-release input impedance to radiated output as if equivalent. The acoustic source is prescribed LF100Hz with unchanged motor/seed/time, 48000Hz×24000 samples and 102 acoustic calls in the old run. No ear-pressure, absolute SPL or biological phonation claims.
Primary independent same-equation oracle computes the 16-tube complex product transfer; second formulation propagates reverse load impedance and segment U ratios. Compare them with the **same physical source/load/outlet/observer**, and compare with actual Core physical outputs at reference and time-evolved shapes. Agreement checks implementation of the chosen 1D equations, not actual vocal physiology.

## Reuse, not two registries
Use existing body_presets.py exact BodyPresetRegistry / preparation_digest as the physical binding authority. A new family-dispatch facade must either (a) extend/reconcile the existing researched #166 Core registry/CLI through a reviewed migration, or (b) extract the minimal trusted mechanism into one replacement Core boundary. Both are *mutually exclusive* implementation tactics; no second running registry. The 'reusable body' is an immutable recipe + derived full rest geometry + parent provenance with an authorized Core digest, not a waveform or selected graph-card position.

## Current graph boundary
src/morphoacoustics_graph/model.py currently represents a fixed passive acoustic.p_u topology. A future Character canvas may render '声道' as an organ node and the glottis→mouth relation as links in a conceptual organ graph; this OD-2 study does not expose the 16 tube cells as editable organ nodes, and does not create an active vocal-fold port or connect the passive OG solver as a new wave-producing engine.

## Studio composition contract
Canonical Studio V2 ADR: docs/product/STUDIO_WORKSPACE_V2_DECISION.md, merged PR #34. Existing slots exactly: global.header, project.library, character.canvas, motion.canvas, scene.canvas, selection.inspector, take.transport, optional hidden research.drawer. Preview PR #33 is draft and unmerged. Studio source code/panel registry/styles/preview changes are STOP-AND-PROPOSE even when Core G3 is green. Exact future action: select one voice-tract node -> Inspector accepts a permitted c and r -> validate -> retain new revision reference -> same Motion -> physical Take -> A/B dock. UI only displays physical data and status; editor changes must go through validated backend domain API.

## Unchanged external and research integration
SMC belongs to task/gesture proposals in Motion, but cannot choose the waveform. ASMR belongs to scene contacts/receiver and is independently gated; no implicit import. VF-1B2/biological tissue/materials are separate future physical fidelities. Neural closures must preserve body-derived causal differences and physical infeasibility; no neural audio beautification in OD-2.

## Selected first operational interface
OD-2 selects a **Core-local versioned CLI ABI** as the initial path rather than adding a production Python API, browser synthesis, fourth Studio mode, or remote HTTP service. Reconcile #165's inspect/perform/verify and #166's register/resolve into **one logical authenticated-by-local-trust Core authority** with exact schema/version and actual artifact readback. Add a bounded shape derive/propose operation for the five-cell family. One manifest and revision identity authority only; no second registry. In the later Studio bridge, a trusted local adapter invokes Core and verifies complete evidence, then Studio stores immutable references. A future importable Python facade is a separate decision, not today's technical selection.

## Runtime safety for a private workstation
Bounded allowed family, fixed parent and source versions; strict rejection on unexpected schema/version/fields/NaN/Inf/bool, hashes and rederived identity, controlled local append-only history and no success until complete verified artifacts. This is not a remotely exposed authenticated SaaS. Preserve refusal provenance; avoid complex security systems irrelevant to personal use, but do not accept false historical Takes.
