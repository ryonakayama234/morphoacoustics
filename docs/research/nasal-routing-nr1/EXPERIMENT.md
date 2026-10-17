## Research-infrastructure integration ledger — 2026-10-17 (NOT ADOPTED)

**Engineering decision:** The project owner permits the design-history PR #116 followed by the bounded Experiment 041 PR #117 to be integrated as research infrastructure *only* after exact-head verification and review. The original Gate A-before-Gate B chronology was not followed; existing 24 N/O/M × 8 frequency outputs are **exploratory/post-hoc**, not a prospective Gate A-confirmatory experiment. This note supersedes any unqualified "not run" statements in the historical proposal below. No scientific Gate A/C acceptance or OG-4/Studio API expansion is implied.

**Reproduction and provenance contract.** The independent source is [global12_oracle.wl](../../../experiments/041_nr1_static_oral_nasal_route/wolfram/global12_oracle.wl) using Wolfram Language 12-complex-state global `Solve`; the checked-in [JSON](../../../experiments/041_nr1_static_oral_nasal_route/wolfram/global12_oracle.json) stores all 24 machine-precision records. The audited candidate bytes are pinned in [SHA256SUMS](../../../experiments/041_nr1_static_oral_nasal_route/wolfram/SHA256SUMS). These pins are **candidate integrity receipts**, not a retrospective scientific freeze.

For independent reproduction on a machine with licensed `wolframscript`:

```bash
cd experiments/041_nr1_static_oral_nasal_route/wolfram
sha256sum -c SHA256SUMS
wolframscript -code '$Version'
python verify_regeneration.py --wolframscript wolframscript
# Alternative: compare an independently archived raw JSON string from the marked
# NR1A_ORACLE_BEGIN / NR1A_ORACLE_END block, without rerunning Wolfram here:
python verify_regeneration.py --regenerated /path/to/reproduced-rawjson.json
```

The verifier **fails closed** on changed case order, metadata, nonfinite p/U/power/impedance or a normalized component difference >1e-12; this is a *numerical regeneration comparator*, not Gate A scientific acceptance. Store Wolfram runtime/version, captured independent raw JSON, verifier stdout (including regenerated SHA256), source/golden SHA256 and reviewing actor in the receipt. Re-run this when WL source/golden changes. Hosted GitHub Actions has no licensed Wolfram by default: its enforced checks are pinned candidate bytes, Python 3.11–3.13 full-state tests and exact-head evidence SHA. **CI does not execute Wolfram; do not claim it does.**

**Prior independent audit receipts:** At candidate `53df08f3d4c74baa91fad0def93a6286c64d9b37`, [Actions run 39012240675](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39012240675) yielded three audited exact-head artifact ZIPs; manifest/CRC passed, 24 p/U and power states numerically matched across Python 3.11–3.13, and the Wolfram 15.0.1 independent re-evaluation numerically reproduced the full 24-record source. The 3.11 JSON bytes were *not* identical to 3.12/3.13: 13 small N/O condition-number diagnostic variations and four dependent OG-4 observation digests differed. Never demand or claim byte-identical **whole evidence** across runtimes; preserve numerical p/U/power equivalence and per-run self-hash instead. This prior review does **not** validate a future modified HEAD; fresh CI and receipt review remain required.

**Post-integration scientific backlog:** prospective independent Gate A with physical-law mutant matrix across N/O/M × eight anchors, scale-defined whole-network conditioning/refusal criteria, separately scoped pole-safe frequency stress, predeclared thresholds and repeatability controls; new confirmation artifacts and independent Gate C (`SUPPORTED_LIMITED` / `INCONCLUSIVE` / `REJECT`) in later work. A closed distal nasal end leaves its upstream reactive nasal side branch coupled to J; this is not VP-junction closure.

---

## NR-1a post-audit candidate hardening (2026-10-17; NOT ADOPTED)

This branch adds *research-only* fail-closed comparison checks before scientific acceptance. The comparator now rejects nonfinite full-state, powers, transfers, impedance and diagnostics; verifies full case/blueprint/backend/observation provenance; and recomputes power/impedance/transfers from p/U. The M-only research observation receives an experimental digest; N/O continue to verify the adopted OG-4 canonical observation digest without changing Core. Negative tests inject nonfinite and stale identity/derived data.

The Wolfram global 12-equation solution at B's mouth-closed quarter-wave pole `f*=343/(4*0.09)=952.7777777778 Hz` is finite; a separate diagnostic-matrix stress test checks f* and f*±1e-6 Hz. The existing M recursive **8-frequency** contract is deliberately unchanged, and its local pole guard is not a global conditioning certificate. New law-level mutants at 733 Hz expand detection; a complete predeclared all-anchor mutant matrix and independent artifact audit are still outstanding.

**No retrospective Gate A pass:** code/test updates are candidates pending exact-HEAD CI and independent review. Historical success at `a0912c2` remains valid for that earlier HEAD alone. Gate A and Gate C are not approved.

## 2026-10-17 NR-1a exploratory implementation ledger — PRE-GATE-A

