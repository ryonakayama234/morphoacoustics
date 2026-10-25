# SMC-4 Gate B decision — REVISE / STOP (2026-10-25 JST)

## Formal bounded decision

**Disposition: `REVISE` / `SOFTWARE_CANDIDATE_NOT_ADOPTED` / `SCIENCE_NOT_ADOPTED` / `NO_MAIN_MERGE`.**

The owner delegated execution of SMC-4 Gate B following [design Gate A's owner-authorized `GO_DESIGN_ONLY`](https://github.com/ryonakayama234/morphoacoustics/issues/174), and approved GitHub `@codex review` as the only available external adversarial **AI software reviewer**. This is an explicit **stop**, not an implementation of the next phase and not a statement that the finite compiler has human phonetic validity.

Research [Issue #179](https://github.com/ryonakayama234/morphoacoustics/issues/179), stacked [Draft PR #180](https://github.com/ryonakayama234/morphoacoustics/pull/180), and its SMC-3 parent Draft PR #164 remain **unmerged into main**. SMC-4 Gate A original protocol plus Amendments 01–03 remain historically frozen. This decision uses the Gate B `REVISE` option without rewriting its preregistered pass/fail criteria.

## Scope achieved — limited synthetic software evidence

- Research-only independent `morphoacoustics_smc.smc4_types` and `smc4_lexicon` implement candidate finite `TaskLexicon` compilation from selected complete `PronunciationPath` to the **unchanged** SMC-3 many-to-many `SymbolicPlan`. This is NOT script-to-Japanese-reading, physical actuation, phonetic correctness, Studio, gesture physiology or WAV.
- Immutable research preregistration, test-only RED-before-code, then bounded implementation and synthetic F01–F32 tests, with versioned lexicon, required additive goal slots, exclusive candidates, Kleene contextual predicates, explicit Task sharing, rational timing and separate provenance receipt.
- The **last code+docs HEAD before the two final falsifiers**, `f05fda35640a47e868574d367f68cdd81a28da2e`, received **all three GitHub Actions workflow groups SUCCESS**: isolated package Python3.11/3.12/3.13 + mypy, existing root tests/typecheck, bounded SV1. This success is limited to tests *available at that commit*, not the complete Gate B claim.
- Ten exact-HEAD manual GitHub `@codex review` rounds identified **28 separate P2 software/design findings** (first 26 addressed and retested, latest two unresolved). Their exact review SHAs, original findings, test-first RED receipts and source repair SHAs are in [the review ledger](SMC4_GATE_B_CODEX_REVIEW.md). These are adversarial AI *code reviews*, not scientific or human peer review.

## The two unresolved counterexamples — why Gate B cannot adopt

Tenth Codex reviewed exact SHA `f05fda35640a47e868574d367f68cdd81a28da2e` and identified:

1. [P2 **input identity collision**](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369147645): invalid runtime context `{1: []}` and `{"1": []}` produce an identical rejected `input_fingerprint` because the request codec coerces mapping keys to strings. Distinct attempted inputs become indistinguishable audit evidence.
2. [P2 **order-dependent rejected cyclic graph fingerprint**](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369147647): two equivalent permutations of a malformed mutually cyclic `definitions=(a,b)` versus `(b,a)` produce different rejected receipts despite F09 order-invariance requirements. DFS active-path cycle tokens are not a canonical graph representation.

Both defects were independently encoded *without modifying compiler source* in `tests/test_smc4_gate_b_codex_p2_round10_stop.py`, test-only SHA **`0904acc071cf3a0583990e079f49a06ace6c6969`**. Its standalone package **RED** [workflow 40148530604](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40148530604), Python3.13 isolated job `121034971880`, confirms **two reproducible failing pytest cases**; root test/SV1 workflows remained successful at this SHA. These new failures are *intentionally retained on the Draft research branch* to prevent a false green/adoption. They do NOT mean Core physics, audio or Studio regressed.

## Underlying design problem

The current API accepts arbitrary Python runtime objects at a research dataclass boundary while simultaneously asking for a **complete and permutation-invariant canonical input identity even for malformed, cyclic, aliased arbitrary Python object graphs**. Ten review iterations repeatedly exposed inconsistencies in early shape validation and failed-request hashing. Another local two-line fix would not establish an exhaustive or bounded semantics for this unconstrained input class.

**Proposed next design task (not authorized/implemented by this STOP):** define a separate versioned `CanonicalRequestBoundary` contract. Choose a finite, typed, acyclic canonical serialization domain with explicit maximum depth/work and UTF-8/Unicode/source-span rules; construct an immutable canonical input snapshot **before** compiling. Decide formally what receipts mean for *out-of-domain* arbitrary Python object graphs (whether a structured `INVALID_INPUT` with an explicit **unfingerprintable input** marker, a trusted raw-byte submission hash, or a bounded canonical graph encoding). Restrict F09 ordering invariance to rigorously declared unordered collections *within the accepted input domain*. A separate Gate B-R **design amendment and test preregistration** is needed before implementing this contract; do not silently weaken the existing protocol or erase RED evidence. Require a finite fresh AI review on exact SHA before revisiting `GO_LIMITED_SYMBOLIC`.

## Ownership and evidence boundaries

No merge to `main`, no adoption of arbitrary Japanese phonetic Task mappings, no executed body/organ physics, no Audio/WAV output, no human peer review. SMC-3, Core, Studio, performance contracts and initial Gate A source remain unchanged by this decision. Any physical body `INFEASIBLE` outcome remains owned by a separate downstream Gate, never by this lexical compiler.

**Final gate:** `REVISE`, pending a consciously narrowed canonical-ingress/provenance design agreement. The primary new evidence is a pair of intentionally RED invariance fixtures, not a new speech capability.
