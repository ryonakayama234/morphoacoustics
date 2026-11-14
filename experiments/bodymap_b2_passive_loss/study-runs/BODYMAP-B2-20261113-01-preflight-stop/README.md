# BODYMAP B2 — 実施前 STOP 証跡（2026-11-13）

**状態: STOP_BEFORE_ENGINEERING_AND_STUDY。科学評価 0/15、negative 0件。**

Owner の実験実施 GO は確認済みであり、取り消した扱いにはしない。
指定された固定条件を検証する段で、以下の2点により開始できなかった。
本提出は停止証跡であり、study runner の提出・凍結・実施完了や結果審査ではない。

## 1. 確認した正本

- [Core GO](https://github.com/ryonakayama234/morphoacoustics/pull/294#issuecomment-6842652177)
- [Studio GO](https://github.com/ryonakayama234/morphoacoustics-studio/issues/61#issuecomment-6842658326)
- [監督者工学受入](https://github.com/ryonakayama234/morphoacoustics/pull/294#issuecomment-6826724845)
- [登録版](https://github.com/ryonakayama234/morphoacoustics-studio/blob/2f7d9546cc888ca43e54a20cf04d3708c95c416f/docs/product/body-map-g2-response-20261112.md): SHA-256 `9a022469264b4789c2d677d163470c4f7f393451635b264920463e6d70d3e41e`。取得原文を `registered-prereg-snapshot.md` に保存し、実バイトで一致を確認。
- Core pin: `0bb60cc227d231ec1cb67b701a849172ed92164b`。入力監査の前後で clean checkout。
- B2 lock SHA-256: `c0bd046498882beb61408440d9eadd1b9708ad8a49ad0035e0bdbaa5d3a6afd7`。

## 2. Blocker A — run manifest 原本の未取得

GO が指定する `BODYMAP-B2-RUNMANIFEST-20261113-01`、SHA-256
`e662141d1f79c7f1bb3663acdd33e476e2c949bf757fcf734a97005ede27aca8`
の実バイトを取得できていない。調べた範囲は receipt に記録した。
Core pinned main／Studio main のファイル一覧と該当PR・Issueの本文／議論には
名前とSHAの引用はあるが、原本または取得先は見つからなかった。
この探索結果は、別の保管場所での不存在を主張するものではない。

Owner の中継文から原本を再構成して同じSHAだと称することはしない。
OS/arch/BLAS等を含む元manifestとの照合は UNRESOLVED。

## 3. Blocker B — B2 lock 単独の新規環境では入力authorityをimportできない

Python 3.11.18 の新規venvへ、B2 lock を
`uv pip install --require-hashes --only-binary=:all:` でインストールした。
8 distributions のインストールは成功し、NumPy 2.4.6／SciPy 1.17.1／
mpmath 1.4.1 とlock SHAの一致を検証した。全distribution、OS、arch、
NumPy/SciPy build config は receipt にある。

固定pinの `geometry_binding.resolve_geometry("M0_REST")` の最初の入力読み戻しで、
以下の依存経路が停止した（実行1回、exit 1、原tracebackを保存）。

`geometry_binding.trusted_m0` → `tools/od2_body_cli.py::_load_context`
→ `tools/cc_a2_live.py` → `from jsonschema import Draft202012Validator`

実エラー: `ModuleNotFoundError: No module named 'jsonschema'`。
B2 lock の8 distributionsに jsonschema／その推移依存は含まれない。
`pyproject.toml` の dev extra は `jsonschema>=4.23` という範囲指定で、
固定環境の不足を無審査で補う根拠にはしない。

既存の `requirements/sv1-physical-py311.lock.txt` には jsonschema の固定closureが
あるが、SV-1専用であり、今回のGOに無断で合成しなかった。元run manifestで
別の補助closureが承認済みの可能性は原本取得まで未確定である。
この失敗は、監督者が既に行った工学受入を反証したという主張ではない。

## 4. 実施台帳と判定

| 項目 | 今回の実績 |
| --- | ---: |
| 入力authorityの読み戻し試行 | 1（失敗） |
| 工学候補／oracleのfull-grid評価 | 0 / 0 |
| 科学主ケース／repeated null | 0 / 0 |
| FZ-N1 negative | 0（全9系統未実施） |
| study試行／再試行 | 0 / 0 |
| study壁時計 | 0秒 |
| 発行pack | 0 |

M0の実digest／直径列照合、source consumed bufferのSHAは未取得。
推測値で埋めず UNKNOWN／null とする。B2候補評価を開始していないため、
失敗・中断した科学ケースは存在しない。入力監査の失敗ログ自体は欠かさず保存した。
この監査にstudy runnerはなく、runner SHA追補も未発行。
`IMPLEMENTATION_CONFORMANCE=UNRESOLVED`、`EFFECT=UNKNOWN`。
FZ-T1の式・閾値は変更せず、独立oracleの実行・確定判定も行っていない。

## 5. 再開に必要な証拠

1. 監督者作成の run manifest 原本または取得可能なimmutable参照を渡し、上記SHAを実バイト照合する。
2. 原本が入力authorityに必要な補助依存closureを既に承認しているなら、その正本と一致を照合する。
   そうでなければ、監督者が不足依存を含む実行環境の固定／manifest追補を審査し、Ownerの実施条件へ反映する。
   既存B2 lockをこの停止提出で変更しない。
3. 環境・入力のpreflightが成立した後に study manifest＋runner を準備し、工学8ケースの受入数値を再現する。
   科学評価前にrunner SHAを追補として固定し、独立プロセスのrepeated nullを含む15 evaluations＋negativeを実施する。
   pinの候補／oracle科学コードの変更が必要になった場合は、指示どおりSTOPし所定の改訂手続きへ戻る。

単なる再許可を求めるものではなく、既存GOの固定条件を実証可能にする不足入力・環境の解消依頼である。

## 6. 証跡ファイル

- `preflight-receipt.json`: 環境、pin別ファイルSHA・Git blob、未実施台帳、二つのblocker。
- `collect_preflight.py`: 最初の入力監査スクリプト。入力読み戻しで停止した原版。
- `input-readback-failure.log`: 最初の失敗の未編集traceback。
- `finalize_stop_receipt.py`: 数値計算やauthorityの再試行をせず、環境と既存失敗からreceiptを作る補助。
- `registered-prereg-snapshot.md` / `verify_prereg_snapshot.py`: 登録原文とそのSHA確認。
- `SHA256SUMS`: このディレクトリの他の提出ファイル全件（自己参照を除く）。

提出は追加のみ。CLI、候補、oracle、src、tools、contracts、既存tests、依存lockを変更しない。
Studio統合・capability・Take・G0特徴量methodの資格変更も行わない。
