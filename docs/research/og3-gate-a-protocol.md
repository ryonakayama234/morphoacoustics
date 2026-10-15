# OG-3 Gate A — public API acceptance & falsification protocol (candidate)

Date: 2026-10-15 JST. Base `1fb6c9f691f94558c6d5ccaf4b018eb05389cafe`. Issue [#100](https://github.com/ryonakayama234/morphoacoustics/issues/100). **NOT an adopted protocol / NOT newly blinded prospective scientific replication / no new Core implementation in this PR.** Freeze after independent design review, before Gate B public implementation. Earlier Experiment039 fixture values and tolerance are inherited **controlled regressions**, not new data-dependent threshold tuning.

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
- Frozen X2a source inventory must not be bypassed. If source modules are added, an audited explicit hash-pinned change with complete legacy preflight and 0.5s live WAV/trace smoke is a **blocking** compatibility gate.
- Existing `CreatureSpec`, `PreparedMorphology`, `BodyPresetRegistry`, v0 contracts and current frozen Experiment039 must pass their unmodified regression scenarios; v1 draft PR #101 is not a dependency.
- Honest `INVALID` / `UNSUPPORTED` / `NUMERICALLY_UNRESOLVED` / `FAILED`; `INFEASIBLE` reserved for supported task realization. If there is no singular case in direct lossless transfer evaluation, do not synthesize one for this gate.

## Evidence & decision format

Gate B submission should contain full names/revisions/units/ports, canonical serialization and digests, all seven frequency-wise complex real/imag matrices, positive + falsifying negative controls, errors and thresholds, exception diagnostics, independent Wolfram source/JSON hash, exact HEAD and base SHA, Python/NumPy/Wolfram versions, two runs of the evidence generator from separate fresh outputs, SHA-256 sidecars, CI run IDs and saved raw artifacts. Execute full `pytest`, relevant `mypy`, Python 3.11–3.13 CI, X2a CLI regression and clean-room consumer import. Reviewer signs exact code SHA in separately documented physical/numerical vs code/API critiques; disclose if the same AI context underlies them.

Explicit `GO_LIMITED_PUBLIC_FIXED_2PORT` / `INCONCLUSIVE` / `REJECT` with resolved findings and known non-goals. CI green is insufficient for GO, and Gate A PR is **not** an adoption.

## Gate A post-author review amendment candidate — not yet frozen (2026-10-15)

[Gate A self-audit PR #102 comment](https://github.com/ryonakayama234/morphoacoustics/pull/102#issuecomment-6188922718) found that a Python source-freeze check, byte-level SHA ABI, terminal condition semantics and observation vector shape need explicit dispositions before implementation. [RFC §8](./og3-public-preparation-rfc.md) proposes them. **No new numerical threshold/fixture is changed; existing Experiment039 original frozen data remains untouched.** Following additional acceptance tests are proposed:

1. Hashing: exact fixture bytes vs declared SHA domain separation; organ tuple reordering same hash, oriented port edge reversal NOT equal; B-only numeric/revision mutation changes structural+prepared hashes but keeps A byte-equal; non-physical canvas coordinates excluded; compare Python/JS canonical byte strings before promising cross-language equivalence.
2. Observation: nonempty 1-D finite nonnegative grid, output `(N,2,2)` complex; terminate metadata only and **full two-port identical for matched vs pressure-release** with same tubes; no falsely emitted loaded impedance in transfer response. Preserve original frequency order; invalid shape/NaN and computed numerical phase failure return no plausible result.
3. X2a: all 23 prior source blob pins byte-identical; each newly introduced .py explicitly pinned; unlisted/tampered file negative tests stay failing; real live 0.5s two-take runs produce 24,000 samples at 48 kHz, 102 acoustic calls per Take, immutable raw pressure/trace/WAV artifact hashes, in **audited NumPy 2.4.6** environment. No silent repin of older research files. A valid generic matrix and pytest alone cannot satisfy this test.
4. Independent reviewer must specifically assess direct `UniformTube` re-use and no eager initializer changes, status boundary `INVALID / UNSUPPORTED / INFEASIBLE / NUMERICALLY_UNRESOLVED / FAILED`, exact typed refusal path, and transparent 1D/ideal boundary physics claims.

A numerical **planning-only** Wolfram calculation gives circular-area-equivalent `A_B=6e-4m²`, rigid Neumann first transverse estimate `r≈0.01381977m`, `f_c≈7272.95Hz`; this is conditional and **not** a validated human vocal tract bandwidth. The direct ideal tube determinant identity remains 1 and isolated matched interface energy 1. Those are supportive algebra, not independent API execution.

**Status: amendment PROPOSED / self-audit, no independent approval.** No Gate B implementation or official v1 contract freeze claimed.

## Gate A Codex-reviewed implementation amendments — 2026-10-15 (proposed, pre-code)

Following [PR #102's two automated review threads](https://github.com/ryonakayama234/morphoacoustics/pull/102), preregister the public API gate as **0 ≤ f ≤ 4000 Hz**, 1D nonempty ≤4096 points, order preserved. `f>4000` ⇒ typed `UNSUPPORTED` capability, malformed/nonfinite/negative ⇒ `INVALID`. **Canonicalize -0.0 Hz to +0.0 Hz before hashing and simulation**, and test exact snapshot/observation digest equivalence. This is *not* full-band scientific validation; the original seven fixed frequencies remain the only frozen Wolfram numerical comparison points. For zero frequency do not perform a traveling-wave power inference. Add wrong physical p/U connection lossless power-flux negative control `T†JT=J`, `J={{0,1},{1,0}}`; Wolfram computes max correct 0 at high precision, wrong particle-velocity junction defect **0.5**. New comparison tolerances and normalization for this **additional** control must be stated before executing Gate B code; inherited OG-2 thresholds unchanged. Human/independent acceptance remains outstanding.

## Gate A correction backed by first failed & later green Gate B trial (2026-10-15)

Initial inherited V3 Experiment028/029 and X2a CI failed with two new `.py` inside `src/morphoacoustics/` even after expanding X2a-only manifest; exact frozen source inventory was changed (not physics tolerance). This rejected the proposed §8 additive-pins solution. The revised **Core sibling package** `src/morphoacoustics_graph/` preserved original `src/morphoacoustics/` and all old oracle/pins, reusing unchanged `UniformTube`. [Trial machine result](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38731394921) passed Exp028/029 original decisions and genuine X2a two-Take smoke; new seven-frequency full complex fixed-oracle error 1.915e-15. Codex's >4kHz typed refusal and ±0 hashing identity were tested. Nevertheless physical/model scope remains the frozen **two passive fixed ideal serial tubes only**, and **no human-independent review or public adoption** is asserted. Exact-head rechecks required after any further correction.
