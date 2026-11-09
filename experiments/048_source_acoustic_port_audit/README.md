# Experiment 048 — SA-1 Source × Acoustic Port Audit

**RESEARCH ONLY / NOT_ADOPTED.** Gate A preregistered separately and earlier in [Draft PR #170](https://github.com/ryonakayama234/morphoacoustics/pull/170): [SYSTEM](../../docs/research/sa-1/SYSTEM.md), [DATA](../../docs/research/sa-1/DATA.md), [EXPERIMENT](../../docs/research/sa-1/EXPERIMENT.md).

The source reproduces the exact four **archived JET-P0 inlet** NumPy SHA-256 digests from previously failed [CI run 39951204385](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39951204385). Source shape and seed are historical hypotheses, not validated turbulence. It uses the frozen CC-A2 M0 rest tract via SV-1's strict preflight and obtains **new actual Core acoustic pressure** via unchanged Exp009/012/023; any unavailable body or source mismatch fails closed.

The analytic glottal and lip pressure/volume-flow ports are **reconstructions** of the 2×2 transfer model, not internal observed states of an FSI solver. Every frequency-domain transfer includes phase and declared units. Two separate Hann overlap-add applications are never claimed to be one physical sequential cascade.

- Independent matching uniform tube analytic reference: Z_in=Zc and U_out/U_in=exp(-jkL).
- Fixed-body zero inlet and exact linear superposition in the real Core renderer.
- Calibration flows at 200 / 1000 / 3000 Hz.
- Source, tract and observer monopole high-frequency gain budget; source-free/receiver-only diagnostics distinguished from actual acoustic pressure.
- Reproduction of original rejected JET-P0 2kHz energy ratios within 0.01 percentage point, without rewriting historical threshold or manipulating final WAVs.
- Saved raw flow m³/s, actual raw observer pressure Pa, derived lip flows and complex gain/impedance arrays, SHA256 integrity manifests and exact-head CI record (SHA256 digests attest integrity, not third-party authenticity).

Run from a prepared WSL2/Linux source checkout with Python dev dependencies:

```bash
python -m pytest -q tests/test_experiment_048_sa1.py
python experiments/048_source_acoustic_port_audit/run.py --out /tmp/sa1-fresh
```

**Gate result remains numeric-only** until exact-head CI, artifacts and retrospective audit are checked; do not call 'better voice' or 'VF-1 ready' from a successful run alone. The constant 0.05 Zc mouth load and separate monopole observer law are not a unified biological radiation impedance: this motivates a separately gated SA-2 physical-port/boundary model if all numerical checks pass.

No public Core/Studio contract changes, no production source model, no SMC or ASMR changes.