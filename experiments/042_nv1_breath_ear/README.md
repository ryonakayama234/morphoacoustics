# Experiment 042 — NV1-EAR W0/W1: physically conditioned audible exhalation

**EXPERIMENTAL / UNCALIBRATED / NOT_ADOPTED.** Implements **only** source W0+W1, NOT measured HRTF B, Studio E2E, speech, whisper, contact, or natural human breath. See Core Issue #133 / Draft PR #138 and `docs/research/nv1-breath-to-ear/{SYSTEM,DATA,EXPERIMENT,PREREGISTRATION,RESULTS}.md`.

## What it actually solves
- Research EXHALE fixture: 2.4 seconds and 48 kHz; `Δp[n]=pressure_peak*sin(pi*n/(N-1))²`, fixed effective aperture.
- Ideal quasi-steady positive volume flow `Q=Cd*A*sqrt(2Δp/rho)` and `U, Re, ΔpQ`; a bounded seeded unresolved stochastic acoustic equivalent monopole source. This is **not** CFD or real human body anatomy. `q_ac` is **not** `Q_mean`.
- Frozen A0 preregistered time-varying STFT filter: PCG64(seed 133041), 2048 Hann/512-hop, heuristic 300 Hz HP / 9k guard / `1.2 U/D` spectral knee, gate `clip((Re-1000)/2000,0,1)`.
- Ideal free-field A model `p=ρ/(4πr) d(q_ac(t-r/c))/dt` with two L/R receiver probes at y±0.09m, source 0.30m front. No measured head/HRTF, no physical eardrum pressure claim.
- 48kHz 24-bit stereo WAV with one **fixed disclosure-only 70x playback gain shared by all runs**. Raw unscaled modeled Pa is kept in NPZ. Do NOT infer calibrated playback SPL from this gain.

## Reproduce (WSL2/Linux, Python 3.11+)

```bash
python -m pip install -e '.[dev]'
python -m pip install 'numpy==2.3.5' 'scipy==1.17.0' 'soundfile==0.13.1'
python -m pytest tests/test_experiment_042_nv1_breath_ear.py -q
python experiments/042_nv1_breath_ear/run.py --output /tmp/nv1-ear-w1-first
```

Do **not** render over an existing output directory. Output `evidence.json`, four new 48kHz/24-bit stereo WAVs (`P0/P2/A2/Z0`) and `traces/*.npz` containing full SI physical and acoustic traces. Z0 must be exactly silent. Every case includes SHA256 of `q_ac`, WAV and trace. Code revision and dirty status are recorded when available; `null` means no verified Git checkout. The exact SHA is not a substitute for a human physics/data audit.

## Baseline numerical and sonic result
Independent Wolfram steady-state peak Q values (P0 0.2757716 L/s, P2 0.3900000 L/s, A2 0.5515433 L/s) are checked by test, as is zero drive. Experimental audio may sound synthetic, hissy or filtered. Air-likeness/ASMR success is **not assumed**. Controls: compare P0/P2/A2 under **identical seed and playback gain**, test the best-fit gain-only null, inspect high-band fraction, then eventually add the W2 real measured SOFA receiver separately. Historical #30 white inlet noise was excessively amplified by the old acoustic chain; this new model is distinct but still uncalibrated.

No B receiver claims, Studio integration, personal HRTF, calibrated SPL, speech, /ha/, /fu/, or full-body dynamics.
