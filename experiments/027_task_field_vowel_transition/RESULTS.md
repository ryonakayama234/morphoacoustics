# Experiment 027 results — low-dimensional task-field vowel transition

Issue: #62  
PR: #63  
Parent: #33

## Decision

**ADOPT_TASK_FIELD_CANDIDATE**

All frozen objective Gates passed without changing task values, realizer constants, or thresholds after Python execution.

This supports the narrow claim:

> On the calibrated reference body, an exact target area-function need not be embedded in the canonical motor command: the frozen three-task normalized field can generate a continuous physical/acoustic transition to an /i/-like endpoint within the preregistered engineering error bound.

It does not establish morphology transfer, arbitrary phonology, natural speech, production motor control, or explicit infeasibility on a second body.

## Canonical execution provenance

The canonical audited run is the post-review timing fix:

- GitHub Actions scientific run: `37614823741`
- tests run: `37614823695`
- branch: `v3a-experiment-027-task-field`
- source head commit: `b15a778409ccf221cc508e0527e74df65c74df7d`
- full output artifact ID: `11478728169`
- artifact SHA-256: `248f46849d10a74468dd84755ad0a387a9b932514834b879988725f02f28cb5a`
- artifact size: 611433 bytes
- Python: 3.11.16
- NumPy: 2.4.6

The repository test workflow and the Experiment-027 scientific workflow both passed.

### Review correction before merge

Codex review found that the first implementation serialized `CandidateTask.onset_s/offset_s` but drove all R1 fields from the inherited Experiment-026 global progress. That made canonical task timing dead metadata. Before merge, the realizer was corrected so each task computes its own sampled smoothstep activation from its own schedule, and the three independently activated fields are then combined.

The audited run above verifies, for every frozen task:

- onset activation = `0.0`;
- midpoint activation = `0.5000000000000001` (floating representation of 0.5);
- offset activation = `1.0`.

The scientific decision remained **ADOPT_TASK_FIELD_CANDIDATE** with no task-value, realizer-constant, or threshold refit.

## Representation boundary

Canonical task plan:

```text
OPEN       location=0.3424849103873983  degree=0.5921764128805103
CONSTRICT  location=0.7167402543883221  degree=0.9235962908995712
CONSTRICT  location=1.0                 degree=0.04495226070116771
```

All three use onset 0.150 s and offset 0.350 s.

Machine Gate:

- `representation_clean = true`
- no area/diameter vector in the serialized canonical task plan
- no section index / mesh node
- no F1/F2/formant target
- no waveform/spectrogram target

Generated section areas are stored only as realized physical-state diagnostics.

## Independent Wolfram oracle reproduction

Start-state reproduction:

- calibrated `/a/` object recovered exactly: PASS

Task endpoint area oracle:

- maximum absolute area error: **6.505213034913027e-19 m²**
- frozen tolerance: `rtol=1e-12`, `atol=1e-15 m²`
- result: PASS

First five segmented-tube response peaks matched the frozen 0.25 Hz-grid Wolfram oracle exactly:

| geometry | P1 Hz | P2 Hz | P3 Hz | P4 Hz | P5 Hz |
|---|---:|---:|---:|---:|---:|
| calibrated /a/ | 720.25 | 1288.50 | 2918.25 | 4196.00 | 4657.25 |
| calibrated /i/ | 281.25 | 2309.25 | 3212.00 | 4102.00 | 4899.25 |
| task endpoint | 275.00 | 2101.75 | 3164.75 | 4352.00 | 4817.75 |

Observed peak error was **0.0 Hz** for all checked peaks.

## Endpoint sufficiency Gate

Calibrated /a/→/i/ P1/P2 distance:

- **1111.1487580427745 Hz**

Task endpoint→/i/ P1/P2 distance:

- **207.59410516678935 Hz**

Normalized endpoint error:

- **0.18682836448690684**
- frozen limit: **<= 0.20**
- result: PASS

Task endpoint→/a/ distance:

- **927.1586299010542 Hz**

Therefore the task endpoint is substantially closer to calibrated /i/ than calibrated /a/: PASS.

## Continuous trajectory

Maximum adjacent 10 ms R1 P1/P2 step divided by the calibrated /a/→/i/ endpoint distance:

- **0.06621354015393985**
- frozen limit: **< 0.20**
- result: PASS

Maximum matched-time R0-vs-R1 P1/P2 displacement:

- **207.59410516678935 Hz**
- normalized by calibrated /a/→/i/ endpoint distance: **0.18682836448690684**

The R1 geometry remained finite and positive throughout the analysed trajectory.

## Source regression

The inherited Experiment-013 source remained unchanged:

- source: `lf_fixed`
- planned F0 identically 100 Hz: PASS
- stochastic-noise component exactly zero: PASS
- cycle-boundary jump / RMS: **4.406218549921945e-05**
- inherited limit: **< 0.01**
- result: PASS
- source float64 SHA-256: `724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc`

## Waveform / numerical stability

All R0/R1/R1-ref pressure arrays were finite.

R1 reset/click diagnostic:

- transition-region maximum adjacent-sample jump: **0.0007408700020673991 Pa**
- steady-endpoint maximum adjacent-sample jump: **0.0007357798018530221 Pa**
- ratio: **1.0069181026735956**
- frozen limit: **< 3.0**
- result: PASS

Temporal numerical floor:

- `d(R1, R1-ref) = 0.009348164942979183`
- frozen limit: **< 0.20**
- result: PASS

R0-vs-R1 waveform difference:

- `d(R1, R0) = 0.08392820574873228`
- effect / temporal floor: **8.978040744966258x**

The latter ratio is a diagnostic, not an added pass criterion. It shows that the observed R0/R1 waveform difference is resolved above the chosen temporal discretization perturbation.

Named comparison WAVs used one common gain and did not clip.

## Gate summary

- representation boundary: PASS
- Wolfram / implementation oracle: PASS
- geometry / resonance trajectory stability: PASS
- source regression: PASS
- waveform finite / artifact regression: PASS
- temporal stability: PASS
- endpoint representation sufficiency: PASS

Final decision: **ADOPT_TASK_FIELD_CANDIDATE**.

## Interpretation

The result removes one important shortcut from the V2 path.

Experiment 026 used:

```text
prescribed target area-function trajectory
    -> physical/acoustic renderer
```

Experiment 027 demonstrates a narrower motor path:

```text
three normalized task commands
    -> experiment-local body-specific field realization
    -> physical tract trajectory
    -> existing physical/acoustic renderer
```

The area vector still exists downstream because the current 1D acoustic body needs a physical geometry. The supported claim is that this vector no longer needs to be present in the **canonical task command**.

## Limitations

- candidate locations/degrees were selected with knowledge of the calibrated /i/ target; this experiment tests representation sufficiency, not unsupervised motor learning;
- only one prepared calibrated body is used;
- the field mapping is experiment-local and not yet a production realizer API;
- section-slot normalization `x=j/(N-1)` is a candidate realization convention, not a universal anatomical coordinate;
- no second-body transfer or deliberate infeasibility is tested;
- no human perceptual Gate is added here;
- current acoustics remain the Experiment-026 quasi-stationary short-time transfer path.

## Handoff

The next #33 experiment may now hold this exact task plan fixed and change only the prepared morphology.

That next step should distinguish:

- same task + second body -> FEASIBLE body-specific realization;
- same valid/supported task + constrained body -> explicit INFEASIBLE;
- backend limitation -> UNSUPPORTED, not confused with physical infeasibility.

Do not claim task transfer until that experiment passes.
