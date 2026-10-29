# SMC-7 L1-R Gate B — immutable historical results and scientific limits

**2026-10-29 JST | owner #242 | Draft PR #243 | Software-only gate; L1 Japanese reading accuracy remains NOT TESTED.**

## A. Before source: prior frozen methodology
- Parent L0 repaired Draft #236 head `4e6b6530247700d70e3ad319e1d6bd0d20e8b962`; independently reviewed accepted L0 code `5b970ebb1ddfbe08313f72116c39a5875148a78f`.
- New research method and T01–T13 falsifiers were frozen in `SMC7_L1R_GATE_A_PROTOCOL.md` at standalone commit **`2dfb61dedf9bab1933ac488e3de5a65490d7ff8a`** before new L1 test/source files.
- Tests only `test_smc7_l1r_preregistered.py` at **`5a5b8fd7ffda571a0d4b8d28e79c18de708dd012`**. Actual GitHub isolated package Python 3.11 job [123260802541](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40817153089/job/123260802541) **RED** during collection: `ModuleNotFoundError: No module named 'morphoacoustics_smc.l1r_evidence'`. This is an observed missing-module RED, not fabricated by writing an expected outcome. Root tests on that SHA separately passed; do not call those failures.

## B. First code: CI success does not override independent software findings
- First code `l1r_evidence.py` at **`38a4c7e84714dadeb0b037127d68a71039d816bf`**. GitHub check-runs API returned **16/16 SUCCESS**, including isolated SMC 3.11/3.12/3.13, full root 3.11/3.12/3.13, typecheck and bounded SV1 checks. New source introduced no runtime package dependency; inherited SMC4/5/6, Core, Studio untouched.
- Independent [Codex first review](https://github.com/ryonakayama234/morphoacoustics/pull/243#issuecomment-6487871331) at **this exact code SHA** completed with two P2:
  1. [Review P2 source script](https://github.com/ryonakayama234/morphoacoustics/pull/243#discussion_r4408671713): `😀`, `甲A`, `ー`, `・` manually labeled with a full source span could incorrectly enter PROPOSED/SELECTED despite preregistered unsupported-source refusal. Inherited L0's full span validation is not a script repertoire oracle.
  2. [Review P2 profile comparison](https://github.com/ryonakayama234/morphoacoustics/pull/243#discussion_r4408671715): caller-defined `__ne__` on profile executed before exact type check.
- **Disposition at first SHA: REVISE_P2_REVIEW** despite 16/16 checks. Do not retroactively call its safety guarantees complete.

## C. Preregistered independent review repair
- Protocol amendment `SMC7_L1R_GATE_B_AMENDMENT_01.md` **`e4d76497ff53f2df0d4f4b2537bbf7e9b29051a2`**, committed **before** new tests or code.
- New tests only `test_smc7_l1r_review_round1.py` at **`c85057d20bf732236e604f4bd8758ce5f86cf9dd`**. Actual GitHub isolated package Python 3.12 [job 123262482953](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40817676580/job/123262482953) **RED**: R01–R04 false acceptance for all four unsupported source fixtures and R06 unchecked hostile profile comparison: **5 observed new failures**, with R05 valid restricted Japanese source positive control. Root/other test statuses must be evaluated independently.
- Source-only minimal repair **`f2ff1e09535fd2578dee4f5a12faca4b228fcdd1`**: O(1) bounded source length before scans; predeclared support for base kanji/hiragana/katakana and exact L0 silent delimiters; all unsupported sources rejected before manifest-proposal acceptance; exact profile type check now precedes comparisons. Did not mutate L0/SMC4/5/6, Core or Studio.
- At repaired **code-bearing SHA `f2ff1e09535fd2578dee4f5a12faca4b228fcdd1`**, GitHub check-runs API **16/16 SUCCESS**: isolated package 3.11/3.12/3.13, full root 3.11/3.12/3.13, strict package mypy/typecheck and bounded SV1, including test-first review regressions. This is exact-source evidence only.
- Independent Codex re-review on exact **`f2ff1e09535fd2578dee4f5a12faca4b228fcdd1`**: [PR review summary](https://github.com/ryonakayama234/morphoacoustics/pull/243#issuecomment-6487871331) reports `status=completed`, `has_any_findings=false`, `has_unresolved_findings=false`. Historical original P2 threads received evidence replies and were resolved **after** clean exact-SHA re-review; not deleted.
- Documentation-only as-built commit `fe11cbb7cd93937d36a794a078f02846221dc021` follows the reviewed code SHA; does not change production/test source.

## D. Technical outcome — narrow evidence and claim ceiling
`GO_LIMITED_L1R_EVIDENCE_SOFTWARE` at **frozen code-bearing SHA `f2ff1e09535fd2578dee4f5a12faca4b228fcdd1` only**: bounded content-identity manifest, context/version-sensitive complete candidate proposals, explicit selected-path research receipt and exact software fixture metrics. A valid L1 selection does **not** automatically invoke `compile_selected` or constitute an accepted Task motor plan, human articulation, or a phonetic reading.

**NOT TESTED, NOT ADOPTED:** H1 contextual heteronym effect, H2 recall@3 gain and burden on independent Japanese references, H3 real ambiguous-corpus false unique, H4 ordinary-text non-inferiority, independent human annotation, licensed corpus provenance, actual pyopenjtalk dictionary hashes, deployed context-aware G2P candidate generator, scientific confidence intervals, phonetically accepted TaskLexicon, Core model-physical mapping, sound/creator quality.

Current program-level Gate C decision: **`MORE_DATA_L1_LINGUISTIC_CORPUS_AND_PROVIDER`**; evidence accession owner [#244](https://github.com/ryonakayama234/morphoacoustics/issues/244). This is a software first slice, not L1 reading scientific GO. No merge to main, no public MotorScore/API, no Studio UI or Core engine change.

## E. Future evidence needed — not implicit tasks done
Before any held-out evaluation: independently licensed/digested 120 pilot and 880 held-out examples, two blinded annotations plus adjudication, sample/family/document leakage audit, provider/dictionary/model hash versions, normalization conventions, independent evaluation and registered bootstrap seed 20261029. A public external [MIT-licensed Joyo Kanji Yomi Benchmark](https://huggingface.co/datasets/sbintuitions/joyo-kanji-yomi-benchmark) is a candidate *secondary* dataset with kanji-level verified target readings, **not proof** that our preregistered 100 heteronym families/whole-utterance gold requirements are met. No data were fetched, merged, or measured in this run.

All timestamps and SHA-specific RED/failures above are historical evidence. Later fixes never turn previous faulty SHA into a passing one.
