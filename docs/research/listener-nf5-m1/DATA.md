# DATA — original corpus, identity and contamination ledger
## Qualified-by-hash source family (structure only)
TH Köln R16-1118, Arend/Neidhardt/Pörschmann near-field KU100; Zenodo v2 https://zenodo.org/records/4297951.
Original ZIP `NFHRIR_L2702_SOFA.zip`: publisher MD5 `1310d2b015c82272cc27d10d680b6bb4`; observed original SHA256 `5f3a4c6df0f0c0bbbce6639f41129a20bc03603d19316db74637f70bfa1ff5f9` [#270 GitHub Actions 41307651527, reproduced 41307934856].
Expected four members `HRIR_L2702_NF050.sofa`, `NF075`, `NF100`, `NF150` with r=.5,.75,1,1.5m; each original metadata: `SimpleFreeFieldHRIR 1.0`, Fs48000, IR [2702,2,128], Delay [1,2], SourcePosition [2702,3] spherical degree/degree/metre, ReceiverPosition [2,3,1] cartesian metre.
The companion `CIRC360` dataset includes 0.25m but is **a different grid**: never infer 0.25m at 2702 Lebedev directions.
## Source versions and rights
2016 publisher paper records near-field CC BY-SA 4.0; SOFA root attributes record `CC 3.0 BY-SA`. Both are copyleft-style attribution/share-alike families but the governing original license edition, derivative and commercial distribution terms require independent review. Neither paper nor archive integrity is sufficient product clearance.
Original archive may be acquired ephemerally for authorized research-only geometry and structural inspection. Never commit source ZIP, raw SOFA, Data.IR/Delay numeric arrays, raw audio, reconstructed filter coefficients or unreviewed model weights. Git evidence receipts only.
Publisher gain note https://audiogroup.web.th-koeln.de/FILES/NF_Datasets_Gains_infos.pdf: .25m=1, .5=.33, .75=.25, 1=.16, 1.5=.095; rounded documented dB differ from log conversions by up to ~.218dB; do not claim a measurement discrepancy or apply coefficients without resolved reference.
## Blind evidence and independence
- NF1/NF2 Aalto/Marschall original; NF3 KEMAR Li original; NF4 SCUT 10 subjects and 344 previously opened final positions: historical or G3a diagnostics ONLY, not new NF5 G3b.
- KU100 full-sphere original family is distinct from these (publisher and measured head); KU100 0.5–1.5m does not validate 0.2m, 1cm, contact or other humans.
- Rehosting or re-zipping KU100 produces no independent new head. All four shells share the same head and acquisition/postprocessing lineage.
## Data receipt
Maintain original hash, individual member hashes from PR270, source link, edition, access terms, physical plane, timing, coordinate convention, head identity, effective angular blocks, role hashes, model hashes, accepted/refused counts, training/selection/calibration/final truth first-read receipt. Null=unverified, NOT_RUN!=FAIL, metadata PASS!=physics PASS.
