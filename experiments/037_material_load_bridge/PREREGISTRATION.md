# EM-1 / Experiment 037 — material-conditioned geometry to stationary acoustic-load feedback

**PREIMPLEMENTATION FREEZE (2026-10-12). DRAFT RESEARCH, NOT APPROVED OR MERGED.**
Parent [Core #87](https://github.com/ryonakayama234/morphoacoustics/issues/87).

## Scientific question

Can a material-conditioned **realized ten-section tract geometry** from already-merged Experiment021 causally change a strong-coupled **fixed-geometry** acoustic pressure and glottal volume flow under the *same* prescribed positive valve aperture and Psub, while remaining passive and numerically reproducible?

This is a deliberately **one-way frozen-snapshot bridge**. The material affects the reduced motion and therefore the chosen static geometry; within each waveguide run that geometry NEVER moves. There is NO time-dependent tissue acoustic wall work, 3D tongue, physical Young's modulus, moving-wall FSI, spontaneous voicing, exact closure, natural speech, or listener/ASMR claim.

## Frozen code provenance, separated PR chain

- Merged Experiment021 (G1-C, merged [PR #50](https://github.com/ryonakayama234/morphoacoustics/pull/50)) `experiments/021_material_conditioned_multimode_transient/run.py` Git blob `9b19f9e9de9bcc60babc3661a27d14278cccd2d6`.
- SFI-2 [Draft PR #81](https://github.com/ryonakayama234/morphoacoustics/pull/81) head `6cdd21768fd92167bbc56c57264fc161c35e7dda` (original `waveguide.py`).
- SFI-3 [Draft PR #84](https://github.com/ryonakayama234/morphoacoustics/pull/84) head `7ab18f25f53bc5f81bcdf5e7697fd11981abe6dd`, implementing `StrongCoupling(PassiveTract(...))`; this research branch STACKS ON the pinned SFI-3 head.
- No predecessor code edits, no production `src/` edits, no Core contract/Studio changes. Review both predecessors before any adoption or merge.

## Input freeze / interventions

- Same Experiment021 10 × 17mm rest geometry, rest section area `3e-4 m²`, default target constraint at section index 6 to `5e-5 m²`, stiffness model `H = diag(k)+λ L^T L`, `λ=1`, modal rate `ω=25/s`.
- Only `k[5]` changes: M0 `k5=1`, M1 `k5=4`, all other `k=1`. These **are unitless effective reduced weights**, NOT tissue Young moduli.
- For both conditions same fixed task duration `0.12s`, evaluate **actual modal transient** `q_M(t*=0.120s)` with zero initial velocity, not equilibrium or retuned source. Exact original `Experiment021._vector_state_at_time` and `_geometry_from_ratios`, no analog lookup.
- Each frozen geometry `A_i=A_rest q_i(t*)` must be finite, strictly positive; nonzero geometry contrast and identical section lengths. Freeze only these snapshots throughout each acoustic run (NO in-place dynamic area changes).
- Fixed `subdivisions=4`, sampling `48000 Hz`, duration `0.030s`, fixed positive `A_glottal=3e-5 m²`, constant `Psub=800 Pa`, exact SFI-3 valve parameters, matched passive outlet per condition, same initial zero acoustic and glottal state.
- One fresh `StrongCoupling` and `PassiveTract` per condition; record every step and its power/energy ledger. No audio, no EQ, no post-simulation pitch/gain trick.

## Frozen condition matrix and negative controls

- M0,C0 / M1,C0: SFI-3 intentional nonreciprocal **open-loop** null. With same valve+drive but different acoustic shapes, **upstream U must be bitwise identical**. C0 has explicitly nonreciprocal port work and is NOT physically passive as a coupled system.
- M0,C1 / M1,C1: Strong, shared midpoint power-port source-filter feedback; demand geometry and acoustic pressure differ, glottal U responds after causal propagation, energy balance holds.
- C1 same geometry with a different *material label*, fresh runner: output must be identical to original M0,C1. This rejects magical direct `material_label -> voice` processing. Extra diagnostic: same geometry under two labels could not create different acoustic results in this rigid-wall model.
- The driven valve remains open. Requested exact glottal closure or tissue self-oscillation must yield `UNSUPPORTED`, not a plausible fake voice.

## Preregistered gates and status

1. **MATERIAL_PROVENANCE**: G1-C implementation blob SHA exactly as above; `q` finite and all ratios positive, same task+ω, area-length geometry valid; material difference in realized q with normalized RMS >1e-6; frozen source SFI-3 branch dependency and parameters visible in manifest. No material-dependent retuning.
2. **NULL_ISOLATION**: C0 source flow arrays must match byte-for-byte for the two material geometries; repeated M0,C1 across different material labels and identical geometry matches *exactly*.
3. **FEEDBACK_CAUSAL_EFFECT**: C1 M0↔M1 acoustic inlet pressure and source flow both have nonzero normalized RMS difference >1e-7. Since changes occur in the interior of the tract, report source-flow difference before first 0.25ms and require max abs ≤1e-7 m³/s, as SFI-3 causal-window sanity. This threshold is a toy numerical guard, not a tissue property.
4. **PASSIVE_ENERGY**: for each C1 step, a joint glottal+tract energy residual from SFI-3 is finite and accumulated absolute residual / max(total accumulated abs drive work,1e-30) <1e-10, and glottal modeled losses/outlet modeled loss each ≥-1e-14J per sample; zero initial energy; no hidden audio production.
5. **NUMERIC_STABILITY**: finite data, no runtime exceptions. A separate repeated run in the same pinned environment yields byte-identical generated condition traces and JSON evidence; no expectation of bitwise equality across platforms.
6. **FAILURE semantics**: a false scientific gate results in a *nonpassing* CI and persisted `NUMERICALLY_UNRESOLVED` or specific gate failure; no changing thresholds after looking. If predecessor chemistry/physical claim review fails, label `MORE_DATA` or `UNSUPPORTED`; research outcome does NOT grant production contract adoption.

Only after independent code/science review and successful CI may this fixture be considered numerical evidence of a reduced **material → realized geometry → acoustic load → prescribed-valve flow** chain. It is not evidence that a real tongue's bulk material directly changes voice, nor that the time-varying wall is energy-correct.

## Independent Wolfram sanity

The stationary 0.17m ideal lossless closed/open tube has first quarter-wave resonance `343/(4*0.17)=504.4117647059 Hz`, **not** a prediction of this segmented dissipative model's resonance. A shared pressure/flow power port must cancel `+pU` on tract and `-pU` on glottis to close the total energy ledger; the strongly coupled SFI-3 midpoint result is the applicable numerically tested identity. Independent oracle and Python invariants must be audited separately.

Theory: [Titze (2008) source-filter coupling](https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/). For future moving walls, the mechanical/acoustic exchange term `p dV/dt` with a consistent sign and geometry/inertance updates must be added and independently audited.