| Task | State | Explicit evidence |
|---|---|---|
| Scope correction: distal terminal ≠ VP closure | WRITTEN / proposed | [WORK_ORDER](./WORK_ORDER.md); N/O/M are terminal-only |
| Independent 12-equation global Wolfram source | EXECUTED candidate | [Source](../../../experiments/041_nr1_static_oral_nasal_route/wolfram/global12_oracle.wl); 24 records, all 6 complex endpoint p/U states each in [JSON](../../../experiments/041_nr1_static_oral_nasal_route/wolfram/global12_oracle.json) |
| Separate Core N/O and new research-only M | IMPLEMENTED CANDIDATE | [run.py](../../../experiments/041_nr1_static_oral_nasal_route/run.py); existing Core OG-4 production unmodified |
| Negative controls and 24 full-state comparisons | TESTS AUTHORED; CI RESULT TO REVIEW | [pytest](../../../tests/test_experiment_041_nr1a.py) |
| Exact HEAD, 2-run evidence + independent review | NOT YET VERIFIED | [CI workflow](../../../.github/workflows/nr1a-research.yml); inspect actual runs/artifacts before any pass claim |
| Gate A preregistration freeze / independent acceptance | NOT ACCEPTED | Separate independent physics + API review and explicit decision required |
| Gate C supported-limited adoption | NOT ACCEPTED | No production or physiological claim |

Candidate units/normalizations: p_ref=1.372 Pa, U_ref=1e-6 m3/s, P_ref=0.5*p_ref*U_ref W; end-to-end complex full-state max error <=1e-10 (not approved), power error <=1e-10 (not approved), per-tube/junction and load-law physics <=1e-10 (not approved). Core N/O retains its own stricter normative checks and refusal types. New M recursion has only an explicit denominator/reconstruction guard and must not falsely claim having implemented a full independent condition-number monitor. Freeze missing singularity controls and analysis prior to approving Gate A.

**Critical status separation:** The executed Wolfram global oracle is independent from candidate Python recursive logic, but Python production Core and research candidate have not yet been proven to agree unless an observed exact-HEAD CI run with all artifacts is inspected. Tests and source in a Draft PR are not numerical trial acceptance, and cannot independently approve their own model.

**2026-10-17 NR-1a scope correction — research only, NOT PREREGISTERED.** Earlier rows that appear to equate nasal-path closure with velopharyngeal (VP) closure are future NR-1b proposals, NOT first-pass capabilities. Immediate candidate cases: N=(B matched, C distal rigid_closed), O=(B matched,C matched), M=(B distal rigid_closed,C matched). N/O should use actual approved OG-4, M requires separate experiment-only law and must remain UNSUPPORTED in published OG-4. A closed distal nasal tube remains acoustically coupled upstream; it does not model actual VP shutoff. [WORK_ORDER](./WORK_ORDER.md) sets the executable scope. The [exploratory 733-Hz Wolfram probe](./WOLFRAM-PROBE.wl) executed successfully, but does NOT constitute frozen/accepted Core-vs-Wolfram evidence or a scientific adoption. Gate A/B/C ledger remains unstarted.

# NR-1 hypothesis protocol and experiment ledger — preregistration *draft*

