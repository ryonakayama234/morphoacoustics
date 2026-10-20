# EXPERIMENT — adoption gate plan, independent falsification, decision rules

**Research plan drafted after seeing Experiment043/044/045 exploratory outcomes. NOT already-accepted preregistration.** New unseen confirmatory conditions and tolerances require independent approval before new implementation/measurements. Register all deviations in a chronological ledger.

## H0 / H1 and confounds

H0: raw p(A.in,t) body differences arise from source, scaling, FFT filter, reference-plane or equation/oracle errors; source/flow/power conservation or causal response fails under disjoint tests. H1 (scoped): identical prescribed U(t), all A/B/J/medium/loads fixed and only C area changed yields a repeatable physically consistent p(A.in,t) difference for exactly two validated matched-load bodies. Equal distal matched-load branch-length changes are a **null** for source pressure; the visual diagram must never imply length creates new source-port coloration here.

## Proposed scientific acceptance grid — TO FREEZE AT GATE A (not retrospective thresholds)

| Test | Candidate acceptance (prospectively review) |
|---|---|
| Wolfram oracle independence | 12×12 global complex pressure/volume-flow equations assembled separately from Python scalar formula, including all six endpoints. Verify a newly reserved holdout grid (not the 16 frequencies/body combinations already seen); all-port normalized rel error ≤1e-10 |
| Junction law | Complex p continuity and oriented U conservation normalized to characteristic p/U scale ≤1e-10; prove active wrong-particle-law, swapped sign, wrong impedance, swapped reference-plane variants are detected |
| Passive power | All tested f with Re(Zin)>0 and end-port mean power balance relative ≤1e-8; time-integrated incident/exit work with sufficient entire response record relative ≤1e-8 |
| Causality / convergence | Pressure exactly zero before prescribed source onset for causal source, analytic omitted-echo upper bound ≤1e-10 Pa; independently compare 48 vs at least 64 reflections and record peak/energy difference |
| Sampling/range | Explicit finite-time source, FFT/alias evaluation even with causal solution, supported band declaration and quantified high-band source fraction (<1e-8 proposed); expose any unsupported source or rate, no extrapolation of OG-4's 8 anchors |
| Morphology causal A/B | C area .00015 versus .00060m² is sole physical delta. Same exact U(t) byte hash; different raw p hash; relative raw pressure RMS difference >1e-3; matched B/C length perturbation **null**; no per-take normalization in causal A/B |
| Integrity/refusals | Unknown body/port/load/law, non-finite source, wrong source plane, corrupt hash, symlink/path escape, stale Core pin, artifact mismatch, partial pair failure => no successful playable Take, no silent fallback |
| Reproduction | SHA-bound Python 3.11/3.13 CI and independent run; exact re-run byte equality in one declared execution environment. Cross-platform numeric tolerance specified separately: do NOT promise cross-architecture identical floating bytes |

Reviewer signs thresholds **before** inspecting freshly reserved Gate B results. Each failure produces a dated append-only exception/amendment and, if acceptance changes, a new reserved test set.

## Evidence roles and gates

- **Gate A physics specification reviewer (not author):** sign H0/H1, physical units, network law, source/monitor planes, oracle + fault mutations, fixed holdout list and numerical scale policy. Wolfram machine is a calculator, not signatory.
- **Gate B independent numerical reviewer + software auditor:** run a separate 12-state Wolfram solver, verify source/ports/energy and exact-head Python 3.11/3.13, wrong-law mutant kills, archive raw evidence/hash; preserve failure records. No conditional tuning to known success.
- **Gate C security/interface reviewer:** separate pinned Core capability and Studio verifier; manipulated/invalid input, storage path, symlink, checksum, resource budget, exact module/body SHA and rejection. Browser tests must exercise actual new computation, not mocks; preserve CC-A2, X2a and v0/v1 contracts.
- **Gate D creator/evaluator:** perform fresh A/B one-shot headphone audition, write distinguishability / tonal & loudness difference / editor usefulness as **three separate questions**, record optional preference but not necessary; preserve immutable take reopen after full restart. A pilot of N=1 is qualitative, never scientific validation.
- **Decision owner:** sign exactly \`GO_LIMITED_CORE\`, \`GO_LIMITED_E2E\`, \`HOLD\`, or \`REJECT\`, with permissible claims and excluded cases, exact code/data/CI hashes, reviewer roles and residual risks. No auto-merge.

## Known unclosed blockers

- Experiment045 research runner is not a new canonical Core API nor fully prepared/verifiable branch3 body receipt; no Studio accepted Take exists.
- Current tests largely assert self-consistency of internally shared J variables; newly reserved independent full-port oracle + mutation tests required.
- Full E2E fresh core-to-studio perform→listen→persist→reload/restart and human usefulness evaluation have not run.
- The fixed analytic U(t) is a prescribed flow test input, **not a Gesture/Script converted into human speech**.
