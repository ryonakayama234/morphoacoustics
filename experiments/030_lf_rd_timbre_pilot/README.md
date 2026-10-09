# Experiment 030 — X2b LF Rd timbre pilot (preregistered)

**Status:** exploratory, physical resynthesis; NOT a replacement for the frozen X2a reference or a general voice-quality claim. Core tracking issue: #71. Based on informal 2026-10-09 user listening: original physical /a/→/i/-like sounded intelligible to one listener but too buzzy/harsh; playback-only attenuation (-3 dB) helped somewhat, while a mild high-frequency EQ was perceived as markedly better at near-identical RMS. That diagnostic EQ is a **perceptual reference, not physical evidence**.

## Prior physical evidence and intervention

- **S0 (baseline):** identical prepared V3c `M_plus` morphology, V3a 3-task frozen /a/→/i/-like movement, `lf_fixed` Experiment 013 source at 100 Hz, `Rd=1.0`, fixed deterministic periodic flow, no microvariation or noise. Same Experiment 029 `evaluate_condition` acoustic renderer. The audited X2a reference is pinned by quantized raw pressure digest `dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e` and Core revision `a75418770ed28cbd301d554171a6b60ee5a05ee9`.
- **P1 (single intervention):** build the same LF volume-flow source, source envelope and same peak volume-velocity `SOURCE_PEAK_M3_S`, with **only source shape parameter `Rd=1.4` changed**. Keep F0 100 Hz, duration 0.5 s / 48 kHz, source period array, prepared body, task sequence/clock, geometry and acoustic path unchanged. A change to Rd mathematically changes LF-derived Ra/Rk/Rg/Tp/Te/Ta jointly, not independent changes to those values.
- **Do not** manipulate finished WAV with EQ, change global `Direction.energy`, claim timbre improvement before hearing, auto-select output using a listener's preference, edit the audited X2a baseline files, or change the Studio live pin.
- The existing LF implementation integrates a differentiated LF flow then interpolates a periodic glottal volume-velocity source; this is a model-based intervention, **not** a simulation of tissue FSI or proof of natural phonation.

## Preregistered hypotheses and contrasts

- H0 null: a controlled Rd increase does **not** produce a meaningful improvement in harshness/preference when output is regenerated through the same physics.
- H1 source: at fixed fundamental and source peak-volume-velocity, P1 source changes the glottal pulse profile and its spectral slope. Prediction: weaker relative high-frequency source energy; this must be measured, not assumed.
- H2 rendered: after the same time-varying vocal tract, the rendered spectral balance and listener impression may change toward the perceived softer EQ preview, without destroying the /a/→/i/-like transition. Spectrum and perceived quality need not move together.
- Source-band spectra are not tract formants; outlet spectra at 0.12–0.22 s and 0.32–0.42 s will be reported *separately*, for predeclared bands 80–600, 600–1500, 1500–3000, 3000–6000 and 6000–10000 Hz. Window: full 0.10-s Hann-weighted rFFT per region, density ratios in dB; no fitted post hoc frequency cutoffs. No implicit cutoff-based "scientific pass" on preference.
- Use two level-matched PCM previews created **only by linear scalar gain**, with the same RMS dBFS and no per-frequency filter; their replay gain and dynamic peak recorded. The original X2a WAV remains immutable and is not retroactively relabeled a physical P1.
- Record input source float64 SHA-256, output raw pressure float64 and quantized digest, normalized audio PCM SHA-256, 102 acoustic-transfer calls per valid condition, feasibility and endpoint equality, sample rate/duration, numerical toolchain and reference Core commit. Assert rebuilt S0 source exact equality to adopted `lf_fixed`, and S0 rendered quantized pressure SHA-256 matches the audited X2a fixture. Always fail closed if either diverges. Distinct P1 output alone does not establish perceptual improvement.
- Final perceptual gate **pending**: at least level-matched blinded, randomized condition presentation with independent reports for (a) 「あい」 identification, (b) transition quality, (c) hardness / metallic buzziness, (d) preference, and (e) volume difference. This first personal listening round is qualitative only; no population-level claims. Measure after the listener responds and keep negative results.

## Execution

In full source checkout on Linux / WSL2, Python 3.11, audited NumPy 2.4.6:

```bash
python -m pip install 'numpy==2.4.6'
python -m pip install -e '.[dev]'
python experiments/030_lf_rd_timbre_pilot/run.py --output-dir rd030-output
```

Expected deliverables in a **new**, nonexistent output directory: `s0_rd1p0.wav`, `p1_rd1p4.wav`, raw pressure `.npy`, source `.npy`, and `metrics.json`. Workflow `experiment-030.yml` executes actual solver physics in Ubuntu GitHub Actions, verifies outputs, then uploads them for listening. Never interpret a processed playback-only diagnostic EQ as a physical P1.

## References and limitations

- Fant et al. (1994), [Voice source parameters in continuous speech](https://www.isca-archive.org/icslp_1994/fant94_icslp.html), DOI 10.21437/ICSLP.1994-377 (source-shape reduction).
- Huber & Roebel (2013), [voice descriptors for glottal shape](https://doi.org/10.1016/j.csl.2013.09.006) (Rd and phonation range).
- [Global waveshape parameter Rd in signaling focal prominence (2022)](https://doi.org/10.3389/fcomm.2022.1026222) (higher Rd tends toward laxer/steeper source spectral tilt; not guaranteed for this solver).
- Kreiman et al., [Perceptual evaluation of voice source models (2015)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4491021/) cautions against inferring voice quality solely from idealized source fit.
