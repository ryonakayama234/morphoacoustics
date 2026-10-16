# OG-5 Gate B1 internal numerical trial — 2026-10-16 JST

**DRAFT IMPLEMENTATION / NOT Gate B accepted / NOT ADOPTED.** Based on merged [Gate A acceptance](./og5-gate-a-acceptance.md), PR #110, commit `36b943532ea0d3de7eb0e63048e985f708bda88d`. Tracks [#109](https://github.com/ryonakayama234/morphoacoustics/issues/109).

## What was implemented

New **isolated** `src/morphoacoustics_graph/tree5.py` candidate (not imported into package initializer): five existing `UniformTube` primitives, two ideal three-port junction constraint rows and full scaled 20x20 coupled solver. Outputs ten endpoint complex pressure (Pa), volume flow (m³/s) and signed mean power, full SVD/rank/condition (A1 bound 1e4), absolute scaled residual (1e-12) and both branch pressure/flow and global passive-power checks. Internal `_solve_fixture` is a **private trial**, not the Gate A public `prepare_tree5/restore_tree5` contract. No snapshot/Blueprint parser, hashing, typed public failures or generic organ graph supported yet.

~~~mermaid
flowchart TD
  FIX["Frozen A1 fixed fixture; INTERNAL ONLY"] --> TUBE["Five unchanged UniformTube transfers"]
  TUBE --> SYS["20 rows: tubes ×10, J1/J2 ×6, source ×1, loads ×3"]
  SYS --> SOLVE["scaled 20x20 SVD + certified complex linear solve"]
  SOLVE --> PORT["10 physical endpoints p/U, powers, diagnostics"]
  PORT --> REF["B1 test: known Wolfram 8 full-port states + 144 passive cases"]
  REF -.-> B2["Future strict Blueprint/PreparedTree5/Observation+digests"]
  B2 -.-> B3["Future 144 Wolfram independent full-port comparison and science gate"]
~~~

## Provenance, tests and claim limit

The author locally exercised an equivalent isolated numerical candidate (temporary UniformTube substitute reproducing the public tube formula, **not** the real repo integration) on 144/144 positive case tuples; no local runtime exceptions. A Wolfram independent scalar impedance recursion gave p_Ain(733 Hz, C=.00015 matched)=1.914554731035266+0.23147567288386767i Pa, and the local numerical candidate gave 1.9145547310352653+0.23147567288386767i Pa. This is a **smoke check**, not proof that the committed GitHub tree imports and passes its complete CI. The PR workflow targets the actual `UniformTube` implementation and original frozen 8 all-port records.

Added trial pytest cases cover 144 condition/physical checks; eight frozen full-port records; wrong J1/J2 volume-flow-law changes; rank, ill-conditioned and nonfinite matrix guards; sign/half-scale power laws. Scope is incomplete against Gate A A1, including **all 27 API errors, all six numerical seams, full 8 wrong-law mutants, immutable hashes, and per-case 144 independent Wolfram full-port cross-comparison**.

Any failing test or mypy/CI requires documented remediation and new exact-HEAD evidence. Do not count the 144 self-consistent solves as 144 independently verified gate samples, and do not call this PR Gate B complete.

## Next B2/B3 implementation milestones

1. B2: strict normalized versioned Blueprint validation, structured/capability error precedence, immutable PreparedTree5 binding and full snapshot/restoration/canonical golden checks. Public `Tree5Error` and output schema must match A1 **exactly**; no silent amendments.
2. B3: observation schema and exact canonical byte/hash, full 144 production-vs-independently assembled Wolfram full-port cases, frozen 8 distinct checks, all numerical seam and wrong-law mutants, two SHA-bound raw evidence runs, all older Core/Studio frozen regression, Python3.11-3.13/mypy.
3. Separate Gate C critical reviews and adoption decision. Studio UI and biological voice/waveform explicitly out of scope.

~~~
# This document and living program/data/execution/ledger updates are part of
# the same Draft PR as the numerical code; experiment history is immutable.
~~~

## First exact-HEAD GitHub CI failure (2026-10-16 JST)

At `82e1c69a1494279d2066901583e4151ce44579ae`, the GitHub Python 3.11 Gate B1 test runner executed **five focused tests successfully**, and the general suite passed on Python 3.11/3.12/3.13. The Gate B1 mypy check failed **one error** in `tree5.py:132`: NumPy solve inferred `ndarray[complexfloating[Any,Any]]` while the return annotation required `NDArray[np.complex128]`. The OG3 and OG4 gate jobs also stopped at the same new-file mypy failure; no reproduced acoustic-law/regression failure. Python3.12/3.13 B1 matrix jobs were cancelled after the failed check; they are not passes. Repair adds a static `typing.cast` after confirmed complex128 matrix/solve input, changing no physical matrix, test threshold, or numerical output. Original failed run IDs: B1 38893915197, general 38893915215, OG4 38893915199, OG3 38893915193; preserve red runs as history and retest exact corrected HEAD.
