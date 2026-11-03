---
id: EL-H06
title: "Interaction scene and shared time"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
depends_on: ["EL-H02", "EL-H04", "EL-H05"]
reference_ids: ["REF-ARCH", "REF-RNV"]
---

# Interaction scene and shared time

**Policy:** 未実装・未検証の研究候補。production API / GestureScore / CreatureSpec / Performance Contract / Studioの変更を許可しない。話者物理モデル研究を優先する。

## Scientific question / H_EL06

声や息のtask、話者の接近/姿勢、listenerの受容姿勢、接触・離隔・頭部運動を一つのtimelineで記述し、音源の波形を指示として直書きしない汎用sceneが必要か。

## Research-only responsibility diagram

~~~text
InteractionScene
  Speaker: CreatureSpec + prepared body + task / realized state
  Listener: morphology + material + prepared rest state + pose
  Relations: world/body/surface coordinates, relative transforms, time
  Interaction: contact state, air gap, airflow, acoustic boundary
  Outputs: named ear-left/right pressure points, contact traces,
           nonacoustic traces, separate human perceptual evaluation
~~~

これはpublic schema案ではない。ListenerSpecが独立であるべきかCreatureSpecの汎用roleで足りるかも未決定。

## Candidate scenario fixtures

NF-0: 無接触、固定源からreceiver distanceのみ介入。
NF-1: 無接触で話者のposition/orientationを連続変化。
C-0: 静的接触、剛性/forceと組織・音響境界を見る。
C-1: 接触/剥離、過渡sourceが生成されるか観測。
C-2: 同じphonation中に接触をON/OFFし、声源変化と受音変化を分離。

## Coordination / representation boundary

「耳元へ近づき、ささやき、触れる」という創作的directiveは目標姿勢/constraint/taskの候補で、結果音声の直接命令ではない。同じtaskが異なる身体でINFEASIBLEになる可能性を許す。身体の頭部運動を話者の声道Gesturesと同一視しない。

世界座標、各body local frame、観測面、最短surface gapと点間距離の区別、global clock、acoustic travel delay、接触時刻、backend fidelity/provenanceを記録。時変境界は固定LTI-HRTFの範囲外となりうる。

## Competing nulls / dependencies

距離とHRTFのキーフレームだけで充分な部分はそれをbaselineにする。既存[shared timeline](../shared-timeline-candidate-v1.md)、[Body Binding v0](../../body-binding-v0.md)、[Performance Contract](../../performance-contract-v0.md)を調査するが、ここから変更しない。

## Claim limit

ここで述べた機構は、引用箇所で示した条件以外での定量精度、口と耳の直接接触音、ASMR知覚の成立を実証していない。既存の[不変条件](../../invariants.md)と[親研究](../nonvocal-oral-nearfield-candidate-v0.md)を優先する。
