---
id: EL-H02
title: "Very-near-field and distributed acoustic propagation"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
depends_on: ["EL-H01"]
reference_ids: ["REF-NF-DATA", "REF-NF-FDTD", "REF-HRTF-MESH", "REF-WOLFRAM-ACOUSTICS"]
---

# Very-near-field and distributed acoustic propagation

**Policy:** 未実装・未検証の研究候補。production API / GestureScore / CreatureSpec / Performance Contract / Studioの変更を許可しない。話者物理モデル研究を優先する。

## Scientific question / H_EL02

固定したsource traceでも、距離・方向・音源面積・耳介との位置関係の違いで、固定遠方場HRTF + 1/r距離補正では説明できない音響差が生じるか。

## Evidence

人体のnear-field HRTF測定は0.2–1.0mの範囲で報告される [REF-NF-DATA]。rigid head replicaの近接HRTF magnitudeと波動数値モデルが特定条件で良く一致した例 [REF-NF-FDTD] もある。これらは1cmの柔らかい口耳接触を検証していない。

## Scale reasoning（Wolfram checked, not biological validation）

音速 c=343m/s として r=1cm に対する kr=2πfr/c は 1kHz: 0.183、5kHz: 0.916、10kHz: 1.832。有限音源・局所境界・散乱が重要な範囲では単純なpoint-source 1/rやfree-field gainから最終音圧を推定しない。

## Compared models

- A: point-source free-field delay/amplitude。
- B: far-field HRTF + distance gain。
- C: near-field distance-dependent HRTF（実際の測定距離内）。
- D: multiple distributed source patches + listener geometry。
- E: full 3D wave/FDTD/BEM oracle for a narrow fixture。

同じsource eventで位置のみ介入してA〜Eを比較し、必要な複雑性を測定誤差と数値誤差に照らして決める。

## Observation contract

source location/patch、距離（耳道入口までの距離か最短表面間gapか）、pose、ear left/right observation plane、p(t)、位相、周波数、HRTF測定位置とheadphone compensationを記録。blocked-canal entrance HRTFにさらにear-canal responseを二重に適用しない。時変接触境界を静的LTI convolutionで完全再現できるとは仮定しない。

## Falsification

C〜Eの複雑性に見合う改善がなければ単純モデルを優先。測定対象外の1cmで精度を主張しない。

## Claim limit

ここで述べた機構は、引用箇所で示した条件以外での定量精度、口と耳の直接接触音、ASMR知覚の成立を実証していない。既存の[不変条件](../../invariants.md)と[親研究](../nonvocal-oral-nearfield-candidate-v0.md)を優先する。
