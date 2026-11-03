---
id: EL-H04
title: "Deformable oral–ear contact mechanics"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
depends_on: ["EL-H01", "R-NV0"]
reference_ids: ["REF-RNV", "REF-WOLFRAM-ACOUSTICS"]
---

# Deformable oral–ear contact mechanics

**Policy:** 未実装・未検証の研究候補。production API / GestureScore / CreatureSpec / Performance Contract / Studioの変更を許可しない。話者物理モデル研究を優先する。

## Scientific question / H_EL04

話者の唇・舌と聴き手の耳介/周辺皮膚が接触したとき、耳の材質や相対姿勢だけを変えても、接触patch・変形・唇開口・空気の閉塞/漏れ・局所振動源が因果的に変わるか。

## Candidate contact variables

接触面と法線、gap/penetration、接触patch、法線力/接線力、stick-slip、剛性/減衰、相対速度、変位、周囲空気の局所境界と隙間、接触開閉の時刻を記録。濡れは液膜厚・表面張力・粘着・流体体積・破断候補だが、constitutive lawをまだ採用しない（R-NV0参照）。

## Reduced fidelity ladder (not implementation approval)

- 0: collision/nonpenetrationと剛体接触。
- 1: compliance + damping（滑りなし）。
- 2: friction/stick-slip + contact transition。
- 3: deformable pinna/lip patch coupled to acoustic boundary。
- 4: wet-film closure / multiphase physics：下位の明確な失敗が観測された後だけ検討。

Rigid contactで音のタイミングを合わせても軟組織物理の検証成功とは言わない。

## Controls, nulls, gates

Nullは無接触、硬い形状での遮蔽、録音SEへの置換。Interventionsは同一speaker taskで相対位置/receiver stiffness/contact forceを個別に変更。Report: contact status, force, relative motion, deformation, local field and sound-pressure traces; numerical convergence, nonpenetration, work-energy sanity checks and error budgets.

## Competing explanations

wet-like transientを液膜作用と早合点しない：接触剥離、空気噴流、摩擦、耳道閉塞、機材由来の雑音も候補。生体への危険な実験を前提にせずファントム材/ダミー耳から開始する研究計画が必要。unsupportedなcontact geometryは黙って別現象へ置換しない。

## Claim limit

ここで述べた機構は、引用箇所で示した条件以外での定量精度、口と耳の直接接触音、ASMR知覚の成立を実証していない。既存の[不変条件](../../invariants.md)と[親研究](../nonvocal-oral-nearfield-candidate-v0.md)を優先する。
