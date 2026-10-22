# CC-B1 Gate C — bounded CLI boundary index (pre-implementation freeze)

Status: **DRAFT / PREREGISTERED ENGINEERING DELTA / NOT ADOPTED / NO MAIN MERGE**.
Parent: Core #160; stacked on draft #163 → #159 → #145. The parent branch is not a released public API.

Read in order: [SYSTEM](SYSTEM.md) (causal authority), [DATA](DATA.md) (strict versioned IO), [EXPERIMENT](EXPERIMENT.md) (falsifiers and audit ledger).
Implementation target: `tools/cc_b1_candidate_cli.py`. Test target: `tests/test_cc_b1_candidate_cli.py`.
This task introduces an **opt-in documented CLI candidate** without changing frozen `src/morphoacoustics/`, `src/morphoacoustics_graph/`, existing contracts v0/v1, or old workflows.
Separate SMC package and ASMR workspaces are untouched. Studio #25/PR #26 is downstream, not implemented by this branch.

Evidence ownership: GitHub exact commit SHA, CI runs and artifacts, Wolfram analytical sanity, independent code/security review, creator blinded audibility are **distinct**.
No signoff or CI outcome is implied merely by writing this file.
