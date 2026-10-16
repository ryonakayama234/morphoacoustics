# OG-5 Gate A — Wolfram exploration receipt, 2026-10-16 JST

**EXPLORATORY / NOT PREREGISTERED / NOT CORE-VALIDATED / NOT ADOPTED.** Scientific issue [#109](https://github.com/ryonakayama234/morphoacoustics/issues/109), [protocol](./og5-gate-a-protocol.md), [runnable independent Wolfram script](./og5-gate-a-oracle.wl).

## Conditions

Five uniform lossless rigid tubes, two ideal 3-port junctions A->(B,C), B->(D,E); rho=1.2 kg/m^3, c=343 m/s; lengths A/B/C/D/E = 0.08/0.09/0.06/0.07/0.05 m, areas A/B/D=0.0003, E=0.0006 m^2, C variable; prescribed peak source U_A.in=1e-6 (1+0.4 i) m^3/s. All results below at 733 Hz, D/E matched. Phasor exp(+i omega t). Reproducible independent paths: 20x20 globally coupled scaled complex linear equations; separately recursively assembled network input impedances + inverse tube transfer matrices to construct **all 20 full-port states**.

## Re-executed three successful independent Wolfram cases

| C area [m^2] | C terminal | p(A.in) [Pa] | Input / terminal total mean power [W] | C share of mean input power |
| --- | --- | --- | --- | --- |
| 0.00015 | matched | 1.91455473103526536 + 0.23147567288386767 i | 1.0035725000944062e-6 / 1.0035725000944062e-6 | 0.571271323773400 |
| 0.0006 | matched | 1.25823347162437859 + 2.10241425481059146 i | 1.0495995867743076e-6 / 1.0495995867743076e-6 | 0.842019872858848 |
| 0.00015 | closed | 0.66655668574530149 - 0.12945139460527360 i | 3.0738806395159602e-7 / 3.0738806395159602e-7 | 0 |

After pressure/flow normalization, the maximum full-20-complex-state global-versus-recursive discrepancy was at working precision zero for matched cases and about 1.68e-49 for the closed-C case; both junction normalized flow residuals and source-minus-terminal mean power residuals were zero at displayed working precision. This demonstrates *internal agreement between two constructions for three test cases*, NOT actual new Core correctness, independent human review, production condition bounds, or a complete 144-case approval.

## Failed exploration is part of the record

1. First *unscaled* 20x20 Solve produced a Wolfram RowReduce badly-conditioned-matrix warning from mixing Pa and m^3/s magnitudes. Replaced equations with fixed dimensionless P=p/Pref and Q=U/Uref. Previous 733 Hz samples produced scaled matrix condition numbers approximately 22.68 for C=0.00015 matched, 18.29 for C=0.0006 matched.
2. First scripted all-port Wolfram run emitted ReplaceAll::reps because AssociationThread[allVariables->solve] was constructed incorrectly. Its numeric output is **INVALID and must not be quoted**. Replaced with Thread[vars->LinearSolve[...]] and independently constructed Thread[vars->Flatten[...]]. Reran all three cases; no reported messages. This is a code-assembly correction, NOT physical hypothesis validation.
3. The **144-case** frequency x area x load x input-scale sweep defined in the runnable script has **not yet been executed or independently inspected** as part of this receipt. Any later sweep result must be dated, linked to an exact code blob SHA, and evaluated against the preregistered decision rule without overwriting this three-case record.

## What remains for Gate A acceptance

Run/review 144 proposed discovery cases; independently review branch recursion and phasor signs; freeze finite/condition tolerance with documented numerical rationale; write wrong-law mutation/control outputs; pin executable source blob SHA and raw case-level outputs; decide whether to ratify candidate schema and thresholds. This receipt authorizes no Gate B implementation until Gate A is approved.


## Follow-up post-commit exploration — executed 2026-10-16 JST (never reclassified as blind preregistration)

**Original Draft commit** 3f92f7506860346a89d83a8630c3b2cb8c276e4e froze the executable *candidate* 144-case grid before this sweep execution. Confirmed exact committed Wolfram source blob d0fd961fdfcc6eae0a263d8e17aba87ba60db8b4 (Git blob SHA-1; not a SHA-256 scientific artifact sidecar). WolframLanguageEvaluator ran precisely that fetched file source with a final duplicate summary expression and produced:

- 144 / 144 scheduled evaluations returned computed records at the specified 30-digit solve precision. Maximum normalized disagreement across **all 20 complex endpoint states** between global 20x20 and separate recursive impedance method: **5.682202313875164e-48**.
- Maximum displayed mean input/terminal power relative defect: **0 at 14-digit reporting precision** (NOT proof of mathematically exact zero for all cases); maximum scaled 2-norm matrix condition number **223.7427248146314**.
- These are Wolfram-vs-Wolfram results; no Python Core tree5 candidate exists yet, no signed full case-level archive, no frozen third-party review. This broad positive sweep neither guarantees negative controls nor proves real-body acoustic physics.

An additional independently constructed Wolfram 733-Hz wrong-law mutation run (new [negative control source](./og5-gate-a-negative-controls.wl)) checked that the *correct* 20-state solution does not accidentally agree with three wrong laws:

| Deliberately invalid alternative | Normalized full-port error vs correct physical solution | J1 physical flow defect (dimensionless) | Relative power defect |
| --- | ---: | ---: | ---: |
| Substitute particle velocity instead of volume flow at J1 | 0.471977331827501 | 0.552670737985430 | 0.363572678461091 |
| Reverse sign of B flow at J1 | 0.886740929596392 | 1.038345977473847 | 6.015444270260797 |
| Mismatch C load to Zref rather than its own Zc | 0.418514495908273 | ~0 | ~0 |

**Interpretation:** all three are easily killed by the all-port independent comparator (proposed threshold 1e-10). The wrong matched-load impedance is still a passive load: it *does not* violate KCL or passive power conservation, and therefore **cannot be killed by conservation-only tests**. This is an essential reason to require full-port oracle comparison. This is exploratory mutation evidence; future Gate B must reproduce it against production Core and store case-level raw evidence with SHA-256 sidecars.


## Archive finalized in this Draft PR — 2026-10-16 JST

Individual **144 case-level summary rows** were exported as [og5-gate-a-cases-144-exploratory.json](./og5-gate-a-cases-144-exploratory.json) after the above exploratory sweep, and immediately re-fetched from GitHub and parsed again. Scientific SHA-256 of the exact UTF-8 JSON bytes, computed with Wolfram Hash[ByteArray[ToCharacterCode[...,"UTF-8"]],"SHA256","HexString"], is **8ca71a44a9f6b7562469cff51acc4ab395d7b5144b0bd617c161e7854889ae7b** ([sidecar](./og5-gate-a-cases-144-exploratory.json.sha256)); Git blob SHA-1 **273d6f374eea1db42db527a926ccc86cb7bee1f6**. The re-read counted 144 distinct (f,C-area,C-load,scale) fixtures, zero duplicates, zero nonfinite numeric fields, zero case-level relative-power failures exceeding 1e-10, max cond2=223.74272481463143, max 20-state comparison discrepancy=5.682202313875164e-48.

The archive contains input pressure, source/terminal aggregate power, C power share, 20-state **comparison summary**, condition number and junction residual for each case; it does **NOT** contain every individual complex p/U state or numerical equation matrices. A full raw 20-state Core-vs-Wolfram archive with independent checksum/case-binding verification remains a Gate B requirement. Conversion from high-precision Wolfram values to machine double in JSON may round tiny comparison residuals to zero; the original run summary above retains the high-precision maximum. These receipts are exploratory—not a blind precommitted scientific pass, nor Core verification.
