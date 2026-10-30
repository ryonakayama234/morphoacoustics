# SMC-7 Solo Reading Workbench — ひとり・無料・ローカル注釈

目的: 自作の台本について、自分の日本語読み（全文カタカナ・複数候補・不明）と理由を記録し、あとからB0/文脈モデルと比較して改良課題を見つける。これは **SOLO_DEVELOPMENT_ONLY**。独立正解・盲検880文・SMC運動プランの認証ではない。

費用0円、他の人不要、WSL2 Ubuntu + Windowsブラウザ、Python3標準ライブラリ。APIキー不要。ブラウザは他所へ通信しない。

## 手順A：まだレポジトリを持っていない場合

WSL2 Ubuntuのターミナルで:

~~~bash
git clone --filter=blob:none --single-branch \
  --branch research/smc7-gate-a-accession-20261030 \
  https://github.com/ryonakayama234/morphoacoustics.git
cd morphoacoustics
python3 -m http.server 8765 --bind 127.0.0.1
~~~

Windows側のChrome/Edgeで次のURLを開く:

http://localhost:8765/packages/speech-motor-compiler/research/solo_workbench/index.html

転送が効かない場合は localhost を 127.0.0.1 にする。注: http.server は受信をローカルに限定した静的ファイル表示専用。アクセスしたプライベートなテキストをネットに送るAPIはありません。

## 手順B：すでにcloneを持っている場合 (mainに触れず別worktree)

~~~bash
cd ~/morphoacoustics
git fetch origin research/smc7-gate-a-accession-20261030
git worktree add ../morphoacoustics-solo origin/research/smc7-gate-a-accession-20261030
cd ../morphoacoustics-solo
python3 -m http.server 8765 --bind 127.0.0.1
~~~

ディレクトリ位置が異なる場合は自分の既存cloneに移動する。別のworktree名でもよい。メインブランチの変更・マージ不要。

## UIでの作業: まず5件、余裕があれば20件

1. sample_cases.json をGitHubから取得し、画面の「JSON読込」で読む。3件の自作練習ケースには**正解を含めていない**。練習後は自分のオリジナル台本を「文章を追加」で登録する。権利のない第三者の文章を公開しない。
2. B0、辞書、モデルの読みをまだ見ないで、本人が思う **全文** の読みを全角カタカナで記入する。複数の自然な読みがあれば2行目以降に追記する。分からなければ UNKNOWN、文脈不足なら CONTEXT_INSUFFICIENT で空欄のまま保存して構わない。
3. 理由や判断に迷った点を書く。注目語を入力することはできるが、元の台本のUnicode位置を自動認証したことにはならない。
4. 「この注釈を保存」→ 数件ごとに「JSON書出」。個人の台本を含むため、**出力JSONは公開GitHubに貼らず自分のPCに保管**する。画面はブラウザlocalStorageに作業コピーを自動保存するが、ブラウザデータ削除やfile方式で消えることがある。JSONがバックアップの正本。
5. 再開するときはJSONを読み込む。最初は5件で終了してよく、120件・880件を一人で書く必要はない。本人の注釈を保存した後で初めて予測器の読みと比較し、誤読ケースを開発課題にできる。回答を見た後の注釈変更は元のJSONを残し、別名ファイルへ書き出す。

## データと実験的な証拠の区別

- 保存JSONのschemaは SMC7_SOLO_WORKBENCH_V1、tierは SOLO_DEVELOPMENT_ONLY。既存の gate_a_manifest_lint.py (2名の別々の注釈者+裁定者/120+880用) へ流用することはできない。
- 一文256 Unicodeコードポイント以内、周辺文脈512以内、案件250件以内。読み候補は最大8行、1行512文字以内。文脈不足や不明は無理に単一の正解を付けない。
- **一人で作問し、一人で正解を付ける**ことで得られるのは設計・デバッグ・例示の証拠まで。既存H1–H4の独立検証や一般化精度、クラスタ信頼区間は主張できない。無料の公開コーパスから補助的に調べられるが、その出版社の注釈権利・公開済み/学習混入リスクを別途記録し、独立ブラインド評価と混同しない。
- 信頼済み原文字位置→SMC5/6→Coreの経路へ渡さない。神経音声生成・身体表現・音質評価は別のゲート。

## 成果をどう使うか

このツールによる「開発用の本人記録」を固定した後、モデルや辞書の予測との差異・UNKNOWN率・候補数・UI操作上の問題点を検討する。設計や予測器の実装に進んでもよいが、既存H1–H6を合格扱いにはしない。

研究用PR: https://github.com/ryonakayama234/morphoacoustics/pull/253
データ依存Issue: https://github.com/ryonakayama234/morphoacoustics/issues/244
C1 Issue: https://github.com/ryonakayama234/morphoacoustics/issues/247
