# VQ-1 G0-P EXPERIMENT — frozen test-first protocol

Status: PRE-IMPLEMENTATION / NO NEW TEST YET (2026-10-28 JST). Registered **before** G0 adapter/test implementation on an independent branch from Core main `727b11ecf103f5c087cfcb820bdec11f883e7c03`. Based on design Draft #237, not its unmerged branch.

## Falsifiable hypotheses
- H0: the proposed snapshot-to-commit port fails to reproduce the actual Core step in nonzero reflection, wrong sign, delayed tick, B0 state, overflow, or out-of-band mutation cases.
- H1: with the unchanged Core numerical law, one native-tick read-only prediction `p=2b+Z0U` and `h*p*U` equals the Core step after exactly one commit, for the qualified fixed serial 1D cases. Energy balance and propagation are consistent with a separate analytical reference.
- No hypothesis about wall pressure, sustained VF oscillation, speech naturalness or GUI change.

## Frozen cases / independent controls
1. Single-section matched, pressure_release, closed, and B0; sections of 2 and 4 native cells. Include initial backward pressure `b !=0`, pulses that generate delayed nonzero b (closed/pressure-release), +U, -U, U=0, pure zero.
2. Two-section equal and unequal areas: e.g. 0.0008, 0.0004 m2; confirm independent junction pressure/flow continuity and signed power on incident waves. A 16-section uniform M0 (L=0.01m) and M1 (L=0.011m), equal area, n=2 cells; if named fixture unavailable report they are **specified surrogate ducts**, not authenticated historical body revisions.
3. Analytic uniform single-section first-return time `2*cells` ticks with closed (positive), pressure-release (negative), matched (zero); independent initial b law `p=2*b+Z0U` without calling adapter; for a two-section junction, analytic pressure reflection `r=(Zright-Zleft)/(Zright+Zleft)`, separate flow/energy check.
4. Test pure multiple peek with `U=0, +/-1e-6`, no FIFO/radiation/tick change; one true Core tick after commit; second commit, stale snapshot, foreign adapter snapshot, out-of-band FIFO/B0 modification, nonfinite and bool input MUST be rejected without corrupting state. Large finite `1e308` expected Core failure should keep state and allow later valid commit.
5. Termination-specific p/U work and source energy ledger over 64 deterministic nonzero signed inputs; full Core residual computed separately as `delta E - source_work + outlet_loss`; nonzero b mandatory somewhere. If B0 q changes, assert q fingerprint reflected in state guard. Intentionally wrong sign, wrong Z and off-by-one tick oracles must not pass.
6. Engineered numeric acceptance (NOT biological accuracy): for non-negligible cases `abs(p_actual-p_ref)/max(abs(2*b)+abs(Z0*U),1 Pa) <= 1e-10`; `abs(deltaE-W+loss)/max(abs(deltaE)+abs(W)+abs(loss),1e-12 J) <= 1e-10`. Separately require exact zero-state silence and refusal atomicity. Any ill-conditioned low-amplitude case is recorded independently and must not silently normalize its residual away.

## Work sequence & exit
- Register all SYSTEM/DATA/EXPERIMENT **now**; then introduce adapter and tests without altering solver.
- Run GitHub Actions exact-head tests on Python 3.11/3.12/3.13 plus dedicated evidence runner retaining failures. Preserve RED runs.
- Independent critique of math, source provenance and false-positives. No merge based only on action green.
- `GO_PORT_RESEARCH_ONLY` only if tests, energy/oracle, observed nonzero reflection, atomicity, exact-head CI and review pass.
- `STOP_PORT` if wrong boundary, energy deficit, impossible same-tick contract, invalid atomicity; `NUMERICALLY_UNRESOLVED` if CI or fixture uninformative. If successful, **task G0 is complete** and G1 static reference proceeds separately without an arbitrary dynamic wall force.

No code has been executed at the time of this pre-source record.


## Executed G0-P numerical pilot — append-only evidence (2026-10-28 JST)

**Exact source SHA:** `ad967d5b978097a40ab8393704ae59e8ef5f96ae`; parent main SHA `727b11ecf103f5c087cfcb820bdec11f883e7c03`. The pre-registration was committed as SYSTEM `08116913`, DATA `968b8ec7`, EXPERIMENT `b5e662a4` **before** implementation `df532390`, adversarial tests `93c1d2c4` and dedicated workflow `ad967d5`.

