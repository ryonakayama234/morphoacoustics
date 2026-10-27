# REVIEW — independent pre-implementation architecture/science checklist

**DESIGN_REVIEW_ONLY.** No binary code, test implementation, experimental runner, Core src edit, ASMR runtime feature, Git merge, Studio UI or release is authorized here.

## Review questions (record each as ACCEPT / REVISE / REJECT + rationale)
1. **What can a result prove?** A synthetic passive, lossless rigid tube with numerical Thévenin source and terminal resistance; not measured ear, physiological drum, fixed external real incident field, listening experience or natural ASMR.
2. **Is the variable assignment auditable?** Are ps,Zs,Zt *exogenous absolute* under the 18-case A,L,f intervention? Does p0 remain solved (not prescribed)? Is synthetic equivalent calibration clearly distinguished from empirical source calibration?
3. **Are reference planes, sign, phasor, flow and units unambiguous?** SOURCE_EQUIVALENT is a virtual drive; canal entrance/terminal are separate physical model ports. The "ear" language never assigns these to real probe, pinna or tympanic positions.
4. **Are measurable quantities primary?** Complex p0,U0,pL,UL and two independent power ledgers first; transfer gains, impedance, reflection and phase only derived with nonzero guards.
5. **Can the source-loading effect be tested against a null?** H_total=H_drive*H_canal; matched source gives no length-dependent magnitude change, but phase delay; fixed absolute and normalized load produce distinct interventions.
6. **Does verification really catch common faults?** 18 rows, independent Wolfram scattering values, determinant, 2 energy balances, source loss, negative mutations, refusal classifications, exact SHA references, repeatability and independent audit.
7. **Are new design choices distinguishable from frozen prereg?** New diagnostics/tolerances are prospective, not retroactively credited as Gate A. Scientific FAIL never becomes UNSUPPORTED to improve pass rates.
8. **Is numerical robustness physically interpretable?** Positive source/load and fixed tube are mathematically passive; matrix scaling uses dimensionless ratios for conditioning checks. No "fix" via arbitrary added damping, gain normalization or silently raising precision.
9. **Are responsibilities clean?** Core UniformTube stays unchanged; research solver if separately approved lives in isolated experiments/044; no imports from unmerged EL-R1, no cloned Core solver in asmr, no Studio and no product type/API changes.
10. **Is future Scene adoption possible without a fake promise?** Reference planes, source/load and sample/time contracts must be explicitly reconciled with measured HRTF and ear-canal termination before a causal binaural renderer is approved. Optional morphoacoustics_asmr adapter must be released/version-pinned and explicitly enabled; future Studio Scene UI changes need creator authorization.

## Blocking decisions required before coding
- Which **secondary** H_B6-H_B8 diagnostics have testable numeric tolerances and which remain explanatory only? Freeze an additive Gate B protocol *before* source coding. Do NOT rewrite Gate A.
- Confirm research-local input envelope and the exact interpretation of INVALID/UNSUPPORTED/NUMERICALLY_UNRESOLVED including divisions by small p0 and zero source pressure.
- Confirm oracle decoder maps the 18 array columns to explicitly named quantities and that source-json reproduction is independent of the Core matrix under test.
- Confirm non-blinded Gate A feasibility is described transparently and external scientific/physical review is not falsely claimed from own GitHub identity or CI.
- Decide STOP if the scientific interface requires changing Core production types or physically meaningless pressure-plane conversion.

## Approved future development sequence (conditional, not execution)
After explicit DESIGN_READY: pin source SHA (Gate A + this reviewed design), create new research-only implementation Draft; freeze supplemental protocol; write minimal isolated solver using existing Core UniformTube; run positive and negative tests; update SYSTEM/DATA/EXPERIMENT/RESULTS together; obtain exact-head CI and independent review; record GO_LIMITED_NUMERICAL, REVISE, REJECT or INDETERMINATE. No automatic merge. Separate Gate C for measurements, Gate D for perceptual/Studio, and dedicated public API promotion PR.

## References / specific limits
- [Frozen Gate A PR #158](https://github.com/ryonakayama234/morphoacoustics/pull/158), [Issue #157](https://github.com/ryonakayama234/morphoacoustics/issues/157), [EL-R1 PR #153](https://github.com/ryonakayama234/morphoacoustics/pull/153).
- [ASMR ARCHITECTURE](../../../asmr/ARCHITECTURE.md); [Core invariants](../../invariants.md); [Studio Workspace V2 adopted design](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md).
- [Nørgaard et al. 2018: undesirable parallel components in Thévenin calibration](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856597/)—measurement pitfalls, **not** validation of this fixture.
- [Nørgaard et al. 2022: calibration waveguide geometry and least squares](https://pmc.ncbi.nlm.nih.gov/articles/PMC8807002/)—future empirical Gate C relevance.
- [Pinna/head/ear-canal SOFA convention](https://www.sofacoustics.org/mediawiki/index.php/SimpleFreeFieldHRIR)—reference plane and load interface must be audited before integration.
