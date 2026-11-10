# B1 P0 audit handoff — supervisor-accepted evidence capture

**Captured:** 2026-11-10 JST. **Status:** P0 ACCEPTED by Muse; P1 independently authorized by Owner.  
**Evidence classification:** Documentary transcription of independently recorded supervisor observations, **not** a new machine re-audit. The original P0 working-paper body was not committed at capture time; this document is a repo-local cross-reference and bounded ledger, not an invented replacement for unpublished source materials.

- [Studio #54 — Muse P0 acceptance, comment 6766562565](https://github.com/ryonakayama234/morphoacoustics-studio/issues/54#issuecomment-6766562565) — authoritative accepted ledger and RQ dispositions.
- [Studio #54 — Owner P1 GO, comment 6766594718](https://github.com/ryonakayama234/morphoacoustics-studio/issues/54#issuecomment-6766594718).
- [Adopted P0–P5 / QP1–QP6 plan](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/body-b1-plan-response-20261110.md).
- [OD-2 inherited research results](../../research/od2-reusable-physical-body-20261102/RESULTS.md).

## Read-only old/new Core comparison recorded by Muse

| Source blob | Observed identical in b569 / 01b2 candidate | Meaning |
| --- | --- | --- |
| `tools/cc_a2_live.py` | `dd90ab5e` | CC-A2 source |
| `src/morphoacoustics/integration/body_presets.py` | `14023932` | registry |
| `src/morphoacoustics/integration/limited_live.py` | `aa729fb6` | frozen limited-live |
| `contracts/performance/v1/common.schema.json` | `37e4403f` | v1 common schema |
| v1 contract text | `9789ee54` | contract document |

Old pin: `b569f044bfda309dff1a00cccf8365754e6b1355`. Compared Core candidate: `01b2a33732c1256764eb91358583e16a1fcee865`; supervisor reported **99 commits** difference. **Candidate is not an adopted product pin.** The new P1 branch head, not this historical SHA, is the subject of P1 exact-head review.

## P0 six-case identity ledger (zero-based center, ratio is a string)

| center | ratio | Core-authoritative revision ID | preparation digest as published in supervisor acceptance | lineage |
| ---: | :---: | --- | --- | --- |
| 4 | 0.90 | `od2-bfb4199f5d3a38ded992d42cbd7858ad5b4ebc34b297c9f1a8411dde88bdbf0b` | `sha256:129bf045…` | nonnull |
| 4 | 1.00 | `v3b-axial-M0@1` | `sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de` | parent alias |
| 4 | 1.10 | `od2-7c2663189d907111665544c67def56c885576f5394e4220ec12251e0ca5ebf67` | `sha256:f2778205243970d43ca3ea0151b91286fd9c46fb85b8867a8efbb7b811e6da0a` | nonnull |
| 8 | 0.90 | `od2-d722dfb9595672f0d19c46a8780c610c9d41fc3a8935b93d3d01a5d68aab4084` | `sha256:4b4300f05d0ea98d2edc3e6c17d8075fd29a51c8de91af599a94fa663b602375` | nonnull |
| 8 | 1.00 | `v3b-axial-M0@1` | same exact parent digest | parent alias |
| 8 | 1.10 | `od2-b04351e9865aef8af2953ed8b585eefa7bf40ec0887214daf4c0e32590478716` | `sha256:649c0b17…` | nonnull |

**Do not complete abbreviated digests by guessing.** The Core P1 catalog checks those P0 prefixes and re-derives the full `preparation_digest` from source-pinned physical Core. Fully resolved values are emitted in the exact-head P1 protocol receipt and must be compared against Muse's independently executed ledger before product pin adoption. The published c4/r1.10 and c8/r0.90 full SHA values are corroborated by the OD-2 RESULTS.

P0 supervisor's Core runtime: Python 3.12.3, NumPy 2.4.6. Source and task are fixed `lf_fixed` / inherited three-task. Observed OD-2 raw-Pa relative L2 examples: center4 about 5.63%; center8 about 2.66%. This does not measure human-perceived voice quality or a new sound model.

## Bounded RQ acceptance and pending conditions

- **RQ1 AGREE:** two earlier complete recipe identities reproduced; two missing identities derived in audited Core. This is the P0 authoritative ledger.
- **RQ2 AGREE:** proposed Core pin comparison is not product pin adoption. Formal pin follows P1 **exact-head audit and Owner decision**.
- **RQ3 AGREE:** old historical Take remains tied to the old pin and classification, query/exportable as archive. A mismatched `core_commit` must fail closed on the active façade. Archive lookup and active façade execution are not interchangeable.
- **P2 prerequisite unresolved:** Owner-PC backups must be rechecked before any pin migration. No P2 work is authorized by P1.
- **QP2 bridge unresolved:** unchanged v1 derived-preset transport remains **conditionally promising, not yet proven**; proof belongs to P1/P2.
- **Source full VERIFIED remains UNKNOWN; Take classification remains INCOMPLETE_PROVENANCE; audio quality NOT_ADOPTED.**

## Scope guard

P1 may issue four nonnull Core body receipts and resolve two M0 aliases only, verify the inherited model/shape/physical evidence and publish candidate protocol records. It may not change Studio, v1 schema, old Take, source physics, material/side branches, product pin or UI. This file records historical P0 evidence and **does not** exercise those later-stage authorizations.
