# EL-NF5 — D0 preregistration / design-only research protocol

**D0 date 2026-11-01 JST. Owner approved documentation-only. All hypotheses, thresholds, experiments and freeze criteria here are PROSPECTIVE PROPOSALS, not executed or validated. Immutable D0 commit is the final SHA of this documentation-only branch state recorded in the Draft PR (not a signed scientific approval).**

## 0. Research scope and epistemic boundary

Question: on a **partially measured, stationary, identified head** and fixed measured source/receiver convention, can independently modeled timing, interaural log magnitude, common spectral magnitude and phase detail improve spatially withheld **bilateral relative HRIR** vs simple local and regularized controls, with empirically calibrated refusals and no numerical contradictions?

The experiment is a measured-data transfer surrogate, not fluid/structural/head PDE physics. No absolute eardrum pressure, unmeasured-head zero shot, subjective ASMR, 1 cm, contact, movement or source/load coupling. Historical NF4 measured results (especially low-frequency C4 regression, B0 posthoc superiority) are **known to the researcher**. A different split of the same original data does not remove that exposure.

## 1. Falsifiable hypotheses and component hierarchy

H1 **timing:** arrival-separated estimation (F1) reduces measured ITD absolute error vs B0/strong local references; compare F1 to same settings without arrival separation.

H2 **interaural magnitude:** F2 common log magnitude `m` plus `ell` improves four-band ILD without lower-band regression relative to identical ear-independent magnitude estimate. Treat left/right channel names as fixed measured geometry, not arbitrary stereo swapping.

H3 **full reconstruction:** F3 models/retains per-ear spectral detail and residual phase, and reconstructs two causal compatible HRIRs while preserving timing and magnitude improvements. Reject a magnitude-only reconstruction which passes ILD but breaks phase.

H4 **complexity null:** B0 measured nearest may outperform regularized spatial fields. Model complexity is not rewarded without demonstrated benefit. B0 mandatory for all final gates.

H5 **support:** a separate empirical calibration of support/error-risk can abstain on out-of-domain queries while preserving >=80% coverage and avoiding unreported error tails. Refusal is not a correct prediction.

These hypotheses are evaluated separately. The only potential fully integrated G3b primary model is **one preselected F1/F2/F3 candidate**; post-final selection forbidden.

## 2. Measurands, analysis and conventions

- Original measured bilateral `h_e[n | q,head]` at the dataset's physically qualified recording plane, original sample rate, response length and declared zero-time/Data.Delay origin; fixed listener-local coordinates `q=(r,az,el)`.
- Forward FFT `H_e[k]`. Unless a prospectively documented device artifact requires another fixed method, compute band energy on the complete measured original FIR (same duration and FFT choices for all models) `E_e,b=sum_{k in band} w_k |H_e[k]|^2` using real-FFT unique positive bins and identical bin weights; `ILD_b=10 log10((E_L,b+eps)/(E_R,b+eps))` dB. `eps` must be derived from training-only noise floor; if not estimable, invalidate below-floor bands and count them in data eligibility (never cherry-pick after prediction).
- Four bands (Hz): [500,1000), [1000,2000), [2000,4000), [4000,8000]. Require Fs>16000 and adequate resolved bins. Prespecify DC/Nyquist and bin-edge rules and a shared FFT zero-padding size before final scoring; FFT padding is numerical interpolation, not new physical detail.
- Position error `e_ILD(q) = mean_b |ILDhat_b(q)-ILDtrue_b(q)|`. **Primary statistic:** median `e_ILD` on accepted positions. Report per-band errors, per-head errors, S1/S2 separately, and accepted/all eligible denominators.
- ITD is the signed (right-minus-left) lag of maximum normalized L/R cross-correlation after a fixed 500–1500 Hz analysis band, searched in [-1,+1] ms with preregistered 8x time interpolation; absolute error in microseconds. Exact interpolation/window/filter implementation must be made deterministic and frozen in G1 before development model selection; method is not adjusted after G3b truth.
- Centered monaural spectral shape: per-ear log-magnitude dB minus the per-ear mean over eligible 500–8000 Hz bins, then RMSE in dB; aggregate per query and report both ears. Common gain and absolute distance law are not inferred.
- Report ILD error p95 and time-domain reconstruction residual / pre-onset energy / nonfinite states. Causality and numerical guards assess a *declared finite measured response window*, not a proof that physical transfer is minimum phase.

## 3. Comparison, ablation and model selection

**Baselines:** B0 training-only nearest recorded 3D Cartesian source position, deterministic tie: source original index; B1 inverse-distance weighted valid-neighbor original bilateral HRIR; B2 strictly in-hull convex/local interpolation where geometry allows (non-covered cells refused; report); B3 regularized spherical harmonics/radius model selected on development. Unsupported methods cannot be called a favorable baseline. **B0 is mandatory even when B3 was prereg-selected historically.** Strongest separate baseline B* is selected *only on development data* by the selection rule below.

