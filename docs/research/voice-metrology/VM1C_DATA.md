# VM-1C exact evidence schema and physical dimensions

**Research-only measurement report, not the permanent OrganGraph or port ABI.**

```text
VM1CReport:
  schema="voice-metrology/sa2a-vs-b0/vm1c"
  result/research_quality/physical_quality/creator_quality
  exact_sa2a_blob_sha1, exact_exp028_blob_sha1
  executed_checkout_git_sha, source_sha256_map
  air: rho [kg/m3], c [m/s]
  aperture_control: {r_m, f_hz, ka, Zc [Pa s/m3],
     ideal_piston {Re,Im}, B0_continuous {Re,Im}, B0_discrete {Re,Im},
     model_rel_complex_error, native_discretization_rel_complex_error,
     normalized_R_X, phase_rad, passivity}
  body_frequency: {M0|M1, 16 actual areas, same r=0.016m,
     frequency, ka, terminal law, HpU[Pa s/m3], HU[1], Zin[Pa s/m3],
     PortPowerAtInlet[W],PortPowerAtMouth[W],energy relative error,
     source_flow_m3_s}
  selectivity: {body, boundary_law, H_600_div_H_100_db,
                comparison_to_ideal_piston_db}
  negative_control: invalid frequency/radius, out-of-domain ka,
                    corrupted sha or erroneous law
  limitations: no radiated receiver sound, no self-oscillating phonator,
               no real mouth geometry, no model/voice/product adoption
```

Stored complex phasors have real and imaginary numeric parts, not just dB spectra. H600/H100 is a *port transfer diagnostic under equal ideal input flow*, not relative energy of an LF-glottal harmonic train and cannot be equated to an actual microphone waveform.

Source references: original SA-2A [unmerged](https://github.com/ryonakayama234/morphoacoustics/pull/172) and authentic Exp028 [immutable blob](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/028_task_field_morphology_transfer/frozen_reference.json). Exact source/tree/CI identities are recorded separately from historical main base.
