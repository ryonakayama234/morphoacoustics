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
