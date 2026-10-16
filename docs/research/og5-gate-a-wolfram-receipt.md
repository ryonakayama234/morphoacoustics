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
