# OG-3 Gate A — public API acceptance & falsification protocol (candidate)

Date: 2026-10-15 JST. Base `1fb6c9f691f94558c6d5ccaf4b018eb05389cafe`. Issue [#100](https://github.com/ryonakayama234/morphoacoustics/issues/100). **NOT an adopted protocol / NOT newly blinded prospective scientific replication / no new Core implementation in this PR.** Freeze after independent design review, before Gate B public implementation. Earlier Experiment039 fixture values and tolerance are inherited **controlled regressions**, not new data-dependent threshold tuning.

**Mandatory domain:** all support/grid acceptance cases apply only to RFC §11's two exact ordered geometries with rho=1.21 and c=343. Other valid geometry/medium is UNSUPPORTED at preparation; the 4 kHz band is never a universal geometry claim.

## Claim and hypothesis

**Narrow claim:** Production API, with no imports from `experiments/039_og2_prepared_graph`, prepares exactly two independently identified fixed rigid uniform lossless 1D acoustic tubes with one typed ideal series p/U port, deterministically binds their identity/provenance, and returns the complete complex two-port response matching existing independently evaluated Wolfram and analytic reference.

**H0 (reject):** production preparation loses/misbinds organ/port identity, accepts a false or unsupported physical law, fails a frozen complex transfer reference, or cannot roundtrip the same physical revision/response.
**H1 (bounded):** all fixed-fixture physics, falsification, refusal, provenance and legacy-regression requirements pass at the **exact implemented HEAD**. This proves only a limited stable software/API/idealized acoustics claim, not human voice or general graphs.

## Frozen inherited numerical setup

- Medium `ρ=1.21 kg/m³`, `c=343 m/s`, common between modules.
- A: `L_A=0.08 m`, `A_A=3×10^-4 m²`, revision `r1`; B: `L_B=0.09 m`, `A_B=3×10^-4` (control) or `6×10^-4 m²` (intervention), exact named B revision.
- Frequency order `[80,200,400,733,1200,2200,4000] Hz`; restrict physical interpretation to valid small-signal plane-wave, rigid-wall, lossless regime; no universal 4 kHz anatomy claim.
- Phasor `e^(+iωt)`; `[p_in,U_in]=T[p_out,U_out]`, positive volume flow A→B. `T(L,A)={{cos(kL),iZ sin(kL)},{i sin(kL)/Z,cos(kL)}}`, `k=ω/c`, `Z=ρc/A`. For a zero-volume ideal two-port `J=IdentityMatrix[2]`, `T_total=T_A J T_B`.
- Compare **all four complex** two-port entries after `S T S^-1`, `S=diag(1, Z_A)`. Never compare raw mixed-unit matrix elements with one absolute tolerance.
- An ideal `p_out=0` pressure release and a `p_out=Z_B U_out` matched traveling-wave load are **different**. Reflected/transmitted *power* formula below concerns the matched interface, not pressure-release outlet power.

## Existing fixed-fixture numerical acceptance (inherit, do not retune)

| Control / failure | Gate |
| --- | --- |
| Equal-area A+B full complex normalized transfer vs single uniform tube `L=0.17 m` | max absolute complex-entry discrepancy <= `1e-10` over 7 frequencies |
| B-area intervention complex normalized two-port vs immutable independently frozen OG-2 Wolfram JSON | max absolute complex-entry discrepancy <= `1e-10` |
| Isolated matched area step: `r=-1/3`, `t=2/3`, `R=1/9`, `T=8/9`, `R+T=1` | max absolute fraction/power discrepancy <= `1e-12` |
| False **particle-velocity** continuity `J_wrong=diag(1,A_A/A_B)` | mismatch > `1e-3` over grid; test must fail |
| Swapped A/B propagation/port order | mismatch > `1e-3` over grid; test must fail |
| New physical fixtures or broader anatomy claim | **NO PASS** until separately pre-registered with independent reference; inherited gates do not apply automatically |

Frozen reference: `experiments/039_og2_prepared_graph/wolfram/og2_oracle.json`; original `PREREGISTRATION.md` and `AMENDMENT_001.md` remain untouched. Current [independent recomputation source](./og3-wolfram-gate-a.wl) is supplementary, not a new replacement oracle.

## Gate A Wolfram planning check — executed 2026-10-15, not Core evidence

Independent Wolfram Language exact-rational `ρ,c,L,A` and 30-digit trig evaluation found at **733 Hz**, for unequal B area:
`S T_A T_B S^-1 = {{-1.4753529760, 0.5343984190 i},{1.2026670440 i,-0.2421770511}}`.
Maximum normalized element difference from **equal**-area comparator at 733 Hz: `0.8221172833`. Reflected/transmitted pressure `-1/3,2/3`; energy shares `1/9,8/9`, sum `1`. Maximum 7-grid wrong-particle-velocity difference `0.9019457527`, swapped order `1.3529186291` (matches recorded OG-2 research metrics). These checks only validate analytic planning; **no OG-3 Python execution, CI, audit or public acceptance occurred**.

## API, identity and negative test cases (to be frozen before coding)

- Valid fixed 2-node serial graph; reproducible physical ordering/port mapping, exact module revisions; no operation imports experiment code.
- Structural INVALID: duplicated organ/port IDs, unknown endpoints, wrong kind/direction, missing source/load boundary, duplicated edge, disconnected/cyclic graph, nonpositive or NaN/Inf SI parameters and overflow/underflow in derived `ρc/A` or its reciprocal. Diagnostics pinpoint graph element, no numerical body returned.
- Structurally legal **three-port branch** to two-port-only backend returns UNSUPPORTED, not INVALID/INFEASIBLE. Unequal media unsupported unless explicitly validated later.
- No implicit graph 'repair', deletion of unknown branches, anonymous tube concatenation or defaulted unknown revision.
- Reordering serialized *named* node collection without altering graph yields identical canonical blueprint/preparation digest; changing only B area/revision changes both appropriate digests while all A fields remain unchanged. Canvas position/theme excluded from both.
- Snapshot → serialization → new process → exact reconstruction must preserve identity, supported capability and response. Separate observation hash tracks frequencies/termination; unchanged old result must not rebind a new preset.
- Frozen Core source inventory and X2a manifest remain byte-identical. Put new OG-3 code only in sibling `src/morphoacoustics_graph/`, audit its source hashes/imports separately, preserve unknown/tampered-file refusals, and require original Experiment028/029 plus exact-head X2a 0.5s live WAV/trace smoke. Extending X2a pins alone is a rejected historical proposal, not an implementation option.
- Existing `CreatureSpec`, `PreparedMorphology`, `BodyPresetRegistry`, v0 contracts and current frozen Experiment039 must pass their unmodified regression scenarios; v1 draft PR #101 is not a dependency.
- Honest `INVALID` / `UNSUPPORTED` / `NUMERICALLY_UNRESOLVED` / `FAILED`; `INFEASIBLE` reserved for supported task realization. If there is no singular case in direct lossless transfer evaluation, do not synthesize one for this gate.

## Evidence & decision format

Gate B submission should contain full names/revisions/units/ports, canonical serialization and digests, all seven frequency-wise complex real/imag matrices, positive + falsifying negative controls, errors and thresholds, exception diagnostics, independent Wolfram source/JSON hash, exact HEAD and base SHA, Python/NumPy/Wolfram versions, two runs of the evidence generator from separate fresh outputs, SHA-256 sidecars, CI run IDs and saved raw artifacts. Execute full `pytest`, relevant `mypy`, Python 3.11–3.13 CI, X2a CLI regression and clean-room consumer import. Reviewer signs exact code SHA in separately documented physical/numerical vs code/API critiques; disclose if the same AI context underlies them.

Explicit `GO_LIMITED_PUBLIC_FIXED_2PORT` / `INCONCLUSIVE` / `REJECT` with resolved findings and known non-goals. CI green is insufficient for GO, and Gate A PR is **not** an adoption.

## Gate A post-author review amendment candidate — not yet frozen (2026-10-15)

[Gate A self-audit PR #102 comment](https://github.com/ryonakayama234/morphoacoustics/pull/102#issuecomment-6188922718) found that a Python source-freeze check, byte-level SHA ABI, terminal condition semantics and observation vector shape need explicit dispositions before implementation. [RFC §8](./og3-public-preparation-rfc.md) proposes them. **No new numerical threshold/fixture is changed; existing Experiment039 original frozen data remains untouched.** Following additional acceptance tests are proposed:

1. Hashing: exact fixture bytes vs declared SHA domain separation; organ tuple reordering same hash, oriented port edge reversal NOT equal; B-only numeric/revision mutation changes structural+prepared hashes but keeps A byte-equal; non-physical canvas coordinates excluded; compare Python/JS canonical byte strings before promising cross-language equivalence.
2. Observation: follow the explicit grid table below; output `(N,2,2)` complex with original order and duplicates preserved. Terminal metadata only; **full two-port identical for matched vs pressure-release** with the same tubes. No loaded impedance in a transfer response. Invalid request or computed numerical phase failure returns no plausible result.
3. X2a: entire original `src/morphoacoustics/`, manifest and all 23 pins byte-identical; new source exists only in sibling `src/morphoacoustics_graph/` and is hashed/audited separately. Preserve unknown/tampered-file negative tests and original Experiment028/029 decisions. Real live 0.5s two-take runs produce 24,000 samples at 48 kHz, 102 acoustic calls per Take and immutable pressure/trace/WAV hashes in **audited NumPy 2.4.6**. No legacy repins; a matrix/pytest alone does not satisfy this gate.
4. Independent reviewer must specifically assess direct `UniformTube` re-use and no eager initializer changes, status boundary `INVALID / UNSUPPORTED / INFEASIBLE / NUMERICALLY_UNRESOLVED / FAILED`, exact typed refusal path, and transparent 1D/ideal boundary physics claims.

A numerical **planning-only** Wolfram calculation gives circular-area-equivalent `A_B=6e-4m²`, rigid Neumann first transverse estimate `r≈0.01381977m`, `f_c≈7272.95Hz`; this is conditional and **not** a validated human vocal tract bandwidth. The direct ideal tube determinant identity remains 1 and isolated matched interface energy 1. Those are supportive algebra, not independent API execution.

**Status: amendment PROPOSED / self-audit, no independent approval.** No Gate B implementation or official v1 contract freeze claimed.

## Gate A Codex-reviewed implementation amendments — 2026-10-15 (candidate requirements; timing clarified below)

Following PR #102's frequency and signed-zero findings, freeze the implementation requirements in the grid table below. They are an engineering capability policy, not full-band scientific validation. Only the original seven positive frequencies have frozen numerical oracle comparison points; 0 Hz is not used for traveling-wave power inference. The additional flux control below is supplementary and is not a retroactive amendment to OG-2. Its explicit thresholds are recorded **after the existing Gate B trial**, before a future acceptance run; do not label them prospective preregistration for that trial. Human/independent acceptance remains outstanding.

## Gate A correction backed by first failed & later green Gate B trial (2026-10-15)

Initial inherited V3 Experiment028/029 and X2a CI failed with two new `.py` inside `src/morphoacoustics/` even after expanding X2a-only manifest; exact frozen source inventory was changed (not physics tolerance). This rejected the proposed §8 additive-pins solution. The revised **Core sibling package** `src/morphoacoustics_graph/` preserved original `src/morphoacoustics/` and all old oracle/pins, reusing unchanged `UniformTube`. [Trial machine result](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38731394921) passed Exp028/029 original decisions and genuine X2a two-Take smoke; new seven-frequency full complex fixed-oracle error 1.915e-15. Codex's >4kHz typed refusal and ±0 hashing identity were tested. Nevertheless physical/model scope remains the frozen **two passive fixed ideal serial tubes only**, and **no human-independent review or public adoption** is asserted. Exact-head rechecks required after any further correction.

## Six-thread correction: observation contract and reproducible flux control (2026-10-15)

All refusals return **no observation**, no response matrix and no observation digest. Validate malformed/type/value errors before capability; otherwise report resource limit before frequency limit when both apply. Boundaries are inclusive; no implicit resampling, sorting, deduplication or truncation.

| Request / fixture | Required outcome / Gate B acceptance case |
| --- | --- |
| `[733]`, `[4000,80,4000]`, and a finite 4096-point 0..4000 Hz grid | Success with `(1,2,2)`, `(3,2,2)`, `(4096,2,2)` respectively; one matrix per input, source order/repeats preserved. These exercise software semantics, not new frozen spectral science. |
| Frozen `[80,200,400,733,1200,2200,4000]` | `(7,2,2)`; compare all four complex entries against unchanged OG-2 reference and inherited tolerances. |
| `[0,4000]` | Success `(2,2,2)`; static T(0)=I, no traveling-wave power claim at zero. |
| `[4000.000001]` or `[100000]` | `UNSUPPORTED`, frequency-capability diagnostic. |
| Finite nonnegative **4097**-point 0..4000 Hz grid | `UNSUPPORTED`, resource-limit diagnostic; never truncate to 4096 or the oracle grid. |
| Scalar, empty, multidimensional, string/bool, NaN/Inf, any f<0 | `INVALID`, precise request-path diagnostic. |
| `[+0.0]` versus `[-0.0]` | Normalize before evaluation/snapshot/hash; canonical frequency hex is exactly `0000000000000000` for both, never `8000000000000000`; identical complete canonical bytes, snapshots, matrices and observation digest. |

**Flux law, normalization and thresholds:** avoid overloading the ideal junction `J=I` above: call the power metric `J_flux={{0,1},{1,0}}`. With `M=S T S^-1`, `S=diag(1,Z_A)`, and phasor state `y=[p,Z_A U]`, mean power is `y† J_flux y/(4 Z_A)`. Define the **dimensionless** defect `d(M)=max_ij abs((M† J_flux M-J_flux)_ij)`; do not compare mixed-unit raw T entries. Evaluate every one of the seven positive fixture frequencies. Correct `M` must have `d<=1e-12`; deliberately wrong particle-velocity junction must have `d>1e-3` and `abs(d-0.5)<=1e-12` at **each** frequency. Algebraically a lossless tube preserves J_flux; `D=diag(1,A_A/A_B)` gives `D† J_flux D=(A_A/A_B) J_flux`, hence this fixture's wrong cascade gives defect exactly 1/2. Reversed organ order can still conserve flux; its separate inherited matrix-oracle mutation must remain.

The committed [Wolfram source](./og3-wolfram-gate-a.wl) now constructs J_flux, proves the symbolic tube/wrong-junction identities, evaluates both defects with 50-digit intermediates, exports per-frequency defects, thresholds and `all_controls_pass`, and exits nonzero on flux-control failure. JSON numbers are serialized as machine reals after high-precision computation. A rerun of this exact source returned both symbolic identities true, correct defect numerically zero at ~49 decimal places, wrong defect 0.5 at all seven points and `all_controls_pass=true`. This is analytic evidence only; Gate B must apply the same checks to its actual output on a new exact HEAD. Preserve/hash the source and raw JSON with that submission.

The [raw JSON from that rerun](./og3-wolfram-gate-a-result.json) and source/result SHA-256 receipt are recorded in the [ledger](./organ-graph-experiment-ledger.md). It is supplementary analysis, never the frozen Experiment039 oracle.


## Geometry correction / implementation reconciliation

[RFC §11](./og3-public-preparation-rfc.md) fixes the supported geometry/medium, exact binary64 capability matching, invalid-before-unsupported ordering and prepared/snapshot bypass protection. [Gate B work order](./og3-gate-b-reconciliation.md) is the acceptance checklist before its next trial. Existing numerical thresholds and Experiment039 oracles remain untouched.
