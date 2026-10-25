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
## Retrospective exact-head CI evidence — 2026-10-26 JST

**Actual implemented VM-1C measurement head:** `54658954fceb30c8baaba4330f0febe7e4a3abbf`.
[Dedicated VM-1C science CI #40245603466](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40245603466) **SUCCESS**, [raw research artifact #12618497145](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40245603466/artifacts/12618497145). At this same head, standard Core `tests`, OG-3, OG-4 and SV-1 workflows also **SUCCESS**. SA-2A canonical reference is the *unchanged imported research source* `experiments/049_baffled_piston_sa2a/run.py`, pinned blob `3e7439b426adfd3549586bb43210eec66242606c`; actual Exp028 frozen body blob `7810dfbb72cb6c41af007db6e9d51c58cad9a522`. The full JSON includes all valid calibration radii/frequencies, entire complex `HpU/HU/Zin`, source/port power, actual git checkout and SHA256 hashes.

**Authentic outlet equivalence:** 16mm radius for the frozen M0/M1 /a/; plane-wave frozen-geometry reference only, no real-human mouth. Same 16 areas but M0 10mm per section / M1 11mm. All measurements held ideal inlet harmonic flow fixed (frequency-domain peak `1e-6 m³/s`); no biological vocal source.

| Frequency Hz | `ka` for 16mm | continuous B0 vs exact ideal piston complex `|ΔZ|/|Zexact|` | discrete n2 B0 vs continuous B0 `|ΔZ|/|ZB0|` |
|---:|---:|---:|---:|
| 100 | ≈0.0293 | 0.00006898158045628934 (0.00690%) | 0.000006989871420244026 |
| 300 | ≈0.0879 | 0.0006201874603043568 (0.0620%) | 0.00006283820155212611 |
| 600 | ≈0.1759 | 0.0024720898819778595 (0.2472%) | 0.00025040622009325065 |
| 1000 | ≈0.2931 | 0.006811088020290449 (0.6811%) | 0.0006894584428757823 |
| 1600 | ≈0.4689 | 0.017104956984485258 (1.7105%) | 0.0017285461132327481 |
| 2500 | ≈0.7327 | 0.040050122639707184 (4.0050%) | 0.004029931857288629 |

These are **full complex impedance** relative deviations under the flanged piston reference, not radiation power or radiated spectrum error. 16mm at 3000Hz (ka≈0.879) is declared outside the registered 1D+aperture validity envelope and is **refused**, not a successful extrapolation.

### Loaded native-like M0/M1 section matrix: 600-to-100Hz port selectivity

| frozen body | ideal baffled piston outlet | B0 continuous shunt outlet | B0 actual n2 discrete phasor outlet |
|---|---:|---:|---:|
| M0 | **+34.726761626206866 dB** | +34.68692724201362 dB | +34.69097556851533 dB |
| M1 | **+55.19947597587261 dB** | +55.18897469648422 dB | +55.19117148698853 dB |

B0 n2 → ideal piston changes H600/H100 by only **+0.0357861 dB for M0** and **+0.0083045 dB for M1** on frozen geometries. This strongly **constrains the hypothesis that B0 approximation error is the sole cause** of the apparent 600Hz selectivity in these calculations. It does NOT tell whether 600Hz is a natural human vocal formant, account for glottal self-oscillation, validate a real unflanged mouth or certify any audience audio. SA-2A's ideal circular piston and B0 both produce a highly reactive low-frequency boundary and strong tract-dependent transfer.

**CI failure and correction retained:** Initial VM-1C comparison [CI #40245362764](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40245362764) passed **dedicated science**, while its general Python matrix [#40245362716](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40245362716) failed because its base `pip install -e '.[dev]'` excludes optional SciPy. Corrected VM-1C focused tests to `pytest.importorskip("scipy")` in ordinary Core suites; dedicated research workflow **explicitly installs SciPy** and runs real Bessel/Struve and quadrature tests. Both suites now green at `54658954`; the original red runs are preserved, not ignored.

**Bounded science verdict:** `SA2A_IDEAL_PISTON_COMPARISON_MEASURED` with passing reference/gate controls. The value `INDETERMINATE_REAL_RADIATION` is **unchanged**, as is `VOICE_NO_GO_UNCHANGED` and `SA2B_TIME_DOMAIN_NOT_RUN`. Present work is a **frequency-domain research-only comparison**, not a new physically causal replacement termination or a universal lip/syrinx model. Independent exact-head Codex review **still required** before final science adoption or any future Core main merge.
