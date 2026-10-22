# CC-B1 Gate A/B — owner-delegated AI technical decision (2026-10-22)

> **DISPOSITION: `GO_LIMITED_1D` FOR RESEARCH ONLY.**  
> **Authority: project-owner-requested AI technical assessment, NOT an independent human scientific review or GitHub PR approval.**  
> **Residual exception: `inherited_solver_internal_fault_injection=NOT_TESTED`, never PASS.**  
> No merge to `main`, no stable BodyRevision API, no Studio deployment, no perceptual/biological accuracy claim.

## Decision and exact immutable target

| Field | Value |
|---|---|
| Gate A | `FROZEN_INTERNAL_ACCEPTED_FOR_LIMITED_RESEARCH` (procedural pre-run freeze, not independent scientific ratification) |
| Gate B | **`GO_LIMITED_1D` — `OWNER_DELEGATED_AI_TECHNICAL_REVIEW`** |
| Third-party independent approval | **`NOT_OBTAINED`** (the connected GitHub account is also the PR author; AI is not a second independent accountable human) |
| Internal inherited-solver fault injection | **`NOT_TESTED`** (risk exception for research only) |
| Gate C PR #145 | **`PROTOTYPE/HOLD`**; security, persistence, Studio bridge, quality, product tests still outstanding |
| Gate A frozen commit | `ca8bf64c8525a9cf59cb1332c4819763a0f9197e` (PR #149) |
| Gate A frozen oracle blob | `046a26a7baf31003244e05088a2b5d19bc7af416` |
| Gate B audited final physical trial | `b6aa1bed340cbd81d90b46bf16639b3fa47a3bb6` (PR #150) |
| CI | [exact-head run #39702992138](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39702992138) — SUCCESS; plus tests, SV1, OG3 and OG4 SUCCESS on same commit |
| Raw evidence | [Artifact #12392884715](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39702992138/artifacts/12392884715), 8 archived files including decision.json; ZIP SHA256 `f456e39f0b2f7f1df534df6356350d9371b5c0c81e39d5e8e55323bb9f7ae881` |
| Prior review packet | [audit evidence packet](GATE_AB_LIMITED_REVIEW_PACKET_20261022.md) and [machine decision JSON mirror](gate_b_site08_evidence_b6aa1bed.json) |

This decision is **an additional subsequent interpretation of the locked evidence**, not a change to Gate A's pre-run prediction, tolerance or acceptance criteria, and not a rewriting of `decision.json` with post-run PASS.

## Review performed

1. **Code/provenance**: Read the fixed Gate A oracle and protocol, Gate B `run.py` and refusal tests, and the inherited Experiment009/023/026/027 physical transfer law / task realization. Verified the frozen SHA identifiers, executed experiment HEAD, documented numerical parameters, 102 acoustic calls per trial, source/task/digest guards and five exact-head CI successes.
2. **Independent Wolfram mathematical implementation (ideal oracle)**: Reimplemented a 16-section serial ABCD pipe with area-dependent (Z_c=\rho c/A), (c=343\,\mathrm{m/s}), (ho=1.20\,\mathrm{kg/m^3}), pressure-release `Z_L=0`, no attenuation; extracted first three input-impedance `|B/D|` peaks over 100–3500 Hz on the **pre-frozen 5 Hz grid**. Matched all 18 fixed Gate A values exactly:
    - ratio 0.90: rest `720,1295,2905`, terminal `275,2110,3145` Hz;
    - ratio 1.00: rest `720,1290,2915`, terminal `275,2100,3160` Hz;
    - ratio 1.10: rest `715,1285,2925`, terminal `275,2095,3175` Hz.
3. **Independent Wolfram reconstruction of actual Core transfer model**: Used the `Experiment009` complex wave number (k=2\pi f/343-0.4 i), (ho=1.21), (Z_L=0.05(\rho c/A_{out})), observable ( |1/(C Z_L+D)| ), 16 exact baseline areas from physical `decision.json`, and three fixed Gaussian task fields from `Experiment027`. A **full 100–3500 Hz 2 Hz grid** found the same three approximate peaks for each of the six static snapshots; localized 0.25 Hz scans around the already recorded Core peaks then independently reproduced **all 18 recorded Core values exactly**. These localized scans are *post-hoc implementation cross-checks*, not new blinded prediction; the complete peak ordering on the full fine grid was not independently re-scanned.
4. **Direct raw artifact verification outside GitHub CI**: Independently opened and hashed the original downloaded artifact ZIP; SHA256 matches the GitHub digest above. All 7 binary files' actual bytes match their respective frozen `decision.json` SHA256 entries. Each of the four NPY pressure arrays is 24,000 finite float64 Pa samples. Independently recalculated relative L2 differences: ratio 0.90 `0.013811261347324754`, ratio 1.00 `0`, ratio 1.10 `0.014914425230425132`. The separately computed baseline replay is **bit-for-bit identical** as an array and as `.npy` file to the first baseline in this archived CI run. This is a **same-run** replay, not a claim of cross-machine unquantized byte identity.
5. **Error/acceptance classification**: 18/18 Core-vs-frozen-ideal comparison values have residual ≤ frozen 7.5 Hz (max **4.75 Hz**). Edited raw differences exceed the prespecified (10^{-8}) relative L2 criterion by large numerical margins. These are numerical effects; no listening or anatomical human evidence is inferred.

## Scientific scope actually adopted

> Under a fixed prescribed LF excitation and fixed three-task movement law, a bounded ±10% rest-area perturbation at zero-based section 8 of the inherited 16×10mm segmented 1D tract numerically propagates through Core's geometry-to-acoustics-to-pressure computation and yields reproducible, nonzero physical-model pressure differences, while the pre-specified six snapshot groups' 18 frequency peak comparisons satisfy the frozen cross-model engineering discrepancy threshold.

The implementation's tract is a **mathematical physical surrogate**, not a measured complete living vocal tract. The phrase `physical-model pressure` describes a computed quantity, not a calibrated in-vivo sound pressure or speaker sound. The pressure difference is modest (relative L2 ~1.4–1.5%) and by itself does not establish audible or aesthetically useful character differentiation.

The Wolfram ideal model uses *input impedance* maxima, no loss, and pressure-release termination. Core uses attenuation, resistive outlet load and *outlet volume velocity* response, followed by a simple monopole radiation approximation for waveform. They are **different boundary value/observation models**; matching frequency locations supports bounded numerical agreement, not identity of transfer functions, absolute pressure accuracy, or biological validity. The 7.5 Hz tolerance is a prespecified engineering comparator, **not** a metrological confidence interval. Site8 was known in previous all-site theoretical study, and must not be described as an entirely blind spatial holdout.

This `GO_LIMITED_1D` does **not** adopt true time-domain bidirectional FSI, energy-passivity validation, organ/gesture generality, phonetic identity, natural sound, creator ABX audibility, arbitrary 3D morphology, production Core interfaces, nor any Studio workflow.

## Residual risks and decision on original negative control

### `inherited_solver_internal_fault_injection` — `NOT_TESTED`, waived **only for this bounded research-use decision**

- Evidence actually present: eight synthetic fault/error cases through Gate B *acceptance boundary* all PASS; source/task identity checks, shape and finite checks, unexpected reported feasibility-status/fallback refusals, null, repeated baseline, and exact-head execution.
- Evidence missing: injection into inherited internal acoustic-solver control flow to demonstrate detection of all plausible silent numerical fallback or malformed internal states. **Do not transform this unmet frozen coverage into PASS.**
- Reason for **narrow exception**, rather than restarting research: the accepted statement is a traceable deterministic **model-specific numerical observation**, directly corroborated by raw bytes plus a separately implemented static spectral check. It does not rely on safe arbitrary user inputs or production runtime error guarantees. Modifying the frozen acoustic solver or re-running a different preregistered experiment solely to claim this limited observation would not proportionately strengthen it. The remaining internal failure path uncertainty is real.
- **Risk owner:** repository owner/maintainer (`ryonakayama234`) for deciding to use these findings as *internal research evidence* under an explicit owner delegation to AI; AI is the documenting technical evaluator, **not** an independent accountable person or person responsible for a production system.
- **Expiration/trigger:** exception **does not carry forward** to Gate C stable API, untrusted creator input, production solver, Studio integration, real-time playback, or main-branch product adoption. At those gates, run inherited/internal solver fault-injection or document explicit bounded alternative with independently inspectable code and written product-risk rationale. If new anomalies or model refinements undermine this narrow numeric claim, reopen science evidence and version the new protocol without altering the original.
- **Independent reviewer missing:** the owner's delegation substitutes a **project-level research disposition**, not a falsely claimed independent sign-off. `INDEPENDENT_SCIENTIFIC_RATIFICATION_NOT_OBTAINED`; any publication or stronger statement requiring independent review still needs one. The earlier #151 *independent-ratification task* can be administratively closed as **not planned** once this waiver/disposition is recorded, rather than marked independently completed.

## Operational next action and non-action

- The frozen **Gate A/B research outcome can be cited as `GO_LIMITED_1D`** in future explicitly labeled internal research; retain exact commit, CI, archive hashes and scope statement each time.
- Keep Gate A #149 and Gate B #150 **Draft**; **do not merge to main** solely because this research GO was documented. This is a science-scope decision, not a code integration/maintainability sign-off.
- Keep Gate C #145 `PROTOTYPE/HOLD` and do not ship a BodyRevision or Studio API. Gate C security/revision-lifetime/persistence/adapter/creator-quality acceptance is separately unresolved.
- The Actions raw artifact currently expires **2027-01-20**; retain downloaded ZIP on durable storage if it must outlive that date. The audit branch stores SHA/digests but not full waveform bytes.
- Authoritative in-repo decision is **this document**, attached to immutable evidence branch. This text is the accountable **AI technical rationale** only, written at the user's request, and it must not be represented as a human expert's independent signature.

**Bottom line: `GO_LIMITED_1D` for numerical research; `NOT_TESTED` remains explicit; no independent ratification; no Gate C adoption; no physics rerun; no silent criterion change.**
