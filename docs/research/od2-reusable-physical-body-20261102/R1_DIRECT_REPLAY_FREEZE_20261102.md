# OD-2 R1 — direct revision-to-physics replay extension, prospective audit (2026-11-02)

**Chronology:** this separate prospective engineering test is added AFTER the first OD-2 machine success on implementation SHA `5003ab497e43ba09ad93ca1f34d3d84e9313b4f9` and BEFORE new direct-replay code. Do not portray it as part of the original A3 freeze. It addresses a material gap: the earlier OD-2 suite matched a derived revision receipt to the independent OD-1 shape/pressure result, but did not re-invoke the physics solver with geometry *reconstructed from that receipt*.

## New falsifiable R1 claim
Given exact Core M0 parent and verified five-cell derived BodyRevision ID, reconstruct a new `Tract1DGeometry` from its recorded binary64 hexadecimal area and length values; bind this geometry to the trusted M0 creature using the existing Core `prepare_tract1d`; use the **same frozen Exp029/Exp027/Exp009** physical realization and LF100 source to generate a *fresh waveform*; compare that waveform to the archived same-case raw Pa from original OD-1.

## Frozen before writing R1 implementation
- Conditions: c4/r1.10 as primary, c8/r0.90 as secondary; both are already observed OD-1 cases, so this is an engineering equivalence test only.
- Exact same verified archive, source/task/solver/observation and pinned NumPy 2.4.6. Require preparation + capability FEASIBLE; 102 acoustic calls; 48000Hz x24000 float64 Pa; all finite.
- Compute dimensionless full-duration relative L2 = norm(new raw Pa - archived Pa) / norm(archived Pa). **R1 equivalence threshold <=1e-12** under the same pinned CI environment. Also require unchanged trustworthy body receipt ID and full rest geometry shape equality. The assertion is about deterministic execution equivalence, not audibility or physiological truth.
- Tamper/unsupported/stale ID must be rejected by the established source + receipt archive re-verification. Do not permit free waveform, desired F0, override source/task or alternate solver.
- No new registry, persistent Take, public Core ABI or Studio edit. Expose an opt-in `reperform-revision` proof operation only, not free speech and not arbitrary new performances. Record actual raw checksum, 102-call proof and relative L2 in output.
- If mismatch, label R1 FAIL/HOLD; do not rescale/filter the waveform. Current G0–G2 body provenance, all earlier negative outcomes, and original OD-1 archive remain immutable.