**Interventions:** F1 timing separated + training-only bilateral magnitude/phase; F2 F1 + common `m` and interaural `ell` instead of independent-ear log magnitudes; F3 F2 + train-only spectral detail and residual-phase modeling, plus phase-complete bilateral reassembly. Mandatory ablations: no-arrival, independent-ear instead of m/ell, no-residual-phase, no frequency-dependent complexity; oracle replacements (true cues) for diagnosis **only**, never a final predictor.

All source-coordinate queries, held-out target sets, model training positions and performance metrics are held identical across comparable methods. When a baseline refuses, report matched-coverage subsets and baseline's own total coverage; an invalid baseline must not be silently dropped merely because it scores worse.

**Frozen pre-final selector:** fit candidates using fit-role data; hyperparameters and any frequency-adaptive representation/crossover are searched on development/selection only; calibrate rejection thresholds on disjoint calibration only. Candidate eligibility = >=80% selection+calibration eligible query coverage, all numeric/causal regression checks, and secondary guards. Among eligible candidates choose lowest pooled development median e_ILD; tie tolerance <=0.01 dB breaks toward F1 then F2 then F3 and lower-order/smaller interpolation neighborhood. Define B* separately as lowest development median among eligible B0/B1/B2/B3, tie to simpler model. **Neither selection can look at final acoustic truth.** Candidate or B* absent → stop/inconclusive, not opportunistic relabel. All final rows report B0 and B* on candidate accepted positions regardless of their relative final ranking.

Exact small hyperparameter grids, magnitude-floor estimator, train-only arrival/phase policy and optional frequency-adaptive crossover grid are software-implementation protocol details that **must be frozen by a named prospective design amendment before any new final acoustic truth is opened**. This D0 fixes the variables, causal degrees of freedom, selection loss/tie rule and anti-peeking boundaries; the remaining concrete grids are explicitly NOT YET FIXED. Do not claim full operational preregistration until those append-only details are frozen.

## 4. Original-data roles and G0 geometry-only amendment

Historical Aalto, KEMAR and SCUT records already used in NF1–NF4 are **G3a development/diagnostic only**. New truly independent original bilateral measured data for G3b are **NOT QUALIFIED / NOT ACQUIRED**. NHK 2026 HATS study is only a source-discovery candidate, not guaranteed data access; actual dataset file/terms must be verified. See [DATA](DATA.md) and [G0_DATA_QUALIFICATION](G0_DATA_QUALIFICATION.md).

For any newly qualified original:
- G0 reads source geometry/headers only. Define deterministic angular block partition and excluded angular buffer; proposal default 20° azimuth ×10° elevation blocks and 5° buffer. Publish exact cell allocation and checksum in **G0 v1.1 BEFORE new final Data.IR values are accessed**; geometry-only changes must be documented and cannot reflect acoustic outcomes.
- Establish four disjoint acoustic roles: fit, hyperparameter selection, support calibration, final. For one newly measured head these roles use spatial angular blocks; for multiple independent heads, retain headwise groups and report each head. Known final geometry is permitted; known final HRIR **is not**.
- **S1:** wholly withheld angular blocks with in-range radii in training. **S2:** withheld angular blocks and withheld *interior radial shell* for that head; target radius must have shorter and longer training radii. No same-angle final HRIR may slip into fit, including across radii.
- A spatial/angular block, not a position, channel, frequency bin or radial-repeat, is the resampling unit. Aim >=8 accepted effective blocks per S1 and S2; else scientific inference INDETERMINATE. If spatial dependence makes this count artificial, qualify the blocks or stop.
- Coverage denominator = **ALL geometrically eligible final positions**; support >=80% **separately S1 and S2**. Accepted-position accuracy must be compared on the exact same positions. Record all refused eligible positions and their reasons, without hiding them from coverage.
- Independent new source cannot prove extrapolation beyond measured support; no subject-population generalization from one HATS.

## 5. G3b integrated primary gate (prospectively proposed)

The candidate selected in §3 passes **only if ALL**:
1. `median e_ILD(candidate) <=0.85 * median e_ILD(B0)` **AND** `<=0.85 * median e_ILD(B*)` on **identical accepted positions**.
2. Spatial-block-paired bootstrap 95% CI lower bound for each positive baseline-minus-candidate error reduction **> 0**; family is an intersection-union requirement (both comparisons must pass; no success declared from either alone). Fixed 2,000 cluster draws; RNG PCG64 seed 20261101; if any material adaptive comparison is added, pre-register multiplicity correction before final. Separate component-level hypotheses use Holm adjustment where applicable.
3. S1 and S2 each have strictly positive improvement against B0 and B* and >=8 independent accepted spatial blocks (confidence intervals pooled only when meaningful).
4. Candidate support coverage >=80% of **all eligible final** queries in S1 and separately in S2, not just predicted/computable rows.
5. ITD absolute-error median <= B0 median +25 microseconds AND <= B*+25 microseconds; centered monaural spectral-shape RMSE median <= each matched baseline +0.5 dB; four-band ILD e_ILD p95 <= each baseline+1.0 dB.
6. Mean over 500–1000 and 1000–2000 Hz band absolute ILD error median <= each baseline +0.25 dB (prospective low-frequency guard; chosen as conservative *engineering guard*, not auditory JND).
7. All reconstruction identity, signal length, explicit time origin, Hermitian/real FIR, phase-consistency, nonfinite, overflow, reference-plane and invalid-support guards pass. Any silent fallback, final-truth leakage, invalid rights/measurement source or inconsistent prediction-seal sequence fails.

