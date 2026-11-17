# R0 — 既存吐息4条件を回収する最初の作業

日付: 2026-11-17 JST。状態: 作業用ラッパーの実装。モデル採用・Studio統合ではない。

**次の一手:** Core PR #138の既存4条件を、Muse＋OwnerのVMで再現し、音と物理traceを回収する。  
**こちらの担当:** 設計・実装・修正・入力整備・結果検査・結果の解釈。  
**Muse＋Ownerの担当:** VM条件の確認、用意したコマンドの実行、結果回収、試聴と感想。

## 今回の到達物

| 条件 | 圧力ピーク | 有効開口 | 回収するもの |
| --- | --- | --- | --- |
| P0 | 120 Pa | 30 mm² | 基準の吐息モデル出力 |
| P2 | 240 Pa | 30 mm² | 駆動条件を変えた出力 |
| A2 | 120 Pa | 60 mm² | 開口条件を変えた出力 |
| Z0 | 0 Pa | 30 mm² | 無駆動・厳密無音の対照 |

元の2.4秒・48kHz入力、seed 133041、理想左右受音A、共通70倍の試聴用ゲインをそのまま使う。WAVは伝搬等による末尾を含むため、ファイル全長は入力の2.4秒より長い。ゲインは音圧較正を意味しない。

**終わりの条件:** 既存4条件のWAV・物理trace・実行記録・条件表・図が一式で返り、破損や取り違えを検出できること。自然な人間の息、心地よさ、モデルの採用は今回の完了条件ではない。

## 準備されたコード

- `tools/r0_breath_replay.py`: 環境の観察、固定した旧コードの実行、出力検査、条件表・図・ZIPの生成。
- `tools/r0_breath_requirements.txt`: 吐息研究で記録されたNumPy/SciPy/SoundFileの版。
- `tests/test_r0_breath_replay.py`: 上書き・入力改変・破損・失敗時保存などの運用テスト。

ラッパーはmain上の新しい運用ツールとして置くが、**計算する物理コードは別チェックアウトの未マージ研究PR**である。Coreの公開APIやASMR機能に昇格させない。元コードをコピーして新しい物理の正本にしない。

## Muse＋Ownerへの手順（Linux/WSL VM、Python 3.11/3.12推奨）

以下は既存作業ディレクトリと別の、新しい親フォルダで行う。各出力先は新規の名前にする。コード修正・新しいパラメータ選定は不要。

### 1. 道具と計算対象を別々に取得

```bash
git clone --branch ops/r0-breath-replay-20261117 --single-branch https://github.com/ryonakayama234/morphoacoustics.git morpho-r0-tools
git -C morpho-r0-tools rev-parse HEAD

git init morpho-r0-nv1
git -C morpho-r0-nv1 remote add origin https://github.com/ryonakayama234/morphoacoustics.git
git -C morpho-r0-nv1 fetch --depth 1 origin 0cffbc29cec4a07c93f60e45084c0e45bde4c058
git -C morpho-r0-nv1 checkout --detach 0cffbc29cec4a07c93f60e45084c0e45bde4c058
```

ツールの実行時点のコミットも返す。計算対象はPR番号の最新headではなく、上記の固定SHA。Git取得に失敗したら、そのエラーを返し、別版へ差し替えない。

### 2. 吐息専用の環境を作る

```bash
python3 -m venv r0-env
. r0-env/bin/activate
python -m pip install -r morpho-r0-tools/tools/r0_breath_requirements.txt
python morpho-r0-tools/tools/r0_breath_replay.py probe --destination . > vm_probe.json
```

GPUは使わない。`vm_probe.json`は観察できるCPU数・ホストメモリ・空き容量・ライブラリ版を記録する。ホストメモリはVMに割り当てられた利用上限を保証しない。Museは別途、利用可能メモリ／CPUの制限、ランタイム寿命、追加課金なしで動くこと、成果の回収先を確認する。APIキーは不要。

### 3. 既存4条件を実行して回収

```bash
python morpho-r0-tools/tools/r0_breath_replay.py run --source-root morpho-r0-nv1 --output r0-results-001
python morpho-r0-tools/tools/r0_breath_replay.py verify --output r0-results-001
```

このラッパーは、原型の`run.py`をそのまま別プロセスで呼ぶ。元のコード2件のSHA-256、Git HEAD、作業ツリーのclean状態、依存版を確認してから開始する。入力・出力先の取り違えを避けるため、出力は計算用チェックアウトの外に置く。計算用チェックアウトにvenvや入力メモを足さない。

標準の実行タイムアウトは120秒で、既存4条件の短い再現作業に対する運用上限である。旧研究の新しい科学的予算・判定条件ではない。超過したらログと途中出力を返し、こちらで資源と実行経路を確認する。最初から大規模走査に広げない。

