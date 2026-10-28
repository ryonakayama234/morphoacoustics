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
