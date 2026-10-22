# CC-B1 Gate A/B — immutable-evidence review packet (2026-10-22)

> **AUDIT HANDOFF / NOT A SCIENTIFIC APPROVAL / NO MAIN MERGE.** This review packet is created in a **separate archival branch** from B evidence HEAD; it does not change PR #149 or #150, physical code, thresholds, solver, or waveform results. Treat references below as exact verified commit identifiers, not floating branch names.

## Status and permitted claim

- Gate A: `FROZEN_INTERNAL` — prespecified procedural freeze established; **independent science approval pending**.
- Gate B: `RESEARCH_MACHINE_PASS_PENDING_INDEPENDENT_AUDIT` — machine outcomes passed on the exact evidence HEAD; **science HOLD**.
- Gate C (BodyRevision, PR #145): `PROTOTYPE/HOLD`; NO production API, Studio deployment, user-facing claim or main merge.
- **Proposed reviewer disposition:** `GO_LIMITED_1D`, `REVISE`, `MORE_DATA` or `REJECT`; no decision may be inferred from CI alone.

**Maximum allowable limited-science statement** (subject to independent acceptance):
> Given the same prescribed LF source and fixed three-task program, changing the static rest area of zero-based section 8 by ±10% in the inherited 16×10 mm serial 1D computational vocal-tract model produces reproducible nonzero simulated 0.5-second acoustic pressure differences, while 18 pre-specified snapshot peak comparisons against the frozen 5 Hz-grid ideal-tube oracle satisfy the predeclared engineering tolerance.

Do **not** infer accurate human anatomy, natural or intelligible voice, perceptual distinguishability, individual speaker identity, validated FSI, time-varying passivity, production-ready morphology APIs or Studio Takes.

## Exact review anchors / chronology

| Item | Exact identity |
|---|---|
| Gate A pre-run protocol (Draft PR [#149](https://github.com/ryonakayama234/morphoacoustics/pull/149)) | `ca8bf64c8525a9cf59cb1332c4819763a0f9197e` |
| Frozen Gate A oracle JSON blob | `046a26a7baf31003244e05088a2b5d19bc7af416` |
| Final Gate B trial and audit hardening (Draft PR [#150](https://github.com/ryonakayama234/morphoacoustics/pull/150)) | `b6aa1bed340cbd81d90b46bf16639b3fa47a3bb6` |
| Exact-head physical CI | [run #39702992138](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39702992138) — SUCCESS |
| Artifact | [#12392884715](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39702992138/artifacts/12392884715), 4 raw Pa NPY, 3 shared-gain WAV, decision JSON |
| GitHub artifact ZIP SHA-256 | `f456e39f0b2f7f1df534df6356350d9371b5c0c81e39d5e8e55323bb9f7ae881` |
| Artifact current expiration | **2027-01-20T00:59:15Z** — ZIP MUST be copied to durable independent storage before expiry, otherwise reproducible raw byte evidence may disappear from Actions |
| Ancillary exact-head CI | tests #39702992251, SV1 #39702992172, OG3 #39702992210, OG4 #39702992225 — all SUCCESS |
| Review source | [independent numerical/contract audit comment](https://github.com/ryonakayama234/morphoacoustics/pull/150#issuecomment-6330106535) |
| Research provenance | Python 3.11.17, NumPy 2.4.6, Linux-6.17.0-1022-azure-x86_64-with-glibc2.39 |

**Prespecification:** site8 was in an earlier theoretical 16-site sensitivity scan, therefore NOT a theory-blind site selection. It was new only relative to previous Core waveform interventions at sites0/2/4. Freeze predates the new Core site8 physical waveform experiment. Do not retrospectively edit the Gate A file/oracle or adjust 7.5 Hz and 1e-8 after seeing outputs.

## Computation and interpretation

- Baseline: 16 serial sections × 0.010 m, source fixed, sample rate 48000 Hz × 24000 samples per trial, 102 actual acoustic transfer calls/trial, 3 ratios (0.90/1.00/1.10) plus one fresh baseline replay.
- Independent Wolfram computations reproduce the **frozen** first-three peak triplets at rest and task terminal states using ABCD input-impedance `|B/D|` and backward impedance recurrence (both within **the same ideal pressure-release, lossless 1D model**). This is an independent *implementation agreement*, not independent real-world validation.
- Frozen reference peaks:

| Area ratio | Ideal rest Hz | Ideal terminal Hz |
|---|---|---|
| 0.90 | 720, 1295, 2905 | 275, 2110, 3145 |
| 1.00 | 720, 1290, 2915 | 275, 2100, 3160 |
| 1.10 | 715, 1285, 2925 | 275, 2095, 3175 |

- Observed Core numbers, with max absolute rest / terminal frequency error relative to frozen 5 Hz grid:

| Ratio | Core rest peaks Hz | Core terminal peaks Hz | Max abs error rest / terminal Hz | Raw relative L2 vs 1.00 |
|---|---|---|---:|---:|
| 0.90 | 721.5, 1291.5, 2906.75 | 275.25, 2109, 3149 | 3.50 / 4.00 | 0.0138112613473 |
| 1.00 | 720.25, 1288.5, 2918.25 | 275, 2101.75, 3164.75 | 3.25 / 4.75 | 0.00000000000 |
| 1.10 | 718.5, 1285.5, 2925.5 | 274.5, 2094.25, 3177.25 | 3.50 / 2.25 | 0.0149144252304 |

- All **18/18** prespecified peak errors ≤ 7.5 Hz (maximum 4.75 Hz). Both edited pressure outputs exceed predeclared relative L2 > 1e-8; null is 0.0. Quantized baseline replay matches the inherited frozen checksum. No cross-platform float64 byte identity is claimed.
- **Different transfer observables and physics approximations:** Frozen Wolfram reference uses lossless rigid 1D pipe, pressure-release `Z_L=0`, density 1.2 kg/m³, input impedance maxima; Core inherited Exp009 uses fixed attenuation 0.4 Np/m, a terminal resistive load `Z_L=0.05 Z_c`, density 1.21 kg/m³ and outlet volume-velocity-transfer maxima; pressure output is further approximated by a monopole observer model. The agreement is **cross-model numerical resonance proximity** under a predeclared engineering discrepancy bound, **not** equivalence of transfer functions or a calibrated uncertainty band.
- Conventional transfer-matrix expressions: `Z_in=(A Z_L+B)/(C Z_L+D)` vs `U_out/U_in=1/(C Z_L+D)`. Shared denominator under ideal assumptions does not establish identical observables or identical boundaries.

## Digests / machine receipts

- Source f64 per-run SHA256: `4d075fd89958ff481507661ea43e4602ed5fe72b0104bc897685b1f696abf529`; source ID `lf_fixed`.
- Task-plan canonical SHA256: `17148dea27e59abfb626b149beebcc7893d4ff9ba04ce4cf3af9ad408ce8a7bf`; frozen same canonical SHA recorded and re-checked.
- Baseline quantized checksum: `dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e`.
- Per-condition quantized SHA256:
  - 0.90: `a5f34b795b886f67f88716be53ebf50dd68731e5b4bd03f2c189a1a17a752aa1`
  - 1.00: `dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e`
  - 1.10: `9f359add71f68ce66a2306d7b5dd66a658b3676d54f66369269eadc71c2c8db6`
- **Actual archived file byte hashes** from `decision.json` (checked against GitHub artifact when downloaded):

| Original artifact file | SHA-256 |
|---|---|
| `pressure_0.90.npy` | `a363336cd30cedda51420dc4843d162a40bddca31ce4f3b6f8d473f22bc6487a` |
| `pressure_1.00.npy` | `b2a4ba9432ddb4397139e238b404af6a43baed27de5a44d9214b43852ba3971c` |
| `pressure_1.10.npy` | `14ccfbdc3e2885b97668dbed37c257c3bf61b224db3997cc3210e619fa58aabd` |
| `pressure_repeat_1.00.npy` | `b2a4ba9432ddb4397139e238b404af6a43baed27de5a44d9214b43852ba3971c` |
| `preview_0.90.wav` | `e04bfd93985480ec3182312abed5f49fae0774d556e8309005731034854b51c3` |
| `preview_1.00.wav` | `453535ce81d517f8d936a0aa0717e81fca3a3b543f440569beb5ffae9dd67f80` |
| `preview_1.10.wav` | `c1bc2be2e77624464b98667c8ebac497cf61abb418798bffae50f8b506a66d36` |

- A copy of machine receipt JSON is retained alongside this packet in `gate_b_site08_evidence_b6aa1bed.json`, for post-expiry numeric/provenance auditing. That copy is semantically reconstructed from CI logs; the original `decision.json` remains in the artifact ZIP and should be preferred for byte-level audits.

## Negative controls and explicitly retained exception

Eight **synthetic acceptance-boundary** fault-injection controls in Gate B runner:

| Fault/control | Outcome | What is actually tested |
|---|---|---|
| `unsupported_site` | PASS | synthetic acceptance boundary |
| `unsupported_ratio` | PASS | synthetic acceptance boundary |
| `source_mutation` | PASS | synthetic acceptance boundary |
| `task_digest_mutation` | PASS | synthetic acceptance boundary |
| `swapped_revision_ratio` | PASS | synthetic acceptance boundary |
| `unexpected_fallback_result` | PASS | synthetic acceptance boundary |
| `nonfinite_solver_pressure` | PASS | synthetic acceptance boundary |
| `nonfinite_peak` | PASS | synthetic acceptance boundary |
| `inherited_solver_internal_fault_injection` | **NOT_TESTED** | Frozen upstream solver internals not fault-injected |

These synthetic controls do not prove coverage of every possible internal failure. Reviewer must choose (a) `MORE_DATA` / additional internal fault injection as an actual blocker or (b) an explicit risk-accepted **exception to frozen negative-control coverage** restricted to `GO_LIMITED_1D`, without ever reporting the skipped case as PASS. Waiver rationale, residual risk, owner and requirements before any product promotion must be written down.

## Required independent review / sign-off

A separate accountable reviewer qualified to assess numerical acoustics and API/contract boundaries must document:
1. Independent identity / competence, audit scope and reviewed exact SHAs. Same-author GitHub comments and automated code review do NOT suffice for independent physical acceptance.
2. The chosen interpretation and limits of the 7.5 Hz engineering tolerance, what oracle-model disagreement remains, fixed LF/task/source trust, initialization and reproducibility, and whether numerical conditioning/stability warrant further data.
3. Explicit `NOT_TESTED` handling: require test now, or waive narrowly with rationale, assigned residual-risk owner, and later trigger to close the gap.
4. One of `GO_LIMITED_1D / REVISE / MORE_DATA / REJECT`, signed reasoning linked to this packet, PRs #149/#150, exact CI and artifact.
5. Even `GO_LIMITED_1D` is **research-only**: it does not authorize Gate C API or Studio or main merge.

No new physical experiment or threshold revision is mandated **merely** by preparing this review packet. If reviewer requests new criteria, version protocol and run new confirmatory study without overwriting original frozen evidence.
