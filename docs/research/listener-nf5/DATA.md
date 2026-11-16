# EL-NF5 — DATA / historical exposure and candidate evidence

**Status: design-only; NO new source has been qualified or downloaded by NF5. All future final-truth access is controlled by [G0_DATA_QUALIFICATION](G0_DATA_QUALIFICATION.md).**

## Historical actual-measured records (development/retrospective only)

| Source family | Prior project exposure | NF5 permitted role | Essential limit |
| --- | --- | --- | --- |
| Marschall/Aalto LIB HRTF, original measured source, Zenodo 7316545 | NF1 [#252](https://github.com/ryonakayama234/morphoacoustics/pull/252), NF2 [#255](https://github.com/ryonakayama234/morphoacoustics/pull/255) | Development; old-study reproduction; ablations | Same head/data already exposed; NOT an independent untouched NF5 final |
| Li et al. near-field KEMAR, Zenodo 7626148 | NF3 [#257](https://github.com/ryonakayama234/morphoacoustics/pull/257): 83,448 measured positions, 48 kHz | Development, topology stress tests | NF3 opened its final; new split does not erase previous exposure; 1 cm refers to distance increment, NOT ear contact |
| SCUT individual near-field measured subjects 0001–0010 | NF4 [#261](https://github.com/ryonakayama234/morphoacoustics/pull/261): 6048 positions/head, 96 kHz | Development; failure and cross-subject diagnostics | NF4 original final opened; 10 files are not all 56 participants described in the article; embedded CC BY-SA-NC noncommercial; reference plane/unity gain unresolved |
| NHK 2026 HATS near-field study reporting 27 distances and 865 directions | Literature-only candidate (not used by NF5) | **Prospective G0 access investigation only** | Original accessible measured HRIR, right to access/use, metadata, calibration and independence NOT VERIFIED |
| Newly conducted, independently sourced HATS/head measurements | Not identified | Alternative prospective G3b original source | Must have auditable provenance, rights, plane, enough spatial blocks and truly unseen final truth |

Historical exposures are scientific development material; they may explain NF4's negative low-band ILD behavior, but using their opened final outcomes for tuning forfeits fresh confirmation. Dataset license conditions do not disappear through model training or code/model freezing.

## Essential recorded previous results (historical, NOT NF5 evidence)

- NF1: same-direction unseen-radius C1 yielded a G3 **GO_LIMITED_NUMERICAL_CANDIDATE** under its prereg, not adopted.
- NF2: unknown-direction C1 1.92128 dB vs B1 2.75161 dB but bootstrap improvement interval included zero; **REVISE_OR_REJECT**.
- NF3: C2 supported 0/155 final queries; **INDETERMINATE**.
- NF4: C4 support 242/344 (70.35% below 80%); median ILD B3 2.06708 vs C4 2.34171 dB, interval crosses zero; **REVISE_OR_REJECT**. B0 posthoc on same accepted positions 1.53527 dB vs B3 2.06708 vs C4 2.34171 dB. C4 better 2–8 kHz but worse 0.5–2 kHz; **posthoc exploratory only**.

Source of record: the exact prior PRs and their frozen `RESULTS`/`DECISIONS`, especially [NF4 Results](https://github.com/ryonakayama234/morphoacoustics/blob/research/asmr-el-nf4-support-field/docs/research/listener-nf4/RESULTS.md).

## Required intake ledger for each newly considered source

Record source owner/publisher, immutable original URL and download timestamp, license/grant/terms with retrieval evidence, SHA-256, file count, participant/head identity and permitted reuse; SOFA convention/Type/Units, file Data.IR dimensions/channel labels, SamplingRate, Data.Delay, SourcePosition and ReceiverPosition, ListenerView/Up, microphone reference plane/open-vs-blocked, source normalization/free-field equalization, anechoic quality, valid azimuth-elevation-distance and geometry block count. Critical gaps are not inferred from SOFA field names.

Do not upload/publish raw human SOFA, HRTF/HRIR audio, identifiable biometric traces, trained restricted weights or reconstructive derivatives to GitHub as experiment artifacts; a non-reconstructive aggregate report can be preserved if licenses permit.

## Claim limits

- Relative measured left/right transfer **at a specific measurement reference plane** only.
- With one new artificial head, accuracy only within that head's measured angular/radial support; no generalization to unknown heads.
- HRTFs measured at >=0.2 m cannot prove accuracy at 0.01 m, ear/mouth contact or tissue/structure conduction.
- Without externally verified acoustic source/reference calibration, do not claim absolute ear-drum pressure or absolute loudness vs distance.
