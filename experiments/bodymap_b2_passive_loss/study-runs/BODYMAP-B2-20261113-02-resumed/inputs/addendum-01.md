# BODYMAP-B2-RUNMANIFEST-20261113-01 — ADDENDUM-01（2026-11-13、監督者）

PR #295 の実施前 STOP（blocker A／B）に対する監督者の解決記録。
科学条件・判定・ケースには一切変更がない。科学評価は依然 0/15 で、
本追補は「結果を見る前」の manifest 訂正として扱う。

## Blocker A（manifest 原本未取得）— 解決

- 原因は監督者側にある: GO 記録は manifest の SHA のみを指定し、
  原本ファイル自体を Lead が取得できる場所に置いていなかった。
- 本 PR ブランチに原本をそのまま追加した:
  `experiments/bodymap_b2_passive_loss/study-runs/BODYMAP-B2-RUNMANIFEST-20261113-01.md`
- 公開後の読み戻しで SHA-256
  `e662141d1f79c7f1bb3663acdd33e476e2c949bf757fcf734a97005ede27aca8`
  と一致することを監督者が確認する（確認結果は PR #295 コメントに記録）。

## Blocker B（jsonschema 不足）— 解決

- 発生経路（Lead 報告・監督者再現済み）:
  `geometry_binding.trusted_m0` → `tools/od2_body_cli.py::_load_context`
  → `tools/cc_a2_live.py`（22行目 `from jsonschema import Draft202012Validator`）
  → `ModuleNotFoundError: No module named 'jsonschema'`
- B2 lock は候補／oracle の数値環境としては完全だが、監査済み M0 読み戻し
  チェーンの import 依存を含んでいなかった。これは監督者の lock 凍結の不足であり、
  工学受入そのもの（監督者環境には jsonschema が存在した）を反証しない。

- 解決: 補助 lock `requirements/bodymap-b2-study-aux-py311.lock.txt` を監督者が凍結した。
  SHA-256 `884ca8de62840b3e41b0204872936ae696504d308b1b16394893c1889d759d22`。
  内容は jsonschema closure の6件のみ:
  jsonschema 4.26.0／jsonschema-specifications 2025.9.1／referencing 0.37.0／
  attrs 26.1.0／rpds-py 2026.9.1／typing-extensions 4.16.0。
  版とハッシュは、同一 repo で凍結済みの `requirements/sv1-physical-py311.lock.txt`
  の closure から逐語的に引き継いだ（新規に版を選んでいない）。
- 実施環境は **B2 lock ＋ 補助 lock の併用**に改める:
  `pip install --require-hashes --only-binary=:all: -r bodymap-b2-physical-py311.lock.txt -r bodymap-b2-study-aux-py311.lock.txt`
  （PYTHONPATH は repo の `src` を指すこと）
- 監督者検証（2026-11-13、pin `0bb60cc2` の clean clone、Python 3.11.18 新規 venv）:
  併用 lock は 14 distributions の導入成功。`resolve_geometry("M0_REST")` が成功し、
  digest `a98d484f…` と直径列（12,12,26,16,12,14,20,26,30,34,38,34,34,30,28,32）mm・
  16×0.010 m が登録どおり一致。対照として B2 lock 単独の新規 venv では
  Lead と同一の `ModuleNotFoundError` を再現した。

## 再開手順（GO は成立したまま）

1. 本ブランチ head から manifest 原本・補助 lock・本追補を取得し、SHA を照合する
2. B2 lock ＋ 補助 lock の環境で M0 読み戻しと source SHA を再確認する
3. study runner を用意し、SHA を科学評価の実行前に追補として固定する
4. 工学8ケースで監督者受入数値を再現してから、登録15ケース＋negative を実施する

手順1〜2で新たな不一致が出た場合は、科学評価を始めず再び STOP して報告すること。
