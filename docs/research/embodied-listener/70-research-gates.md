---
id: EL-GATES
title: "Research gates and preregistration"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
---

# Research gates — 着手条件と証拠の限界

**これは将来の研究backlogであって実装許可ではない。** 当面は話者の身体・声源・声道・source–filter couplingが優先。聴き手のモデルは事前に保存するだけ。

## Dependency route

~~~text
existing speaker physical state / source interfaces ───┐
                                                        ├→ EL-H05 coupling → EL-H06 scene
independent calibrated sources → EL-H01/H02/H03 ──┐     │
                                                 └→ EL-H04 contact
                                                        ↓
                                             separate perception studies
~~~

EL-H01/H02/H03の一部は話者の完成を待たず校正済み試験音源で独立検証可能。EL-H05で話者への反作用を研究するには、必要なspeaker mechanical/acoustic portを明示する。依存先が未成立のときは先に実装しない。

## Gate matrix

| Gate | Intervention | Null / comparator | Observable |
| --- | --- | --- | --- |
| G1 Listener shape | source・pose固定、耳のgeometry/material変更 | no pinna / rigid pinna | pressure, vibration, spectrum |
| G2 Near-field | source固定、距離/方向を変更 | 1/r + far HRTF | binaural phase/magnitude/delay |
| G3 Ear reception | air field固定、組織伝導経路切替 | air-only | ear canal pressure, vibration |
| G4 Contact | pose/force/stiffnessを変更 | rigid/no contact | contact force, gap, energy |
| G5 Source attribution | touch/slip/release, paths ablated | source unchanged, filter only | trace + acoustic output |
| G6 Scene | 同taskを異なる身体へ投影 | pre-rendered scripted effect | feasible/unsupported + trace |

## Experiment preregistration checklist

1. 仮説ID、操作する単一の因子、固定条件、独立したnull/comparison。
2. source、形状、材質、測定点、座標系、時刻、SI単位、校正、出典/利用条件。
3. 事前に凍結したnumeric/perceptual gateと評価閾値、対照条件、ブラインド判定手順。
4. passivity/energy residual、収束性、解析解・Wolframなどのoracle（適切な場合）、測定不確かさ。
5. 失敗状態の意味：INFEASIBLE = body、UNSUPPORTED = solver、INVALID = request/state。
6. 結果後のCLAIM LIMIT（成立した条件と成立しない一般化）と証拠リンク。

本ディレクトリは**研究構想**であってpreregistered experimentではない。実験fixture/閾値を定める前から「ゲート合格」と扱わない。

## Promotion gate

- 複数の形態・条件でnullより再現可能に優れ、過剰な自由度によるfitでない。
- 物性値の根拠・外挿範囲・solver fidelityを明示。
- 音源変更と受音変更と知覚変更を分離して再現。
- endpoint (ear entrance, blocked canal, eardrum)を混同しない。
- 安全性・被験者同意を含む方法が設計されている。
- 別レビューでversioned production APIを提案する。研究文書から自動昇格しない。

## Parking-lot questions

ListenerSpecは独立型かCreatureSpecのroleか？ 軟骨伝導を必要とする周波数帯は？ 接触による新規sourceと声源の変調をどう同定するか？ 液膜のclosureはいつ必要か？ 知覚の近接・接触感をどうブラインド測定するか？ これらは研究の着手時に個別Issueへ切り分ける。
