# Foundation Chat Program Charter — 計測科学から器官グラフ型の物理発声エンジンへ

**版:** 2026-10-26 / v1 proposal for durable work contract  
**担当:** このチャットにおける Core の測定・設計・実験・独立監査・GitHub管理  
**親Issue:** [Core Foundation #199](https://github.com/ryonakayama234/morphoacoustics/issues/199)  
**性質:** 開発運用方針および達成基準。**新しい採用済み物理理論・Production API・UI改修・商品品質認定ではない。**  
**既に合意された制約:** Core 測定科学・ロジック／アルゴリズムの技術的判断を委任。創作的な意味・基盤の保証範囲・永久的な公開モデル形式などは事前提案。承認済みの Studio 三モードUIは凍結し、必要になったら必ず作業を停止して具体的拡張案を提示する。

## 1. 最終的に作りたいもの（North Star）

器官を**ノード**、物理的な接続を**エッジ**で表現し、材質・形態・器官の選択、ポート、接続則、器官状態の時間発展、身体ごとの実現可能な運動、MotorSkill / MotorPersona から、身体に因果的に由来する声を創作できる物理エンジン。

単一の固定声道を少数の音色スライダーで変形させる音声合成器ではない。多様な実在生物・架空生物を最終的な拡張目標とする。ただし **未知の器官構成の声が真実として検証できるという意味ではない**。未対応・外挿・同定不能・失敗は明示する。

概念的因果鎖（現在の実装が全区間を満たすという意味ではない）：

```text
Character identity
  ├─ OrganGraph Blueprint: model choice, anatomy, material, interfaces
  ├─ MotorSkill: reusable task and coordination goals
  ├─ MotorPersona: persistent habitual control strategy (research hypothesis)
  └─ Direction: this performance's transient intent
          ↓ body capability/preparation
  supported or INVALID / UNSUPPORTED / INFEASIBLE
          ↓ constrained motor actuation and coupled physical state
  tissue movement ↔ airflow ↔ acoustic load ↔ resonating cavities
          ↓ radiation + scene propagation
  named receiver pressure / physical audio and immutable Take
          ↓ independent scientific & creator-specific assessment
```

**不変条件:** 音源や声を、物理が作ったかのように後付け波形操作で捏造しない。波形・スペクトログラムは観測値であり、発声を駆動する身体内部状態ではない。能力のない身体にニューラルが自然な発話を代行してはならない。

## 2. このチャットの範囲と完成の定義を分ける

**当面の主戦場（今すぐ取り組むもの）:** `morphoacoustics` Core の測定科学、受動音響・放射・能動発声連成の最小参照エンジン、器官の物理ポートと最小交換可能性を裏付ける実験。科学レベルで検証された事実から、初めて限定的な基盤モデル契約を提案する。

**このプログラムの基盤達成（Foundation Acceptance）:** 第3節の S0–S4 の各関連ゲートで、少なくとも一つの参照身体と再現可能な能動発声経路が独立参照・エネルギー・因果性・受音点の観測まで追跡でき、**少なくとも二つの真正に異なる物理器官モデルを共通の検証済みポートで交換**できることを示す。複数の身体に対する意味ある物理介入の影響と、明示的な能力拒否を記録する。これは **商品品質の GO ではない**。

**長期的な製品達成（Creator/Product Acceptance）:** 創作者が選べる器官モデル・材質・幾何・接続・MotorPersona の組合せによって、同じ演技と異なる身体の声が因果的に変化する。複数のキャラクターの音声が識別可能で、対象用途の品質について**創作者自身が実際の Take を聴いて GO と判断**し、制作フローで利用できること。これは基盤の科学PASSと独立であり、達成までは「未達成」と記録する。

「このチャット」は、ここに記した段階を順に検証する **一連の会話とGitHub作業の運用単位**であり、すべての生物・音声品質を特定の期限や一度の回答で保証するプロジェクトではない。各ターンで実施した操作と確認できた状態のみを報告する。

## 3. 開発ステージ：入口、成果物、出口

| ステージ | テーマと狙い | 次へ進むための証拠 | 非達成 / 保留 |
| --- | --- | --- | --- |
| **S0 測定の信頼性** | 物理計器・入力・出力のSI、複素伝達、時間窓、失敗証拠、実行コミットと元データの同定 | 独立した解析基準、両境界・M0/M1の再実行、負例・収束・物理ポート・失敗時証拠保持・レビュー、記録の永続性 | green CIだけの「真実」認定、口端圧力をマイク音圧と呼ぶ |
| **S1 受動声道と放射** | 境界モデルを物理法則として検証する | 円形バッフル付きピストンなど**幾何を宣言した**SA-2A独立参照と、B0の複素インピーダンス・位相・パワー・低ka領域を比較。時間領域へ入れる場合は因果・安定・受動性・収束・声道負荷変化を再検証 | 「ピストン参照が正しい」→「人間の口を再現できる」と飛躍する |
| **S2 最小能動発声** | 実際に供給される空気力学的仕事から自励振動し、音響負荷と双方向に相互作用する最小モデル | 固定された生理/幾何の範囲で、駆動を変えた時の振動開始／消失、運動・圧力・流量・能動仕事・受動損失、負荷介入と時間分解能収束を独立参照で検証 | 事前生成した100Hz音源を流して「声帯の自励発声」とする |
| **S3 器官グラフ基盤** | 器官ノード・ポート・エッジ法則・物理状態を混同せず接続し、モデル交換の根拠を得る | 単位・符号・共役パワー、接続則、相互作用、状態連続、能力判定、身体revisionを確認。**最低2種のモデル**と**意味ある2身体条件**、合法/不合法接続を反証する。既存OG3/OG4を尊重 | UIノードがあるだけで連成したと称する、汎用ABIを早期凍結する |
| **S4 放射から聴取まで** | 口端ポートと受音点を分離した受音音圧と再現可能な発声Takeを検証 | 固定した音源/身体/演技/出口/観測点の下で実音響の再現性・音声としての必要な特性・身体介入を評価。独立する人間聴取ゲートは創作者が GO/NO-GO | 理論的な伝達関数だけで商品品質を認定する |
| **S5 運動習慣と多様性** | 研究仮説のMotorSkill/MotorPersonaが本当に声の個性を担うか | 身体×習慣の対照実験、同一身体での反復可能な運動差、音響的影響と知覚上の識別を**別々に検証**。習慣と演技Directionを混同しない | 人格ラベルや任意のF0/フィルタ値をMotorPersonaと呼ぶ |
| **S6 創作拡張（別途合意）** | 検証済み器官・材質・接続のカタログとStudio編集/試聴の統合 | 使用目的と物理能力を明示し、旧UI維持/拡張案を提案して承認後にだけ着手。必要ならニューラルclosureを独立アブレーション | 未承認UI変更、未検証の生物能力、専用TTSによる物理の迂回 |

順序は**証拠依存**であり、S2のポート候補の設計をS3の正式ABIと勘違いしない。S0の測定整備は以後すべての段階で維持。S5/S6への研究着手は、合意済みの本線を逸脱して優先度を奪わない。

## 4. 物理・科学・創作のゲートを混ぜない

- **G0 Evidence / Measurement:** 計測量、SI、刺激、初期/境界条件、原データ・ソース・コード・clock SHA、時間窓、測定位置、再現性、**失敗証拠の保存**。足りなければ `NOT_MEASURABLE` または `EVIDENCE_INCOMPLETE` とし、科学PASSにしない。
- **G1 Numerical / Mathematical:** 独立した数式・別実装・解析参照への複素量の一致、収束、エネルギー・質量・仕事、安定性、悪いケースを拒否。共通の仮定を使った実装間一致は **`NUMERICALLY_CONSISTENT_WITH_DECLARED_MODEL`** の範囲だけ。
- **G2 Physical Model:** 適切な幾何・振動・放射・材質・周波数領域に対する**独立した物理参照または計測**と不確かさ。独立参照がない主張は `INDETERMINATE`、数値整合性で代用しない。
- **G3 Bioacoustic / Capability:** 明示された身体・音源・運動の発声が実現し、受音点の音と動力学が再現できること。特定の生物/課題についてのみ判断し、万能自然声スコアを作らない。
- **G4 Creator / Product:** G0–G3で候補と認定されたTakeを、制作側が同条件A/Bで聴いて品質・個性・使い勝手を判断する。**ユーザーの耳でGO/NO-GO**。音声の自然さと声の個性を別評価する。

研究・実装の状態は `RESEARCH_ONLY` → `ADOPTED_LIMITED_PHYSICAL` → `CREATOR_CANDIDATE` → `PRODUCT_APPROVED`。適切な検証なしに段階を飛ばさない。失敗種別は `INVALID` / `UNSUPPORTED` / `INFEASIBLE` / `NUMERICALLY_UNRESOLVED` / 科学的 `FAIL` / 品質 `NO_GO` を区別する。

**ゲートの閾値はモデル・物理問題ごとに事前登録する。** このチャーターは科学測定を行う前に普遍的な誤差%・音圧/音色の数値を捏造しない。

## 5. 研究サイクルと作業単位

```text
現象・解決すべき問題を特定
 → 代替物理仮説と独立参照を比較
 → Gate A 事前登録（測定量、合否、反例、限界）
 → SYSTEM / DATA / EXPERIMENT 設計を固定
 → 実験ブランチに最小試験実装
 → 単位/ポート・対照群・負例・独立参照・収束・CI
 → 結果と失敗証拠を不変のSHA/Artifact付きで保存
 → @codex 等による別視点コード/計測監査
 → 範囲限定のADOPT / REVISE / REJECT / MORE_DATA / HOLD
 → 採用なら次の依存課題へ、否なら原因分離して別方式へ
 → 音声候補になって初めて創作者の試聴と品質ゲート
```

1実験＝1つの主要物理仮説と明確な証拠。アルゴリズムAが失敗したら閾値を後付けで下げず、失敗記録を保持してAを改良またはBを試す。

すべての実装課題に **SYSTEM**（因果・計算構造と接続図）、**DATA**（単位、型、revision、物理ポート、所有者）、**EXPERIMENT**（事前条件、手法、実際の値、負例・失敗・不確かさ・CI）の対応を求める。プログラム全体の追跡票では現状・次の唯一の主要ゲート・ブロッカーを更新する。

GitHubでは親Issue #199をプログラム索引、各科学Issueを課題、各Draft PRを検証の作業単位とする。未審査研究ブランチや延期中の音声品質PRは無言でmainに取り込まない。CoreとStudio・SMC・ASMRの境界を保つ。

## 6. 器官グラフのデータと物理計算の境界（候補であってAPIではない）

```text
CharacterSpec / OrganGraph Blueprint  = 何の器官・形状・材質・関係があるか
PreparedPhysicalGraph                 = 特定backendで実際に計算できる固定化された身体
MotorSkill / MotorPersona / Direction  = 何をし、どの習慣で、今回どう演じるか
PhysicalSession + state(t)             = 連続時間にわたって発展する運動・流れ・圧力等
PhysicalObservation                   = どのセンサー/受音点で何を測ったか
ValidationReceipt                     = 独立参照、誤差、モデル限界、環境とSHA
Take                                  = 一意の身体・演技・場・物理実装に由来する音
```

ポートは法則と仕事の向きを持つ。例えば音響は圧力 `p` と体積流量 `U`、機械は力 `F` と速度 `v` の共役量。エッジの見た目やInspectorの値ではなく、明示した法則・連成・単位・符号・時刻と物理状態によって計算が成立する。エンジンはモデルの種類を増やす**拡張点**を持つが、現時点でありとあらゆる器官/生物/材料のソルバを持つ必要はない。

型付きモデルの汎用JSON形式やABIを**この文書では採用しない**。最低2つの物理モデル交換と既存Core契約の相互運用で反証した後にバージョン付候補を提示する。

## 7. 意思決定権限と「停止して提案する」トリガー

| 決定の種類 | 運用 |
| --- | --- |
| 独立参照の選定、物理数式/アルゴリズム、局所のコード実装、テスト拡充、CIや証拠保存、失敗分析・研究候補比較 | **技術側の裁量で継続。逐次承認不要。** ただし仮説・ゲートは事前登録し、結果を報告する。 |
| 研究専用API・一時的な試験境界・研究用Draft PR | 技術側の裁量。**main昇格や一般公開契約の自動許可ではない**。 |
| Engineが保証する物理能力・適用生物の範囲、将来の器官モデル選択の意味、汎用の正式Graph/Port ABI、創作操作の根本的意味、MotorPersonaの製品定義 | **停止し、利点・不利益・代案・物理根拠・移行負担を短く提示して明示合意を得る。** |
| StudioのCharacter/Motion/Scene UI、canvas・Inspector・Take dock・新パネル・既存Draft #33の採用 | **完全凍結**。必要になる段階で**作業を停止→変更の意味・既存UIを活かす案を提示→承認後のみ実装**。 |
| 音声の商品品質、キャラクターらしさ、実際の試聴GO、制作フロー受け入れ | **創作者のみが判定**。科学的に検査できる候補Takeを提示する前に聴感だけのデバッグ負担をかけない。 |
| 高リスクな既存production変更、研究を超えた大規模/不可逆な採用、前段ゲート不合格のままの昇格 | 科学監査と影響評価を行い、合意を要する意味変更なら停止・提案。 |
| Neural closure/代理モデル/質感補完 | 物理を消す代用は禁止。学習モデルを使う場合も同一身体介入・能力拒否・因果状態・除去実験に合格する必要。ユーザーの品質評価は別。 |

ユーザーは技術者の代わりに実装細部をGO/NO-GO判定しない。一方で創作の意味が変わる重要設計を既成事実にはしない。

## 8. このチャットでの報告書式

各まとまった開発ターンで、原則として次を簡潔に報告する。

```text
目標：創作・物理上の意味（何の能力を得るためか）
手段：比較した主要モデル、測定量・独立参照と適用範囲
証拠：実行済みGate、数値結果・失敗、正確なGitHub Issue/PR/CI/Artifact/commit
判定：研究PASS / FAIL / INDETERMINATE、品質GO/NO-GOは別欄
次：残っている最大の技術的ボトルネック、採用の前提、合意が必要か
```

研究が複数分岐したときは優先度を整理して、全てを同時に本線マージしない。必要なら科学監査担当を独立に置く（@codexなど）。更新できていないPRのレビューやCIは「成功」と言わない。**CI成功＝数値ソフト検証、第三者レビュー完了＝科学物理の真実、ではない。**

## 現在の実行進捗（随時更新）

本チャーターの原則・達成条件と、時々刻々変わるCI・観測値・レビュー状況は分けて管理する。実行証拠と未解決点の最新台帳は **[PROGRESS_LEDGER.md](PROGRESS_LEDGER.md)** を参照する。新しい結果で科学的な見解が変わるときは失敗記録を削除せず、実験の差分・物理適用範囲・次の反証対象を台帳に追記する。

## 9. 基準日での現状・次の順序（2026-10-26）

- Core main は固定ベース `e05e3274ad69bfb9202816049f6661a18ba39ec0`。既存全体アーキテクチャは `docs/architecture.md`・`docs/invariants.md`・OG3/OG4研究を参照。
- [VM-1A Draft #198](https://github.com/ryonakayama234/morphoacoustics/pull/198): **口端**の静的インパルス伝達は科学的な診断ができた。声の品質は未認定。
- [VM-1B Draft #201](https://github.com/ryonakayama234/morphoacoustics/pull/201): B0の共有仮定の下で、独立数式と時間領域の**数値整合**を測定。**履歴（修正済み）**：浅いGit checkoutでのparent記録、エネルギー異常時の失敗レポート、先行テスト失敗後の測定についてP2指摘があった。**現行判定**：これらを含む5件の証拠・CI指摘を修正し、厳密に `269082d51e24190209e832991ca3c9056883428a` に対するCI成功とCodex再レビューで新規重大指摘なし（詳細は [PROGRESS_LEDGER.md](PROGRESS_LEDGER.md)）。**ただし研究Draftは未マージ**。この結果は数値整合であり、実際の生物の音響放射・声品質の物理検証ではない。
- [SA-2A Draft #172](https://github.com/ryonakayama234/morphoacoustics/pull/172): 厳密に定義した**バッフル付き円形ピストン**の解析参照は研究CIで検証済み。これは実際の人間・動物の口の測定ではない。
- [SA-2B Issue #173](https://github.com/ryonakayama234/morphoacoustics/issues/173): この参照とB0の差、時間領域で因果・受動な放射負荷、必要な場合の改良モデル。**二重研究を避け既存SA-2A参照を再利用**。
- [Evidence durability #197](https://github.com/ryonakayama234/morphoacoustics/issues/197): Artifact保存期間を越えて証拠を再検証できる構成は未完。並行して設計する。
- [VM-1C Draft #204](https://github.com/ryonakayama234/morphoacoustics/pull/204): `7113758a7bea2806c378da6f76aa9f278e09371d` で理想バッフル付き円形ピストンとB0の複素比較を実施し、CI成功とCodex再レビューで新規指摘なし。凍結M0/M1で600/100Hzの口端圧力選択性は双方で大きく、**B0近似誤差のみが原因という仮説は支持されない**。実口腔・受音点の物理的妥当性は未確定、研究Draftは未マージ。
- 次のゲート順（現在）：**入口流量固定の仮定・声道共鳴・壁損失・有限源インピーダンスの分離 → 必要な因果受動放射負荷 → 能動発声器官+声道の双方向連成 → 2種器官交換と身体介入 → 放射受音点と初めての声品質候補**。各段階の合否・適用範囲を別々に判定する。

Studioは [Workspace v2 Draft #33](https://github.com/ryonakayama234/morphoacoustics-studio/pull/33) の受け入れ済みビジュアル・三モード構成を保護し、現在は一切実装しない。MotorPersonaは [現行の仮説文書](https://github.com/ryonakayama234/morphoacoustics/blob/main/docs/research/motor-skill-persona-hypotheses-v0.md) のH1–H4という**未検証**地位を維持する。

## 10. プログラム終了条件と継続条件

**「基盤エンジンの科学的達成」**を宣言できるのは、S0–S4で定義した再現可能な証拠が揃い、何を解けないかも明示され、少なくとも一つの能動発声から受音点までが物理的に因果接続され、2つ以上の器官モデルの本物の交換が反証可能に実証された場合だけ。適用範囲が限定的でもよく、全生物・最高品質・汎用FSIを要求しない。

**「創作者向け声の製品達成」**は別の条件であり、創作者による実際の音声GOおよび制作可能性を得た時のみ言える。NO-GOの場合でも科学的に成立した基盤は維持し、発声物理・制御・聴感上のボトルネックを再計測して改善する。

達成までの見通しが変わる実験不成立や実装制約は明確に報告する。テクニカル詳細は委任された裁量で進めるが、基盤が保証する能力・創作操作・UIの意味を変更するときは本チャーターの停止・提案ルールを優先する。

---

**Sources of existing commitments:** [Core architecture](../../architecture.md), [Core invariants](../../invariants.md), [Foundation #199](https://github.com/ryonakayama234/morphoacoustics/issues/199), [VM-1 #196](https://github.com/ryonakayama234/morphoacoustics/issues/196), [VM-1B #201](https://github.com/ryonakayama234/morphoacoustics/pull/201), [SA-2A #172](https://github.com/ryonakayama234/morphoacoustics/pull/172), [SA-2B #173](https://github.com/ryonakayama234/morphoacoustics/issues/173), [MotorSkill/MotorPersona research](../motor-skill-persona-hypotheses-v0.md), [Studio Draft #33](https://github.com/ryonakayama234/morphoacoustics-studio/pull/33). The present document **organizes the agreed development process**; it does not turn research hypotheses into observed facts.
