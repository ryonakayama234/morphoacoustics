# SMC-7 L1-R C0 — bounded decision ledger (2026-10-29)

**Owner #245 | Research Draft PR #246 | Parent L1 issue #242 | Linguistic corpus #244 | Follow-on C1 #247**

## D01. Admit an actual reference G2P, not a contextual scientific result
**Decision: `GO_LIMITED_C0_REAL_B0_EXECUTED`** at the exact reviewed *code-bearing* SHA **`5087bd5775a148655188df9918d6faaff6a8ea4a`**. The bounded claim is: a research-only optional `pyopenjtalk==0.4.1` module truly executed a text-only Japanese G2P reading through a newly instantiated private, explicit OpenJTalk dictionary snapshot, with no user dictionary or cached global engine, and measured immutable directory-byte provenance.

Actual GitHub Actions job [123365200272](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40849518746/job/123365200272) succeeded: `人気のない場所` -> `ニンキノナイバショ` (actual **output**, not gold accuracy), Linux/Python 3.11.17, dictionary fingerprint SHA-256 `88167f04755fe6f0973f5be05bf839aad53d600e190d7068b29d7af15c594dbd`. It does **not** establish the correct reading for this utterance, context understanding, or human phonetics. Normal pyopenjtalk itself may use sentence context, so do **not** label B0 context-free.

This adapter produces a text-only `BaselineReading`, **not** a complete authenticated source-span `ReadingProposal`, a selected task, a MotorScore, a body command or sound.

## D02. Conditional software accept after actual adversarial red-green-red-green
Method freeze `b1c88e3` preceded test-only RED `838b01f`; independent Codex reported four P2 in first review, frozen amendment `7263f4c` -> adversarial test-only RED `08d0465` -> code `9b89815`; second review reported four further P2, frozen amendment `9cff1e5` -> test-only RED `1cefe74` and stronger FIFO test-only RED `c116b02` -> exact fixed code `5087bd5`.

Independent Codex **exact-code re-review** at `5087bd5775a148655188df9918d6faaff6a8ea4a` completed with `has_any_findings=false` and `has_unresolved_findings=false`. After evidence replies, all eight historical P2 review threads were resolved without deleting their failure records.

GitHub Actions exact code SHA reported **17/18 checks success** (isolated Python 3.11/3.12/3.13, full root 3.11/3.12/3.13, mypy, bounded SV1, and real B0). The **one remaining failed check is the intentionally isolated public corpus reconciliation gate**, not to be reported as all-green. This is a **limited software and actual optional B0 execution result**, not certification for arbitrary runtime sandboxes or production.

## D03. The corpus gate is NOT accepted
Exact public source is SB Intuitions Joyo Kanji Yomi Benchmark Git revision `2ae383bcdac88dacf89c9ab84f9990eec55fe5c9`, JSONL raw SHA-256 `32a843f662c55f1876baf64f8dc3475cc7b777c576a8fea6b43a2343ff46e897`. Our strict internal format predicate reports **13,095 rows**, **13,056 admitted**, **39 `RECONCILIATION_REQUIRED`** (8 source/key and 31 marked-pronunciation discrepancies), and among admitted rows **11,833** currently allowed by strict L1 Unicode repertoire. These are observed *strict internal eligibility* numbers, **not** proof of 39 errors made by the dataset's publisher.

**Decision: `MORE_DATA_C0_PUBLIC_CORPUS_RECONCILIATION`; dedicated audit job remains failed.** No silent drop, no automatic rule-loosening, no training or scoring on the public references until independent reconciliation, rights/NOTICE, annotation validity and leakage constraints documented in Issue #244.

## D04. H1–H4 remain deliberately UNTESTED
No 120-example independent pilot or 880 held-out independent whole-utterance acceptable readings and double-blind adjudicators exist. No full-utterance contextual candidate generator C, bounded common-pool B1/C-mask experiment, family bootstrap or H1/H2 target gains were measured. Do not claim `GO_LIMITED_L1_READING` or a model trained/validated for creator use. These remain **`MORE_DATA_L1_LINGUISTIC_CORPUS_AND_PROVIDER`** and successor [#247](https://github.com/ryonakayama234/morphoacoustics/issues/247).

## D05. Engineering and merge boundary
Draft #246 remains **unmerged**, stacked on unmerged #243 and #236. **No main merge, Core physical actuator changes, speech-to-motor semantic binding, Studio UI, waveform/audible quality or public MotorScore API.** Need independently approved integration and further physical/acoustic gates. Retain all prior P2/RED results and time-local historical decisions; later fixes do not retroactively validate faulty code SHAs.

## References
- [C0 original protocol](SMC7_L1R_C0_PROTOCOL.md), [Amendment 01](SMC7_L1R_C0_AMENDMENT_01.md), [Amendment 02](SMC7_L1R_C0_AMENDMENT_02.md), [Amendment 03](SMC7_L1R_C0_AMENDMENT_03.md)
- [Append-only historical results](SMC7_L1R_C0_RESULTS.md), [Draft PR #246](https://github.com/ryonakayama234/morphoacoustics/pull/246), [Gate C corpus #244](https://github.com/ryonakayama234/morphoacoustics/issues/244)
