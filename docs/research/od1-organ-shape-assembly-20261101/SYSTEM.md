# OD-1 SYSTEM v1 — Physically scoped shape modeling & assembly
Prospective conceptual architecture, NOT new API exports.

## Boundaries and composition
~~~mermaid
flowchart TD
 UI["Studio Character / Inspector<br/>selected organ and bounded edit draft"] -. "UI separately approved" .-> ED["Core EditProposal<br/>center, ratio, parent exact revision"]
 BASE["Core known M0 16-section rest geometry"] --> SH["Shape construction + physical validation"]
 ED --> SH
 SH --> REV["Immutable BodyRevision candidate<br/>geometry recipe and prepared digest"]
 REV --> PREP["PreparedMorphology[Tract1D]<br/>existing capability checker"]
 M["Studio Motion<br/>unchanged three-task GestureScore"] --> EX["Core existing 1D realization and acoustics"]
 SRC["Same LF 100Hz prescribed source"] --> EX
 PREP --> EX
 EX --> P["Raw pressure Pa + actual area(t) + provenance"]
 P --> OBS["Independent geometry and matched acoustic observer"]
 P -. "future trusted adapter" .-> T["Studio verified immutable Take"]
 T --> DOCK["Existing Take Dock A/B"]
 OBS -.-> R["Existing Research Drawer"]
 SH --> BAD["INVALID / UNSUPPORTED / INFEASIBLE / NUMERICALLY_UNRESOLVED"]
~~~

Core does NOT import Studio identity or Script; Studio does NOT store/edit solver states. Graph's organ node conceptually references one serial 16-section vocal tract. The 16 numeric cells are not 16 organ nodes. OG-3 fixed passive acoustic junctions remain separate and are not falsely declared active voice source ports.

## Exact mathematical rest shape
i=0..15, glottis→mouth; c∈{4,8}; r∈{0.90,1.00,1.10}; θ=ln(r).
~~~text
w_i(c) = 1       if i=c
       = 1/2     if |i-c|=1
       = 1/4     if |i-c|=2
       = 0       otherwise.
A_i^rest(θ,c)=A_i^base exp(θ w_i(c)) [m²].
L_i=0.010 m; Ltotal=0.160m.
~~~
Rest area A>0 for valid finite base and accepted r. This is a **sectionwise positive area field**, not a smooth 3D surface or a tissue stress response. A physical change in total rest volume is allowed:
~~~text
V(θ,c) = Σ L_i A_i^base exp(θ w_i)
dV/dθ = Σ L_i A_i^rest(θ,c) w_i.
Characteristic impedance Z_i=ρ c_air / A_i.
d ln Z_i /dθ = -w_i (for fixed model ρ,c_air).
~~~
Do not impose false fixed volume or tissue mass. Air medium properties do not stand for biological tissue material.

## Motor/physical path
For the inherited log-area field realizer, when verified separable with unchanged G:
~~~text
A_i(t;θ,c,G) = A_i^base exp(θw_i + g_i(t;G)).
ln[A_i(t;θ,c,G)/A_i(t;0,c,G)] = θ w_i.
~~~
This equation MUST be checked against the exact frozen Exp027/029 realization code before A3 and must not be asserted if constraints make it nonseparable; stop rather than inject a source-independent forced geometry. Same source, task, time and backend required, physical infeasibility is a possible outcome and never repaired by audio.

## Static acoustic oracle: do not compare mismatched endpoints
For a static lossless cylindrical control section with area A_i, acoustic characteristic impedance Z_i=ρ c/A_i and k=ω/c:
~~~text
T_i = [[cos(kL_i), j Z_i sin(kL_i)],
       [j sin(kL_i)/Z_i, cos(kL_i)]]
M = T_0 T_1 ... T_15, [p_in,U_in]^T=M [p_out,U_out]^T.
If p_out=Z_L U_out, H_U=U_out/U_in=1/(M_21 Z_L+M_22).
~~~
Actual inherited Core Exp009 acoustic has a resistive outlet/load and output proxy. A3 must read its exact boundary and output definition. If source or load differ from the mathematical control, derive the correct complex transfer (including load and source boundary) and compare the same observable at matching reference planes. **Ideal pressure-release input impedance peak != loaded Uout/Uin != waveform or ear SPL.** Two genuinely independently programmed numerical formulations (matrix product and recurrence/scattering) check the matched case; no shared simulation verdict helper. Static pass does not prove real-time moving-wall energy-conservative FSI or perceptual voice.

## Proposed research services, not published ABI
validate_shape_edit(base exact ref, c, r) -> typed result/refusal.
derive_rest_shape(...) -> deterministic area vector + analytic geometry receipt.
prepare_body(...) -> Core-authoritative BodyRevision + existing PreparedMorphology + supported capability or refusal.
perform_frozen_task(...) -> Core authentic physical raw Pa, actual geometry trace, source receipt.
independent_observe(...) -> raw-array observer, analytic shape, load-matched transfer, numerical errors.

No edit of src/morphoacoustics, src/morphoacoustics_graph or performance contracts in this design. Prototype implementation begins in experiments/ after A3. Core public API promotion separate; existing private Gate-C CLI/registry is historical and remains exact revision, not silently generalized.

## Frozen UI responsibilities (no changes)
character.canvas organ selection; selection.inspector selected supported rest-shape parameter only after separate UI authorization; project.library refs; motion.canvas fixed script/direction/gesture; scene.canvas unchanged; take.transport real verified replay and A/B only; research.drawer hidden physics receipts, SHA and uncertainty. No additional panel/mode or simulated listening ear.
