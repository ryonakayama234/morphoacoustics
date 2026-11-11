# RESULTS — append-only actual execution ledger

## R0 (2026-11-04 JST; D0 registration)
**Status: PREREGISTRATION_ONLY / NO RP1 EVALUATOR EXECUTED / NO RESEARCH RESULT CLAIMED.**
The analytic fractions in HYPOTHESES and EXPERIMENT are preregistered expected values, not an observed test PASS. Existing Core EL-R2-S1 evidence belongs to predecessor PRs and does not become new RP1 outcome.

| Gate | Recorded evidence | State |
| --- | --- | --- |
| E0 H2 analytic counterexample | Predeclared exact rational values only | NOT_RUN |
| E1 H1 type/refusal controls | Predeclared categorical outcomes only | NOT_RUN |
| E2 H3 bounded Core vs wave oracle | Design specification only | NOT_RUN |
| E3 H4 split-tube invariance | Design specification only | NOT_RUN |
| Gate C measured generalization | No dataset or measurement authorization | NOT_AUTHORIZED |

Append subsequent dated sections with exact commit SHA, test counts, provenance and CI URL; retain all failed trials. Do not edit this initial D0 entry.

## R1 — Gate A and B actual computational evidence (2026-11-04 JST)
**Original science D0** `a33c8c68879f732cd830b2caab6b8024b5322297`; **original independent B0 reference** `624ce156a4c377ec742794ea6a3278e61a6651e4`, 16×15 frozen JSON blob `81286d0a2b7ea26cf33ce65d0eb98be6df47b607`; **tested code head** `d2cd21094b8c855af4fd37814e5936c89bab9ada`.

Observed **SUCCESS** for both Python 3.11 and 3.12 in [exact-head push CI 41787761522](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787761522) and [PR CI 41787767484](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787767484). Both version jobs recorded **8 Gate A unittest tests** and **24 pytest cases** covering Gate A/B and existing Core `UniformTube` regressions; CI D0/B0 historical integrity checks passed. Core [full root tests](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787767532), [SV1](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787767490), [OG3](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787767518) and [OG4](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787767472) PR workflows also SUCCESS at the same tested SHA. These are CI regression results, not independent science review.

### E0/E1 outcomes
- Both normalized ideal-source candidates gave `pL(ZL=1)=1`; under `ZL=2`, candidate A = `1` and candidate B = `1.3333333333333333`, matching exact fractions `1` and `4/3`. A single fixed-load pressure observation remains `UNIDENTIFIABLE` for changed-load prediction.
- Gate A: evidence union and purpose-specific refusals, **14 registered adversarial mutations** in 1 test method plus additional invalid, rights and unknown-op controls passed; not a complete proof of type-system soundness.
- Synthetic only fully declared port can be classified `SYNTHETIC_GATE_B_ELIGIBLE`, not by itself a physical prediction or API adoption.

### E2/E3 actual numerical comparison
All **16/16** previously registered 2×2×4 synthetic source/load/geometry/frequency conditions passed strict fully authenticated 15-field static JS wave-oracle comparisons. End-port pressure, `Zc`-scaled volume flow, four powers, source/tube power conservation, terminal/source equations, passive signs, and one-versus-two tube reference-plane representation were covered.

| Metric | Both Python 3.11 and 3.12, Core matrix vs frozen JS wave |
| --- | ---: |
| Maximum pressure component error | `2.220446049250313e-16 Pa` |
| Maximum volume-flow component error × Zc | `1.373219078511532e-16 Pa` |
| Maximum power component error | `1.3234889800848443e-23 W` |
| Split tube 0.4L+0.6L representation | 16/16 PASS, including normalized T and source/terminal port fields |
| Mutations | truncated/extended/malformed/duplicate/reference and sign/phase/power-refusal controls PASS |

The actual machine-readable `gatea.json` and `gateb.json` receipts are attached to [CI 41787761522](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787761522) as `el-rp1-gates-a-b-py3.11` and `el-rp1-gates-a-b-py3.12`; independent inspection found identical numerical receipts across both Python versions.

### Cross-runtime regeneration and preserved failure
Historical initial exact-byte comparator **FAILED** (F1, [run 41787476209](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787476209)), original B0 untouched. Subsequent strict 16×15 structural + frozen E2 numerical tolerance comparator passed. Regenerated Node.js vs frozen original:
- max pressure component difference `1.1102230246251565e-16 Pa`;
- max volume-flow component difference ×Zc `6.86609539255766e-17 Pa`;
- max power component difference `6.617444900424222e-24 W`.
See [B1-AUDIT-AMENDMENT](B1-AUDIT-AMENDMENT.md), [FAILURE_LOG](FAILURE_LOG.md). No posthoc physics threshold relaxation; no new data, model fit, human ear observation, HRTF manipulation or original oracle modification.

**Result classification:** `GATE_A_PASS`, `GATE_B_SYNTHETIC_NUMERICAL_PASS`, `INDEPENDENT_PHYSICAL_REVIEW_PENDING`, `H5_NOT_TESTED`, `PUBLIC_API_NOT_ADOPTED`. No measured predictive accuracy or subjective ASMR claim.
