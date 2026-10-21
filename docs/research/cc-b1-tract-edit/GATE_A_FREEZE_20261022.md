# CC-B1 Gate A — prospective Core-run protocol freeze (2026-10-22)

**State:** `FROZEN_FOR_NEW_CORE_RUN / INDEPENDENT_RATIFICATION_PENDING`. This is an **internal procedural freeze**, NOT an externally approved scientific Gate A and NOT a claim of a blinded holdout. Once this file and oracle commit are committed, DO NOT edit primary conditions, endpoints, decision thresholds or oracles after seeing Gate B measurements. Changing a criterion requires a NEW dated protocol and NEW confirmatory run; preserve this record.

## Research question and separation of claims
Under an *unchanged* audited Experiment029/028/027 source, task, realization, acoustic backend, frequency grid and output pipeline, does a **single rest-area** intervention yield independently predicted pressure-impedance resonances and a reproducibly distinct raw 0.5s physical pressure trace? Only **physical numerical evidence** is in scope. Audibility, voice naturalness, Studio use, radiation SPL, 3D organ topology, FSI, gender/voice character are OUT OF SCOPE.

## Prespecified conditions (read before implementation)
- Base: `EXP26.EXP23.primary_geometry("a")`, exact 16 serial sections × `0.010 m`, glottis→lips, pressure-release outlet; adopted Core package and `tools/cc_a2_live.py` as loaded from the **exact new experimental commit**. Do not modify existing solver or adopted package.
- **Site:** zero-based **8** (ninth section, approximately central). Chosen a priori *for mid-tract coverage*, NOT because it maximizes previous sensitivity. Earlier Wolfram full-16-site POST-HOC scan already included site8, thus ideal-model predictions are **not unseen**. Site8 was **not** used in earlier Core physical pilot sites 0,2,4. This is a prospective NEW Core pressure-run relative to those Core experiments, NOT a statistically independent blind anatomical discovery.
- **Arms:** rest area ratio `0.90 / 1.00 / 1.10`, exactly one section altered for alternatives, no-op `1.00` baseline and an independently evaluated second `1.00` rerun. The other 15 cells must be bit-identical. No source, motor task, oral reach, solver or gain edits.
- Sample rate `48000 Hz`, samples `24000` (0.5s), 102 acoustic calls per evaluation, existing LF source `frozen.SOURCE_ID`, existing `exp.task_plan_payload()`, existing NumPy exact audited version. Source and plan digests recorded per trial. Model has no stochastic RNG in this path; absence of random seed is explicit.
- Same-body rerun: `quantized_waveform_sha256` must agree with baseline and with adopted `AUDITED_QUANTIZED_WAVEFORM_SHA256`, while *unquantized f64 SHA is recorded* and exact f64 cross-platform identity is **not** required because SIMD differences were already documented.
- Temporal invariance: at t={0.0,0.20,0.35,0.50}s same frozen task field, every section-area ratio vs baseline must equal unity except section8 with the specified ratio, within rtol=2e-12, atol=2e-12.
- Boundaries: reject unsupported site, ratio, NaN/Inf, no-op-as-new-revision, malformed section count or length, mutated source, corrupted task/digest and nonfinite pressure. No failure may silently emit a success receipt.

## Precomputed independent ideal-acoustics oracle (BEFORE new Core waveform evaluation)
See `gate_a_site08_oracle.wl` + `gate_a_site08_oracle.json`. Two separately coded methods: 2×2 ABCD transfer-matrix multiplication and lip→glottis impedance recurrence, `Z_out=0`, `z=ρc/A`, `ρ=1.2 kg/m³`, `c=343 m/s`, 16×10mm rigid lossless sections; ideal pressure-release lip. Fixed frequency grid 100..3500 Hz in increments 5 Hz, first three local impedance maxima at rest and fixed terminal task field.

| rest area ratio | rest peaks (Hz) | terminal peaks (Hz) |
|---|---|---|
| 0.90 | 720,1295,2905 | 275,2110,3145 |
| 1.00 | 720,1290,2915 | 275,2100,3160 |
| 1.10 | 715,1285,2925 | 275,2095,3175 |

Each of the three **Core 0.25Hz-resolution peak** differences from the frozen oracle must be ≤ **7.5 Hz** for rest AND terminal state (six observations per condition); this threshold is a preexisting exploratory engineering discrepancy bound, **not** a calibrated statistical or physiological uncertainty interval. The two independently written Wolfram algorithms agree to the displayed 5Hz grid. A lossless transfer-matrix determinant near 1 is a numerical sanity check, NOT an energy/passivity claim for the driven time-varying system.

## Prespecified outcomes and refutation
1. Objective ORACLE_MATCH if all 18 corresponding Core peak absolute errors ≤ 7.5Hz.
2. Objective CAUSAL_CHANGE if each edit yields a finite 24k Pa array, acoustic_call_count=102, valid shape, **raw relative L2 vs exact baseline > 1e-8**, unchanged source/task, and the intervention survives time-varying realization. A difference smaller than threshold is `NUMERICALLY_UNRESOLVED`, not a physical success.
3. NULL_MATCH only if second baseline run and original baseline pass adopted quantized M0 checksum. A mismatched replay is `FAILED`.
4. Reject deliberately invalid edits BEFORE any complete physical result; preserve negative-test receipts. Unchecked negative groups remain `NOT_TESTED`, never passed implicitly.
5. Overall `RESEARCH_MACHINE_PASS_PENDING_AUDIT` only if all prespecified machine checks succeed. `GATE_B_SCIENTIFICALLY_RATIFIED` requires **separate independent physics/contract review after** the new Core data, not just author and CI. Fail closed on missing oracle, version mismatch, source drift, bad physical data or incorrect output artifact.

## Evidence, review, decision
New reproducible output on GitHub Actions must include three raw SI Pa .npy arrays, two independent baseline runs (second may be archived as fourth), common-gain mono PCM16 previews for 3 arms, `decision.json` with SHA256 of source, tasks, bytes, exact code SHA, solver+NumPy versions, numeric results, refusal controls, and CI run URL. `allow_pickle=False`; never overwrite evidence. Archive even failure when safe. Experimental code/test/Action + synchronized SYSTEM/DATA/EXPERIMENT/INDEX records must be in one B PR. Require another reviewer for scientific validity; do not promote to main or Core stable API on self-evaluation alone.

## Important pre-known limitations
Baseline and LF source are adapted from historical Exp029 with simple time-dependent prescribed log-area gesture and **no anatomical FSI**. Previous 16-section theoretical scan included every site, so this is *not* a virgin theoretical holdout. A 5Hz static ideal-tube oracle validates only restricted acoustic resonance snapshots. The waveform difference is NOT evidence of audible character identity or natural voice. Human ABX must be separately preregistered.
