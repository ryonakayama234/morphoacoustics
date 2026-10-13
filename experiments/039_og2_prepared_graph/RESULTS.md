# Experiment 039 — results and gate status

## Current status (2026-10-13)

- **Research implementation** under isolated branch; independent solver, numerical-acoustics and code/API human review **PENDING**.
- Independent Wolfram table frozen before OG-2 Python code; 7 full complex frequency-domain 2-port reference matrices plus exact ideal discontinuity power fractions.
- Local algebra exploratory check supported expected mismatch `r=-1/3`, `t=2/3`, `R=1/9`, `T=8/9`; this is **not** evidence of a validated Python implementation.
- `AMENDMENT_001.md` openly discloses dimensional normalization correction after first implementation. Existing values/limits not fit to data.
- Numerical gate and Python 3.11/3.12/3.13 remote CI have **not yet been verified in this document**. Inspect attached fresh run outputs/PR checks for results; do not infer passing from intended tests.
- **GO/NO-GO for adoption: PENDING**. Even if all CI passes, production API and Studio changes are out of scope.

## Independent reviewers must verify

1. Sign of p/U wave convention, true volume-flow continuity, the `S T S^-1` scaling, and isolated matched-junction versus pressure-release interpretation.
2. Oracle file provenance relative to Python and the disclosed amendment.
3. False particle-velocity and reversed-order mutations die for physically meaningful reasons.
4. Graph topology validation and INVALID/UNSUPPORTED taxonomy, unchanged original modules, stable backend preparation digest and unchanged `src/`.
5. Exact CI SHA, source/evidence artifact checksums, test/mypy execution across Python versions, plus reproducibility.


## Self-audit and correction record

The first green head `2ff80c25` passed the expected full test/CI outcomes, but its research **runner's negative-control error magnitudes were invalid** due to a second uncorrected scaling operation in the two intentionally false matrices. The standalone pytest negative-control matrices were already normalized correctly. Runner correction is commit `b2732946`; final numerical evidence must be taken only from a later commit containing this correction. Full details in `AMENDMENT_001.md`. This transparent repair does not count as blind prospective replication.


## Corrected quantitative execution — pinned code `b27329464ee46d3e2c8803790ee09894f2d2af80`

CI [OG-2 scientific run 38407003941](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38407003941) passed **Python 3.11, 3.12, 3.13** independently, including experiment tests, full regressions, production mypy, runner numerical gates, refusal to reuse stale output, and artifact upload. Generic [tests run 38407004608](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38407004608) also passed for that code commit.

Observed Python 3.12 raw metrics (all satisfy locked thresholds; output value depends on machine-precision rounding):

| Gate | Measured | Frozen requirement |
|---|---:|---:|
| Equal-area 2-tube versus one-tube scaled full matrix max error | `1.1102230246251565e-16` | <= `1e-10` |
| Different-area full 7-frequency complex Wolfram oracle max error | `1.915134717478395e-15` | <= `1e-10` |
| Matched isolated interface pressure/power error | `2.220446049250313e-16` | <= `1e-12` |
| Wrong particle-velocity continuity, scaled oracle discrepancy | `0.9019457527234934` | > `1e-3` (and post-hoc sanity bound < 10) |
| Incorrect swapped tube order, scaled oracle discrepancy | `1.3529186290852406` | > `1e-3` (and post-hoc sanity bound < 10) |

Wolfram Language **independently** recomputed the mutation discrepancies as `0.901945752723493589...` and `1.352918629085240383...`; these agree with corrected Python errors. This cross-check is an independent numerical execution, not an independent human scientific peer review.

**Automated verdict: PROVISIONAL_NUMERICAL_PASS / REVIEW_PENDING / NOT_ADOPTED.**

Further documentation-only commits after `b2732946` require their **own current head CI checks** before interpreting this as verification for the new PR head. Independent physics and code/API reviewers remain pending. Experimental adoption and production promotion remain blocked as documented in #93/#94/#96.
