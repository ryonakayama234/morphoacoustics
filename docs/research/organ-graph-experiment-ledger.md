# Organ Graph scientific ledger — status and update template

**Record date: 2026-10-14 JST.** This file is a searchable index, not a replacement for original evidence, post hoc corrections, frozen protocols, or actual GitHub Actions records. Experiment-local success must never be described as public API or biological validity.

## Current experimental gates

| Gate | Question / actual scope | Research decision / integration | Evidence entry |
| --- | --- | --- | --- |
| OG-0 / Experiment 030 | Do exactly two named rigid 1D tubes joined by an ideal p/U serial port obey transfer, reflection and conservation identities? | **Limited research SUPPORT**, merged via [#91](https://github.com/ryonakayama234/morphoacoustics/pull/91) and [#92](https://github.com/ryonakayama234/morphoacoustics/pull/92); not public API | [audit decision #93](https://github.com/ryonakayama234/morphoacoustics/issues/93#issuecomment-6159433812), [post-merge CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38500523397) |
| OG-1 / Experiment 038 | Does exactly one fixed ideal three-port junction in three separately identified rigid tubes satisfy full p/U, branching and energy tests? | **Limited research SUPPORT**, merged via [#95](https://github.com/ryonakayama234/morphoacoustics/pull/95) to main `0def163fadcf8fc59aece773faecd7ca852e1ea7`; not generic graph or nasal voice | [audit decision #94](https://github.com/ryonakayama234/morphoacoustics/issues/94#issuecomment-6160396315), [post-merge CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38507786003) |
| OG-2 / Experiment 039 | Can a typed two-organ serial graph blueprint be validated and bound to an immutable backend-specific prepared graph preserving physical IDs/provenance? | **Draft / NOT ADOPTED** [#97](https://github.com/ryonakayama234/morphoacoustics/pull/97); earlier fixture pass and code fixes but must re-integrate/validate against new main, audit against exact new head, decide separately | [tracking #96](https://github.com/ryonakayama234/morphoacoustics/issues/96), [open audit #98](https://github.com/ryonakayama234/morphoacoustics/issues/98), [remediation](https://github.com/ryonakayama234/morphoacoustics/issues/98#issuecomment-6150236719), [upstream release](https://github.com/ryonakayama234/morphoacoustics/issues/98#issuecomment-6160415926) |

The OG-0 and OG-1 verified phenomena are *ideal* zero-volume, rigid, fixed, linear 1D, lossless passive port laws. The experimental agreement with Wolfram and falsification controls is not a validation of 3D area-step evanescence, tissue mechanics, active phonation, real speech, arbitrary anatomy, or user-editable module plug-and-play.

## Immediate experiment gate — OG-2 completion plan

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
