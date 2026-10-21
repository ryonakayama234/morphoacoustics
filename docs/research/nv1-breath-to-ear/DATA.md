# NV1-EAR / Core — research-only DATA v0

## Purpose and safety
These are **proposed experiment-local structs/JSON**, not public `CreatureSpec`, `GestureScore`, Production Performance Contract v0/v1 or an adopted API. Schemas must be explicit, versioned and refused on invalid input. Use SI values internally; display convenience units only in Studio.

## Proposed BreathEarScene v0
```json
{
  "schema": "nv1-breath-ear.scene.v0",
  "sample_rate_hz": 48000,
  "duration_s": 2.4,
  "seed": 133041,
  "actuation": {
    "kind": "EXHALE_EXPERIMENTAL",
    "pressure_peak_pa": 120.0,
    "pressure_envelope": "raised_cosine_v0",
    "effective_aperture_m2": 0.000030
  },
  "air": {"density_kg_m3": 1.2, "dynamic_viscosity_pa_s": 0.000018, "speed_of_sound_m_s": 343.0},
  "closure": {"id": "nv1-aperiodic-monopole-v0", "discharge_coefficient": 0.65, "fluctuation_fraction": 0.002, "re_gate_low": 1000, "re_gate_high": 3000, "spectral_knee_st": 1.2, "max_acoustic_power_fraction": 0.01},
  "listener": {"position": "center", "distance_m": 0.3, "receiver": "ideal_A"},
  "sofa_path": null
}
```

Listener alternatives: `ideal_A`, `measured_B`. A/B **same-source control** fixes every source parameter and seed and varies only the receiver. For B, demand the exact trusted SOFA file hash and measured center/left/right direction available in experiment 041. Do not infer a continuous spatial renderer or arbitrary positions.

## Required physical traces (time-sampled or losslessly referenced)
- `drive_delta_p_pa[t]`, `aperture_area_m2[t]`; `Q_mean_m3_s[t]`, `jet_velocity_m_s[t]`, `Re[t]`, `pneumatic_power_w[t]`.
- `noise_seed`, closure version, raw deterministic `eta[t]` reference/hash, spectral-knee/handoff trace, `q_ac_m3_s[t]`, `d_q_ac_dt_m3_s2[t]`, modeled acoustic power budget and any safety limiter activation. Do not claim unfiltered Gaussian noise is CFD.
- `receiver_A_pa[t,2]` may be model Pa; `receiver_B_relative[t,2]` **must not be labeled Pa**. Store channel order L/R, fixture xyz, delays and handling, actual matched SOFA sample indices, IR provenance, and raw/unscaled peaks.
- `audio/*_L-R_48k_24bit.wav`; playback gain and any B-wide *single* relative gain separately from raw samples. Never normalize L and R independently.

## Manifest / reproducible Take receipt
```json
{
  "schema": "nv1-breath-ear.evidence.v0",
  "claim": "EXPERIMENTAL_NOT_ADOPTED",
  "core_commit_sha": "<exact-40-hex>",
  "git_dirty": false,
  "source_scenario_hash": "<sha256>",
  "run_id": "<collision-resistant-id>",
  "closure_id": "nv1-aperiodic-monopole-v0",
  "receiver_id": "ideal_A",
  "sofa_sha256": null,
  "sofa_md5_legacy": null,
  "wav_sha256": "<sha256>",
  "trace_sha256": "<sha256>",
  "playback_gain": "<number, separately recorded>",
  "limitations": ["equivalent stochastic source not calibrated to human breath", "no glottal vibration"]
}
```
Placeholders are template strings, never valid accepted manifests. Every actual render must replace with verified values. `run_id` not derived only from mutable client labels. Artifact directory creation is exclusive: collision/refusal, no overwrite.

## Failure semantics
`INVALID`: nonfinite/negative pressure, negative/zero/unsupported area (unless explicit `zero_drive` case), bad duration, seed, units, clip, dirty checkout for trusted E2E claim, corrupted hash.
`UNSUPPORTED`: unmeasured direction, unverified/unsupported SOFA, phonation/whisper/word request, dynamic organ geometry or inaccessible calibration.
`INFEASIBLE` reserved for genuinely modeled body limitation rather than unsupported feature.
Refusal returns structured outcome with **no playable WAV/Take**; never silently replace real measured B with mock A or an old WAV.

## Revision policy
Unknown schema versions fail closed. Material changes to field/unit/claim semantics require a schema revision, fixture test and peer review.
