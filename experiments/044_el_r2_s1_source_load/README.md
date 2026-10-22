# EL-R2-S1 Gate A — source impedance and terminal load contract

**NOT A SOLVER; preregistration and independent Wolfram oracle only.** Parent [#156](https://github.com/ryonakayama234/morphoacoustics/issues/156), exact [#157](https://github.com/ryonakayama234/morphoacoustics/issues/157).

[Experiment preregistration](../../docs/research/listener-r2-s1/EXPERIMENT.md) / [System](../../docs/research/listener-r2-s1/SYSTEM.md) / [Results](../../docs/research/listener-r2-s1/RESULTS.md).

## Wolfram replay
~~~bash
wolframscript -file experiments/044_el_r2_s1_source_load/wolfram_oracle_18.wl > /tmp/el-r2-s1-18.json
~~~
Source `wolfram_oracle_18.wl` independently computes the traveling-wave solution. Frozen file `wolfram_oracle_18.json` captures its evaluated result in Wolfram and includes provenance. Future Core ABCD solver (Gate B) must numerically match it; this commit has **no Python physical solver and no newly claimed CI pass**.
