# Research index — Core physical capabilities and hypotheses

**Causal owner:** `morphoacoustics` decides physical laws and what may be simulated. `morphoacoustics-studio` owns creative editing, request orchestration, audition and immutable Takes. Research branches/Draft PRs are not necessarily adopted.

## Organ graph and creative link
- [Living organ-graph architecture](./organ-graph-program.md) — nodes, typed ports, junctions, physical law, preparation, source and observation boundaries.
- [Organ-graph work orders](./organ-graph-execution-plan.md) — stage/Gate dependencies and older execution receipts.
- [Organ-graph data candidates](./organ-graph-data-candidate.md) — semantic Blueprint vs prepared graph vs physical state.
- [Organ-graph evidence ledger](./organ-graph-experiment-ledger.md) — old OG-0/1/2 graph science records.
- [OG-4 adopted bounded 3-port contract](./og4-branch3-api-v1.md) — 8 verified frequency anchors; *not* general audio synthesis.
- [OG-5 accepted design/spec](./og5-gate-a-acceptance.md) — 5 tubes/2 junctions; separate implementation [Draft PR #112](https://github.com/ryonakayama234/morphoacoustics/pull/112) not yet merged.
- **[OG-AUD1 proposed E2E audible organ graph](./og-aud1/SYSTEM.md)** — [DATA](./og-aud1/DATA.md) / [EXPERIMENT+decision ledger](./og-aud1/EXPERIMENT.md). **Gate A candidate only; no runtime audio yet.** Core [#130](https://github.com/ryonakayama234/morphoacoustics/issues/130) ↔ Studio [#20](https://github.com/ryonakayama234/morphoacoustics-studio/issues/20).

## Other independent research
- [CC-A2 adopted two-body live](./cc-a2-two-body-live.md) — fresh two fixed-body serial-tract Takes, not branching graph audio.
- [NR-1 nasal-routing research directory](./nasal-routing-nr1/) — static terminal loads vs true velopharyngeal gate; do not claim accepted articulatory motion.
- [MotorSkill / MotorPersona hypotheses](./motor-skill-persona-hypotheses-v0.md) — voice individuality through habitual motor control, not accepted backend.
- [Neural causal boundary](./neural-causal-boundary.md) — physical causality not bypassed by a voice model.

Every implemented work package must update physical SYSTEM, exact DATA contract and EXPERIMENT/evidence record together. Separate exploratory results from frozen tests, numeric gates from listening gates, and public adopted APIs from draft research.

### OG-AUD1 / physical graph → audible source-port monitor (2026-10-20, draft)

- [Core SYSTEM](./og-aud1/SYSTEM.md) · [DATA](./og-aud1/DATA.md) · [EXPERIMENT](./og-aud1/EXPERIMENT.md) — all **Gate A candidate**, unadopted.
- [Focused physical audit](./og-aud1/GATE_A_REVIEW.md) — matched-branch length null, 3-port law, shared A/B gain, no radiated-mouth claim.
- [Experiment 043 executable Wolfram global 12-state preflight](../../experiments/043_og_aud1_preflight/README.md) · [results](../../experiments/043_og_aud1_preflight/RESULTS.md) — **exploratory executed**; no broadband solver, audio or preregistered science pass.
- [Studio creator handoff](https://github.com/ryonakayama234/morphoacoustics-studio/blob/docs/og-aud1-creator-handoff-20261020/docs/og-aud1-creator-handoff.md) — read-only 3-organ visualization and future immutable A/B Takes; no implemented Studio bridge yet.

### OG-AUD1 Experiment 044 (2026-10-20, runnable research, not adopted)

- [Prospective but **unreviewed** numerical/source candidate](../../experiments/044_og_aud1_monitor/PROTOCOL_CANDIDATE.md).
- [Runnable experiment-local Core code and data flow](../../experiments/044_og_aud1_monitor/README.md), [local results and sample hashes](../../experiments/044_og_aud1_monitor/RESULTS.md), [off-anchor full-matrix Wolfram script](../../experiments/044_og_aud1_monitor/oracle_fft_bins.wl). **Two 48kHz preview pressure-monitor WAVs were computed, not speech or adopted Core broadband output.**
- Parent [SYSTEM](./og-aud1/SYSTEM.md) / [DATA](./og-aud1/DATA.md) / [EXPERIMENT](./og-aud1/EXPERIMENT.md) updated together. Gate A acceptance/reviewer, confirmatory Gate B, Studio adapter and creator audition still outstanding.


### OG-AUD1 causal graph-to-monitor, Experiment 045 (research, 2026-10-20)

- [Six-port physical model, node/edge diagram, executable reproduction](../../experiments/045_og_aud1_causal_monitor/README.md)
- [Causal experiment code](../../experiments/045_og_aud1_causal_monitor/causal_monitor.py) · [scientific/regression tests](../../experiments/045_og_aud1_causal_monitor/test_causal_monitor.py) · [Wolfram oracle](../../experiments/045_og_aud1_causal_monitor/oracle_echo.wl) · [exploratory result and limitations](../../experiments/045_og_aud1_causal_monitor/RESULTS.md)
- Canonical triad: [SYSTEM](og-aud1/SYSTEM.md) / [DATA](og-aud1/DATA.md) / [EXPERIMENT](og-aud1/EXPERIMENT.md). This independent stacked Draft branch does **not** authorize public API, Studio actor/Takes, radiation, or confirmatory adoption.
