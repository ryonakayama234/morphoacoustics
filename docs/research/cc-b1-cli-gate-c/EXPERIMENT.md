# EXPERIMENT — prospective CLI Gate C negative-control ledger

**Freeze status:** acceptance criteria written before coding and before fresh exact-HEAD checks. This is engineering contract testing, not a new scientific Gate B or auditory claim.

| Intervention | Expected | Recorded outcome |
|---|---|---|
| Missing/wrong protocol version | fail-closed; no physics | NOT_RUN |
| Two operations / missing operation | parser refusal | NOT_RUN |
| Duplicate nested `rest_area_ratio` or parent digest | INVALID; no output | NOT_RUN |
| NaN / Infinity / invalid UTF-8 / >4096 request bytes | INVALID; no output | NOT_RUN |
| Existing destination / symlinked request or ancestor | non-success; no Take | NOT_RUN |
| Malformed archive manifest, duplicate key, linked/missing marker | no `SUCCEEDED` | NOT_RUN |
| Exact legitimate v1 inspector and request | unchanged baseline/profile and physically fresh pair via inherited engine | NOT_RUN |
| Genuine two-ratio archive readback | exact receipts/raw Pa/WAV and original Gate B oracles | NOT_RUN |
| Core v0/v1, CC-A2, OG3/OG4/SV1, all tests | no regression (exact HEAD) | NOT_RUN |
| Filesystem symlink swap during read/write / crash/partial publish | documented residual risk | NOT_TESTED |
| Human blinded ABX, naturalness, identity and usability | future Studio Gate E | NOT_TESTED |

Independent Wolfram **simplified ideal-model sanity only** (no relation to frozen 16-section numerical acceptance):
Two equal tubes of length 0.08m with ideal pressure-release outlet, c=343m/s, first tube A1=0.0003m², second area ratio r×A1:
`f1(r)=c/(2 Pi 0.08) ArcTan[Sqrt[r]]`.
Wolfram evaluation on 2026-10-22 gives `r=.90 → 517.97191442245 Hz`; `1.00 → 535.9375 Hz`; `1.10 → 552.19071361832 Hz` and monotonic ordering. **This is not the audited Core site08 16-tube result or auditory discriminability.**

After implementation: fill the ledger with exact SHA, CI URLs, failures/repairs and regression result; independent security and science reviews must disclose reviewer relationship. No main merge on author assertion or green CI alone. Core #160 Gate C and Studio #25 D/E remain separate gates.

## Executed CI chronology — immutable source-specific observations
- **First implemented HEAD `9855d2ee7a5b82f6e56b49e05602822bfe20c1c8`, [CI #39778206417](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39778206417): FAILED**. Strict CLI including two real physical pairs **22/22 PASS**; inherited physical performer **6/6 PASS**, selected legacy regression tests completed without failure; `mypy` found one API override error: `argparse.ArgumentParser.error` now has return type `Never`. This is a real gate failure and must not be rewritten as success.
- **Repair HEAD `4cfef6532fd63e12ffca5442ce5e55ce634a46a2`** changed only the CLI parser override annotation to `NoReturn`, not numerical physics, requests or measured bytes. [Dedicated CI #39778369325](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39778369325) SUCCESS, including physical pair test, legacy cases and type checking. This is an engineering pass, NOT independent scientific or security ratification.
- **Extended evidence workflow HEAD `211eaa8c8f604609dd391379dda2a0a7f968fc61`** adds fresh command-line generation for two stored 48kHz×24000Pa physical pairs, then verifies exactly the same archive via the public CLI candidate and uploads artifact even on partial failures. Outcomes must be inspected at exact final commit; no PASS is presumed by this statement.
- **Wolfram:** `wolfram_ideal_two_tube.wl` and `wolfram_ideal_two_tube_result.json` preserve the separate ideal two-tube result. Do not apply the simple 517.97–552.19Hz model to the 16-section solver or to ABX probability.

**Remaining Gate C**: independently inspect path/storage trust against symlink swaps, on-disk canonical revision registry across restart, status-contract completeness, packaging/support and multiple commit CI exactness. **Studio Gate D and auditory Gate E have not started here.**

## Adversarial audit amendment A1 — metadata must not impersonate physics
Found by code inspection **after initial CLI code** and **before the added negative tests/repair**: inherited `verify_output_archive` validates waveform/revision but does not re-derive every asserted `source`, `task_plan_sha256`, semantic artifact kind and `provenance` field. A copy of real WAV/Pa with a falsely claimed source or Task could therefore receive an overbroad verification label.

New prospective refusal probes for the opt-in CLI layer (not retroactive Gate B): change only `source.id`, `source.sha256_le_f64`, `task_plan_sha256`, `sample_rate_hz`, `acoustic_calls_per_body`, artifact `kind`, and Gate A/B pin string while leaving all six authentic physical files and their hashes intact. Expected: **no `SUCCEEDED`**. Good untouched archives must still pass. Freeze the supported manifest field set and read it against trusted installed Core fixed source/Task; do **not** claim that an unsigned `core_checkout_sha` proves origin or that a checksum is a cryptographic signature. Tamper against signed, durable, hostile storage remains a separate `NOT_TESTED` gate.
