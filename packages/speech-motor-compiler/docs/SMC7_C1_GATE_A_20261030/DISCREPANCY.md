# C0 audit result drift: 39 early, 45 at accepted code SHA
2026-10-30 JST. Verified from actual GitHub Actions logs, not Japanese-reading gold.

## Primary observations
- Early [run 40846865407](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40846865407), job 123356379123: original Joyo JSONL SHA-256 32a843f662c55f1876baf64f8dc3475cc7b777c576a8fea6b43a2343ff46e897, 13,095 rows, 13,056 internally admitted, 39 internally rejected (INVALID_SOURCE 8; INVALID_TARGET_MARKER 31), 2,129 accepted target-kanji identities, L1 repertoire eligible 11,833.
- Later [run 40849518746](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40849518746), job 123365200966: SAME JSONL raw SHA, 13,095 rows, **13,050 admitted, 45 rejected** (INVALID_KEY 6, INVALID_SOURCE 8, INVALID_TARGET_MARKER 31), 2,128 accepted target-kanji identities, L1 eligible 11,833. Exact code-bearing reviewed source SHA 5087bd5775a148655188df9918d6faaff6a8ea4a.
- C0 RESULTS / DECISIONS reported 39 from the earlier predicate and subsequent log described continued 39. **This is incomplete as an exact-current-SHA account.** Preserve historical 39 and explicitly report 45 for latest code. Neither figure is 880 heldout accuracy.

## Mechanism and limits
Current audit_joyo_jsonl adds strict nonempty key reading, one basic-U+4E00..9FFF target character and validated key components. C0 independent software review earlier identified previously admitted malformed/nonkanji key forms. New strict predicate adds six INVALID_KEY at the SAME corpus hash, also changing distinct admissible target identities by one. This is **code-policy drift, not evidence the publisher supplied six linguistically wrong readings**. The exact six rows, intersection with earlier categories, and publisher validity require original line-by-line review before adjudication. The 8 and 31 other failures may include acceptable notational conventions, not errors.

## Disposition and action
- Maintain RECONCILIATION_REQUIRED; no silent exemptions, no Green by dropping rows, no publisher correction claims.
- Re-fetch exact revision, hash original bytes; compare both exact predicate versions on the same rows and export line number, key, reason, publisher policy before writing any mapping.
- Investigate six key, eight source, 31 marker cases with original source and expert review; classify publisher-valid/internal-unsupported vs suspected source error vs unresolved, preserving raw data.
- This public Joyo format audit is **separate** from acquiring a lawful independent 880 whole-utterance multi-gold corpus; it should not become an artificial blocker if that new corpus is independent.
- Original 39 historical counts may remain in time-local C0 ledger, but any present-day C0 acceptance summary should mention 45 under the exact accepted code.

## 2026-10-30 exact row-level reproduction: 6 newly rejected keys identified
The research-only, pinned-source row-policy reproduction in [SMC7 Gate A public Joyo audit run 40988272321](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40988272321), actual SUCCESS, downloaded original data and verified the **same exact SHA256**, independently computed both category sets: old 39, latest 45, with exactly six status transitions ADMITTED→INVALID_KEY. It produced a public, line-numbered 45-row manual queue in the Actions log, *not* any phonological/gold accuracy result.

**All six changed rows are the same valid orthographic character 𠮟 (U+20B9F, CJK Unified Ideographs Extension B):**
- JSONL line 1654–1656: 𠮟_シツ_0, 𠮟_シツ_1, 𠮟_シツ_2.
- JSONL line 1660–1662: 𠮟_しかる_0, 𠮟_しかる_1, 𠮟_しかる_2.

Unicode identity is externally attested as U+20B9F at https://www.cns11643.gov.tw/wordView.jsp?ID=666183 and Japanese common-use status / readings シツ・しかる are described by https://www.kanjipedia.jp/kanji/0002920800 . These references support a **real character and legitimately formed common-use reading key**, not full-sentence phonological gold truth. The latest strict C0 parser only admits U+4E00..9FFF in its **key**, therefore rejects this supplementary-plane Joyo character. This is a **confirmed parser repertoire incompatibility**, not a source-key typo. Mark six as PUBLISHER_KEY_PLAUSIBLE_INTERNAL_REPERTOIRE_UNSUPPORTED; natural sentence reading is still unreviewed. Preserve original byte identity (do NOT silently rewrite 𠮟 into 叱 or fold Unicode).

The remaining 8 INVALID_SOURCE and 31 INVALID_TARGET_MARKER rows have now been identified by key+line in the Actions manual queue, but linguistic/reference judgments have **not** been performed. Their statuses remain OPEN_RECONCILIATION. The current 45 classification is compatible with 6 explainable repertoire mismatches + 39 other strict-format differences; it is not an independently validated 39-row linguistic error rate. Add a typed unsupported-ideograph classification only via a future audited parser amendment and tests, not by loosening C0 silently.