Report **raw, unfiltered errors for all computable final positions** too; do not optimize abstentions on final. 15%, 25 us, 0.5/1 dB, 0.25 dB and 80% are **engineering decision thresholds, not human perceptual JNDs**. They are not adjustable after final reveal. If geometry/source rights/measurement make a gate unknowable, verdict = INDETERMINATE/BLOCKED, not PASS.

## 6. Separate prospective component validations / freeze-eligible gates

Component evidence may be declared only if explicitly identified *before G3b reveal*:
- **C-TIME (arrival/ITD estimator):** synthetic oracle/coordinate and reconstruction identity PASS; on matched independent G3b positions, ITD median <=0.80 × both B0 and B* and both block-paired improvement intervals lower >0 after Holm correction across candidate freeze claims; S1/S2 both improve, >=80% coverage and >=8 blocks each. ITD measurement uncertainty must be audited; don't award improvement below instrument resolution.
- **C-LEVEL (common+interaural magnitude):** four-band ILD median <=0.85 × both B0 and B* with both block-paired improvement intervals lower >0 after Holm; S1/S2 both improve, 500–2000 Hz guard, coverage and tail constraints as in §5. A correct algebraic decomposition alone is only a numerical artifact, not scientifically validated prediction.
- **C-REASSEMBLY (reconstruction transform):** forward+inverse synthetic oracle exact to declared floating tolerance `relative L2<=1e-9` and original train-only measured round-trip at bounded measurement precision; Hermitian, causal-window, left/right polarity, 0/Nyquist and phase/time checks. This may be frozen as **VERIFIED_NUMERICAL_TRANSFORM only**, not as a receiver-prediction capability. Any claim of experimentally validated reconstructed HRIR also requires the integrated §5 G3b.
- **C-SUPPORT:** cannot independently be frozen as an interchangeable classifier. It can be frozen only **with a specific hash-locked predictor and calibration set**, with >=80% S1/S2 final coverage, appropriate rejection reasons and matched accepted p95 <= both baselines+1 dB; uncertainty-calibration diagnostics and independent reviewer acceptance. Coverage/precision tradeoff is recorded, including refused positions.

Freeze approval also requires independent G5 scientific/code reviewer, correct reference-plane and rights audit, complete source/training split hashes and no major unresolved regression. G4 listening is required only to claim perceptual quality, not limited numeric validity. See [COMPONENT_FREEZE_POLICY](COMPONENT_FREEZE_POLICY.md). **No component is frozen by this document.**

## 7. Evidence and final-truth seal

- D0 commit SHA, any G0 v1.1 SHA, software model/config hash, original source SHA256, role and query hashes, source rights, exact env/library versions, selected model and B*, all thresholds, calibration decisions and predicted final outputs must be immutable/auditable **before first G3b final acoustic truth read**.
- Save at least signed-or-SHA256-hashed prediction seals with checkable manifest timestamps and controlled run boundaries, numeric non-reconstructive receipts and all refusals. Raw publisher measured IR/audio and restricted model coefficients must not be redistributed.
- Evaluation uses an independent-from-predictor implementation to recompute ILD, ITD, spectrum, bootstrap/coverage, refused reason distribution and final verdict. Same author arithmetic audit is **not** a distinct human science review.
- G3b output is append-only, whether PASS, NEGATIVE, INVALID, BLOCKED or INDETERMINATE. No posthoc coefficient/crossover/split tuning against opened final truth. Any successor requires a new D0 and genuinely new blind evidence.
- Only a **separate authorized research implementation** stage may begin coding. This PR is docs only.

## 8. Decision nomenclature

`D0_DESIGN_DOCUMENTED` (no model/evidence) → `G0_BLOCKED / QUALIFIED_LIMITED` → `G1_G2_TECHNICAL_ONLY` → `G3A_DEVELOPMENT_ONLY` → `G3B_PASS_LIMITED_NUMERICAL / REVISE_OR_REJECT / INDETERMINATE / INVALID / BLOCKED` → `G5_REVIEWED_COMPONENT_CANDIDATE` → optional `VALIDATED_COMPONENT_FROZEN` → independently authorized `ADOPTED_CAPABILITY`.

A CI process exit 0, preregistration document, arithmetic audit or historical test score by itself is **not scientific success**.
