# VQ-1 G0-P DATA — local port identity, SI and evidence

Status: PRE-IMPLEMENTATION; not a public serialized schema. Pin Core main `727b11ecf103f5c087cfcb820bdec11f883e7c03`.

| Name | Unit / meaning | Source |
|---|---|---|
| native `tick` | integer, pre-shift Core session tick | `PassiveWaveguideSession.ticks` |
| `b_pa` | Pa, first pre-shift incoming backward pressure | native FIFO `backward[0][0]` |
| `z0_pa_s_m3` | Pa*s/m3, `rho*c/A0` | `PassiveWaveguideConfig` |
| `dt_s` | s, (L/(c*n_{m cells})) | Core config native clock |
| `flow_m3_s` | m3/s, signed positive **into tract** | caller chooses one candidate |
| `pressure_pa` | Pa, `2*b_pa + Z0*flow` | pure research prediction |
| `work_j` | J, `dt*pressure*flow` | pure research prediction; compared to actual Core work |
| `owner_token` | process-local adapter identity, not global id | prevents cross-instance replay |
| `state_digest` | SHA-256 of exact native tick, wave state, outlet B0 q, config repr | detects out-of-band changes, not scientific validity |
| `WaveguideStep` | Core's actual observed tick/flow/pressure/work/energy | existing `step`, never simulated receipt |

Local immutable `PortSnapshot` includes tick, digest, owner identity, inlet b, Z0, dt. `PortPrediction` includes snapshot, signed flow, predicted inlet pressure and work. User-facing Studio/Character/Performance schemas and existing Takes do not change.

The adapter is restricted to one validated **fixed** 1D `PassiveWaveguideSession`; input flow must be finite real and not bool. For a large finite input that causes Core overflow, Core step fails before mutating; the adapter does NOT falsely label it a physical result. Outside this backend, return unsupported; do not convert native clocks or create a new graph edge.

Evidence to retain per case: scenario id, source/head SHA, geometry and termination, native h, tick, nonzero/zero b, chosen U, predicted and actual p/U/W, duct + radiation energies, outlet dissipated energy, signed residual; no hidden waveform normalizer or source F0. For failures retain error type, state digest before/after, refusal meaning.

No anatomical/material calibration, measured wall p(z), audience SPL or WAV is available in this study.
