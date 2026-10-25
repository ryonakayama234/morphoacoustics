# VM-1C preregistered experimental ledger

Status: **BEFORE SCIENCE IMPLEMENTATION**, 2026-10-26. Scientific hypotheses, conditions and prospective gates: [VM1C_GATE_A.md](VM1C_GATE_A.md).

| Control | Actual manipulated dimension | Outcome to measure | Falsifier |
|---|---|---|---|
| C0 | exact SA-2A unmodified function and Exp028 frozen body | Git blob SHA/content hash and original source provenance | hash mismatch→fail |
| C1 | ka=0.02/0.10/0.25/0.55/0.80 | SA-2A Bessel/Struve against Rayleigh disk-overlap | complex abs err>2e-9→fail |
| C2 | ka=0.001 low frequency | B0 leading R/X vs SA2A exact | normalized abs error>2e-6→fail |
| C3 | 5mm /10mm /16mm, f=100/300/600/1000/1600/2500 (valid-only) | exact-vs-B0 complex Z and phase plus time-discretization effect | nonfinite/negative passive R→fail; deviation size otherwise descriptive |
| C4 | original 16-section /a/ M0 vs M1, exact/B0cont/B0discrete, same ideal inlet U | all HpU,HU,Zin, p/U power balance, H600/H100 dB | port-energy rel mismatch>1e-8 or missed valid frequency→fail |
| C5 | 16mm/3000Hz deliberate domain crossing and wrong body | explicit refusal | silent extrapolation or fabricated geometry→fail |

Expected *interpretation*, not predeclared result: if 600Hz high selectivity persists under exact-piston load, this constrains the hypothesis that B0 model error is its sole cause. It does not prove actual human voice quality, ear receiver pressure or truth of an infinite rigid baffle anatomical model.

**Retrospective results are appended only after actual GitHub Actions science run** with immutable commit, code/geometry/hash provenance, error and failed-gate evidence. No historical source outputs hard-coded as success.