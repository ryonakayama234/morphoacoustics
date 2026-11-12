# BODYMAP B2 passive-loss — isolated Core research implementation

**State:** IMPLEMENTATION GO 2026-11-12; **NOT ACCEPTED / REGISTERED_NOT_RUN / EXPERIMENT_GO_PENDING**.
Authoritative frozen [Studio registration](https://github.com/ryonakayama234/morphoacoustics-studio/blob/2f7d9546cc888ca43e54a20cf04d3708c95c416f/docs/product/body-map-g2-response-20261112.md) SHA-256 \`9a022469264b4789c2d677d163470c4f7f393451635b264920463e6d70d3e41e\`; approved [Core plan #293](https://github.com/ryonakayama234/morphoacoustics/pull/293), head \`f63b4bf933df4e351f25a8565c463f2f3e81b29f\`.

This directory is **not** imported by Fidelity 0, Studio or any production adapter. Its only legal input authority for M0 and LF is the original audited Core chain. Uniform U6/U19 are mathematical references, not BodyRevisions. No interpolation with historical 0.4 Np/m attenuation.

## Unchanging physical contract

Static no-slip/isothermal rigid-wall, serial circular 1-D LRF; phasor exp(+jwt), oriented **volume** flow U, z/y interpolation, positive dissipation, fixed R=0.05 rho c/S_last; observed 0.20 m *uncalibrated* pressure proxy. 351 bins 100:2:800 Hz, source 48kHz/24000 f64 \`lf_fixed\`, out-of-band bins zero, 1/N inverse Fourier normalization, no preview or playback gain. The native raw output is periodic band-limited model pressure in Pa, **NOT** prior broadband raw or dB SPL.

## Boundary and stop rules

- This Draft's candidate code and candidate-side diagnostics **are not independent reviewer adjudication**.
- A dedicated Python 3.11 full hash-locked NumPy 2.4.6 / SciPy / mpmath environment and separate reviewer oracle/independent commit+SHA must be frozen **before** engineering fixtures. No pin guess, no opportunistic install, no study cases.
- Supervisor's independent recalculation of chosen grid points is additionally required.
- Eight engineering full grids only, at most one M0-null separate-process repeat; nine typed fault families at most twice each. All are \`engineering_only\`. Missing FZ evidence is UNRESOLVED, not PASS.
- Local ≤20 min, oracle ≤12 min/batch, B2 CI 2×45 min, inherited CI ≤75 runner-min, ≤6 person-days and ≤2 corrective revisions. STOP if exceeded.
- No edits under src/, contracts/, checks/, tools/, old experiments, existing tests/workflows, pyproject.toml, old requirements, or Studio.
- Frozen source Git blob OIDs, exact-head no-regression and source inventory must be evidenced separately. Empty protected diff is not enough.

The fixture manifests are intended to freeze **qualitative expectations before any B2 numerical fixture execution**. They have no numerical outputs and do not establish FZ-T1 PASS. Core source-inventory derivation requires the approved exact source, clean checkout, matching NumPy version and its existing transitive pins.

## Execution state

The initial candidate commit contains no independently attested oracle, complete lock, verified pack, mutation evidence, or exact-head acceptance. This is deliberate fail-closed staging, not a report of a completed engineering run. Never issue a Take or change \`DEFINED_NOT_VALIDATED\` G0 feature state from this project.
