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