- [Dedicated G0 workflow run #40686704409](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40686704409) **SUCCESS**. Pytest output: **40 passed in 0.33s**. Independent run script reports `GO_NUMERIC_PORT_CANDIDATE`; artifact [#12814748143](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40686704409/artifacts/12814748143) stores raw signed 128-tick traces and per-case maxima, including nonzero inlet reflections.
- Four 128-tick cases: single matched seeded incoming wave, two-section unequal-area B0, 16-section M0/M1 *surrogate* physical lengths of 0.01 / 0.011m, terminators closed/pressure_release. Max scaled inlet pressure error 0; maximum scaled energy residual **1.0339757656912846e-13**, compared to preregistered **1e-10** threshold; this is a floating-point/discrete port consistency result, not a continuum experimental accuracy.
- [Core full test workflow #40686704428](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40686704428) **SUCCESS**: pytest Python 3.11, 3.12 and 3.13; mypy typecheck. 
- Direct nonzero-b algebra, signed work, analytic closed/open first return and unequal-area junction, B0 termination, zero-drive silence, foreign/stale/duplicate and mutated wave/B0 rejection, nonfinite/overflow failure atomicity were tested. The artifact contains a **small set of diagnostic samples per case** plus aggregate maxima, not full wave traces for every tick; tests process every tick. Do not describe these sparse samples as full retained time histories.
- **Code-review gate:** `@codex review` requested on Draft PR #238 for the tested source head; currently running at documentation time. **Numerical verdict = PASS / code-review verdict PENDING**, so final `GO_PORT_RESEARCH_ONLY` remains pending review. G1-S actual tap-profile data still unqualified and G1-D moving-wall reference still HOLD. No human voice claim, playback Take, Studio GO or Core main merge.


### Audit-added falsifier (2026-10-28; after first green run, BEFORE G0 final acceptance)
The 40-test `ad967d5` result was numerically green but did not exercise `dataclasses.replace(snapshot, b_pa/z0/dt)` with an unchanged digest. This is a real API invariant gap and not a new aerodynamic law. A regression now verifies altered cached pressure, impedance, timestep, digest or tick must all refuse while live Core state remains unchanged; a valid original snapshot can still commit exactly one tick. Implementation commits the exact checked flow value once. **Prior 40-test receipt remains the historical pilot; the refined head requires a NEW exact-head CI and review.** This amendment does not relax or retroactively change preregistered physical/energy thresholds.


### Codex P2 findings and corrections R1 — before final research adoption
At reviewed exact source `ad967d5`, Codex reported four **P2 findings**: (1) reconstructible snapshots can keep the state digest while modifying cached b/Z/h; (2) the previous 1e308 overflow check fails **during peek**, so cannot establish Core's downstream failure atomicity; (3) the runner discards raw measured tick values on a failure; (4) the workflow's default dependency skips the runner after red pytest. These limitations make initial 40/40 evidence insufficient for the **final** research gate, despite numerical consistency.

Mitigations now authored (require their own new exact-head CI): full snapshot equality; conversion once on commit; a finite `peek(U=1e150)` whose actual Core `step` overflows on pressure-wave energy and must leave state unchanged for subsequent valid retry; every attempted tick and before/after fingerprint retained, including injected wrong-pressure negative control; and `if: !cancelled() && tests != skipped` for JSON receipt producer with explicit failed-test gate. New injected RED tests must never produce `GO_NUMERIC_PORT_CANDIDATE`. This is a quality/measurement remediation, NOT a change of physical force law or numeric tolerance.

**Do not count previous Codex review at older SHA as review of the corrected head.** A second exact-head review is required before final `GO_PORT_RESEARCH_ONLY` scientific sign-off.


### Review-added source-provenance falsifier
After 44/44 numerical tests at PR merge checkout, raw receipt `git rev-parse HEAD` did not match the branch's candidate head because default checkout uses GitHub's synthetic PR merge ref. This was detected by *reading the retained JSON artifact*, not inferred from an Actions green badge. Numerical content remains prior evidence but not the exact-head claim. G0 workflow now pins PR head checkout; runner requires `checkout_sha == expected_candidate_head_sha` before running, with a negative SHA mismatch test preserving STOP JSON. **A new exact-head workflow is required**; previous merge-ref successes do not close that gate.


## FINAL G0-P scientific verdict: GO_PORT_RESEARCH_ONLY (2026-10-28)

- **Actual code/test candidate:** `af41041086115e2cd04d66a8611fb21007e63efb`, based on main `727b11ecf103f5c087cfcb820bdec11f883e7c03`.
- [Dedicated *actual candidate* exact-head G0 Actions 40688026925](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40688026925): 45/45 test success, JSON receipt `GO_NUMERIC_PORT_CANDIDATE`; checkout and expected candidate SHAs **equal**, proven by reading [artifact 12816390431](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40688026925/artifacts/12816390431), not just CI green. Full **512 signed/native tick records retained**, with max normalized energy residual `1.0339757656912846e-13` vs frozen `1e-10`. Nonzero reflection on every case, including seeded matched inlet. Four explicit fixtures, not a general organ graph or human voice.
- [Core overall tests run 40688026978](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40688026978): **SUCCESS** (Python 3.11/3.12/3.13 and mypy). Codex final code review of exact `af410410`: **COMPLETED / no findings**. Prior four P2 review threads on Draft PR #238 remediated with proof, replied to and resolved.
- Falsifiers now explicitly tested: b/Z/h snapshot tampering; real downstream Core energy overflow *after finite peek*, with zero-state mutation and successful retry; scientific record preservation on injected corrupted observed pressure; failed pytest step cannot issue positive numerical gate; fake PR merge checkout SHA cannot masquerade as exact head.
- **Bounded verdict: G0-P PASS / GO_PORT_RESEARCH_ONLY.** No G1-S static wall-pressure digitization or G1-D wall-work proof was acquired. No new organ force model, tissue vibration, self-sustained phonation, verified receiver sound or Studio user-quality evidence. Production adoption, merging and G1 force law selection remain **separately gated**. The historical red/pending runs remain available in Actions, not rewritten.

This final evidence appendix is documentation-only after the reviewed `af410410` code. A further current-head CI check is required for the final amended Docs HEAD; code remains byte-for-byte the reviewed implementation.
