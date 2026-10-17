# OG-5 Gate C remediation — 2026-10-16 JST

Current: R5 outer-version-group repair candidate; final exact-HEAD CI/evidence
and a separate Gate C technical disposition are pending. This file does not declare adoption or authorize merge.
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


## R3/R4 follow-up: one frozen capability selection rule

The [final review at 3eeab25](https://github.com/ryonakayama234/morphoacoustics/pull/112#pullrequestreview-5549383591)
found that the D/E matched-only restriction ran after topology/geometry, and
geometry's first field in implementation order won over the A1 ASCII pointer.
Both are frozen A1.3 API violations, not altered physical solutions.

After complete shape/relationship/graph validation and canonical collection
normalization, capability validation collects applicable refusal candidates and
selects by A1 code-table rank, then escaped ASCII pointer. Known D/E load
restrictions join the other LOAD_NOT_SUPPORTED candidates. Fixed geometry is
examined only when the exact organ/port/junction mapping is recognized; lawful
unsupported names do not cause fixed-dictionary lookup errors. Restore retains
its outer schema/digest-version/backend ordering before Blueprint capability,
and hash checks still follow capability. No physical law, supported input,
public schema, canonical byte encoding or frozen golden fixture changes.

The new contract suite exercises every nonempty combination of six Blueprint
capability categories, prepare/restore and reversed collection order, plus all
pairs of geometry fields on all five organs, same-code pointer ties and unknown
organ mapping. **320 assertions: 54 FAIL / 266 PASS before the fix**. The existing
R3/R4 six reproductions are covered. The post-fix results belong to the PR receipt.
Expectations derive from A1, without importing the production selection helper.

The B3 workflow now watches its golden-input dependency on both push and PR.
The standalone twin audit also compares every archived oracle case directly
with the checkout's eight pinned shards, so matching rehashed states/references
cannot replace the immutable reference values. This check imports no Core or
NumPy; altered references are explicitly tested. Earlier source/hash/power audits
remain in force. The two fresh raw runs must use this auditor's new source hash.

Architecture and data flow remain:
validated Blueprint -> normalized semantic mapping -> capability candidates ->
A1 code/pointer selection -> immutable Snapshot -> unchanged physical solve ->
atomic Observation -> source-pinned independent evidence audit.

This is a repair receipt and execution handoff, not SUPPORTED_LIMITED adoption.
Keep the PR Draft/unmerged until the corrected committed HEAD has all required
CI and raw evidence and a separate critical Gate C disposition. The earlier
3eeab25 INCONCLUSIVE review remains accurate for its historical version.


## R5 follow-up: outer Snapshot version group and phase boundaries

The [R5 final review at 532051c](https://github.com/ryonakayama234/morphoacoustics/pull/112#pullrequestreview-5550086282)
found a Snapshot-specific gap outside the earlier 320 Blueprint tests. When both
outer schema and digest_version are unsupported, A1.3 requires /digest_version
before /schema within the outer version group. Both candidates are now collected
and the lowest escaped ASCII pointer is selected. The group order remains:
shape/scalar -> relationships -> cycle/connectedness -> outer versions -> backend
-> nested Blueprint capability -> blueprint hash -> preparation hash.
The binding is still reconstructed before any response-request validation.

New unittest tests run without a pytest dependency and are also collected by the
normal pytest CI. Six test methods exercise 78 cases: all 15 nonempty combinations
of the four outer/nested markers, shape/relationship/digest-syntax priority,
capability-before-hash, hash order and receiver-before-request. Before the fix,
the primary matrix had 4 failures and 11 passes; its copy with inconsistent hashes
also had the same 4 failures. The remaining boundary cases passed. After the fix,
all 78 cases pass. The fixtures and expectations do not import a production
selection helper. Both dedicated workflows watch the new test file and B1/B2
explicitly executes it on all three supported Python versions.

Wolfram separately encoded the four-marker/group-order truth table and confirmed
15 cases, four old-code mismatches, ASCII outer order /digest_version,/schema,
and backend before nested Blueprint version. This checks a written API rule;
it is not new physical or blind numerical evidence. Correct ASCII comparison uses
an equal-length base-256 key of zero-padded ASCII+1 bytes, rather than Wolfram's
canonical ordering of variable-length lists of character codes.

Only the outer version group's choice changes. Unknown marker shapes still
refuse before capability, outer groups still precede nested capability, and
physical responses, hashes on valid values, frozen A1/goldens and Wolfram
physical references are unchanged. Collect exact-HEAD CI and two fresh B3 raw
archives, inspect inherited compatibility, and issue a separate scoped technical
review. The earlier INCONCLUSIVE decisions remain historical for their old HEADs.
