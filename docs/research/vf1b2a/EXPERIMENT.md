# VF-1B2a EXPERIMENT — preregistered scientific pilot
**Pre-source registration**, 2026-10-27 JST, issue #215. NO measurements have yet been run at this point. Source base main `e05e3274ad69bfb9202816049f6661a18ba39ec0`. VF-1B1 cannot be independently Codex-certified yet because Codex review replies explicitly say usage limit exceeded; this independent rigid-glottis study may proceed without using or promoting that candidate.

## Hypotheses
H0: toy Bernoulli+declared geometric separation closure is internally inconsistent or fails analytic reference tests. H1: it is numerically consistent for the declared 1D, **rigid** conditions while leaving G2 validation unresolved. Its output CANNOT establish a realistic pressure profile, viscous boundary-layer separation, or tissue work.

## Frozen protocol
- Baseline `rho=1.21kg/m³`, `L=0.006m`, `Pup=800Pa`, `Pout=0Pa`, `Cd=0.7`, sample grid `N=41`.
- Three frozen shapes: parallel `[A0,AL]=[3e-5,3e-5] m²`, convergent `[6e-5,3e-5]m²`, divergent `[3e-5,6e-5]m²`.
- Controls: `Pup=0` parallel, `Pup=400` parallel, `Cd=1` parallel, divergent `N=161` geometrical sampling refinement. If `Pup=0`, q=0, p=0; do not claim a physically meaningful separation point.
- Divergent analytic separation at `zsep=0.0012m` and area `3.6e-5m²`, both from linear geometry and fixed ratio `1.2`. Convergent/parallel `zsep=L`. Predeclare qualitative pressure sign: at divergent narrow throat with positive flow `p(z=0)<Pout` under this particular closure; post-separation p=Pout. **This sign is a consequence of the hypothetical model, not a prediction established by experiments.**
- Analytic flow scaling `q(400Pa)/q(800Pa)=sqrt(1/2)` same geometry, `q(Cd=1)/q(Cd=0.7)=1/0.7`; `q/Asep=Cd*sqrt(2∆p/rho)`. Verify no negative pressures for zero drive and not confuse q with pressure.
- Energy identity: `(Pup-Pout)*q` equals named declared farfield power loss by definition, not an independent physical validation; adversarial corruption of receipt's flow, profile pressure, or power MUST fail comparison/reconstruction controls. An analytic oracle may independently reconstruct q and separation from input geometry; do not import production-model functions into the independent tests.
- Freeze G1 numerical error tolerances: analytical `q` relative <= `1e-12` with absolute floor `1e-15 m³/s`; separation `z` <=`1e-12m`, area <=`1e-15m²`; each profile pressure <=`1e-8Pa`; flow conservation absolute <=`1e-14m³/s` when measured at all samples; farfield bookkeeping power <=`1e-10 W`. Resolution refinements cannot change analytic q or zsep beyond tolerances.
- Invalid input negative/zero area, nonpositive rho or length, Cd outside (0,1], too-small sampling, nonfinite, reverse pressure, bool-as-number; refuse visibly.
- Dedicated CI must execute tests first; runner always archives raw results including failure. Full scientific PASS requires actual independent test receipt; no "green" due to only the runner succeeding.

## Scientific decision
`G0,G1`: testable consistency. `G2`: **not certified** until independent measured numeric pressure tap profile / uncertainty and a model-selection criterion are sourced. `G3`: rigid geometry **not a phonator**. `G4`: unchanged NO-GO. **STOP before moving-wall FSI** if pressure/force law is not energetically conjugate or independent review remains unavailable; report as explicit dependency blocker with GitHub traces rather than quietly copying #214 into main.

## External references
- [Deverge 2003](https://pubmed.ncbi.nlm.nih.gov/14714815/) rigid glottis experiments.
- [Zhang 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2646589/) influence of separation location.
- [2023 Scientific Reports reference for heuristic 1.2](https://www.nature.com/articles/s41598-023-48080-x).
- [Scherer-related static pressure measurements (PMCID PMC4804921)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4804921/).


## Executed results and decision — 2026-10-27, append only
**Historical RED:** [CI #40425826631](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40425826631) **FAIL**, 15/16 tests successful, 1 failure from incorrectly classifying `Pup=0` as an invalid parameter **in the test itself**; 7/7 flow fixtures computed, actual scientific verdict `NUMERICALLY_UNRESOLVED`. Raw evidence ZIP artifact ID `12699513144`. Fixed by isolated test update `ee7f522`, which leaves model equations unchanged and refuses fake test receipts.

**Source HEAD PASS:** `ee7f5224596dd2cf47dc6996b2b4365801e49867`, [dedicated CI #40425929420](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40425929420) **SUCCESS**, 16/16 stdlib tests, seven rigid cases and seven declared reference controls success, valid self-hashed `vf1b2a_receipt.json`, artifact ID `12699682538` (expires 2027-01-25).

### Actual model-predicted SI metrics
| Fixture | q [m³/s] | zsep [m] | Entry pressure relative to outlet [Pa] |
|---|---:|---:|---:|
| Parallel 800 Pa, Cd .7 | 0.0007636363636363637 | 0.006 | 0 |
| Convergent 800 Pa, Cd .7 | 0.0007636363636363637 | 0.006 | +294 |
| Divergent 800 Pa, Cd .7 | 0.0009163636363636364 | 0.0012 | -172.48 |
| Parallel 0 Pa, Cd .7 | 0 | 0.006 (geometric-only, inactive) | 0 |
| Parallel 400 Pa, Cd .7 | 0.000539972451087909 | 0.006 | 0 |
| Parallel 800 Pa, Cd 1 | 0.001090909090909091 | 0.006 | 0 |
| Divergent 800 Pa, Cd .7, 161 samples | 0.0009163636363636364 | 0.0012 | -172.48 |

All sample traces and tamper tests agree **with the declared algebraic closure**, not independently observed wall pressure, boundary-layer flow or human larynx physics. Parallel 800 Pa far-field reservoir input `800*q=0.610909090909091 W`; the same term is DECLARED dissipated by the toy closure, so the identical numbers are **not** independent energy evidence. Rigid-wall work exactly 0 W by assumption. The paper-supported 1.2 criterion is an empirical heuristic, not a universal separation predictor.

### Gate and HOLD boundary
- G0: `PASS_RIGID_NUMERIC_RECEIPT` on source SHA; raw red history preserved.
- G1: `PASS_ALGEBRAIC_QUASISTEADY_PROXY` on source SHA; checks are model-consistency only, not independent CFD/FSI.
- G2: `INDETERMINATE_NO_INDEPENDENT_NUMERIC_PRESSURE_DATA`. Literature demonstrates flow separation/pressure-profile importance; this project has not matched a specified real pressure-tap array with uncertainty.
- G3: `NOT_APPLICABLE_RIGID_NO_TISSUE`; any apparent self-oscillation or wall work claim is prohibited.
- G4: `VOICE_NO_GO`.
- **VF-1B2c moving-wall FSI remains HOLD:** independent exact-head code/physics review unavailable at VF-1B1 Draft #214 because Codex bot explicitly returned **usage limit exceeded**, the assumed Cd/area ratio are not independently calibrated against a numeric pressure dataset, and no power-conjugate moving-wall flow-control-volume law has yet been audited. Do not bypass with ad hoc force or negative tissue damping. If discussing progression, bring the underlying red/green receipts and this quantitative state, not just preference.
