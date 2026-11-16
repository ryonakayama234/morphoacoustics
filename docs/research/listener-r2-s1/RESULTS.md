# RESULTS — EL-R2-S1 Gate A outcome ledger

2026-10-22 JST.
- **Gate A registration:** methodology and falsifiable thresholds frozen on research-only branch; issue #157. Preliminary Wolfram algebra and 18 synthetic fixture evaluations informed the registration; disclosed, not an independently blinded test.
- Symbolic feasibility: det(T)=1, scattering-source transfer agrees exactly with matrix-source transfer, acoustic source resistor balance=0 for real resistive source and load.
- Frozen full 18-row [Wolfram oracle](../../../experiments/044_el_r2_s1_source_load/wolfram_oracle_18.json), generated from [source WL script](../../../experiments/044_el_r2_s1_source_load/wolfram_oracle_18.wl). Numeric results are **analytic toy outputs**, not validated physiological observations.
- Pre-identified reference matched-source null: source Zs=Zc at A=3e-5m² implies |pL|=2/3 Pa for **all lengths** in 18-row grid. At A=6e-5m², same absolute source/load changes this behavior; e.g. L=.025m,f=3000Hz gives |pL|≈0.449247 Pa.
- **Gate B status: NOT IMPLEMENTED / NOT TESTED** at this commit. GitHub CI not yet claimed.
- **Gate C measured ear/source: NOT AUTHORIZED. Gate D product adoption: NOT ADOPTED.** Main and Studio unchanged.

The reproducibility comparison between WolframScript-generated JSON and frozen JSON should use field identity, 18-row ordered fixture identity and per-number max absolute 1e-11 or proportionate tolerance for powers; do not simply compare prettyprinted JSON byte streams.
