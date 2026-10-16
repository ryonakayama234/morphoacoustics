# OG-5 Gate C remediation — 2026-10-16 JST

Current: implementation repair candidate; final exact-HEAD CI/evidence and Gate C
re-review are pending. This file does not declare adoption or authorize merge.
The [review at ca07c974](https://github.com/ryonakayama234/morphoacoustics/pull/112#pullrequestreview-5549021528)
remains an immutable INCONCLUSIVE receipt for that old implementation.

## Frozen semantics restored

R1: object keys are checked for built-in str and ASCII before constructing
unknown-field paths. A non-ASCII key returns INVALID_STRING at its containing
object path, including nested Blueprint and Snapshot readers (A1.1).

R2: relationship validation chooses once among independent error candidates by
escaped-pointer ASCII order (A1.3). Input object positions identify organ owners
until ID uniqueness is established, so duplicate semantic IDs cannot invent a
self-connection. Ambiguous duplicate Port IDs are reported at their definitions;
role/owner/binding errors that would require choosing one of their definitions
are suppressed. Independent missing references and other errors still compete.
No changes to A1, the 27 frozen refusals, golden bytes, physical laws or oracle.

Reproduction tests were added first: 11 failed / 1 passed against ca07c974
(Unicode cases, compound-reference/duplicate cases and fresh-process imports).
After repair, all pass alongside the existing frozen cases. Both prepare and
restore are covered, with duplicate organ, Port and junction identities.

## Related audit repairs

Contract/kernel imports are deferred until capability/response use, removing the
fresh-process circular-import failure. The normal tree5 facade stays identical.

B3 refuses an existing output directory before writing anything, rejects a dirty
tracked worktree in addition to mismatched HEAD, and records production
kernel/adapter/primitive/manifest/auditor hashes plus actual Python/NumPy/platform
and NumPy BLAS build configuration. Failed attempts cannot overwrite a previous
successful evidence directory. CLI rejection and a real temporary dirty Git
repository are tested.

The standalone twin auditor imports no Core or NumPy. It independently encodes
A1 binary identities, recomputes all Observation/Blueprint/preparation digests,
checks the exact 144-case grid and case/input identity, compares raw full states
with both archived Wolfram references, recomputes port powers/energy balance,
and verifies source hashes and HEAD against its checkout. Rehashing tampered
states and claiming zero comparator errors cannot pass. Each archive retains
its own raw bytes; across-worker floating point uses frozen physical tolerances.

B1/B2 and B3 path filters now cover the contract, physical primitive, tests,
scorers/auditor and dependency manifest. General tests and inherited OG3/OG4
compatibility remain required. Prior unsuccessful runs/old evidence are retained.

## Review and release boundary

Collect two fresh B3 workers and all applicable CI on the committed repair HEAD;
examine downloadable raw artifacts and inherited Exp028/029/X2a again. Record
separate physical/numerical and API/data/provenance critical assessments, disclose
shared assistant context, and only then decide SUPPORTED_LIMITED / INCONCLUSIVE /
REJECT for that exact version. A green numerical job alone is never Gate C.

Possible supported capability remains fixed five lossless 1D tubes, two ideal
zero-volume junctions, eight frequency anchors, C area in three values, C load
matched/closed, source scale in three values, at most 256 ordered samples, with
all ten complex p/U endpoints and signed mean powers. No continuous-frequency,
arbitrary-topology, moving-organ, speech/WAV or Studio integration is introduced.

Final local/CI counts, commit/run/artifact identities and the re-review disposition
belong to the PR review receipt, avoiding a self-referential commit hash here.
