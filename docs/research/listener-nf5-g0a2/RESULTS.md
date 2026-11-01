# G0-A2 RESULTS — append only

## 2026-11-01: publisher source/gain desk inspection (DOCUMENTED)
- Original Zenodo v2 page lists `NFHRIR_L2702_SOFA.zip` 13.6 MB, **publisher-listed** MD5 1310d2b015c82272cc27d10d680b6bb4; this is not a locally computed source SHA256.
- Publisher gain-info document explicitly lists distance-specific gains: 0.25 m ×1.00, 0.50 ×0.33, 0.75 ×0.25, 1.00 ×0.16, 1.50 ×0.095; published dB entries respectively 0, -9.65, -12.1, -15.7, -20.4. Simple logarithms show up to ~0.218 dB nominal table rounding/precision difference. Not an empirically measured inconsistency.
- Source publisher report: 48 kHz / 128 samples => 2.66667 ms; 375 Hz native DFT spacing. At c=343 m/s, free-space 1.5 m travel =4.373 ms, **longer than the stored FIR support**, which is a reason to audit `Data.Delay` and origin, NOT proof of discarded physical arrival information.
- Original author paper asserts CC BY-SA 4.0 for dataset; *no independent legal reviewer* has checked file-level notices or derivative/Studio distribution conditions.
- Physical receiver plane, original SOFA channel identity, absolute time origin, per-position delay, data normalization implementation, uncertainty, S1/S2 independent spatial blocks **NOT VERIFIED**. No measured acoustics or predictive scores have been computed.
- Local environment direct Zenodo binary download failed due to DNS/network. Public web Zenodo ZIP fetch returned HTTP 429. No original bytes were available to the local environment at document creation; original metadata CI is proposed and its result must be appended ONLY after its actual outcome is observed.
- **Current conservative scientific verdict: G0-A2 INCOMPLETE; G3b BLOCKED.** This is NOT model failure.

## CI evidence
Synthetic metadata/format tests and original integrity workflow are described in `experiments/051_el_nf5_g0a2/` and `.github/workflows/el-nf5-g0a2.yml`. Their success/failure will be recorded with exact run URL and immutable code SHA when available; do not infer CI success from presence of workflow.
