# SMC-1 — EXPERIMENTS and adoption ledger

**Research date:** 2026-10-21 JST. **Status:** EXPLORATORY IMPLEMENTATION, NOT PREREGISTERED CONFIRMATORY SCIENCE, NOT ADOPTED. Do not edit historical evidence retroactively.

## Questions / falsifiers
H1: an explicit finite kana lexicon can parse known source positions and retain every undecidable unit deterministically without silently replacing unknown characters. **Falsifier:** unknown character yields READY, silent loss, or misaligned source offset.
H2: motor-planning capability is independent of a body's implemented articulators. **Falsifier:** mapping unknown /h g t ɾ/ directly to supported A/I physical GestureScore or emitting waveform from the planner.
H3: candidate coordination relation arithmetic can reproduce the previously validated Experiment011 sequential/overlap timing using a synthetic two-CONSTRICT adapter. **Falsifier:** 0.08–0.26 / 0.26–0.44 versus 0.08–0.26 / 0.20–0.38 differs by >1e-9 seconds, contradictory constraints silently resolve, or changing lexical text changes the frozen oracle.
H4: comparable results are reproducible with the exact same code/inputs. **Falsifier:** differing dataclass results across repeated runs or unstable order in resolved events.

## Independent Wolfram arithmetic: exploratory oracle (run before repository code)
`wolfram-oracle.wl` evaluates exact rationals, then displays 16-digit decimal approximations.

| condition | A window (s) | B window (s) | overlap (s) | max constraint residual |
|---|---|---|---|---|
| sequential | 0.08–0.26 | 0.26–0.44 | 0 | 0 |
| overlapping | 0.08–0.26 | 0.20–0.38 | 0.06 | 0 |

Wolfram independently returned both exact-zero residuals on 2026-10-21. **This verifies constraint arithmetic only**, NOT articulatory physiology, phoneme identification, audio continuity or pronunciation of Japanese words.

## Fixed inputs and negative controls
- `あい`: orthographic units [a,i], two symbolic intents; only *synthetic* event fixture may yield GestureScore.
- `あいあい`: 4 symbolic events in one CoordinationPlan, never concatenated WAV.
- `おはよう` and `ありがとう`: provisional orthographic units retained, missing motor gestures and contextual phonology explicit; **no score**.
- `お早う`: explicit unsupported-character refusal at code-point position 1.
- `あ、い。`: punctuation retained but physical pause/prosody unresolved.
- empty segment, non-string input, contradictory timing relation: fail closed.
- No CreatureSpec, PreparedMorphology, F0, source pressure, mesh nodes or area-function arrays in planner.

## Implementation and reproduction
Candidate file: `src/smc1_research/speech_motor_candidate.py`.
Test file: `tests/test_speech_motor_candidate.py`.

WSL2/Linux from repository root:
```bash
python -m pip install -e '.[dev]'
python -m pytest tests/test_speech_motor_candidate.py tests/test_shared_timeline.py -q
python -m pytest -q
python -m mypy src/morphoacoustics
```

Record actual CI exact HEAD, Python/NumPy versions, test counts, failures, artifact checksums and reviewer findings as **new dated appended receipts** once executed. No presumed PASS here.

## Decisions and claims
| Gate | Present status | What would be required |
|---|---|---|
| Gate A representation / prereg | PROPOSED (exploratory code exists) | independent design review; freeze future confirmatory oracle and thresholds before trials |
| Gate B bounded candidate | IMPLEMENTED / UNVERIFIED | exact-HEAD unit, regression and numerical checks, reviewed semantics |
| Gate C physical execution | NOT STARTED | approved A/I gesture adapter, source/tract single-run physical waveform and capability refusal |
| Gate D formal adoption | NOT DECIDED | review and recorded GO_LIMITED / REVISE / MORE_DATA / REJECT |
| Gate E Studio | NOT STARTED | separate Studio PR, version pin, immutable new Take and creator audition |

## Source boundary
[Experiment011 RESULTS](../../../experiments/011_gesture_coordination_overlap/RESULTS.md) supports two-Gesture overlap acoustic dependence, but not natural coarticulation. [Shared timeline candidate](../shared-timeline-candidate-v1.md) already implements constraint solving. [M5 #11](https://github.com/ryonakayama234/morphoacoustics/issues/11) remains the parent for later phonetic/physical end-to-end validation. [V4-A #123](https://github.com/ryonakayama234/morphoacoustics/pull/123) remains a separate unfinished physical boundary.

## 2026-10-21 — executed exploratory CI and remediation receipt

- Initial exploratory commit `0831fd81`: multiple CI failures. Cause A: event variable `offset` shadowed an earlier integer in `mypy`. Cause B: new Python file under the existing frozen physical package violated the intentional full-package source-inventory lock for CC-A2/OG3/OG4/SV-1. **The Core inventory guard was not modified or bypassed.**
- Correction `916bc2c1`: moved the code out of `morphoacoustics` to standalone `tools/`, fixed variable typing. Typecheck passed; test discovery failed (`ModuleNotFoundError: tools`) in [run 39538792419](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39538792419).
- Final exploratory correction `05d2e80d`: installed candidate as a distinct `src/smc1_research/` package, **outside** frozen physical `src/morphoacoustics/`; source contract, physics and pretrained/frozen receipts untouched. [Tests run 39539177849](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39539177849) reports **SUCCESS** for Python **3.11, 3.12, 3.13** and typecheck. Exact commit also reports successful `og3-gate-b`, `og4-gate-b`, `sv1-sustained-vowel-physical` workflows. These are software/regression results, **not independent scientific confirmation or future physical speech gate**.
- Reviewer independence still pending; formal SMC-1 adoption `NOT_DECIDED`. The protocol and code were explored together, so retrospective CI cannot establish preregistered experimental science.

## Wolfram four-event extension (independent arithmetic, 2026-10-21)

The expanded source in `wolfram-oracle.wl` separately evaluates a four-symbol schedule with rational onset increment `3/25 s`. It returned windows `{0.08,0.26}, {0.20,0.38}, {0.32,0.50}, {0.44,0.62}`, adjacent overlap `{0.06,0.06,0.06}` seconds, and exactly zero timing-equation residual. This is *a synthetic timing example*, **not evidence of human speech articulation**.
