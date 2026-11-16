# Source and rights ledger (publisher-level evidence, updated 2026-11-01 JST)

## Original source family K1
- TH Köln publisher: https://audiogroup.web.th-koeln.de/ku100nfhrir.html — R16-1118, Lebedev 2702 × 0.50/0.75/1.00/1.50 m, circular 360 × 0.25/0.50/0.75/1.00/1.50 m.
- Zenodo DOI https://doi.org/10.5281/zenodo.4297951 — files `NFHRIR_L2702_SOFA.zip` (**publisher-listed MD5 `1310d2b015c82272cc27d10d680b6bb4`**) and `NFHRIR_CIRC360_SOFA.zip` (MD5 `6380cf3e4592e2adcb8bb01ad79f0679`). Zenodo v2 published 2020; source host lists R16-1118 (2016). These metadata dates are not necessarily equal to byte-level editions. SHA256 is UNKNOWN until **downloaded and locally hashed**.
- 2016 authors' paper https://audiogroup.web.th-koeln.de/PUBLIKATIONEN/Arend_TMT2016.pdf states CC BY-SA 4.0 for near-field SOFA+miro set. Zenodo page Rights field is not displayed with a concrete license value; do not mislabel source as unlicensed. File notices and downstream derivative distribution need independent review.
- Publisher method: postprocessed 48-kHz, 128-tap source magnitude/phase compensated, 200-Hz bass extension, trimmed and normalized responses, robot-arm shadow (rear Lebedev angles). Exact file convention/plane and signal/Delay remain unverified before source metadata job.
- Publisher's 2020 gain note: https://audiogroup.web.th-koeln.de/FILES/NF_Datasets_Gains_infos.pdf. **Restore natural level differences** in SOFA and miro by applying factors by distance, not MIRO `normalization` (ignores varying preamp gains).

| Radius m | Publisher factor | Published dB | 20 log10(factor) dB |
|---:|---:|---:|---:|
| 0.25 | 1.00 | 0 | 0 |
| 0.50 | 0.33 | -9.65 | -9.6297 |
| 0.75 | 0.25 | -12.1 | -12.0412 |
| 1.00 | 0.16 | -15.7 | -15.9176 |
| 1.50 | 0.095 | -20.4 | -20.4455 |

**Interpretation**: the published factors and rounded dB entries are not exact conversions (notably the 1.0-m row differs by 0.218 dB); treat the note as approximate/document-level until gain precedence/precision is clarified. Do NOT claim measured discrepancy or silently use `MIRO.normalization`. No factors applied in G0-A2. Explicit attenuation values are not a universal free-field inverse-square law.

## Distinct NHK candidate
2026 paper DOI https://doi.org/10.1250/ast.e25.48; author-reported 865 upper-hemisphere directions ×27 radii; original HRIR distribution/data rights NOT VERIFIED. Do not substitute NHK for K1 or transfer article CC BY-ND to data.

## Historical non-blind
NF1/NF2 Aalto, NF3 KEMAR, NF4 SCUT previously exposed; not fresh G3b. NF4 C4 only 242/344 accepted (70.35%) and four-band ILD C4 2.34171 dB vs B3 2.06708 dB and posthoc B0 1.53527 dB. Failures retained.

## Privacy and distribution
Do not add SOFA, archive, audio, per-position derived acoustic responses, model weights or final truth to git. Publisher and mirror identities are aliases until hashes establish exact copies; never count them as independent heads.

## Verified original header/ZIP findings (2026-11-01; commit 8f663af, run 41307651527)
Original full-sphere ZIP MD5 match and SHA256: `5f3a4c6df0f0c0bbbce6639f41129a20bc03603d19316db74637f70bfa1ff5f9`. Four SOFA files each [2702,2,128] original response shape and [1,2] Data.Delay shape; recorded SOFA convention version 1.0, Fs=48k. Confirmed original SOFA root `License = CC 3.0 BY-SA`, different from paper's dataset licence CC BY-SA 4.0. Do NOT silently reconcile notices; independent rights review required. Full non-reconstructive per-file SHA256 and structure are in RESULTS and CI stdout. No original audio/IR or per-position geometry has been committed.
