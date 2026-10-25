# SMC-4 Gate B-R — frozen prospective ingress falsification protocol

**State:** FROZEN_BEFORE_TESTS_AND_CODE; 2026-10-25 JST. Research Issue [#188](https://github.com/ryonakayama234/morphoacoustics/issues/188). Parent proposed design [#186](https://github.com/ryonakayama234/morphoacoustics/pull/186) under independent GitHub Codex design review. This is a research protocol, NOT an adoption verdict. Historical rejected Gate B [#180](https://github.com/ryonakayama234/morphoacoustics/pull/180) unchanged.

## Executable slice bounded by this preregistration

In-scope: **isolated boundary only**. No legacy unadopted SMC-4 TaskLexicon source is copied or executed. `parse_canonical_request(bytes)` returns a frozen `CanonicalCompileRequest` holding canonical UTF-8 bytes + digest and a verifiable `IngressReceipt`; it does not generate `SymbolicPlan`. A valid accepted request may later be mapped by a separately audited motor compiler. `GO_LIMITED_INGRESS` is the maximum positive verdict for this slice, never `GO_LIMITED_SYMBOLIC` or phonetic/physical proof.

Exact root keys: `schema_version,segment,pronunciation,motor_mapping,coordination`. Segment: `segment_id,source_text,source_revision,language`. Pronunciation: `paths,selected_path_id`. Each path: `path_id,units,required_spans,complete`; unit: `unit_id,symbol,start_offset,end_offset`. Motor mapping: `profile,lexicon,context`; lexicon: `revision,rule_revision,definitions,bundles`. Definition: `definition_id,semantic_revision,variable,value_domain,goal_kind,applicability_domain,capabilities,algebra`. Bundle: `bundle_id,unit_id,symbol,slots,context,priority,profile,target_scope_kind,target_unit_ids`. Slot: `slot_id,candidates`. Candidate: `template_id,definition_id,semantic_revision,lower,upper,context,priority,evidence_id,status`. Predicate: `op,key,expected,operands`. Coordination: `shares,anchors,relations,coordination_kind`; share `episode_id,members`; anchor `unit_id,slot_id,event,time_s`; relation `from_unit,from_slot,from_event,to_unit,to_slot,to_event,lag_s`. Fraction `numerator,denominator`. **All listed keys mandatory**, even empty arrays or null priority; no unknown keys, duplicate keys or inferred defaults. JSON booleans are distinct from integers; exact finite int64 only; float/exponent/nonfinite rejected everywhere. Nullable fields: `priority` only; all other scalar strings nonempty; selected_path_id required nonempty. Strings must be valid Unicode scalars, no silent NFC. `Event` is `ONSET|OFFSET`, `op` in `TRUE|FALSE|EQ|NOT|AND|OR`. Strong Kleene expression shape strict; unordered operands are *not* canonicalized in this v1 (prospective future amendment needed). Rational fractions canonical/reduced, positive denominator, absolute magnitude <=2^63-1.

Limits: <=262144 UTF-8 bytes; <=32 container levels; <=4096 parsed value/container nodes; <=16384 source code points; <=256 paths/units; <=256 task definitions; <=512 bundles; <=1024 total slots+candidates; <=1024 anchors+relations; <=256 code points each other string; time numerator and denominator int64. Enforce wire length before decode/hash; enforce stack depth with bounded lexical scanner *before* JSON parse; enforce parser object duplicate-key rejection; enforce node counts with bounded iterative traversal after parse. Deep invalid input must not generate graph, accepted request, or semantic digest.

Raw `submission_sha256 = sha256(exact admitted input bytes).hexdigest()` for byte-backed <=limit valid or invalid; null for nonbytes, overlimit. For accepted v1 JSON only: canonicalize schema-declared unordered `paths` by path_id, `definitions` by (definition_id,semantic_revision), `bundles` by bundle_id, `slots` by slot_id, `candidates` by template_id, `shares` by episode_id, `anchors`/`relations` by typed tuple, `members`/ `target_unit_ids`/`capabilities` by typed tuple/string; preserve selected-path `units` and `required_spans`, source Unicode, time direction, predicate operands. Canonical JSON `ensure_ascii=False,sort_keys=True,separators=(',',':')` encoded UTF-8. Semantic hash `sha256(b'SMC4-BR-CANONICAL/v1\\0'+canonical_bytes).hexdigest()`; receipt hash `sha256(b'SMC4-BR-RECEIPT/v1\\0'+deterministic receipt fields)`. `schema_version` included and v1-hash domain fixed.

For schema-valid structurally complete path but *motor-mapping disagreement* do not infer `UNMAPPED` or `INFEASIBLE`: accepted boundary snapshot is independent of later mapping. If selected path not unique, incomplete, invalid source coverage or invalid bundle object structure: schema ingress refusal, canonical semantic digest null. Definition->candidate references and prospective physical feasibility are NOT verified by this isolated ingress and must be deferred, never claimed proven.

## Preregistered falsifiers (record RED before implementation)

- **BR01/02:** raw JSON key and declared unordered set permutations produce distinct raw digests but identical accepted canonical digest/bytes.
- **BR03:** source-ordered pronunciation units and directed timing reference reversals must not yield equal semantic identity.
- **BR04/05:** duplicate key, unknown field, bad version, nonfinite float, invalid UTF-8/lone surrogate are rejected (raw digest present) without plan/semantic hash.
- **BR06:** unreduced, zero-denominator, float/boolean integer-coercion and too-large rational refused.
- **BR07:** oversized bytes refused without digest; beyond max JSON depth/node budget refused without plan, bounded; exact ceiling admits bounded payload.
- **BR08:** a cyclic list and any arbitrary nonbytes object rejected *without traversing it*; both hashes null.
- **BR09:** selected pronunciation path change alters canonical identity and receipt.
- **BR10:** accepted schema-valid fixture with missing lexicon or mapping ambiguity remains ingress-accepted; does not prematurely assert mapping output.
- **BR11/12:** SMC-3 `SymbolicPlan` equivalence and historical F01–F32 require **separate bridge**; explicitly `NOT_RUN/MORE_DATA` in this slice.
- **BR13:** accepted F09 deterministic equivalence across permitted unordered collections, including canonical rejected mapping snapshot; no malformed-Python-graph equivalence claim.
- **BR14:** raw vs canonical hash domains/versions distinguish and receipt evidence is stable for repeated identical bytes.

## Test-before-code sequence and decision
1. Commit this file alone.
2. Commit executable tests which import a missing `canonical_ingress` module and preserve RED CI.
3. Implement isolated module and tests GREEN, exact SHA Python 3.11, 3.12, 3.13 + mypy, existing root and SV1.
4. Independent GitHub `@codex review` on final implementation SHA (AI code audit only). Review the design PR separately.
5. Explicit `GO_LIMITED_INGRESS / REVISE / MORE_DATA / REJECT` decision limited to this ingress boundary; red historical Gate B and missing symbolic bridge remain in effect. No `main` merge, Core, Studio, speech science or physical sound claims.
