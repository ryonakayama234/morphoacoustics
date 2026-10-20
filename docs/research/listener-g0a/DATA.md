---
id: EL-G0A-DATA
schema_version: el-g0a-evidence-v1
status: RESEARCH_SCHEMA_CANDIDATE
---
# Data contract and reproducibility

1. Input SOFA file SHA-256, original Zenodo file name, CC BY 4.0 provenance and synthetic source generator's content SHA-256.
2. Coordinates in SOFA system (`+x` front, `+y` left, `+z` up), with named direction (`center/right/left`), `measurement_index`, absolute source cartesian metres, azimuth/elevation degrees and actual center distance.
3. Receiver positions either from `ReceiverPosition` measured HRTF meta (shape R=2, C=3), or documented fallback ideal ±0.09 m. Do not imply they are eardrum positions.
4. Source `Q(t)` cubic metre/sec at sample rate 48kHz, derivative times rho/(4πr) yields **A raw Pa**, physically meaningful under ideal monopole assumptions.
5. B uses HRIR/transfer relative coefficient and derivative drive, not independently verified Pa. `Data.Delay` in samples with explicit units; preserve measured ITD and relative ear spectrum.
6. `evidence.json` retains model IDs, source/receiver geometry, source code hash, SOFA file SHA-256 and metadata, A's delay and right/left ratio, all WAV hashes/length, unnormalized peaks, common playback gain and B-only scene-wide RMS compensation. A/B source signal identical; B level vs A not physically calibrated.
7. `audio/<case>_A.wav`, `<case>_B.wav`: 24bit/48kHz stereo PCM, left channel zero / right channel one; exactly six reproducible primary clips.
8. `index.html`: static UI; no third-party scripts, no analytics, no network writes. `el-g0a-listening-notes.json` user download optional; do not auto-upload user's subjective notes to GitHub.

Schema changes need version bump; do not mutate original EL-G0 `el-g0-result-v0` or its numerical oracle.
