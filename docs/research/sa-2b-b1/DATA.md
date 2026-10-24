# DATA — explicit physical state and evidence schema
All stored quantities use SI units. Fixed tube configuration is separate from observations.

```text
B1Config
  length_m: 0.16                     # uniform calibration tube, NOT authentic M0 area profile
  area_m2: B0-derived M0 lip area    # 0.000804247719318987
  rho_kg_m3: 1.21
  sound_speed_m_s: 343
  cells: 16 / 32 / 64
  sample_rate_hz: 48000 / 96000 / 192000
  termination: closed | matched | b0
  inlet_volume_flow_mid_m3_s[n]      # externally driven, not VF-1
PhysicalState[n]
  pressure_cells_pa[N]
  internal_face_flows_m3_s[N-1]
  lip_inertial_flow_m3_s             # B0 termination only
PhysicalTrace[n]
  inlet_pressure_mid_pa
  lip_pressure_mid_pa
  inlet_volume_flow_mid_m3_s
  outlet_volume_flow_mid_m3_s
  lip_incident_pa / lip_reflected_pa # B0 only
  tube_energy_j / mouth_energy_j
  drive_work_j / terminal_dissipation_j / energy_residual_j
ArchiveManifest
  schema: research.sa2b_b1.v0
  decision: NOT_RUN until exact CI
  source_sha: verified by CI only
  gate_A_source_ref
  units / config / numerical scheme / oracle / exclusions
  artifact_sha256: {*.npy: sha256}
```

No Studio Take, listener WAV, spectral post-processing, utterance label, or invented acoustic-source provenance. Potential voice quality/character separation belongs to later frozen source + physical listener and Studio Voice Atlas records, not B1 data.