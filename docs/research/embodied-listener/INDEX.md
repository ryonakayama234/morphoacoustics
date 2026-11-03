---
id: EL-INDEX
title: "Embodied Listener / Two-Body Interaction Research Index"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
---

# Embodied Listener Research — INDEX

**AIはこのINDEXから必要な文書へ進む。** ここは聴き手の身体性・二身体の相互作用を検討する「仮説の保管庫」であり、実装計画ではない。

**RESEARCH_CANDIDATE / PARKED / NO IMPLEMENTATION / NO PRODUCTION CHANGE**

## 正本と依存関係

1. 現行の[architecture](../../architecture.md)・[invariants](../../invariants.md)・[model assumptions](../../model-assumptions.md)が現行の契約。
2. [R-NV0 非発声音源・近接受音候補](../nonvocal-oral-nearfield-candidate-v0.md)と[Issue #53](https://github.com/ryonakayama234/morphoacoustics/issues/53)が親トラック。既存のsource taxonomy/wet-contact用語を重複させない。
3. [SFI-3 #82](https://github.com/ryonakayama234/morphoacoustics/issues/82)は別の声門—声道連成の研究計画。二体接触の完成を意味しない。
4. ここでのListenerSpecやInteractionScene等は仮の研究語彙であり、現行の実装クラスやAPIを表さない。

## AI検索ルーティング（read first）

| Query / keyword | First document | Related |
| --- | --- | --- |
| なぜ分割する / 非目標 / ownership / priority | [00-scope-and-boundaries.md](00-scope-and-boundaries.md) | architecture、R-NV0 |
| 耳介 / 耳道 / geometry / material / morphology | [10-listener-morphology.md](10-listener-morphology.md) | 30、40 |
| 近接 / 1cm / HRTF / scattering / distributed source | [20-near-field-propagation.md](20-near-field-propagation.md) | 10、REFERENCES |
| 聴覚 / 鼓膜 / cartilage / perceptual ASMR | [30-auditory-reception.md](30-auditory-reception.md) | 10、40 |
| 舌・唇と耳の接触 / 湿潤 / 変形 / 摩擦 | [40-contact-biomechanics.md](40-contact-biomechanics.md) | 50、R-NV0 |
| 二体連成 / emergent sound / 反作用 / energy | [50-two-body-coupling.md](50-two-body-coupling.md) | 40、20、SFI-3 |
| 接近 / listener pose / gestures / scene / timeline | [60-interaction-scene.md](60-interaction-scene.md) | 50、shared timeline |
| research gate / null model / falsification | [70-research-gates.md](70-research-gates.md) | 対象仮説 |
| 情報源 / 文献 / 数理検証の根拠 | [REFERENCES.md](REFERENCES.md) | 各文書 |

研究ID: **EL-H01** 形態、**EL-H02** 近接伝搬、**EL-H03** 受容、**EL-H04** 接触、**EL-H05** 二体連成、**EL-H06** シーン。IDは参照用で、採用・実装・検証済みを意味しない。

## AI reader / editor contract

- INDEXを読んでから対象文書と依存文書だけを読む。既存issue/コードの実態確認は別に行う。
- Established Evidence / Candidate Hypothesis / Proposed Interface / Numerically Checked Identity / Human Perception を明示的に区別する。
- 距離20cmでの測定から1cmや接触の精度を主張しない。形状・材料・音源・測定点・周波数・研究条件を記録する。
- 音源生成・伝搬・受音・接触フィードバック・最終観測を説明可能に分ける。ただし高忠実度では連成solverで解いてよい。
- source material, contact pressure, wetness, humidity, temperatureとaudioの観測を混同しない。
- 当ディレクトリからproduction APIを直接作成しない。着手前に[70-research-gates](70-research-gates.md)を読む。
- 既存研究#53/#30/#82との重複を確認し、必要になるまで個別の実装Issueを作らない。
- 仮説IDを安定させ、反証・修正時には旧仮説と理由を残す。

**最優先は話者身体の物理モデル。** このトラックは情報を保管するものであり、話者開発のブロッカーではない。独立した校正済み音源で受音側だけを研究する道は残す。

## Files

[00 Scope](00-scope-and-boundaries.md) · [10 Morphology](10-listener-morphology.md) · [20 Near field](20-near-field-propagation.md) · [30 Reception](30-auditory-reception.md) · [40 Contact](40-contact-biomechanics.md) · [50 Coupling](50-two-body-coupling.md) · [60 Scene](60-interaction-scene.md) · [70 Gates](70-research-gates.md) · [References](REFERENCES.md)
