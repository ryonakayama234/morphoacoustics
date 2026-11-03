# EL-R1 Audit Amendment A1 — Independent scientific and implementation review response

**Registered after Gate A/B, on 2026-10-22 JST.** Parent [Issue #152](https://github.com/ryonakayama234/morphoacoustics/issues/152) and [Draft PR #153](https://github.com/ryonakayama234/morphoacoustics/pull/153). Baseline audited `fea964e852957f35b5ab4f372299517d530c83e6`. Original [Gate A EXPERIMENT](./EXPERIMENT.md) and its sealed commit `db2f871...` remain unchanged. This **post-hoc audit remediation** must never be reported as pre-registered Gate A findings.

## Audit verdict and response map

| Audit finding | A1 action | Scientific status |
|---|---|---|
| P1 entrance pressure vs incoming wave | Explicit independent test `test_audit_distinguish_total_vs_incident_pressure_boundaries`, fixed incident amplitude emulated with a separately computed length-dependent total-pressure boundary; production solver **still only accepts fixed total pressure** | Confounding demonstrated; external sound-field coupling **not** validated |
| P1 zero frequency AC mean power | Outputs `ZERO_FREQUENCY_LIMIT` with AC `mean_active_power_w=null`, `power_residual_w=null`, formal algebraic `formal_phasor_power_limit_w` for both planes; physical DC flow/work rate *not inferred* | Interpretation repaired with explicit schema amendment |
| P1 area/load coupling | Fixed R=Zt/Zc area null verified (H and Gamma invariant; flow/power change). `Zt` changes when area changes; not an isolated area intervention | Null effect documented; absolute-fixed Zt experiment **deferred** |
| P2 8kHz, idealized geometry | 8kHz retained solely as **numeric research guardrail**; no accuracy statement for ears/higher modes/ossicles | Not physiologically validated |
| P2 resistive terminal | `TERMINAL_SIDE` is a mathematical load plane, never mechanical drum model | Experimental passive load only |
| P2 incomplete wide-band oracle | Independent Wolfram `wolfram_oracle_36.wl` and `wolfram_oracle_36.json`; 3 length × 3 loads × 4 f (including f=0 *formal* power limit), including **all** complex H, Gamma and normalized formal power | Reproducible algebraic oracle, not measured human accuracy |
| P3 huge integers and extreme stimuli | Convert/check numeric fields safely and reject overflow as INVALID; dimensionless `epsilon=|p0|/(rho*c²)` constrained to 1e-3, outside declared small-signal envelope UNSUPPORTED | 1e-3 is **an engineering research cutoff chosen for this fixture**, not a universal validity or hearing-safety threshold |

## Boundary analysis — do not overclaim
For load Zt=R Zc, terminal reflection `Gamma_L=(R-1)/(R+1)`, `q=exp(-ikL)`, input reflection `Gamma_0=Gamma_L*q²`. If **total** p0 is fixed, terminal pressure H=`q(1+Gamma_L)/(1+Gamma_L*q²)`. If **incident** `p0+` is fixed, terminal pressure=`p0+ q (1+Gamma_L)`; **its magnitude does not depend on L** at fixed R and source wave. This does **not** imply a free-field source can be directly replaced by prescribed incident wave. Actual field/entrance coupling and source/load impedance are separate unsolved physics.

Area null: with fixed R, `Zt=R rho c / A`, so H and Gamma are A-independent by construction. With **fixed absolute Zt** at differing A, R changes and H differs; that is a distinct research experiment without changing the solver's meaning.

At f=0, `P=(1/2) Re(p U*)` is merely the mathematical limiting value of a harmonic AC expression. Actual steady work rate would not carry the factor 1/2 and the present tube model does not establish a physiologically valid DC flow through a human drum. Consequently A1 returns null in AC power fields at 0 Hz. Other modeled phasor quantities H, Gamma, p, U remain useful as limiting expressions.

## Schema and contract
Existing research output version `el-r1.passive.uniform.v0` is retained **only as historical Gate A/B record**. The non-backward-compatible per-frequency power interpretation changes require `el-r1.passive.uniform.v0a1`. New `frequency_interpretation` discriminant and `formal_phasor_power_limit_w` are explicit. Downstream code must not assume numeric `mean_active_power_w` at f=0. The small-signal envelope ratio, its conservative 1e-3 cutoff and refusal are reported in the output. This is not a public package contract.

## Oracle reproducibility
- Re-run independent calculation (WolframScript required for regeneration, **not** for CI consumption): `wolframscript -file experiments/043_el_r1_ear_port/wolfram_oracle_36.wl > /tmp/el-r1-36-rebuilt.json`.
- Compare regenerated dataset using `python experiments/043_el_r1_ear_port/verify_wolfram_oracle_36.py /tmp/el-r1-36-rebuilt.json`.
- CI compares checked-in independent Wolfram records to the existing Core ABCD solver across all 36 fixtures and enforces closed-form boundary nulls. CI does not run Wolfram itself.

## Gate status
Audit baseline CONDITIONAL PASS; A1 follow-up implementation provisional until latest CI verified. Gate A untouched; Gate C/D and physiological realism NOT AUTHORIZED / NOT ADOPTED; PR #153 remains Draft. Remaining separate proposals: fixed absolute terminal load, frequency-dependent passive load, source impedance/field-coupled port, actual reference-plane HRTF and measured ear transfer, sampled causal audio, perceptual validation.
