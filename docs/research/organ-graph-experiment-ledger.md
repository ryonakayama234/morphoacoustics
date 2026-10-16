# Organ Graph scientific ledger — status and update template

> **OG-5 Gate B3: MACHINE PASS at candidate `205484690250b366760c574f8621dc066710e5a0`, NOT ADOPTED (2026-10-16):** [B3 experiment/architecture/data/traceability](./og5-gate-b3-trial.md) | [Wolfram independent dual-path source](./og5-gate-b3-independent-oracle.wl) | [fail-closed Core scorer](../../checks/check_og5_gate_b3.py) | [full run 38911540920](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38911540920) | [Draft PR #112](https://github.com/ryonakayama234/morphoacoustics/pull/112). 144/144 complete 20-complex outputs matched global+recursive independent Wolfram, 8/8 wrong-law/output mutants killed, twin SHA-bound raw artifacts audited; OG-3/OG-4 (including frozen Exp028/029 and genuine 2-Take X2a), original Gate A and 3.11–3.13/mypy all passed at candidate HEAD. **This is a historical pinned machine receipt, not Gate C adoption; every later HEAD requires fresh exact-SHA checks.**


**Gate C outcome (2026-10-16):** OG-3 fixed2 Core backend **ADOPTED LIMITED**, [PR #104 merged](https://github.com/ryonakayama234/morphoacoustics/pull/104) to `main@8fb021ef2abc9eb92275a9e6cc6f92e8a6cb405f`; [exact-head audit decision](https://github.com/ryonakayama234/morphoacoustics/pull/104#issuecomment-6197561497), [post-merge OG-3 + X2a genuine physics](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38773196170), [post-merge Python+typecheck](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38773196256): 27/27 post-merge workflows green. Original Exp028/029 decisions and frozen Experiment039 oracle unchanged; 2 historical P1 Codex issues fixed and re-reviewed. [Full decision ledger](./og3-gate-c-limited-adoption.md). Table rows and entries below record earlier research stages and premerge candidate decisions and remain valid historical evidence, **not current status**.

**Record date: 2026-10-14 JST.** This file is a searchable index, not a replacement for original evidence, post hoc corrections, frozen protocols, or actual GitHub Actions records. Experiment-local success must never be described as public API or biological validity.

## Current experimental gates

| Gate | Question / actual scope | Research decision / integration | Evidence entry |
| --- | --- | --- | --- |
| OG-0 / Experiment 030 | Do exactly two named rigid 1D tubes joined by an ideal p/U serial port obey transfer, reflection and conservation identities? | **Limited research SUPPORT**, merged via [#91](https://github.com/ryonakayama234/morphoacoustics/pull/91) and [#92](https://github.com/ryonakayama234/morphoacoustics/pull/92); not public API | [audit decision #93](https://github.com/ryonakayama234/morphoacoustics/issues/93#issuecomment-6159433812), [post-merge CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38500523397) |
| OG-1 / Experiment 038 | Does exactly one fixed ideal three-port junction in three separately identified rigid tubes satisfy full p/U, branching and energy tests? | **Limited research SUPPORT**, merged via [#95](https://github.com/ryonakayama234/morphoacoustics/pull/95) to main `0def163fadcf8fc59aece773faecd7ca852e1ea7`; not generic graph or nasal voice | [audit decision #94](https://github.com/ryonakayama234/morphoacoustics/issues/94#issuecomment-6160396315), [post-merge CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38507786003) |
| OG-2 / Experiment 039 | Does a two-organ passive graph preserve typed ports/identity and the frozen complex acoustic transfer? | **ADOPTED LIMITED RESEARCH**, [#97 merged](https://github.com/ryonakayama234/morphoacoustics/pull/97) into `main@2f325956a98b527f295821522ef844540e734cd8`; public API **not** adopted | [formal #98 decision](https://github.com/ryonakayama234/morphoacoustics/issues/98#issuecomment-6182585021), [integrated science CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38667264999), [integrated standard CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38667265000), [real evidence ZIP](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38667264999/artifacts/11942775721) |

The OG-0 and OG-1 verified phenomena are *ideal* zero-volume, rigid, fixed, linear 1D, lossless passive port laws. The experimental agreement with Wolfram and falsification controls is not a validation of 3D area-step evanescence, tissue mechanics, active phonation, real speech, arbitrary anatomy, or user-editable module plug-and-play.

## 2026-10-15 exact-head WP-01 evidence / decisions

- **Integrated experiment HEAD** `5711a3addfbc43707f0f735b3bd15950c93a3ef4` (parents research `68b24375`, then-adopted main `0def163f`), accepted under independent Wolfram+machine+disclosed correlated AI critical reviews: [physics](https://github.com/ryonakayama234/morphoacoustics/issues/98#issuecomment-6182566797), [code](https://github.com/ryonakayama234/morphoacoustics/issues/98#issuecomment-6182571942), [separate decision](https://github.com/ryonakayama234/morphoacoustics/issues/98#issuecomment-6182585021).
- **Fixed controls measured**: maximum scaled Wolfram-complex transfer error `1.942890293094024e-15` (<=1e-10); equal-area error `2.220446049250313e-16` (<=1e-10); isolated matched interface power error `2.220446049250313e-16` (<=1e-12); false velocity junction `0.9019457527234934` and reverse order `1.3529186290852406` (both >1e-3).
- **Raw artifact:** [#11942775721](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38667264999/artifacts/11942775721), SHA-256 of `decision.json` `52bdbee59c353d33bb05adf87d9cfd477e0f20ebf5bdbf60a87fb765c9a722d8`, equals sidecar; clean integrated HEAD and CI run `38667264999`, 7 frequencies and 11 checked machine gates. Machine record remains historically provisional until issue decision.
- **Merged research**: [PR #97](https://github.com/ryonakayama234/morphoacoustics/pull/97) → main `2f325956a98b527f295821522ef844540e734cd8`; post-merge [science push CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38668133904), [general push CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38668133891) are independent status gates.
- **WP-03 in progress / not adopted**: [CC-A1 contract v1 Draft PR #101](https://github.com/ryonakayama234/morphoacoustics/pull/101), initial schema+fixtures and semantic helper; exact-version historical bodies, v0 compatibility; no confirmed Studio live two-body audio. Frozen limited-live code manifest kept intact after correcting CI-discovered source-inventory coupling.
- **Boundaries:** no general graph/3D/FSI/TTS/API/Studio availability. Earlier `AMENDMENT_001` remains disclosed post-implementation controlled regression, not blind preregistration.

## Historical experiment gate — OG-2 preregistered completion plan (completed 2026-10-15)

**H0:** preparation misbinds module or port identity, changes physical response relative to adopted reference or fails to reject incorrect topology/derived quantities.  
**H1:** for the fixed two-organ rigid 1D passive serial fixture, correct graph preparation preserves immutable module identities/revisions and produces the same full complex two-port response as the adopted reference; illegal graphs are refused.

**Frozen/recorded input fixtures (current Experiment 039, not newly invented here):** A/B 0.08/0.09m, A=3e-4 m² and B=3e-4 or 6e-4 m², rho=1.21 kg/m³, c=343m/s, frequencies 80/200/400/733/1200/2200/4000 Hz, `exp(+iωt)`, transfer state `[p,U]`. Track the corrected dimensionless transform `S T S^-1` with `S=diag(1,Z_ref)`; the original erroneous direction is disclosed in `AMENDMENT_001.md` and must not be relabeled prospective. Engineering thresholds live in the committed original/amended protocol, **do not retune here**.

**Evidence already recorded:** prior isolated [PR #97 head `68b24375`](https://github.com/ryonakayama234/morphoacoustics/commit/68b24375d374902f4793d32e35214d07bc720f4d) passed [science CI 38430414632](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38430414632) and [general CI 38430414649](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38430414649); independent Wolfram and bounded engineering fixtures were recorded with explicit amendment, mutation kills and evidence SHA. This is **not a current-main integrated check**. The repo has since merged OG-0 and OG-1; do not assert current integrated success without a new exact-head run.

**Required next actions:** compare or rebase PR #97 onto merged main, examine conflicts/new code interactions; rerun exact-head scientific + complete tests and experiment-specific mypy on Python 3.11/3.12/3.13; independently verify Wolfram controls, false laws, derived impedance negative case, evidence signature and fresh artifact hashes; perform new physics and code/API adversarial passes (disclosing AI correlation); record signed-by-evidence issue-local `SUPPORT_LIMITED_PASSIVE_2PORT_PREPARATION` / `INCONCLUSIVE` / `REJECT`. Only then decide research-only merge. **A public Core API and Studio feature require independent later design/adoption gates.**

## Research record schema / minimum checkable evidence

Store each experiment under a stable numbered directory, with frozen protocol, explicit amendments, runnable code/test(s), independent oracle, raw results, machine-readable decision and a readable `RESULTS.md`/index entry. Do not remove failed runs or overwrite historical evidence.

```json
{
  "record_schema": "science-gate-candidate/v0",
  "experiment_id": "039_og2",
  "hypothesis": "fixed two-node passive graph preparation retains identity and physics",
  "scientific_claim_scope": "ideal fixed rigid linear 1D two-port only",
  "protocol_ref": "experiments/039_og2_prepared_graph/PREREGISTRATION.md",
  "amendments": ["experiments/039_og2_prepared_graph/AMENDMENT_001.md"],
  "status": "INCONCLUSIVE",
  "head_sha": null,
  "base_sha": null,
  "input_fixture_digest": null,
  "preparation_digest": null,
  "oracle_source_digest": null,
  "thresholds_and_justification": null,
  "positive_controls": [],
  "negative_mutation_controls": [],
  "metrics_with_units": {},
  "raw_artifact_links": [],
  "ci_run_ids": [],
  "audits": {"physics": null, "code_api_evidence": null},
  "known_limitations": [],
  "decision_ref": null
}
```

This JSON is a **template with null placeholders**, not an actually executed or accepted Experiment 039 result. Keep hypotheses/test fixtures frozen in their original protocol; do not retroactively change results or imply the template is the actual machine evidence format.

## Architecture/data/evidence must move together

| Every work package / PR should update | Durable location |
| --- | --- |
| What changed in causal/physical architecture, supported backend and node/edge law | [living program](./organ-graph-program.md) + `docs/architecture.md` if production boundary changes |
| What changed in canonical/data schemas, versioning, units, validation and hashing | [candidate data map](./organ-graph-data-candidate.md) + authoritative contracts only after acceptance |
| What was proposed, falsified, measured, corrected and adopted | **this ledger** + original experiment directory / `experiments/README.md`, exact SHA CI/evidence |
| What Studio can legitimately edit/display | Studio [Character Creator #12](https://github.com/ryonakayama234/morphoacoustics-studio/issues/12) and version-pinned contract consumer, once public gate is accepted |

**Practical PR policy:** no changing a physical capability without updating all three views, declaring old/new limits, linking tests/oracle/CI and recording acceptance or rejection. For pure documentation plans, explicitly label the record PROPOSED and do not synthesize test results.

Companions: [program](./organ-graph-program.md) · [data candidate](./organ-graph-data-candidate.md).

## OG-3 public API Gate A planning record — 2026-10-15 (PROPOSED / NOT ADOPTED)

- Tracker [#100](https://github.com/ryonakayama234/morphoacoustics/issues/100); base `1fb6c9f691f94558c6d5ccaf4b018eb05389cafe`. This entry records **design and Wolfram analytic planning only**, not OG-3 production code, successful production tests, new prospective blind science, or adoption.
- [RFC/diagram](./og3-public-preparation-rfc.md), [candidate validation protocol](./og3-gate-a-protocol.md), [independent Wolfram source](./og3-wolfram-gate-a.wl). Original OG-2 oracle/AMENDMENT_001 unchanged. Reused seven-frequency physical fixtures are **controlled regressions**.
- Direct Wolfram calculation for B area 3e-4→6e-4 m², f=733 Hz gave dimensionless transfer `[[-1.4753529760, +0.5343984190i],[+1.2026670440i, -0.2421770511]]` and max intervention deviation `0.8221172833`; matched-interface r/t = -1/3, 2/3; R/T = 1/9, 8/9; power sum 1. Over the seven frequency fixture: false particle-velocity junction max deviation `0.9019457527`, reversed organ order max `1.3529186291`. These match the OG-2 limited regression expectations; **not** an execution of proposed OG-3 API.
- **Compatibility blocker / current disposition:** in-package additions violate frozen X2a and Experiment028/029 source identity. Use only sibling `src/morphoacoustics_graph/`, keep original tree/manifest/pins byte-identical, audit new source hashes/imports separately and require exact-head legacy plus X2a smoke. The earlier X2a-only pin extension failed (history below); never recapture legacy sources.
- Next evidence slots: Gate A reviewer dispositions and frozen contract; then Gate B implementation/head SHA, 7 complex frequency matrices, mutation rejects, identity/digest, raw artifacts, Python 3.11/3.12/3.13 CI and legacy X2a smoke; finally separate Gate C public decision. Current `GO`: **not evaluated**.

### OG-3 Gate A self-audit disposition / candidate protocol amendment (2026-10-15)

[PR #102 self-audit](https://github.com/ryonakayama234/morphoacoustics/pull/102#issuecomment-6188922718) is **author-context AI inspection, not independent approval**. Four implementation-contract questions identified: frozen X2a hash manifest, SI binary64 digest byte ABI and identifier normalization, terminal metadata vs unloaded transfer, frequency/output/diagnostic shape. Proposed solutions recorded together in [RFC §8](./og3-public-preparation-rfc.md), [proposed protocol amendment](./og3-gate-a-protocol.md) and living architecture/data diagrams. Wolfram gave conditional rigid circular duct area-equivalent B cutoff estimate ~7272.95 Hz (A=6e-4 m²) and algebraic det(T)=1, matched energy=1; these **do not certify full bandwidth/anatomical voice**. No new Core source, produced WAV, changed frozen research fixture, reviewer signoff or adopted public API. Gate A independent reviewer decision and Gate B evidence **PENDING**.

### Gate A additional automated review response (2026-10-15; NOT ADOPTED)

Codex on [PR #102](https://github.com/ryonakayama234/morphoacoustics/pull/102) raised two actionable issues: unbounded frequency capability and different signed-zero frequency hash identities. **Accepted as implementation requirements** in RFC §9 and the protocol: 1-D nonempty ≤4096 frequencies within 0..4000 Hz, >4000 `UNSUPPORTED`, malformed/negative `INVALID`, `-0.0` canonicalizes to `+0.0` before digest and evaluation. No new Core run or public adoption was performed by this doc amendment. Distinct Wolfram power-flux invariant check supports false-law rejection but is a supplementary Gate B test candidate, not a retroactively altered OG-2 frozen test. Independent human signoff still missing.

### Gate A design evidence disposition after Gate B trial (2026-10-15)

Draft [PR #104](https://github.com/ryonakayama234/morphoacoustics/pull/104) initially **failed** strict original Exp028/029/X2a source fingerprint protection at `e4baefc` despite explicitly pinning new modules in X2a; [failed Exp028](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478556), [failed X2a](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478509), [failed generic CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478593). Root: add-on files inside frozen `src/morphoacoustics` violate Experiment028 upstream full source fingerprint; **do not recapture frozen sources**. Updated physical topology implementation lives in sibling `src/morphoacoustics_graph`; old source tree and X2a pins unchanged. Corrected exact trial `ce6af25a630fb5cd19510948ce7f1393d9391780` passed [3-Python/typecheck](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38731395318) and [specialized frozen V3 + X2a genuine 2 Take + fixed Wolfram oracle](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38731394921), max transfer error 1.9151347e-15; dedicated artifacts uploaded. **Engineering machine PASS, not independent human audit or public adoption**. Corrected packaging/protocol still subject to critical review.


### PR #102 six-thread correction / analytic rerun (2026-10-15; NOT ADOPTED)

All six P2 design findings are accepted: mandatory 0..4000 Hz support, exact ±0 byte normalization, N-dependent output including non-seven grids, explicit N>4096 UNSUPPORTED/no observation, executable flux-law control with thresholds, and consistent sibling-only source/audit instructions throughout the RFC and plan. The protocol includes 1/3/7/4096/4097-point, endpoint/out-of-band, malformed and exact zero-byte acceptance cases. These are design corrections, not implementation-test results; PR #104 was not changed by this review.

The actual revised `og3-wolfram-gate-a.wl` was sent in full to Wolfram Language: symbolic tube and wrong-junction flux identities both true; seven-frequency correct dimensionless J_flux defect numerically zero at ~49 digits; wrong-junction defect 0.5 at every point; <=1e-12 correct/error tolerance and >1e-3 mutation rejection passed. Original r/t/R/T, matrix and reversal controls reproduced. New explicit flux thresholds are recorded after the historical Gate B trial, for future exact-head acceptance; they are not relabeled prospective evidence. Original Experiment039 source/oracle/tolerances remain untouched. Review is AI analysis in this task context, not human sign-off or public release.

Reproduction receipt: Wolfram `15.0.1 for Linux x86 (64-bit) (July 2, 2026)`. [Executed source](./og3-wolfram-gate-a.wl) SHA-256 `44817a3d366762bc5742cebfa31c04ae2d28d69e8347852ac803cd38bf7eec08`; [raw exported JSON](./og3-wolfram-gate-a-result.json) SHA-256 `f7e9e6a67d1b1182e8726a59a417b0be251e61db93a667c73dbf1dcfab7a90f1`. JSON parses strictly, contains seven rows, both symbolic identities true and all flux controls passing. Result is supplementary Gate A analysis, not a replacement Experiment039 oracle.


### Geometry-domain correction and Gate B handoff (2026-10-15)

[RFC §11](./og3-public-preparation-rfc.md) restricts every 0..4000 Hz support claim to the two frozen **ordered** fixtures (first 0.08 m/3e-4 m², second 0.09 m/{3e-4,6e-4} m²; rho 1.21, c 343). All other valid geometry/medium is UNSUPPORTED before preparation; malformed input is INVALID. No arbitrary-geometry 4 kHz claim. Caller IDs/revision labels and collection reorder remain independent of physical path. Backend candidate v2 must refuse old candidate snapshots and forged prepared values rather than bypass capability. New code stays in the sibling package; old Core tree/oracles/pins stay unchanged. The [reconciliation work order](./og3-gate-b-reconciliation.md) records #104 blockers and acceptance before its next exact-head run. Design-only merge does not release or scientifically adopt Gate B.


## Historical Gate B trial receipt retained during design reconciliation

### OG-3 Gate B separate Draft implementation record (2026-10-15, NOT_ADOPTED)

Separate implementation candidate on `feat/og3-gate-b-minimal-public-fixed2`, based on Gate A PR #102 design commit. New production submodules `src/morphoacoustics/{physical/organ_graph.py,preparation/graph.py}` with initial Git blob IDs `ea72548dd3fb771436dbfe0980ae5ab5ed3e9b17` / `405fb65ce65118b86384896e3406871da9408528`. These are **candidate implementation bytes, not a passed scientific result**. A new public test reads **existing** OG-2 Wolfram JSON and checks full complex 7-point response, identity and wrong-law flux. Legacy X2a manifest explicitly gains only these new hashes and keeps existing 23 pairs unchanged, but genuine X2a live smoke and independent review are **not complete**. Needed evidence: exact Draft HEAD + 3-Python green matrix + mypy, 2 fresh raw runs, 2 genuine X2a Takes, negative pin tests, numerical audit and independent API signoff; no merge/release before resolution. See [Gate B notes](./og3-gate-b-implementation.md).

### OG-3 Gate B first-CI failed evidence and corrective isolation (2026-10-15)

- Initial Draft HEAD `e4baefcad9cc7d5f597e0af6a4eac2ca2a536659`: [generic tests #38730478593](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478593) **FAILED**, with 7 mypy errors and frozen Experiment028 failures; [Exp028 #38730478556](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478556) / [Exp029 #38730478713](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478713) **FAILED** as `IMPLEMENTATION_MISMATCH`; [X2a physical smoke #38730478509](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38730478509) **FAILED** preflight; no genuine new Take produced. These failures were real and **not passing gates**.
- Root cause: original Experiment028 frozen source fingerprint includes `src/morphoacoustics/physical/organ_graph.py` when added; even explicitly expanding only X2a hash pins does **not** preserve upstream identity. The corrective approach physically isolates new Core-owned package at `src/morphoacoustics_graph/` and restores **all** files beneath `src/morphoacoustics/`, including `limited_live.py`, untouched. Mypy issues (wrong reused type for port loop and float narrowing) were corrected. Original scientific reference/oracle/pinned inputs unchanged.
- Retest exact new corrected commit, document all 3.11–3.13, V3b/V3c and X2a smoke outcomes; still `NOT_ADOPTED / NO GO` pending evidence/audit. This is an *amended implementation response to observed failures*, not an untouched preregistered success.

### OG-3 Gate B dedicated science workflow added (2026-10-15; result pending)

New `checks/check_og3_gate_b.py` and `.github/workflows/og3-gate-b.yml` introduce **separate new scientific evidence**, preserving original Experiment039 oracle. GitHub run must execute entire 7-frequency real/imag response, frozen seven-point `1e-10` threshold, fresh checkout SHA and output attestation, two independent observations, Exp028/029 full independent executions, X2a test and two live CLI Takes. **No passing result is claimed by this ledger entry before an actual workflow run**. CI logs/artifacts must be linked and reviewed at exact HEAD. This is still `NOT_ADOPTED`.


### Gate B reconciled implementation trial (2026-10-15; verification pending)

PR #104 incorporates merged Gate A main `6d38d8b`. Sibling backend v2 enforces RFC §11's two exact geometry/medium fixtures and reconstructs prepared binding before evaluation. Old v1 candidate snapshots are refused, never rebound. Observation validation preserves original scalar types, checks all malformed values before resource/frequency capability, returns UNSUPPORTED for valid 4097-point grids, preserves N matrices/order/duplicates and hashes exact positive-zero bytes. Supplementary per-point flux threshold <=1e-12, wrong defect 0.5 and separate reverse-order controls are explicit. Tests and evidence runner match the [reconciliation work order](./og3-gate-b-reconciliation.md); current exact-head CI/artifact receipt will be attached to [#104](https://github.com/ryonakayama234/morphoacoustics/pull/104). No legacy package, source pins or experiment/oracle changes; no release/adoption. Old trial receipts above are historical and do not attest this new implementation.

### Gate C new Codex P1 findings, amendments pending exact-HEAD rerun (2026-10-16)

At PR #104 HEAD `a97a9ac31322996647fa96e6c12d22e232a7c07c`, external Codex identified two **blocking P1** issues after the author-context physics/API reviews: recursion failure for a valid >1000-organ graph and stale OG-3 path-filtered CI on changes to `UniformTube`/research oracle/deps. Both findings were accepted, NOT suppressed. A correction introduces iterative DFS with a >1200-node valid unsupported test plus malformed graph INVALID precedence, and extends push/PR workflow dependency filters. Prior 535-test/green evidence for `a97a9ac` is historical, **NOT proof for the new corrected commit**. No scientific law change or legacy pin recapture. Independent re-review and exact corrected-HEAD CI are mandatory before a new adoption decision; see [PR #104](https://github.com/ryonakayama234/morphoacoustics/pull/104).

### OG-4 Gate A planning and inherited OG-1 Wolfram reproduction (2026-10-16; NOT_ADOPTED)

Main baseline `f82cff7e9e887b44ca3dfb26f9a41b36a5dbe3fa`. Parent [#106](https://github.com/ryonakayama234/morphoacoustics/issues/106); [Gate A RFC](./og4-three-port-public-preparation-rfc.md); [acceptance protocol](./og4-gate-a-protocol.md); [new symbolic Wolfram source](./og4-wolfram-gate-a.wl) + [result](./og4-wolfram-gate-a-result.json). **Already executed independently against exact frozen OG-1 archive**: original `experiments/038_og1_passive_branch/wolfram/oracle.wl` source blob `b066307176f72c3c519feb581356f2b1ed6e55bc`; frozen `oracle.json` blob `8f3ef44a079fe468348c7c4b1c66a42cca5c77d5`. 24 records × 6 ports × 2 complex p/U × 2 real components = **576** separately compared real state values, and 24 × 3 = **72** power values; **both max numerical recorded-value differences 0**. Weighted symbolic scattering metric residual `0_{3×3}`. New symbolic rational control yields correct `r=.5: (1/25,16/25,8/25)`, `r=1: (1/9,4/9,4/9)`, `r=2: (1/4,1/4,1/2)`; deliberately false equal-particle-velocity law weighted-energy defect `8/9` at r=2, zero at r=1 (non-discriminating control). This is a **reproduction and analytic design sanity check** of already visible values, not independent empirical validation, fresh OG-4 public API evidence, or new preregistration. Frozen original source/oracle not changed; new result is named proposed, not a replacement.

### OG-4 Gate A Amendment A1 — PR #107 review corrections (2026-10-16)

Codex review at `4161e6d` found four issues: unspecified source/load/schema; incomplete digest bytes; unbounded repeated frequencies; incorrect all-288 Wolfram attribution. [Amendment A1](./og4-branch3-api-v1.md) and the [corrected protocol](./og4-gate-a-protocol.md) address these. The immutable Python reference is pinned separately from the 24-record Wolfram JSON. Wolfram separately recomputed baseline C impedance 1372000, rematched half/double-area impedances 2744000/686000 and case counts 288/24. This is arithmetic/design verification, not executed branch3 evidence. Encoding fixtures include an explicitly synthetic observation, never a physical result.

State remains **DESIGN PROPOSED / NOT ADOPTED / no branch3 runtime**. Existing physical sources, frozen experiments and adopted OG-3 behavior remain unchanged.


## OG-4 Gate B implementation receipt — 2026-10-16 JST (provisional; evidence pending)

| Field | Record |
| --- | --- |
| Gate A authority | Merged design-only [PR #107](https://github.com/ryonakayama234/morphoacoustics/pull/107); approved design HEAD `37d15e2dac2fbfcc72d43efe681c3042a521ac4a`; main `572c115ea54084ea85acf13e2cf447e6a700d134` |
| Gate B branch | `implementation/og4-gate-b-branch3-20261016`; separate Draft implementation |
| Implemented source candidate | `src/morphoacoustics_graph/branch3.py`: typed preparation/snapshot/full-port solver and canonical identities |
| Test source | `tests/test_branch3_public.py`: new Core responses vs 288 Python and **separately** 24 archived Wolfram full-port records plus ABI/refusal controls |
| Evidence source | `checks/check_og4_gate_b.py`; strict HEAD/source hashes, 288+24 expected/actual endpoint payloads, 2 same-HEAD runs, stale/wrong HEAD negative controls, SHA sidecars |
| CI source | `.github/workflows/og4-gate-b.yml`; frozen OG3/X2a and dedicated complete case evidence |
| Wolfram analytic check | Separately executed rational ideal 3-port S weighted-energy and reciprocity residual matrices are exactly zero for arbitrary positive admittances; incoming-A splits for C area ratios 0.5/1/2 are (1/25,16/25,8/25), (1/9,4/9,4/9), (1/4,1/4,1/2). This is **local ideal law evidence**, not new Core finite-length acceptance. |
| Current status | **CANDIDATE / GATE B MACHINE EVIDENCE PENDING / NOT ADOPTED**. No experimental evidence should be declared passed until exact branch HEAD CI and raw artifacts are inspected. |
| Refusal/falsification | Wrong signed U / particle velocity, ill-conditioned singular test, malformed/unsupported input, forged snapshot, altered OG-3 source, stale artifact and wrong expected HEAD remain mandatory negative controls. |

Original Exp038/Wolfram reference contents and OG3/X2a sources were not modified. Existing inherited thresholds remain openly non-blind controlled regression, not prospective unseen physical evidence.

### OG-4 Gate B first full machine pass — exact code HEAD a5d0b4c242637bcd48430fc742cbd138e260e21a (2026-10-16 JST)

| Metric | Measured, actual fresh Core outputs |
| --- | --- |
| General CI | [Success: Python 3.11/3.12/3.13 and mypy](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38844651423) |
| OG-3 compatibility | [Success: adopted frozen Core, research and actual X2a](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38844651429) |
| Dedicated OG-4 Gate B | [Success: full-port science, ABI, two fresh SHA evidence, X2a](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38844651462) |
| Python 288 comparisons | All 288 new actual Core samples; maximum normalized complex endpoint error **9.425709178869422e-15** vs frozen independent `reference.py` |
| Wolfram 24 comparisons | All 24 new actual Core samples; maximum normalized complex endpoint error **2.738160251773752e-15** and three outlet/input power errors **1.8521128584277705e-15** vs frozen `oracle.json` |
| Mutation control deviations | Wrong particle velocity **0.4950242761670201**, wrong pressure sign **1.6642784627981486**, wrong signed volume flow **2.2947995211646948**; all falsifiers exceed 1e-3 |
| Scattering check | Ratios 0.5/1/2, weighted-power/reciprocity/complex mixed incidence all ≤ **8.9e-16**, plus independently executed symbolic Wolfram exact zero matrices |
| Determinism | Two fresh complete **1,206,981-byte** expected/actual ledgers were byte-identical; both SHA-256 **8c203c7feff21503c0a079a6427ac0d49115c297b411833e2ee197e8bca6371e**. Wrong expected HEAD and stale-output negative controls rejected. |
| Downloaded raw artifact | [GitHub artifact #12021939977](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38844651462/artifacts/12021939977); independently unpacked ZIP SHA-256 **3132ac1c66ea9b94dfc879a4593414813297ad000bca98535e1dae045286b9d7**. Valid ZIP, 14 files. |
| Live preservation | Both genuine 24,000-frame, 48 kHz X2a WAV Takes; stored hashes per manifest, both WAV/raw-pressure/physical traces byte identical; Exp028/029 original accepted decisions retained. |
| Scope | Eight accepted frequencies, C ratios 0.5/1/2, B matched and four C loads, source scales 1/0.5/-1; **no physiological human voice or WAV from OG-4 graph**. |
| Adoption | **MACHINE_NUMERICAL_PASS / CRITICAL_EXTERNAL_REVIEW_PENDING / NOT_ADOPTED**. Automated confirmation cannot replace Gate C. |

Critical external review of [PR #108](https://github.com/ryonakayama234/morphoacoustics/pull/108) was requested via Codex; the service reported an **account review-usage limit**, so there is no completed independent code audit. This is not a numerical or code defect determination. The test provenance is `a5d0b4c`; any subsequent documentation-only HEAD requires fresh CI before being called the final exact-head evidence. Do not backdate this machine pass to the original Gate A proposal, or claim 288 directly frozen Wolfram records.


### OG-4 PR #108 critical review corrections — 2026-10-16 JST

Starting review SHA `43fb39bebaec7a818f64d1b5afc8f3d0ad4a4583`. Reproduced error-priority and JSON Pointer failures before fixing them; found snapshot envelope invalidity hidden by unsupported-version classification. Added regression coverage and a typed forged-JSON recursion failure. The original singular condition-only test was insufficient; new tests exercise actual numerical refusal after an earlier valid sample and prove that no observation digest is emitted. Scattering now compares separately solved incident bases against unchanged Wolfram matrices, including unequal-area wrong-law power control. Evidence v2 persists full input/output identity payloads and verifies their case bindings. New Wolfram execution gives exact zero weighted-energy/reciprocity defects and singular rank 11/nullity 1; finite ratio-2 closed-C 733 Hz ports also checked. These are analytic ideal-model checks. [Detailed findings and decision boundary](./og4-gate-c-review.md). Corrected-HEAD CI/raw artifact receipt is required on PR #108; old green runs remain historical evidence. No merge or human-review claim.

Local verification note: the first full-suite run during editing returned 577 passed / 4 failed because frozen research runners correctly refused `DIRTY_TRACKED_CHECKOUT`; this is retained as a failed verification attempt. Re-run on the committed clean checkout and corrected-HEAD CI before deciding acceptance. No freeze guard was weakened.

Corrected-HEAD trial `ac8c416`: dedicated OG-4/OG-3 CI passed, but general CI failed with 580 passed / 2 failed because two newly added tests imported non-package `checks` by namespace. `python -m pytest` adds the repository root while the workflow's `pytest` entry point does not. Fixed by explicit `importlib` file loading, matching existing reference-test practice; no production/numerical change. Both original red workflow attempts remain visible. Re-attest all gates at the new HEAD.

## OG-5 Gate A preregistration candidate / Wolfram preliminary execution — 2026-10-16 JST

**Decision:** `PROPOSED / NOT RATIFIED / NOT ADOPTED`. Parent [#109](https://github.com/ryonakayama234/morphoacoustics/issues/109). Baseline main SHA `af10985f180f7b9a8f1dbca269c1133bc1a94c0a`, after adopted limited OG-4 [#108](https://github.com/ryonakayama234/morphoacoustics/pull/108). New Gate A Draft is source-only and cannot itself validate any new Core backend. Related synchronized architecture [program](./organ-graph-program.md), [data](./organ-graph-data-candidate.md), [plan](./organ-graph-execution-plan.md), [protocol](./og5-gate-a-protocol.md).

Wolfram Language evaluator executed fresh on 2026-10-16 JST. New [source](./og5-wolfram-gate-a.wl) and [machine records](./og5-wolfram-gate-a-result.json) have eight cases: f=733/997 Hz × C area=0.00015/0.0006 m² × C termination matched/rigid_closed, scale 1.0, 10 endpoints per case and p/U complex for each. Distinct algorithms: dimensionless global 20×20 LinearSolve and scalar impedance recursion + propagated full endpoints, with common physical transfer identity. **Exploratory nonblind results predate acceptance of the protocol**, not fresh blind confirmation or 144-case success.

| Preliminary metric | Actual evaluated maximum |
| --- | ---: |
| Max dimensionless all-endpoint global-vs-recursive complex difference | 9.930136612989092e-16 |
| Max dimensionless global equation residual | 2.2887833992611187e-16 |
| Max dimensionless J1/J2 signed flow residual | 1.1102230246251565e-16 |
| Max dimensionless J1/J2 pressure residual | 2.220446049250313e-16 |
| Max relative source vs 3 terminals mean-power defect | 8.094900779320129e-16 |
| Max dimensionless coefficient matrix condition2 | 24.344944491350603 |

Initial non-normalized mixed-Pa/m³/s full-system Solve emitted **ill-conditioning warning**; corrected via p/(Z_ref*U_ref), U/U_ref. Do not discard this observed failed numerical attempt; Gate B condition handling remains a genuine test obligation. [Golden proposal](./og5-blueprint-goldens.json) gives four candidate digest checks (baseline/area/revision/reordered); independent cross-language confirmation and exact snapshot/output golden vectors pending ratification. No Gate A external reviewer signature, no new Core outputs, no CI and no merge receipt can be inferred from these numbers.

**Future Gate B planned, NOT executed:** 144 scenarios, new backend *actual* 20 complex values per sample compared to independent reference, 8 archived Wolfram records separately, source/power/revisions/port map/invalid topologies and wrong-law kills, immutable SHA evidence with exact git HEAD. Review decision `SUPPORTED_LIMITED` / `INCONCLUSIVE` / `REJECT` cannot be declared from this author-authored design.



## OG-5 Gate A Amendment A1 — 2026-10-16 JST, candidate review pending

Addresses [PR #110 R1–R4](https://github.com/ryonakayama234/morphoacoustics/pull/110#pullrequestreview-5546195786). The [normative complete handoff](./og5-gate-a-amendment-a1.md) and [complete fixtures](./og5-contract-goldens.json) define Snapshot and N×10 Observation fields/identity bytes, stable refusal codes and escaped-pointer precedence, revisions scoped per organ, and lawful vs malformed topology. The split-only connected v1 language admits trees; cycles are INVALID and a complete 7-organ/3-junction tree is the UNSUPPORTED control.

State/digest flow is Blueprint -> complete structural validation -> fixed capability -> recomputed immutable Snapshot -> rank-safe coupled solve -> atomic full Observation. Snapshot digests bind normalized anatomy/source/load; Observation digests bind exact ordered numeric outputs/diagnostics. Neither includes UI layout, timestamps or Git/CI metadata. Full SVD retains zeros; condition2<=1e4 and scaled equation residual<=1e-12 precede success. All 144 positive samples must succeed and pass independent full-state comparators; no refusal reduces the denominator. Child-slot permutation has a distinct bounded mapping identity but identical ideal junction physics; actual output identity swaps and signed/particle-velocity row mutants test numerical mistakes.

Standalone Python regeneration and an independent JavaScript encoder confirm full golden bytes/hashes; they do not implement Core validation. [A1 Wolfram receipt](./og5-wolfram-gate-a-a1-result.json) contains 144-case supplementary design maxima, eight mutant margins and numerical rank/condition/nonfinite refusals. Original 8-case exploration is preserved. No new production module, Studio support, new Core run, scientific adoption or merge is implied. Exact amended HEAD review must precede a separate Gate B Draft.

A1 reproducibility detail: Wolfram 15.0.1 Linux x86-64 reproduced all 8 archived summary values and evaluated all 144 positive design samples. Max comparator=1.320372144714677e-14, scaled residual=3.376611507232129e-16, condition2=223.7427248146297, power defect with floor=4.220610523881094e-16. Separately assembled six-node pressure-admittance vs 20-state equations gave max 3.356621199780979e-14 over 144; against archived eight records max 1.047382306668854e-15. See the archived standalone `og5-review-nodal.py`, requiring NumPy, with no Core imports.

Retained failed A1 development attempt: the first supplementary mutant calculation incorrectly used AssociationMap on an Association, passing rules instead of row arrays and producing CoefficientArrays::poly / LinearSolve::matrix / AssociationMap::invrlf; JSON export failed. It was not a passed evidence run. Replaced it with value-preserving Map, reran the complete source, and only the corrected finite receipt is archived. The original mixed-unit ill-conditioning failure above remains historical too.

The 27 error receipts and 6 numeric seam fixtures are preregistered expectations. This docs-only work does not claim the nonexistent Core validator or late-sample atomicity implementation passed them. A future exact-HEAD Gate B must execute each such path. The signed-zero Blueprint example is canonicalization-only: zero imaginary source is structurally lawful but outside fixed tree5 source capability, so neither prepare nor restore may treat its illustrative hash-bound envelope as an accepted prepared object.


## OG-5 Gate A specification accepted — 2026-10-16 JST

Decision **ACCEPTED_FOR_GATE_B / SPECIFICATION_FROZEN**. [Acceptance and scope](./og5-gate-a-acceptance.md) supersedes the earlier pending status. Technical specification reviewed at `b7fb56c66236b0cbdb532fec8c75d46709c95bd0`; A1's schemas/bytes/refusal rules, fixed five-organ/two-junction fixture, 144/144 positive requirements and explicit numerical controls are frozen for a separate implementation trial. This accepts the design handoff only. Runtime tree5 support and scientific implementation adoption require Gate B execution and Gate C decision; #109 remains open. Original candidate receipts retain their historical status and hashes.

## OG-5 Gate B1 numerical trial checkpoint — 2026-10-16

**Decision: TRIAL_IMPLEMENTATION / MACHINE_GATE_PENDING / NOT_ADOPTED.** Canonical [Gate A acceptance](./og5-gate-a-acceptance.md), new [B1 trial report](./og5-gate-b1-trial.md). Draft physical kernel (20×20 globally coupled) uses unchanged public `UniformTube` by import but must pass exact-HEAD repo CI.

Prior to this Draft, an equivalent local isolated physical kernel with a temporary mathematically matching UniformTube surrogate produced 144/144 no-exception positive cases, including p(A.in) = 1.9145547310352653 + 0.23147567288386767i Pa at 733Hz C=.00015 matched; independent Wolfram scalar recursion in this review yielded 1.914554731035266 + 0.23147567288386767i Pa. Local `pytest -k 'not eight_immutable'` equivalent checked 4 passes and left the frozen-eight fixture file unread: **not a Core integrated or complete Gate B pass**. The GitHub trial test now reads actual frozen Wolfram 8 records in Core source tree and requires exact CI.

Unmet Gate B: 144 actual Core vs *independently assembled Wolfram full-port* records, public strict Blueprint/Snapshot/Observation and hash goldens, all 27 error fixtures, 6 numerics seams, 8 mutation controls, complete regression, exact SHA dual evidence, independent critical review. Do not promote this exploratory checkpoint to scientific approval.

**OG-5 B1 red CI evidence (retained), 2026-10-16:** Trial `82e1c69a1494279d2066901583e4151ce44579ae`, GitHub runs B1 38893915197, main tests 38893915215, OG4 38893915199, OG3 38893915193: numerical pytest tests completed successfully (B1 5 and general on 3.11–3.13), but mypy reported `tree5.py:132` numpy inferred complexfloating dtype vs explicit complex128 annotation; 3.12/3.13 B1 jobs cancelled before their own checks. This is a true red CI attempt. A typing-only cast repair at next HEAD requires complete re-attestation. No failure erased and no scientific Gate B pass asserted.

## Gate B2 contract checkpoint (2026-10-16; DRAFT)

OG-5 Gate B2 implementation candidate (2026-10-16 JST): Separate typed and domain-hashed Blueprint/Prepared/Observation API added to the B1 branch under Gate A frozen A1. Proposed assertions: 8 Blueprint/Snapshot variants, 6 canonical byte vectors, 27 error receipts, repeated frequency requests, immutable receiver and late-sample numeric refusal. Results remain **NOT VERIFIED on exact HEAD** until linked CI completes; no Core/Wolfram 144 independent full-port acceptance or Gate C. [Contract record](./og5-gate-b2-contract.md).

**OG-5 B2 red CI checkpoint (2026-10-16):** first B2 commit `fd52b4b` returned Python3.13 619 passed/7 failed and 11 mypy type errors. Six errors from test wrapper not extracting frozen `frequencies_hz`, one primary duplicate ID error shadowed by downstream connection error. Patch is typed validation/test correction, not acoustic equation edit; preserve failed run `38895168890`, OG4 `38895168822`, ensure exact-head CI rerun. [Detailed receipt](./og5-gate-b2-contract.md).

**B2 science ledger: 6 registered numerical-seam controls** added at actual matrix/solve boundary, expected `NUMERICALLY_UNRESOLVED` across exact status/code/frequency-pointer fixtures, with no observation/digest returned. Previous exception-only late-sample test is historical smoke test, not proof of a real singular matrix route. These controls are new assertions requiring exact-HEAD CI. No Wolfram/Core 144 full-port comparison or adoption claimed. [Contract log](./og5-gate-b2-contract.md).


## OG-5 Gate C remediation — 2026-10-16 JST

[Gate C remediation record](./og5-gate-c-remediation.md) restores A1 Unicode-key
refusal and compound-error priority, removes import-order dependence, and hardens
source-bound B3 raw evidence and CI triggers. Architecture remains validated
Blueprint → immutable PreparedTree5 → full-port Observation → separately audited
evidence. No physics/schema/oracle or Studio boundary changes. Old ca07c974
INCONCLUSIVE review remains historical; new exact-HEAD trials and separate
critical review are required before a LIMITED adoption decision.


## OG-5 Gate C R3/R4 capability-order remediation

The [R3/R4 repair record](./og5-gate-c-remediation.md#r3r4-follow-up-one-frozen-capability-selection-rule)
records the 3eeab25 INCONCLUSIVE findings and correction. Data/architecture flow:
complete structural validation -> normalized Blueprint -> applicable capability
candidates -> frozen A1 code priority and ASCII pointer selection -> immutable
Snapshot -> unchanged solver -> atomic full-port Observation -> independently
source-pinned raw audit. Unsupported organ mappings never enter fixed geometry
lookups. The 320 added contract cases first gave 54 FAIL / 266 PASS; old frozen
fixtures and physical/oracle values remain immutable. B3 now watches its golden
input, and raw oracle values are directly bound to the checkout's eight shards.
Execution requires all CI plus two fresh raw evidence runs on the corrected
committed HEAD and a separate Gate C adoption review. **Repair candidate only;
Draft/unmerged/not adopted.** See the PR receipt for actual final counts and SHAs.
