# OG-5 Gate A acceptance — frozen specification for Gate B

2026-10-16 JST. Decision: **ACCEPTED_FOR_GATE_B / SPECIFICATION_FROZEN**.

The owner requested final specification ratification and merge in the review
session. Final technical review covered PR #110 at
`b7fb56c66236b0cbdb532fec8c75d46709c95bd0`. The ratification commit adds this
decision and updates current status/index text; it does not change any normative
schema, fixture value, hash domain, refusal rule, numerical threshold, source,
oracle or design workflow from that reviewed technical revision.

## Accepted scope and source of truth

- [Amendment A1](./og5-gate-a-amendment-a1.md) is normative over conflicting
  original draft language in [API](./og5-tree5-api-v1.md) and
  [protocol](./og5-gate-a-protocol.md). The original eight records and four
  Blueprint vectors remain immutable.
- Exactly five fixed passive lossless 1D acoustic tubes, two ideal zero-volume
  branch constraints, prescribed peak volume flow, specified loads/geometries
  and eight frequency anchors. No arbitrary topology, biological anatomy,
  moving organs, voice/WAV or Studio integration is accepted.
- Snapshot/Observation/complex/diagnostic fields, all three canonical hash
  domains, exact bytes, stable error code/path precedence and atomic refusal
  are frozen as v1 implementation requirements.
- Complete structural validity before capability, cycle INVALID, legal larger
  binary tree UNSUPPORTED, scoped revision strings and recomputed preparation
  binding are required.
- Full-rank SVD including zero values, condition2<=1e4, scaled equation
  residual<=1e-12, full-state error<=1e-10 and defined power/junction tolerances
  are required. The positive denominator is 144 successful samples out of 144.
- Eight explicit wrong-law/output mutants plus actual numerical/late-sample
  seams are future implementation obligations. An unsupported input cannot
  substitute for a solver-level numerical refusal.

## Final review disposition and evidence

| Finding | Final Gate A disposition |
| --- | --- |
| R1 missing serialization/refusal contract | Closed: A1.1–A1.3; complete normalized inputs, snapshots, observations, domain-prefixed byte vectors, errors and numerical seam fixtures |
| R2 unrepresentable valid cycle | Closed: split-only connected validity implies a tree; cycle and lawful seven-organ fixtures have explicit, distinct receipts |
| R3 truncated SVD misses singularity | Closed: full SVD/rank guard with actual duplicate-row, full-rank bad-condition and nonfinite negative matrices |
| R4 ineffective child-slot permutation | Closed: physical symmetry is separate from bounded mapping identity; eight explicit mutants have observable margins |

The existing [verification inventory](./og5-gate-a-a1-verification.json) is an
immutable receipt for the technical candidate above; its REVIEW_PENDING status
and content hashes are historical, superseded for acceptance by this record.
The status/index-only ratification changes are not a new physics experiment.

Validated design evidence at the reviewed technical revision:

- Wolfram 15.0.1: 144/144 positive design samples; maximum global/recursive
  scaled endpoint difference 1.320372144714677e-14; condition2 maximum
  223.7427248146297; equation residual maximum 3.376611507232129e-16.
- Independent six-node pressure assembly vs 20-state equations:
  maximum 3.356621199780979e-14 over 144; vs archived eight records:
  maximum 1.047382306668854e-15.
- All eight numerical mutants exceed 1e-6; smallest discrepancy
  0.3681067345986977. Rank/condition/nonfinite refusals are reproduced.
- Python and independent JavaScript agree on complete canonical vectors/hashes.
  Design CI and existing tests/OG3/OG4 compatibility CI all succeeded at that
  exact technical revision (four PR and four push workflows).
- Final ratification HEAD must pass applicable CI before SHA-guarded merge;
  exact run/merge receipts belong to the PR conversation and postmerge receipt.

Review provenance is owner-authorized AI technical review with shared author
context. Independent algorithms/encoders provide numerical and byte checks;
there is no claimed independent human or institutional approval. Acceptance is
based on the reviewed written contract, explicit negative controls, byte
agreement, algorithmic comparisons and compatibility evidence together.
This scope is a design handoff, not a Gate C runtime release.

## Next authorized development boundary

A separate Gate B Draft may now implement `morphoacoustics_graph.tree5` against
the frozen specification. It must execute all 144 positive samples against each
independent reference path, the archived eight separately, all malformed/refusal,
immutability, mutation and atomicity controls, Python 3.11–3.13/mypy and original
OG3/OG4/Exp028/029/X2a preservation requirements.

The 27 error and six numerical seam fixtures are expectations for that future
Core API; this acceptance does not claim they ran against an implementation.
Any necessary change to frozen normative behavior requires an explicit reviewed
amendment/version and updated goldens; no silent contract invention in Gate B.
Gate C critical physics/numerics and data/ABI review, exact-HEAD evidence and a
separate scoped adoption decision remain mandatory. Parent issue #109 stays open.
