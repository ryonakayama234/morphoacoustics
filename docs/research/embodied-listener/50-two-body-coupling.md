---
id: EL-H05
title: "Two-body coupling and emergent acoustic events"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
depends_on: ["EL-H04", "EL-H02", "EL-H03", "SFI-3"]
reference_ids: ["REF-CC-PATH", "REF-CC-REVIEW", "REF-SFI3", "REF-WOLFRAM-ACOUSTICS"]
---

# Two-body coupling and emergent acoustic events

**Policy:** 未実装・未検証の研究候補。production API / GestureScore / CreatureSpec / Performance Contract / Studioの変更を許可しない。話者物理モデル研究を優先する。

## Central scientific question

**「二つの身体が相互作用することで、一つの身体だけでは生じなかった音が生まれる」**を、真の新規音源、元の声源の変更、伝達経路の生成、受音伝達変化、知覚変化に切り分けて実験可能にする。

## Classification — do not conflate

| ID | Event class | 物理的な候補 | 競合する説明 |
| --- | --- | --- | --- |
| EL-C-A | New acoustic source | 接触、擦過、剥離、振動が新たな局所音源となる | 原音の増幅 |
| EL-C-B | Source modification | 唇の変形・開口・音響負荷が発声/噴流源を変える | 受信HRTFだけが変わる |
| EL-C-C | New transmission pathway | 軟骨が振動→耳道内空気を励振 | 耳道入口からの普通の空気伝導 |
| EL-C-D | Receiver transfer modification | 耳介の変形/閉塞/インピーダンス変化 | 元のsource spectrum変化 |
| EL-C-E | Perceptual interpretation | 近接/接触感の主観的変化 | 実際の組織接触・熱・湿潤 |

Cにはトランスデューサ励振によるcartilage-airの先行知見 [REF-CC-PATH, REF-CC-REVIEW] があるが、柔軟な唇や舌との接触の音響効果を実証したものではない。Eは心理音響の評価であり機械的な新規音源の証拠ではない。

## Causal candidate

話者state S、listener state L、相対位置R、contact C、source field Aを追跡する。無接触なら一方向 source(S) → propagation(R,L) → reception(L)へ縮退してよい。接触ではlistenerからspeakerへの力と境界負荷、speakerからlistenerへの力と流体負荷が変化し、接触起源のsource、組織内経路、外耳道内fieldを連成させる余地を残す。意味上sourceとreceiverを区別しても、一方向の固定audio filterに拘束しない。

## Elementary passivity derivation (Wolfram verified, not a validated tissue model)

最も単純な1自由度の接触バネ/ダンパーを仮定し、二体速度 va,vb、相対変位 d と d'=va-vb、k>=0、b>=0 とする。FA=-k d-b(va-vb)、FB=-FA、Ec=(1/2)k d^2。このとき記号的に：

~~~wolfram
FullSimplify[
 (-k d - b (va-vb)) va +
 ( k d + b (va-vb)) vb +
 k d (va-vb),
 Assumptions -> {k>=0,b>=0,Element[{d,va,vb},Reals]}
]
(* -b (va-vb)^2 *)
~~~

ゆえに FA va + FB vb + dEc/dt = -b(va-vb)^2 <= 0。これは接触の力学的passivity sanity check。吸気/呼気外部駆動や声源のエネルギー供給、組織摩擦、音響放射などを含む現実の完全系の保証ではない。物理境界候補としてmechanical power F·v と acoustic power pQ（Q=体積速度）を識別して相互交換を計上する。接触開閉・摩擦・非線形組織は別モデルと検証が必要。

関連：[SFI-3 #82](https://github.com/ryonakayama234/morphoacoustics/issues/82)は声門—固定声道の受動連成研究計画であって、本トラックの二体solverがあることを示さない。

## H_EL05 and falsifiable interventions

同じspeaker motor task・同じ初期声源を固定し、no contact / touch / contact+sliding / release、receiver stiffness、局所閉塞、構造伝導ON/OFFを系統的に変える。source trace・contact power・伝達応答を別々にログし、EL-C-A～Dのどれで違いを説明できるか測る。

Null model = 元のsource+近接filterのみ。対立モデル = sourceだけ変化、receiverだけ変化、新規接触source、構造経路有り。nullで同等に予測可能なら新しい物理層の必要性は未支持。録音SEの追加で似た音が作れることは物理仮説の証拠ではない。

## Required evidence

force/velocity/displacement/contact patch、pressure/flow、局所source、ear-left/right observation point、energy bookkeeping、数値誤差、測定誤差を保存。心理的リアリズム・ASMR好感度は別の主張レベル。

## Claim limit

ここで述べた機構は、引用箇所で示した条件以外での定量精度、口と耳の直接接触音、ASMR知覚の成立を実証していない。既存の[不変条件](../../invariants.md)と[親研究](../nonvocal-oral-nearfield-candidate-v0.md)を優先する。
