# BODYMAP B2 — 実験実施 run manifest（BODYMAP-B2-RUNMANIFEST-20261113-01）

Owner 実験実施 GO（2026-11-13）に対応する実施 manifest。監督者（Muse）が作成し、
GO 記録とともに Core PR #294／Studio Issue #61 に要約を残す。

## 固定する実施条件

- **事前登録**: `BODYMAP-B2-PREREG/1`（登録版 commit `2f7d9546cc888ca43e54a20cf04d3708c95c416f`、
  内容 SHA-256 `9a022469264b4789c2d677d163470c4f7f393451635b264920463e6d70d3e41e`、FZ 14件＋MQ1–4裁定）
- **実施 pin（exact clean head）**: Core main `0bb60cc227d231ec1cb67b701a849172ed92164b`
  （PR #294 の merge commit。候補 head `0fda8f6e1a29c0695b8d4d477c09d72c9888f122`、
  oracle commit `71c7c89f7f86712f12aad31dfa5ee210830e536d` を含む）
- **依存 lock**: `requirements/bodymap-b2-physical-py311.lock.txt`
  SHA-256 `c0bd046498882beb61408440d9eadd1b9708ad8a49ad0035e0bdbaa5d3a6afd7`
  （Python 3.11.18／NumPy 2.4.6／SciPy 1.17.1／mpmath 1.4.1／pytest 9.2.0、145 hashes）
- **実行環境の記録**: executor は run receipt に OS／arch／Python patch／各ライブラリ版を必ず記録する。
  lock と異なる環境では実施しない（STOP）。
- **source**: Exp013 `lf_fixed` の consumed f64 buffer（48 kHz／24,000 samples／seed 0、全条件で同一 buffer）。
  buffer の SHA は run receipt に記録する。source の資格表示は登録どおり
  （ACTUAL_RUN_ATTESTED は同一 run の chain 検証が成立した場合のみ、`full_verified_source_state` は UNKNOWN のまま）
- **幾何**: M0_REST は preparation digest `sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de`、
  直径（mm）`(12,12,26,16,12,14,20,26,30,34,38,34,34,30,28,32)`、16×0.010 m。
  U6_REF は半径 0.006 m、U19_REF は半径 0.019 m、いずれも全長 0.160 m。
  入力台帳で digest／全セルの照合が不一致なら実施前に STOP。
- **周波数格子**: 100,102,…,800 Hz の 351 点、全ケース共通。複素 HU／Zin／Hp の Re/Im を保存する。

## 実施ケース（正確にこれだけ）

- **主ケース 12**: {M0_REST, U6_REF, U19_REF} × λ {0, 1e-6, 0.5, 1} を各1回
- **repeated null 3**: 各幾何の λ=0 を独立プロセスで各1回再計算
- **合計 15 evaluations**。これ以外の科学評価（追加の λ・幾何・掃引）は実施しない
- **negative**: FZ-N1 の 9 系統（NEG-LAMBDA／ACTIVE-ZY／SWAP-COEFF／SWAP-LOAD／SWAP-GEOM-PORT／
  RAW-FORGE／LOSS-IGNORED／OLD-ATTENUATION／SHA-SOURCE）を各最大2回まで。科学ケースには数えない。
  入力拒否・内部物理拒否・来歴拒否を別記録にし、全件の stdout／typed result／期待と実際を保存する
- **既知データの開示**: 工学受入で実施した 8 ケース（U6 全λ、U19 λ0/λ1、M0 λ0/λ1）は
  KNOWN_ENGINEERING_DATA であり、本実施はそれらの条件については初見ではない。
  工学データを本実施のデータに混ぜない（別 run・別成果物として提出する）

## 判定（登録 FZ-T1 のまま、変更なし）

- 二軸判定: `IMPLEMENTATION_CONFORMANCE` × `EFFECT`
- 複素 oracle 照合 `|ΔX| ≤ 1e-10 + 1e-8|Xref|`（無次元化量）、raw 波形相対 L2 `≤1e-8`、
  λ=0 復帰 `≤1e-12 + 1e-10|Xref|`、repeated null raw L2 `≤1e-12`、
  近傍 null（λ=1e-6）は `≤1e-4`、受動性・パワー収支は FZ-T1 表のとおり
- 効果床: M0 λ=1 対 0 で `max|Hp1−Hp0|/max(Hp*,|Hp0|)>1e-6` かつ raw L2 `>1e-6`
  かつ ある格子点で `D_int/P*>1e-10` → `EFFECT_DETECTED_IN_BAND`
- G0 feature method は合否に使わない（DEFINED_NOT_VALIDATED のまま）
- 式・閾値・ケースの変更が必要になったら、その場で変えず STOP し、
  新しい事前登録改訂の手続きに戻る。許容差の緩和は本登録では行わない

## 実施経路についての前提（監督者が main の実物で確認済み）

- merge 済み CLI は工学ゲート専用で **study mode を持たない**
  （fixture manifest は `study_evaluations_authorized=0` の8ケースに固定され、
  `verify-engineering` も CLI からは未統合として停止する設計）。
  したがって本実施は CLI の改変では行わない。
- executor（Research Lead）は、pin の候補モジュールと凍結条件をそのまま使い、
  **study 実行パッケージ**（study manifest＋study runner）を新規に用意して実施する。
  runner のファイル SHA は、科学評価を1件も実行する前に本 manifest への追補として固定・記録する。
  runner はまず工学8ケースで受入数値（監督者 acceptance-report）を再現してから本実施に入る。
- pin の候補／oracle の科学コード自体の変更が必要になった時点で STOP する。
  その場合は実施ではなく、実装改訂＋事前登録改訂の手続きに戻る。

## 役割・成果物・上限

- **executor = Research Lead（ChatGPT）**: 候補側で 15 ケース＋negative を実施し、
  全ケース（失敗・中断を含む）の複素配列・raw・内部状態・パワー量・pack/0・run receipt を提出する
- **監督者 = Muse**: 提出後に独立 oracle で全15ケースを照合し（bulk 格子＋認証スポット）、
  パワー収支と mutation 裁定を行い、二軸判定の結果審査を行う。結果審査と限定採用判断は本 GO に含まれない
- **提出先**: Core への新規 Draft PR（追加のみ）。study run の成果物一式
  （manifest 追補・receipt・配列・pack・自己検証ログ）を1つの新しい study-run ディレクトリに置く。
  既存ファイルの変更はしない
- **上限**: 科学評価は 15 件で打ち止め／壁時計は候補＋自己検証で合計 ≤60 分／
  実施の試行は1回（インフラ障害で結果が1件も記録されていない場合のみ再試行1回まで。
  部分結果がある場合は保存して STOP し報告する）／executor の作業は ≤2 人日
- **主張の射程**: 本 GO は登録された in-model の研究実施のみ。Studio 統合・B1 P2・OMA 昇格・
  音質や製品能力の主張は含まれない
