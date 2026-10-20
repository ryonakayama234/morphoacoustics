# Experiment 041 — EL-G0a: embodied-reception A/B audition

**RESEARCH-ONLY / DRAFT / NOT_ADOPTED.** Independent calibrated source + headless acoustic model, no production Core or Studio change. On existing [EL-G0 PR #114](https://github.com/ryonakayama234/morphoacoustics/pull/114), with [Embodied Listener PR #83](https://github.com/ryonakayama234/morphoacoustics/pull/83) as parked parent.

## Creator's experience

Using headphones, choose **front / right / left**, then alternate **A** (free-field mathematical 2-point receiver) vs **B** (artificial-head measured near-field HRTF). Turn on hidden labels, listen and reveal afterward. The purpose is to test why a sound can be left/right-correct but insufficiently externalized. This is not an ASMR quality promise.

## Source and measured reference

[Marschall et al. 2023, near-field HRTF database](https://zenodo.org/records/7316545) (Aalto University, CC BY 4.0), record DOI `10.5281/zenodo.7316545`, 196 positions at distances 20/30/40/50 cm. Default: `NF_LIB_HRTF_measured.sofa`, MD5 `4ba9cc348801a6805265c7168b5b3227`, no LFE. Caution: measurements have limited low frequency fidelity (~200 Hz), thus the test source emphasizes 460–9000 Hz. No extrapolation to 1 cm/contact. File is fetched externally, not vendored into this repository.

### Reproduce in WSL2 / Linux (Python >=3.11)

```bash
python -m pip install -e '.[dev]'
python -m pip install 'scipy>=1.11' 'h5py>=3.8' 'soundfile>=0.12'
python -m pytest tests/test_experiment_040_listener_g0.py tests/test_experiment_041_listener_g0a.py -q
mkdir -p /tmp/el-g0a-dataset
curl -fL --retry 3 --connect-timeout 20 --max-time 120 \
  'https://zenodo.org/records/7316545/files/NF_LIB_HRTF_measured.sofa?download=1' \
  -o /tmp/el-g0a-dataset/NF_LIB_HRTF_measured.sofa
printf '%s  %s\n' '4ba9cc348801a6805265c7168b5b3227' /tmp/el-g0a-dataset/NF_LIB_HRTF_measured.sofa | md5sum -c -
python experiments/041_listener_g0a/run.py \
  --sofa /tmp/el-g0a-dataset/NF_LIB_HRTF_measured.sofa \
  --output /tmp/el-g0a-evidence-001
cd /tmp/el-g0a-evidence-001
python -m http.server 8765
# Open http://localhost:8765 in a browser, wearing headphones.
```

**Generated files:** `index.html`, `evidence.json`, and six stereo 48 kHz 24-bit PCM WAVs in `audio/`. Running again on an existing evidence directory refuses overwrite.

**Reproducibility caveat:** local automated tests use a *synthetic* SOFA fixture for unit coverage. It cannot prove the real Marschall dataset's metadata or acoustic quality. The real-data GitHub Actions job must pass and deposit six actual WAVs; if it fails, retain `UNSUPPORTED`, not a substitute simulated head.

## Physical and playback scopes

- A: each ideal probe `p(t)=rho/(4πr)·dQ(t-r/c)/dt`; units Pa before playback. Analytic `r/c` travel-time and geometric R/L ratio use matching measured source coordinates. PR #114's old fixture/frozen oracle remains untouched.
- B: SOFA HRIR, or inverse FFT of SOFA uniformly sampled `SimpleFreeFieldHRTF` transfer data, convolved with the *same source derivative*; no extra `1/r` or ear-canal correction. **B's absolute Pa scale, reference-plane calibration, and agreement of A vs B physical SPL are UNVERIFIED.** It is an objective HRTF reference response, not a fully calibrated common physical source-to-ear experiment.
- Position selection: actual SOFA measurements near 30 cm, azimuth about `0°`, `-30°`, `+30°`, elevation <=10°. Fails rather than invents an unmeasured direction.
- SOFA axes: +X front, +Y left, +Z up. Receiver array order MUST be L then R. Reads `ReceiverPosition` when usable; otherwise ideal L/R probes at y±0.09 m and discloses the fallback.
- SOFA delay is distinct from `Data.IR`/TF; never double-apply a pre-existing acoustic propagation delay. HRIR sample time origin and calibration remain a data audit item.
- Playback uses one global gain per scene; additionally applies a **single B-wide RMS matching gain** for listenability. Neither channel is normalized independently. `evidence.json` saves both raw peaks and gains. **No calibrated SPL or relative A/B loudness inference.**
- Headphones only, safe volume, no personalization / room / head tracking / pinna material / moving bodies / contact / Studio renderer.

## Review and decision

See [PREREGISTRATION](../../docs/research/listener-g0a/PREREGISTRATION.md), [SYSTEM](../../docs/research/listener-g0a/SYSTEM.md), [DATA](../../docs/research/listener-g0a/DATA.md), [RESULTS](../../docs/research/listener-g0a/RESULTS.md). Numeric checks and actual real-SOFA CI must be distinguished from the user's blinded listening evaluation and independent physics/data audit. Passing code checks never automatically promotes PR #83 EL-G1/G2 or production APIs.