**STATUS: PROPOSED / NOT FROZEN / NOT RUN / NOT ADOPTED** as of 2026-10-17 JST.
Parent: [Core #115](https://github.com/ryonakayama234/morphoacoustics/issues/115). Source architecture [SYSTEM](./SYSTEM.md), candidate data [DATA](./DATA.md).

## Scientific question
Does a precisely typed, passive linear oral–nasal branch circuit predict reproducible **different frequency-domain small-signal acoustic loading and routing** when VP coupling and terminal closures are changed, without falsely claiming that the model generates nasal breathing, biological velum motion, or a voice waveform?

### H0 — falsification target
Under intervention, network solution is indistinguishable where the law predicts change; or conservation/port-ID/orientation fails; or an independently assembled global-equation oracle disagrees; or invalid/unsupported inputs accidentally yield a plausible observation.

### H1 — bounded positive claim
For a separately fixed, supported passive 1D oral/nasal geometry, an explicitly lawful change in boundary/VP coupling yields the **predicted complex endpoint p/U, junction balance, conservation and changed input/output transfer**, consistent with *independently assembled* equations and mutation tests. A pass licenses only that specific linear network phenomenon.

## Gate A: freeze BEFORE Gate B implementation
- [ ] Cite adopted OG-4 and candidate OG-5 input models; select the **smallest exactly supported** topology or explicitly require a new separately versioned scope. Do NOT relabel a generic graph as OG-5 accepted.
- [ ] Freeze geometry, materials (rigid wall), common medium, positive area, incidence/excitation phasors, output loads, VP representation/closed-limit semantics, exact frequency grid and reference data. Distinguish a VP area change from a terminal nasal closure.
- [ ] State outward sign at every port; state frequency phasor convention, transfer ratio normalization, radiation *impedance* model and source normalization. Use full complex values, not magnitudes alone.
- [ ] Derive independent global complex linear system in Wolfram; avoid relying solely on code under test, and preserve fixed oracle data + hashes.
- [ ] Freeze absolute/relative/scaled tolerances with conditioning-aware rejection; define singular, nonfinite, invalid, unsupported, and execution failure boundaries; include exact-head evidence format and repeat-run hash.
- [ ] Independent physics + ABI + safety review of Gate A BEFORE claiming preregistration freeze.

## Minimum three interventions (not yet numerical fixtures)
| ID | Hypothesis intervention | Expected primary observables | Prohibited inference |
|---|---|---|---|
| A | Mouth open, nasal path physically closed by a valid terminal/coupling law | Oral transfer and input impedance of the remaining circuit; no nasal radiated contribution under an ideal closure assumption | A literal zero-area tube is not automatically lawful |
| B | Mouth open, nasal path connected through finite VP element and a validated nasal termination | Nonzero nasal endpoint acoustic contribution; load-/geometry-dependent peaks or notches; changed complex input impedance | Not proof of living nasal vowels |
| C | Oral terminal sealed, valid nasal path open | Revised reflected/transmitted complex states and changed radiating endpoint; power balance with proper seal boundary | Not yet sound of breathing through a closed mouth |

## Independent verification and deliberate wrong laws
1. **Reference:** separately assembled Wolfram full global complex solution (all endpoints) and passive port energy audit.
2. **Mutation A:** wrongly enforce particle velocity continuity across different areas instead of *volume flow*; compare against independent full state.
3. **Mutation B:** reverse an oriented port sign; must be detected by endpoint/current/power evidence.
4. **Mutation C:** swap nasal vs oral module identity while keeping geometry: canonical structural provenance changes, physics invariances distinguished from labeled output.
5. **Mutation D:** change VP path while holding frozen source and oral tube: input/load and relevant transfer change where theory predicts, never post-hoc EQ.
6. **Refusal:** invalid graph, duplicate/dangling port, nonexistent terminal law, nonfinite/negative parameters, out-of-scope valid topology, mathematically unresolved case; never return WAV/partial physical results as success.

## Demonstrative arithmetic only — *not* a frozen experiment or a simulation of anatomy
At an ideal common-pressure junction with **two matched purely real terminal admittances** and the same medium,
Y_o=A_o/(rho*c), Y_n=A_n/(rho*c). The fraction of power *delivered to the two terminal paths* is Y_n/(Y_o+Y_n). For A_o=3 cm²: A_n=0.3 cm² gives about 9.09% nasal and 90.91% oral; A_n=1.5 cm² gives about 33.33% nasal and 66.67% oral. Verified by Wolfram Language 2026-10-17. This is an illustrative **algebraic limiting case only**, not source-power efficiency, generic nasal sound spectra, an accepted VP parameter, a reference fixture, or research pass.

## Evidence ledger
| Date | Gate / data | Outcome | Exact commit + linked artifacts | Meaning |
|---|---|---|---|---|
| 2026-10-17 JST | Gate A planning | DRAFT ONLY | [Issue #115](https://github.com/ryonakayama234/morphoacoustics/issues/115); proposal SYSTEM/DATA/EXPERIMENT | Unfrozen conceptual hypothesis and engineering guardrails |
| — | Gate A protocol acceptance | NOT STARTED | — | Requires review/frozen values |
| — | Gate B implementation & independent Wolfram comparison | NOT STARTED | — | No measured pass to report |
| — | Gate C scientific decision / post-merge verification | NOT STARTED | — | No production or scientific adoption |

## Future evidence record required per run
- Case ID + changed **one** physical factor + unchanged controls.
- Exact repository commit/branch, complete backend/module/law versions, schema versions, all asset/content digests.
- Full inputs with SI units, body/module revisions, scenario boundary loads and excitation, frequency grid, port orientation.
- Every complex p/U endpoint; input impedance and declared transfer; signed mean acoustic power, conservation and solver conditioning, failure result if any.
- Independent Wolfram executable source/frozen goldens, test runner, repeat-run outputs, negative-control margins, CI links, SHA256 artifacts, known scientific limitations and post-hoc amendments.
- Independent reviewer assessment and signed-off scoped decision; distinguish machine numerical conformance from biological/acoustic perceptual validation.

## Related independent tracks
- OG-5 review [#109](https://github.com/ryonakayama234/morphoacoustics/issues/109)
- Materials EM-1 [#87](https://github.com/ryonakayama234/morphoacoustics/issues/87)
- Nasal breath turbulence/nonvocal near-field [#53](https://github.com/ryonakayama234/morphoacoustics/issues/53)
- Creator staged adoption [Studio #12](https://github.com/ryonakayama234/morphoacoustics-studio/issues/12)

## Sources
- Velopharyngeal opening, nasal antiresonances: https://pmc.ncbi.nlm.nih.gov/articles/PMC8492006/
- Acoustic side-branch waveguide precedent: https://pmc.ncbi.nlm.nih.gov/articles/PMC2677336/
- Nasal emission and aeroacoustic turbulence (distinct regime): https://pmc.ncbi.nlm.nih.gov/articles/PMC7043896/
