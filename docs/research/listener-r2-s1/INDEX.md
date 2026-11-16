# EL-R2-S1 — Calibrated source and listener load two-port research

**2026-10-22 JST | Gate A after preliminary symbolic/numeric feasibility exploration, before solver implementation | Research only / no public adoption.**

Primary [Issue #157](https://github.com/ryonakayama234/morphoacoustics/issues/157); parent [#156](https://github.com/ryonakayama234/morphoacoustics/issues/156). This study is independently branched from Core main and does not import/stack EL-R1 [Draft #153](https://github.com/ryonakayama234/morphoacoustics/pull/153) or [ASMR workspace Draft #155](https://github.com/ryonakayama234/morphoacoustics/pull/155).

Read [SYSTEM](./SYSTEM.md), [DATA](./DATA.md), [EXPERIMENT](./EXPERIMENT.md), [RESULTS](./RESULTS.md), [REFERENCES](./REFERENCES.md), then the [reproducible independent Wolfram oracle](../../../experiments/044_el_r2_s1_source_load/).

## Why this is the next scientific gate
EL-R1 prescribed the **total entrance pressure**, so its shape-dependence is valid only under that pressure-source boundary. This new gate fixes *external Thevenin-equivalent acoustic source parameters* ps and Zs and fixes *absolute terminal impedance* Zt while changing tube geometry. It is a causal circuit fixture, **not a measured free field and not the same real-world external acoustic field**. It quantifies how source loading changes p0, pL, U and real active power.

No anthropomorphic 'listener', eardrum pressure accuracy, HRTF, skin, tactile ASMR or Studio implementation is claimed. No merge to main until separately reviewed.
