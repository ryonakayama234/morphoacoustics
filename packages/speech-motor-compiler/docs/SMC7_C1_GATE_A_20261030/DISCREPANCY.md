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
