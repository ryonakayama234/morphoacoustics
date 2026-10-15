# Organ Graph scientific ledger — status and update template

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
- **Open blocker:** adding a public Core `.py` module violates the audited X2a complete-source inventory. Require explicit hash-pinned inventory design and independent compatibility audit plus current-head X2a CLI smoke **before** Gate B can be accepted; do not silently disable manifest or rehash legacy accepted files.
- Next evidence slots: Gate A reviewer dispositions and frozen contract; then Gate B implementation/head SHA, 7 complex frequency matrices, mutation rejects, identity/digest, raw artifacts, Python 3.11/3.12/3.13 CI and legacy X2a smoke; finally separate Gate C public decision. Current `GO`: **not evaluated**.
