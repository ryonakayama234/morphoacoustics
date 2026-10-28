# RESULTS — pre-implementation decision and evidence ledger

**2026-10-27 JST | DESIGN_REVIEW_ONLY | Gate B solver NOT RUN.** Never call a design review or a simulated analytic oracle a physiological / perceptual result.

## Evidence currently available from earlier work
- PR #158 Gate A: frozen mathematical source/load hypothesis; non-blinded preliminary Wolfram symbolic equivalence and 18-row synthetic traveling-wave predictions, committed before any Gate B Python solver.
- Frozen Gate A oracle JSON Git blob f89ccf20cb60019c4487873a13af678e983beb6b, Wolfram source blob fa8c2112f36f2b7119d40e8125e4d979ba091eef. This branch does not modify either source or acceptance threshold.
- Frozen model checks predict at A=3e-5 m² and source matching |pL/ps|=2/3, independent of length, while phase varies; a fixed-absolute-load A=6e-5 m²,L=.025m,f=3000Hz condition predicts |pL|=0.4492470594476995 Pa. **These are predictions, not observations of an anatomical ear.**
- The existing Core UniformTube implementation supplies the lossless 1D ABCD matrix. The ASMR package currently publishes only a research catalog.

## Outcomes for this incremental task
| Item | Status | Claim |
|---|---|---|
| Computational measurands, interventions and confounds | DESIGN_PROPOSED | architecture and measurement semantics refined in SYSTEM/DATA |
| Hypotheses + falsifiers + anti-claims | DESIGN_PROPOSED | existing primary gates distinguished from newly proposed diagnostics |
| Documentation/architecture and provenance | DESIGN_PROPOSED | this docs-only research branch |
| New solver or numerical experiment | NOT_RUN | no Gate B implementation, new CI result, performance number or acoustic WAV |
| External science audit | NOT_RUN | no independent scientific approval inferred |
| Empirical ear/source calibration | NOT_AUTHORIZED | Gate C separate |
| ASMR perception and Studio adoption | NOT_AUTHORIZED | Gate D / API promotion separate |

## Open decision register
D1: sign/port convention and H_drive×H_canal attribution acceptable?
D2: new H_B6-H_B8 diagnostic tolerances and null definitions appropriately bounded?
D3: research-local domain guards/refusal classification finalized prospectively?
D4: independent review of oracle row mapping, reproducibility and actual empirical-claim boundary complete?
**Current disposition:** DESIGN_PENDING_REVIEW; IMPLEMENTATION_NOT_STARTED. Record any future disagreement and decision as an additive dated entry, preserving this initial declaration rather than rewriting history.

## 2026-10-28 additive design-protocol record (not a numerical result)
- [PROTOCOL-V1.md](./PROTOCOL-V1.md) defines prospective H_B6-H_B8 numeric comparison rules, a dimensionless passive denominator check, exact 10-column frozen oracle coverage, and a zero-drive/negative-input policy.
- Status remains **PROTOCOL_REVIEW_REQUIRED / GATE_B_SOLVER_NOT_RUN / NO_NEW_CI / NO_INDEPENDENT_APPROVAL / NO_IMPLEMENTATION_AUTHORIZED**. Proposed new tolerances have not been reviewed or executed; frozen Gate A thresholds and oracle bytes are unchanged.
