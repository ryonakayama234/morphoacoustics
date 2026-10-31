# EL-NF4 — DATA / original measured source audit

Official directory: https://sofacoustics.org/data/database/scut/ . Candidate files: `SCUT_NF_subject0001_measured.sofa` through `SCUT_NF_subject0010_measured.sofa`, each listed ~48 MB. This is a *10-file access claim*, not 56-file full public availability.
Scientific report: Yu et al., JASA 143(3):EL194 (2018), DOI 10.1121/1.5027019, described 56 subjects, seven source distances and 685 directions each.
**G0 rights = UNVERIFIED.** Directory availability is not a distribution/commercial-use grant. Do not publish source audio, subjects' biometric or personal measurements; do not distribute SOFA or per-position raw HRIR in evidence artifacts. Audit file/source terms before any shareable binary or released model.
**G0 receiver reference plane = UNVERIFIED.** `ReceiverPosition` metadata alone does not establish microphone at canal entrance / eardrum, open/blocked-ear conditions, source equalization or absolute pressure calibration.
**G0 source-normalization = UNVERIFIED.** Relative ILD and monaural centered spectral shape do not imply reliable absolute loudness versus distance.
**G0 coordinate topology = UNVERIFIED.** Geometry-only audit must record HDF5 convention, Type/Units for SourcePosition and ReceiverPosition, ListenerView/Up, Data.IR shape, Source/Receiver sample order, sampling rate, Data.Delay, complete actual radii/azimuth/elevation, duplicate/missing positions and potential spatial dependence.
External KU100: https://audiogroup.web.th-koeln.de/ku100nfhrir.html ; recorded normalization/gain cautions at https://audiogroup.web.th-koeln.de/FILES/NF_Datasets_Gains_infos.pdf . Only a separate external comparison after format/rights validation.


## 2026-10-31 actual original source audit after G0

Original ten publisher-hosted SCUT `*_measured.sofa` all downloaded for the measured G3 run. Actual measured source SHA256 and source geometry SHA256 pinned in [MEASURED_SUMMARY_2026_10_31.json](MEASURED_SUMMARY_2026_10_31.json); source bytes are NOT in Git. Observed original metadata each SOFA: `SimpleFreeFieldHRIR`, `Data.IR=(6048,2,512)`, `Data.SamplingRate=96000` Hz, zero `Data.Delay`, spherical source degree/degree/metre, 864 directions at each seven distances. Public-file direction count differs from older article's 685; **the original file, not the abstract count, is used as measurement truth**.

Embedded global `License: CC 3.0 BY-SA-NC` is a **noncommercial** constraint; G3 research diagnostics only. It is NOT a grant to distribute source audio, head-specific measured IR, model weights or a commercial Studio adapter. Exact legal text/redistribution, physical receiver/microphone plane, free-field stimulus reference and absolute pressure normalization still require independent rights/metrology audit. Never infer an ear-drum observation point from merely finding `ReceiverPosition`.
