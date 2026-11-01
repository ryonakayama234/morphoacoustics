# MORPHO / OD-1 — Organ Shape & Physical Assembly 設計決定稿 v1
2026-11-01 JST | 主担当：Core / Organ Modeling & Physical Assembly
Status: DESIGN_CANDIDATE / DOCS_ONLY / NO IMPLEMENTATION / NOT A3 PREREGISTRATION / NO STUDIO UI / NO MAIN MERGE.

## One selected capability
既存の単一区間editを再実装しない。固定済みの1D声道上で、一つの局所形状パラメータを検証可能な五区間rest-area分布に展開し、Coreが新しい計算可能BodyRevisionとして準備し、同一運動・音源から新規音響結果を得る能力を検証する。Organ Modeling and Assemblyの最初の限定形態であり、3D解剖器官、材料構成則、FSI、自然音声を意味しない。

## Four synchronized decision files
- DECISION.md: 先行成果の監査、技術代替案、選定、能力別採否。
- SYSTEM.md: 具体的な数理・音響・準備・実行、CoreとStudioの境界。
- DATA.md: 型付き参照、SI、物理的revision、エラー、所有権。
- EXPERIMENT.md: H0–H6、予測と反証、A0–E、数値/創作ゲート。

## Source inventory
Core/main 727b11ecf103f5c087cfcb820bdec11f883e7c03. Studio/main 6bc0d715e0a66b1e770091ffdcb44cdf1a4bfca9. Core #141, exploratory PR #143 (site0), spatial PR #144 (0/2/4), prereg PRs #149/#150 (site8), stacked Core Gate-C Draft #166 @ ef23738e1e6e3c631de5e36912bf5b601c7a17b3. Studio merged PR #27 (local site8 editable physical A/B) and frozen V2 layout; visual PR #33 unmerged. Core VF-1B2a #259 is separate moving-wall research, not a dependency or evidence of natural phonation.

## Governance
No API, UI, runtime, existing source, Performance Contract, SMC, ASMR, Take or panel registry edits in this decision. A3 exact-head protocol freeze is a separate later prerequisite for new confirmatory code. Every implementation PR must update SYSTEM/DATA/EXPERIMENT together and append genuine RESULTS. Keep failure records; owner agreement to architecture does not imply code approval or a biology claim.


## Gate B workstream
- [A0–A3 preimplementation frozen physics protocol](A0_A3_FREEZE_20261101.md) — immutable before any new OD-1 study code.
- [RESULTS.md](RESULTS.md) — exact-head machine evidence and limitations, not Studio Take or creator evaluation.
- Core stacked [Draft PR #268](https://github.com/ryonakayama234/morphoacoustics/pull/268) implements experiments/od1_local_shape/{oracle,run}.py, tests/test_od1_local_shape.py and .github/workflows/od1-local-shape.yml. Source/solver, performance v0/v1, Studio, SMC, ASMR, VF-1B2a and original CC-B1 site08 revision semantics remain unchanged.
