---
id: EL-H01
title: "Listener morphology and physical preparation"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
depends_on: ["R-NV0"]
reference_ids: ["REF-HRTF-MESH", "REF-CC-HARDNESS"]
---

# Listener morphology and physical preparation

**Policy:** 未実装・未検証の研究候補。production API / GestureScore / CreatureSpec / Performance Contract / Studioの変更を許可しない。話者物理モデル研究を優先する。

## Scientific question / H_EL01

同じ音源・pose・環境を固定して、耳介・耳珠・耳甲介・耳道・周囲頭部の幾何や物性だけを介入した場合、受音音圧と局所組織振動を予測できるか。

## Evidence and its limits

頭部・耳介の幾何から音響散乱を計算するBEM先例 [REF-HRTF-MESH]、材の硬さの異なる耳介模型の振動/音圧測定 [REF-CC-HARDNESS] がある。耳への柔らかい口の接触モデルや人体の完全な材料定数までは支持しない。

## Candidate physical variables

- rest geometry: left/right pinna, concha, tragus, head, ear-canal centerline・断面・入口・終端。
- material: density, stiffness, viscoelastic loss, heterogeneity（未知は未知のまま）。
- spatial metadata: left/right, world/body coordinates, scale, measurement planes。
- preparation: backend固有のmesh/sectional geometry、solver、calibration、provenance。
- dynamic state: rest geometryとは別の組織変位・速度・接触力・音響負荷。

鼓膜側の終端は負荷インピーダンス候補であり、固定pressure-releaseを普遍モデルにしない。

## Nulls, intervention, observations

Null: 同じ点での自由音場、耳介なし、剛体耳介、形状固定HRTF。Intervention: 一度に形状/硬さ/左右差の一軸を変更。Observe: ear entrance/eardrum-side p(t)、組織速度、共鳴/位相/伝搬損失、数値収束。

## Falsification / boundary

独立実測への改善が測定誤差以下なら追加されたmaterial degrees of freedomは未支持。listener morphologyをCreatureSpecのroleとして再利用できるか独立ListenerSpecが必要かは保留し、型を固定しない。

## Claim limit

ここで述べた機構は、引用箇所で示した条件以外での定量精度、口と耳の直接接触音、ASMR知覚の成立を実証していない。既存の[不変条件](../../invariants.md)と[親研究](../nonvocal-oral-nearfield-candidate-v0.md)を優先する。
