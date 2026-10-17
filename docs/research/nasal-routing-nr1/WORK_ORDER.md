# NR-1a implementation work order — fixed oral/nasal terminal routes

2026-10-17 JST. DESIGN HANDOFF ONLY; NOT ACCEPTED, IMPLEMENTED, OR ADOPTED. Parent: https://github.com/ryonakayama234/morphoacoustics/issues/115; draft PR: https://github.com/ryonakayama234/morphoacoustics/pull/116 .

## Single goal
Using a fixed three-tube, one-junction passive acoustic network with identical source and geometry, independently demonstrate that changing **one** terminal condition causes lawful, measurable changes in full complex acoustic p/U, terminal power, load impedance and frequency response. Preserve raw state and exact provenance. No voice, waveform, changing soft palate, turbulent breath, materials, Character Creator UI or dynamic gestures.

## Essential physical distinction
Closing the **nasal distal terminal** (U_C.out=0) does NOT close the velopharyngeal port. Its upstream finite nasal tube remains acoustically coupled to the branch as a reactive side cavity. A closed mouth distal terminal likewise leaves a closed oral resonator. Actual **VP closure at the junction** / adjustable finite connecting tube requires a separate NR-1b topology-law design gate. Never set tube area=0 as a surrogate or label distal closure “VP closed”.

## Geometry and three interventions — proposed Gate A freeze
Adopted OG-4 branch3 has A -> J -> B (mouth-like), C (nose-like), where A/B/C are rigid lossless 1D uniform tubes, not actual nasal/lingual anatomy. 3 tubes, 6 endpoints, one typed junction. Hold all geometry and source fixed:
- A: length 0.08 m, area 0.0003 m2.
- B: length 0.09 m, area 0.0003 m2.
- C: length 0.06 m, area 0.00015 m2.
- rho=1.2 kg/m3; c=343 m/s; phasor exp(+i omega t), inlet prescribed volume flow (1+0.4i)e-6 m3/s.
- Frequencies 80,250,400,733,997,1200,2000,4000 Hz; no interpolation/continuous band claim.
- Matched load: Z=rho c/A; rigid closed: outlet U=0. Matched load is NOT a measured physical mouth/nostril radiation impedance.

| Case | B mouth distal load | C nose distal load | Scope |
|---|---|---|---|
| N | matched | rigid_closed | Already supported by OG-4 |
| O (reference) | matched | matched | Already supported by OG-4 |
| M | rigid_closed | matched | NOT supported by OG-4 public capability; research-only new proof |

Compare N vs O and M vs O as **separate one-variable interventions**. Never claim all three are accepted OG-4 cases. If Gate A review opts for a new versioned API, that requires an independent design/release decision and must not retrofit OG-4.

## Proposed runtime/data path
Frozen three-tube blueprint -> typed port/junction + scenario -> actual adopted OG-4 Core N/O or separately scoped experiment-local transfer solver M -> six-endpoint complex p/U, load response, signed peak-phasor power, input impedance, diagnostics -> independent Wolfram twelve-complex-state global equation oracle -> regression + mutation checks -> immutable evidence/result verdict.

The Core owns laws, preparation and the physical result; Studio later consumes only version-pinned supported results, not this exploratory backend. Persistent blueprint and backend preparation are distinct from instantaneous p/U state and Studio canvas layout. See SYSTEM.md, DATA.md, EXPERIMENT.md.

## Work packages
### Gate A: NOW — research design, no runtime change
1. Review compatibility with normative adopted OG-4 (do not copy its implementation into a new general graph engine). Pin physical law, six-endpoint sign convention, full complex observation fields, source/load identity, exact input bytes, independent Wolfram source and goldens, status/refusal precedence, repetition/hashes and conditioning threshold.
2. Suggested numeric criteria to **review and freeze**, not retrospective passes: normalized endpoint error <=1e-10; scaled junction/power residual <=1e-10; linear system residual <=1e-12; explicit singularity/conditioning guard. Compare complex values at every frequency rather than amplitudes only.
3. Require independent physics and API/data review, then an explicit Gate A decision before Gate B. Synchronize SYSTEM/DATA/EXPERIMENT.

### Gate B: isolated implementation, separate Draft PR AFTER Gate A
1. Build experiments/041_nr1_static_oral_nasal_route/ with a reproducible Python run script, frozen fixtures and results; tests/test_experiment_041_nr1.py with negative controls; use OG-4 public prepare_branch3().response() for N/O without duplicating its source.
2. Build only the M research-local extra B-terminal closure solver using transfer-matrix/impedance recursion + complete state reconstruction; **the adopted OG-4 must report UNSUPPORTED on M**.
3. Compare independent Wolfram GLOBAL 12-variable complex solution against **all six endpoint p/U pairs** for all three cases at all eight anchors. Verify junction pressure, signed flow, real power conservation and nonzero expected outputs.
4. Kill mutations: wrong particle-velocity junction law, reversed flow orientation, swapped B/C output IDs, stale geometry/source/boundary hashes, malformed/dangling/duplicate ports and unsupported topology; singular cases must fail explicitly (no guessed WAV).
5. Execute fresh exact-HEAD CI, original OG-3/OG-4 and OG-5 where relevant, Experiment028/029 and X2a protection; capture two-run data/source SHA256, raw JSON, plots, independent oracle file and full decision ledger.

### Gate C: scientific decision only
Independent physics/numerical and code/API reviews. Write SUPPORTED_LIMITED / INCONCLUSIVE / REJECT with narrow claim, limitations, exact artifacts and post-merge receipts if any. No publishing in Studio, no generic anatomy/API adoption by inference.

## Definition of done: outcomes must all be true
- N: C distal U_out=0, zero nasal terminal power, positive mouth terminal power; **C inlet need not be zero**.
- O: both terminal powers positive with full complex states independently matched.
- M: B distal U_out=0, zero mouth terminal power, positive nasal terminal power; M remains separate research logic and official OG-4 rejects it.
- Every full complex endpoint matches independent Wolfram within pre-frozen thresholds; source vs delivered power and junction law balance pass; wrong-law mutants fail.
- Identical version/preset/source/case/seed(if used) repeats reproducibly with content digests; status taxonomy respected; legacy physics not modified.
- System, data, experiment ledger and raw machine evidence updated together in same implementation PR; reviewer signs limited scientific decision.

## Exploratory Wolfram evidence — NOT frozen, not a physics adoption gate
At 733 Hz, separate well-scaled 12-unknown global WL Solve (35-digit working precision) gives:
| case | source power W | B mouth distal W | C nose distal W |
| N | 5.3130604780595185e-7 | 5.3130604780595185e-7 | ~0 |
| O | 9.2980511855474507e-7 | 6.1987007903649672e-7 | 3.0993503951824836e-7 |
| M | 8.6128929520173005e-8 | ~0 | 8.6128929520173005e-8 |

Source power differs because **prescribed source flow** interacts with changed acoustic load. Displayed precision conserves delivered power, but this is only algebraic exploratory evidence, not Core-vs-Wolfram validation, biological nasal speech or preregistered pass. Exact exploratory WL code to be added separately and reviewed before frozen protocol.

Sources: https://www.sciencedirect.com/science/article/pii/S0892199721000655 (nasal coupling can introduce transfer-function dips); https://pmc.ncbi.nlm.nih.gov/articles/PMC8492006/ (VP anatomical interpretation).
