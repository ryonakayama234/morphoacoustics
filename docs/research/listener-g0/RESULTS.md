---
id: EL-G0-RESULTS
status: NUMERICAL_GATE_PASS_REVIEW_PENDING
adoption: NOT_ADOPTED
parent: "Issue #113 / PR #83"
---

# EL-G0 — Evidence / experiment log

## 2026-10-17 — Gate registration and independent oracle

**Hypothesis:** ideal known source + two mathematical pressure probes must produce the free-field propagation symmetry and distance relations of [PREREGISTRATION.md](PREREGISTRATION.md). Do not interpret this as human listening, near-contact, wet sound or subjective ASMR evidence.

| Measurement | Independent Wolfram numerical result | Model meaning |
| --- | ---: | --- |
| Left source–probe distance | 0.29000000000000004 m | rigid fixture |
| Right source–probe distance | 0.20223748416156684 m | rigid fixture |
| R-L propagation delay | -0.2558673931149656 ms | right receives first |
| R/L level difference | +3.1307268779057047 dB | right probe has larger amplitude |
| Mirror-delay residual | 0 s | sign symmetry |
| Mirror-level residual | 8.881784197001252e-16 dB | sign symmetry within float error |

**Source:** independent Wolfram Language evaluation performed 2026-10-17; numeric coordinate oracle. This is mathematical arithmetic for a **specified ideal free-field null**, **not an external biological measurement**. See the frozen protocol for the geometry.

## Recorded correction (before automated evidence)

Initial runner documentation described exp(-i omega t) while using outgoing exp(-ikr) and +i omega. Corrected the **convention label only** to exp(+i omega t) in the runner and schema. The physical pressure formula, output metrics, hypothesis and registered thresholds were not altered. No post hoc numeric threshold changes.

## 2026-10-17 — GitHub Actions numerical execution

- **Run:** [38928661444](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38928661444), status SUCCESS.
- **Branch head at test:** `87f26e08e7e05448db13f6ed86189698b5e1ea44`.
- **Python:** GitHub runner Python 3.11.17, `python -m pytest tests/test_experiment_040_listener_g0.py -q` — **9 tests passed** (nine dots, 100%; successful exit).
- **Runner:** `python experiments/040_listener_g0/run.py --output .../RESULTS.json` — successful exit. Since its exit code requires all registered gates true, this run satisfied those programmed gates.
- **Evidence:** artifact `EL-G0-analytic-null`, ID `12057019254`, zipped artifact SHA-256 `5630bd6a1f72af26cd612ce11bbd4de6c2cfc81892ff6c77a13eeec327ac4ed4`.
- **Decision:** `PROVISIONAL_ANALYTIC_BASELINE`; **NOT_ADOPTED** pending independent model review. Success is a consistency check of an ideal free-field null, not an independent physical measurement.

## Execution and review gate

- Preregistration: saved to the research branch before implementation.
- Source and test fixture: added in a separate commit.
- Independent mathematical oracle: **CHECKED** (Wolfram).
- Python automated tests: **PASS** in run 38928661444 (nine tests, no failures).
- Empirical ear/pinna/ASMR comparison: **NOT PERFORMED**.
- Production adoption: **NOT_ADOPTED** (still requires independent critical review and empirical validation for later listener physics).
- Recorded interpretation: `PROVISIONAL_ANALYTIC_BASELINE` (analytic/null numerical checks only); independent review still required.

## Claim limit

This experiment does not model the pinna, head, external ear canal, ear canal obstruction, materials, contact, cartilage air conduction, realistic near-field HRTF, two-body mechanical feedback, or perception. At very short distances, distributed oral sources and listener boundaries cannot be replaced by this model without separate validation. Frozen gates are not evidence for PR #83 G1/G2.
