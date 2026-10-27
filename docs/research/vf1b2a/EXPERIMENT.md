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