返すものは **`r0-results-001/bundle.zip`、`vm_probe.json`、ツールのコミット、短い試聴メモ**。ZIPにはWAV・NPZ・元のevidence・実行記録・条件表・図・ログ・完了ファイル一覧が入る。ピークメモリとGPU適性はこのコードでは測っておらず、未測定と記す。壁時計時間と保存サイズは記録する。

### 4. 失敗と回収後の確認

- 失敗時は`failed.json`とログを残し、`complete.json`を発行しない。失敗したフォルダへ上書き・途中再開はしない。短い4条件の作業なので、修正後は`r0-results-002`等の新規出力先へ実行する。
- 完了時は`complete.json`に各ファイルのSHA-256を残す。回収ZIPを新しい空フォルダに展開し、同じ`verify`コマンドで確認できる。
- 検査は運用上の改変・破損検出であり、作成者の暗号学的認証や物理妥当性の独立審査ではない。
- 実行で困ったらエラー全文・実行コマンド・環境情報をこちらへ返す。Museに実装やコード修正を依頼しない。

## こちらでの検査と、VM実行の区別

こちらでは変更していない元コードの15テストと、ラッパーの9テストを確認する。ラッパーの実レンダー統合テストでは、元のコード2件を一時Gitリポジトリへ置き、ラッパー内の期待pinだけをその一時コミットへ差し替える。これはコマンド→音・trace→検査→ZIP→展開→再検査という経路のfixture試験であり、歴史的なPR HEADのclean checkout再実行ではない。生成物はテスト用で、正式な科学結果として提出しない。

```bash
python -m unittest discover -s tests -p 'test_r0_breath_replay.py' -v
```

通常は8件の運用テストを実行し、実レンダー統合1件はskipする。元コードのチェックアウトを用意した場合だけ、以下で統合1件も走らせられる。

```bash
R0_TEST_SOURCE_ROOT=/path/to/pinned/nv1-checkout python -m unittest discover -s tests -p 'test_r0_breath_replay.py' -v
```

上記テストにはNumPy/SciPy/SoundFileが必要。元の15テストを走らせるには、その別チェックアウトでpytestを用意して`tests/test_experiment_042_nv1_breath_ear.py`を実行する。

## 「あい」系は次に別環境で扱う

| 項目 | 今回確認した入口／区別 |
| --- | --- |
| Coreの入口 | `tools/cc_a2_live.py`。単一の「あい」、seed 0、固定LF source、M0/M1の限定条件 |
| 既存Studio導線 | Character→固定演技→Takeの既存導線。旧Takeの現物を今回取得していない |
| 既存資料の基準pin | `b569f044bfda309dff1a00cccf8365754e6b1355`。B1用`b5dc95d...`の採用経緯と混ぜず、実行前に現行運用pinを照合する |
| 依存版 | 記録された「あい」用NumPyは2.4.6。今回の吐息用2.3.5と同じvenvに押し込まない |
| 次の作業 | こちらが別環境の実行パッケージと入力を用意する。今回Museに「あい」用コードの設計・実装は依頼しない |

## 結果が返ったら

こちらで物理状態と音の変化を読み、次の問いを一つ決める。候補は、呼気の時間変化、音源の未較正なスペクトル則、発声源側の不足のいずれか。最初から結論を固定しない。試聴用の区間分けや比較入力が必要になれば、その時点でこちらが小さなHTML等の作業道具を用意する。

これはロードマップR0→R1への入口である。逆路線、受音研究の追加実験、Studio移行、外部公開・販売・マージを今回の作業に含めない。

## 根拠

- [Core PR #138](https://github.com/ryonakayama234/morphoacoustics/pull/138)と[固定run.py](https://github.com/ryonakayama234/morphoacoustics/blob/0cffbc29cec4a07c93f60e45084c0e45bde4c058/experiments/042_nv1_breath_ear/run.py)、[固定source.py](https://github.com/ryonakayama234/morphoacoustics/blob/0cffbc29cec4a07c93f60e45084c0e45bde4c058/experiments/042_nv1_breath_ear/source.py)。
- [元の登録](https://github.com/ryonakayama234/morphoacoustics/blob/0cffbc29cec4a07c93f60e45084c0e45bde4c058/docs/research/nv1-breath-to-ear/PREREGISTRATION.md)と[結果台帳](https://github.com/ryonakayama234/morphoacoustics/blob/0cffbc29cec4a07c93f60e45084c0e45bde4c058/docs/research/nv1-breath-to-ear/RESULTS.md)。今回は条件・判定規則・モデルを変更しない。
- [Studio CC-A2記録](https://github.com/ryonakayama234/morphoacoustics-studio/blob/47fa3f8571ffe2296c524e2111b2d32a4c06894e/docs/cc-a2-two-body-studio.md)と[Studio B1計画](https://github.com/ryonakayama234/morphoacoustics-studio/blob/47fa3f8571ffe2296c524e2111b2d32a4c06894e/docs/product/body-b1-plan-response-20261110.md)。歴史的な記述と後続の採用状態を区別する。
