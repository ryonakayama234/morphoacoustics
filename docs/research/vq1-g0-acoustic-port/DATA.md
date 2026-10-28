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


## Actual numerical data at tested commit (append-only, 2026-10-28 JST)
Source/test SHA `ad967d5b978097a40ab8393704ae59e8ef5f96ae`; dedicated CI [run 40686704409](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40686704409), artifact `vq1-g0-acoustic-port-evidence` id `12814748143`. Research evidence was **read from the uploaded JSON** (not predicted). Four 128-tick fixtures with signed SI observations, not authentic character IDs:

| Fixture | Native Hz | Nonzero-b ticks | max scaled pressure error | max scaled total energy error | max |energy residual| J |
|---|---:|---:|---:|---:|---:|
| single matched (seeded b=0.25 Pa) | 68600 | 1 | 0 | 3.258565479983608e-16 | 4.8467614016778965e-27 |
| two-section B0 (unequal area) | 68600 | 124 | 0 | 6.119036269618344e-14 | 1.2924697071141057e-25 |
| M0 16-section **surrogate** closed | 68600 | 64 | 0 | 1.0339757656912846e-13 | 1.0339757656912846e-25 |
| M1 16-section **surrogate** pressure_release | 62363.63636363637 | 64 | 0 | 1.0339757656912846e-13 | 1.0339757656912846e-25 |

These are the recorded maxima for these chosen fixtures, not independent wall-pressure measurements. Explicit matching of algebraic source pressure is *not* an external physiological validation. All numeric result categories remain research-only, with no inferred voice-like sound.
