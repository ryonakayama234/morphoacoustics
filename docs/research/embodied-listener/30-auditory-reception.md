---
id: EL-H03
title: "Auditory reception versus subjective perception"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
depends_on: ["EL-H01", "EL-H02"]
reference_ids: ["REF-CC-REVIEW", "REF-CC-PATH", "REF-CC-HARDNESS"]
---

# Auditory reception versus subjective perception

**Policy:** 未実装・未検証の研究候補。production API / GestureScore / CreatureSpec / Performance Contract / Studioの変更を許可しない。話者物理モデル研究を優先する。

## Scientific question / H_EL03

外耳道入口の音圧が同じでも、接触による耳介軟骨の振動と耳道内の音響負荷が異なると、鼓膜側応答が異なる条件が存在するか。主観的近接感/接触感は物理的受音と別にどう評価すべきか。

## Established evidence and scope

耳介軟骨を専用トランスデューサで励振する軟骨伝導研究はcartilage-air経路等の可能性を示す [REF-CC-REVIEW, REF-CC-PATH]。耳素材の硬さの異なるモデルでも振動/音響応答が測られている [REF-CC-HARDNESS]。口・舌で接触したときの強度を予言する根拠ではない。

## Candidate layers

(1) 入射音場と散乱、(2) 耳道入口、(3) 外耳道の波動・損失・終端、(4) cartilage/skinの振動と空気への放射、(5) 鼓膜/中耳の段階的な近似、(6) 聴覚神経以降の知覚評価。6を完全な脳モデルと見なさない。

## Intervention and nulls

- 同じ空気音圧＋組織振動OFF対ONという計算上のablation。
- 耳道開放/部分閉塞、終端負荷、硬さの変更。
- 同じwaveform提示でも補償方式を記録し、耳道伝達の二重算入を避ける。
- 音響objectiveと盲検human ratingsは別の実験段階。

## Measurables and falsification

耳道入口/鼓膜側の測定面と単位、振動速度、接触力、吸収/放射エネルギー、主観尺度を別列で保持。構造経路追加が物理観測を改善しない場合、当該条件で不要と判定。知覚差から組織力学を勝手に確定しない。音声再生は皮膚への実接触を作らない。

## Claim limit

ここで述べた機構は、引用箇所で示した条件以外での定量精度、口と耳の直接接触音、ASMR知覚の成立を実証していない。既存の[不変条件](../../invariants.md)と[親研究](../nonvocal-oral-nearfield-candidate-v0.md)を優先する。
