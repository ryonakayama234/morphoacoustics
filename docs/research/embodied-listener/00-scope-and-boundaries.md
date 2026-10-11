---
id: EL-SCOPE
title: "Scope and boundaries"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
depends_on: ["R-NV0"]
reference_ids: ["REF-ARCH", "REF-RNV"]
---

# Scope and boundaries

**Policy:** 未実装・未検証の研究候補。production API / GestureScore / CreatureSpec / Performance Contract / Studioの変更を許可しない。話者物理モデル研究を優先する。

## Scientific question

聴き手の身体を、話者の音を収録する固定マイクでなく、形態・組織・受音境界・運動を持った物理的存在として追加した場合、どの因果的な機能が必要になるか。

## 現行モデルとの関係（established project contract）

- morphology → task-level motor program → realized physical state → acoustic field → observation。
- GestureScoreは波形・スペクトル・「ASMR音」を直接命令しない。
- solverのUNSUPPORTED、身体のINFEASIBLE、無効な入力INVALIDを混同しない。
- receiver/environmentはmotor representationに入れない。Studioはscientific ownerではない。
- 現行のCreatureSpec、PreparedMorphology、Performance Contractは変更しない。

## 新たな仮説

H0: 従来のsource→near-field transfer→receiver観測の一方向モデルで十分。H1: 耳介が変形し話者へ反作用する場合には両身体を結ぶ状態が必要。H1が常に有効と先取りせず、どの実験条件で必要かを明らかにする。

## Research vocabulary, not schema

ListenerSpec（耳介/外耳道形態の意味情報）、ListenerPreparedState（solver固有の数値rest形状）、InteractionScene（双方のposeと時間）、ContactState（力と変形）、AcousticReception（測定面付き音響出力）。この名前でproduction型やenumを今固定しない。

## Explicit non-goals

物理接触をステレオSEで表すこと、濡れ音をテクスチャとして直接音声出力へ注入すること、完全な聴覚神経モデル、湿潤CFD/全身FEM、触覚再生、アプリ機能の今すぐの追加はしない。

## Observable boundary

耳道入口の空気音圧、鼓膜側音圧、軟骨変位、接触圧、湿度、温度、知覚ラベルを別フィールド/別計測として扱う。音だけで物理的触覚が伝わるとは言わない。

## Claim limit

ここで述べた機構は、引用箇所で示した条件以外での定量精度、口と耳の直接接触音、ASMR知覚の成立を実証していない。既存の[不変条件](../../invariants.md)と[親研究](../nonvocal-oral-nearfield-candidate-v0.md)を優先する。
