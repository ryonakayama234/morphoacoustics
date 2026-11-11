# B1 — Audit amendment: cross-JS-runtime regeneration semantics

2026-11-04 JST | Historical first Gate B CI head `b152a5cb59e33c642eba03fef9a9e62055838eb4` **FAILED** at bytewise regenerated JS JSON comparison. The B0 source/output blobs remained untouched; see F1 failure log.

## Distinct requirements
- **Original reference integrity:** the frozen Git blob `81286d0a2b7ea26cf33ce65d0eb98be6df47b607` is immutable and authenticated byte-for-byte. The original `B0-ORACLE-FREEZE.md` has not been edited, even though its suggested cross-runtime `cmp` is not a scientifically necessary test.
- **Independent regeneration scientific validity:** compare exactly 16 rows × 15 columns with strict type, unique fixture, column order, source/load/medium, phasor, preregistration SHA and method. Confirm every numeric component under *previously frozen D0 E2 tolerances* (complex pressure ≤1e-11 Pa, Zc-scaled complex flow ≤1e-11 Pa, four powers ≤max(1e-13W, 1e-10×scale)). Refuse shortened rows before any zip.
- **Independent physical validity:** neither the original byte hash nor a numerical regeneration is evidence for a real ear, measured source impedance or future Studio API.

## Actual outcome at tested SHA
Corrected comparator + mutation tests and the original static JS-wave vs Core-matrix 16 cases were successful at `d2cd21094b8c855af4fd37814e5936c89bab9ada` in [CI 41787761522](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787761522) (3.11/3.12). Cross-JS-engine differences were at 1e-16 Pa pressure component order, far beneath the already preregistered E2 error limit. These are computational facts, not permission to revise a scientific hypothesis after seeing a negative real-world result.

The initial failing bytewise reproducibility requirement remains a genuine process failure. It did not produce any Gate B physics values because the job stopped earlier. Future code should report both original byte integrity and regenerated numeric equivalence separately, rather than silently equating them.
