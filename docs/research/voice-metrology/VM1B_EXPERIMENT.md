# VM-1B experiment ledger — prospective record

**Design commit required before code.** [Gate A](VM1B_GATE_A.md), [SYSTEM](VM1B_SYSTEM.md), [DATA](VM1B_DATA.md), Core issue [#200](https://github.com/ryonakayama234/morphoacoustics/issues/200).

| ID | Manipulation | Independent control | Falsifier / failure result |
| --- | --- | --- | --- |
| B0 | frozen Exp028 body digest | exact Git blob SHA1; same areas M0/M1, distinct section length | hash mismatch or masked invalid area → FAIL |
| B1 | M0/M1 + ideal matched, 0.30s | 16-section matrix separate from waveguide | any full complex HpU,Zin,HU rel_err > 1e-9 → FAIL |
| B2 | same + discrete B0 0.30s | exact discrete shunt admittance, not hand-selected impedance | any full complex rel_err > 0.002 → FAIL |
| B3 | B0 0.60s vs 0.30s | identical initial conditions, native clock, geometry, source | truncation errors not decreasing or >1e-5 at 0.60s → FAIL |
| B4 | n=2,4,8 at exact 100/600 | continuous B0 R+inertance analytical limit | complex-convergence monotonicity fails → FLAG |
| B5 | incorrect model / silent source | matched substituted for B0; zero pulse; modified geometry | wrong law accidentally accepted as B0 → FAIL |
| B6 | exact software/physics provenance | per-tick original native energy ledger, source/hash/units | missing/false origin → FAIL |

**Status at preregistration:** no GitHub code or CI results are claimed. Results must be appended after actual execution with exact-head CI run, artifact SHA and review status. Preliminary **local** mathematics / prototype was used to assess prospective engineering tolerances; confirmatory CI is not independent of that exploratory tuning. No listener WAV and no quality GO, no renderer acceptance, no Studio change.

**Candidate outcome labels (not predecided):** `NUMERICALLY_CONSISTENT_WITH_DECLARED_B0`, `FAIL_NUMERICAL_REFERENCE`, `INDETERMINATE_REAL_RADIATION`. All accepted calculations remain research-only until Gate C and independent review.

## Actual CI measurement — 2026-10-25 16:25 UTC (after preregistration)

**Exact instrument+test head tested:** `33b95b7570a3eeaa68738b92b4cda4096497a24a`.
[VM-1B science CI run #40211570360](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40211570360) **SUCCESS**: focused 14 parametrized tests passed, full authentic frozen-M0/M1 standalone six-case instrument reported `NUMERICALLY_CONSISTENT_WITH_DECLARED_B0`, **all three complex physical-port transfers** at nearest 100/600 Hz passed their prospectively stated bounds. Actual research artifact [#12605627758](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40211570360/artifacts/12605627758) stores full real/imag references, native values, per-port relative errors, physics clocks, source/geometry hashes, SI model limitations and n=2/4/8 checks. Retention 90 days; separate permanence task [#197](https://github.com/ryonakayama234/morphoacoustics/issues/197).

| frozen body | boundary | finite impulse time | largest observed complex relative error (HpU/Zin/HU, both frequencies) | preregistered cap |
|---|---|---:|---:|---:|
| M0 | matched | 0.30s | 1.1688175779594876e-15 | 1e-9 |
| M1 | matched | 0.30s | 1.995472778451747e-14 | 1e-9 |
| M0 | discrete B0 | 0.30s | 4.949774467330014e-05 | 2e-3 |
| M1 | discrete B0 | 0.30s | 0.0007794892838775678 | 2e-3 |
| M0 | discrete B0 | 0.60s | 7.748369360739949e-11 | 1e-5 |
| M1 | discrete B0 | 0.60s | 1.3157280707760298e-08 | 1e-5 |

M0/M1 extension to 0.60s decreases each tested point/physical port's complex error. All four M0/M1×100/600 refinement cases reported monotonic n=2→4→8 approach to the specified continuous-time B0 shunt-law reference. Wrong load cannot masquerade as B0 at the preregistered M0/100Hz control; silence yields no native sound. Separate **general regression, VM-0, SV-1, OG-3 and OG-4** pull-request CI runs passed at this exact head.

**Bounded scientific disposition:** `NUMERICALLY_CONSISTENT_WITH_DECLARED_B0` (same assumed load, independent mathematics and discrete simulator), `INDETERMINATE_REAL_RADIATION` (no independent empirical/higher-fidelity mouth measurement), `VOICE_NO_GO_UNCHANGED` (no external received sound or user audition). This does not mean natural 600Hz resonance, physical Q, viable universal organ connection or species flexibility was validated. Finite-window relative error is not an estimate of uncertainty of the underlying physical law.

**Review/adoption:** Draft PR #201, no release/merge/quality approval. Pending independent Codex review of final amended head; exact-head CI after this evidence commit must be reported separately. No Studio/default UI edits.


## Codex review findings and evidence-gate repair (2026-10-26; not a scientific amendment)

Exact original reviewed head `a5f6150d65e329a0a1736634b0f60158ad2a5b21` passed six scientific CI groups but **Codex returned two unresolved P2 points**: (1) the workflow discarded report upload on numerical failure, (2) the JSON contained historical `base_main_sha` and frozen-body hashes but did not identify the code that actually executed. Both are evidence integrity failures, **not** new radiation-physics reference measurements.

Remediation on same VM-1B research branch: checked-out Git commit/tree + SHA256 of actual instrument, waveguide, physical/domain, test and workflow source; refuse dirty/unknown checkout; failure-case JSON written before scientific nonzero exit; unconditional artifact upload and distinct deliberately failing step to verify downstream evidence retention. Focused tests cover executable provenance identity and wrong/dirty checkout refusal as well as the report-first failure path.

No numerical acceptance thresholds, B0 impedance law, source volume, M0/M1 geometry, physical results or scientific claim have been changed in this repair. The negative-control failure JSON is **synthetic test evidence only**, not a physical failure or creator audio result. Updated exact-head CI and an independent exact-head review required before final Gate C disposition. Studio UI remains explicitly frozen.

## Post-Codex round 2 evidence repair — 2026-10-26

Independent review of exact head `acb871a839f4f518676add84c66925c393872d57` found **three additional P2 scientific evidence omissions**, beyond the initial two addressed: shallow-checkout parent provenance; finite measured native energy-gate failure lost before JSON; and conditional diagnostic generation skipped after a failing focused pytest. They are tracked in original [VM-1B Draft #201](https://github.com/ryonakayama234/morphoacoustics/pull/201) and were **not** interpreted as physical validation passes.

**Repair source head:** `4438affee6db65ac2bf4de79d3a76ce03719dd42`.
- Commit parent list now comes from *raw* `git cat-file -p HEAD` (true parent headers in a depth-one checkout), checked against actual Git tree. A real depth-one isolated Git fetch test is included.
- Finite energy-ledger violations become `energy_gate_pass=false`, `pass=false` plus bounded `energy_failure_samples` including exact step/residual/tolerance/work/stored energy/loss. Native p/U port traces remain available for diagnostics. Nonfinite traces still refuse non-measurable outputs and cannot be falsely reported as physical data.
- Separate focused pytest failure cannot silently skip full scientific diagnostic execution: report step has explicit `if: always() && steps.install.outcome == 'success'`, with resulting job still red on test failure. Artifact upload remains `if: always()`.
- An injected finite bad native energy ledger is executed through the real instrument `main()` in a negative-control test; a failed scientific gate writes an actual full six-case numeric JSON and raises nonzero **after** it is saved.

**Confirmatory CI at repaired code head:** [VM-1B #40244835133](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40244835133) **SUCCESS**, [artifact #12618785603](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40244835133/artifacts/12618785603) with source/fixture provenance and measured complex port traces. At this same source head, Core general tests, VM0, SV1, OG3 and OG4 pull-request workflows also SUCCESS. Measured B0/SA-2A physical truth is **not** claimed; no change to original scientific acceptance thresholds or original frozen geometry.

**Gate verdict:** software/evidence repair test PASS. Physics verdict remains `NUMERICALLY_CONSISTENT_WITH_DECLARED_B0` only; actual human mouth radiation `INDETERMINATE`; voice `NO_GO`. New exact-head independent review **requested but not yet accepted**. All historical reviews and failures remain available; Draft stays unmerged.
