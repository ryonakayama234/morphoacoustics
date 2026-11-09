# VM-1A data schema — exact physics ports and evidence

**Candidate research-only `voice-metrology-transfer/vm1a`**, never production `CharacterSpec` or `PerformanceResult`.

```text
VM1AReport
  schema_version, kind=RESEARCH_ONLY, gate, quality_status=NOT_ASSESSED
  physics_model {rho_kg_m3,c_m_s, static=true, wall_loss=UNMODELED}
  provenance {core_base_sha, geometry_json_blob_sha1, geometry_digest_sha256}
  stimulus {kind=single-tick-flow-pulse, injected_volume_m3, source_flow_digest_sha256}
  runs[M0-b0,M0-matched,M1-b0,M1-matched]
     body {reference_preset_id,section_length_m,areas_m2,physical_clock_hz}
     boundary {termination,source_boundary=ideal-prescribed-volume-flow}
     measurement {N,dt_s,df_hz, ports, observer=mouth-port-not-listener}
     transfer_points[] {target_hz,actual_hz,bin, HpU_real,HpU_imag,
                        Zin_real,Zin_imag,HU_real,HU_imag}
     diagnostic {H600_to_H100_db, no_normative_voice_threshold}
     validation {energy,amplitude_linearity,analytic_match_status}
  limitations [no acoustic source coupling,no walls,no ear pressure,
               no physical audio quality,finite-window FFT/no Q]
```

The volume integral is explicitly `1e-13 m³`. Frequency-domain pressure/flow transfer has SI impedance units Pa·s/m³, outlet/inlet volume flow transfer is dimensionless. `mouth` denotes waveguide **boundary port** and is NOT a radiated microphone reading. The pressure arrays are *physical simulator output*; no WAV normalization or filters.

Experiment-028 [frozen_reference.json](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/028_task_field_morphology_transfer/frozen_reference.json) owns audited section areas, and its full Git blob SHA identifies research inputs. A derived geometry SHA-256 hashes canonical SI values, enabling replay independently of project/UI IDs. `M0/M1` are **historical body labels**, not associated with user-local Take UUIDs.

Only `research.drawer` may eventually render a signed/traceable `ValidationReceipt`, after its own Studio contract review. No transfer spectrum becomes a new Character editable parameter or voice quality score.
