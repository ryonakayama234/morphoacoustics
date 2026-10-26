# Sources and scope of evidence

1. Rosowski, Stenfelt, Lilly, *An overview of wideband immittance measurements techniques and terminology*, Ear Hear (2013). https://pmc.ncbi.nlm.nih.gov/articles/PMC3800001/ — source parameters as acoustic Thévenin/Norton equivalents; entrance pressure alone is insufficient.
2. Non-invasive estimation of middle-ear input impedance and efficiency (2015), https://pmc.ncbi.nlm.nih.gov/articles/PMC4545079/ — empirical residual ear canal impedance, reflectance, middle-ear load dependence. This is **not** validation of EL-R2-S1's synthetic resistor loads.
3. Quantifying undesired parallel components in Thévenin-equivalent acoustic source parameters (2018), https://pmc.ncbi.nlm.nih.gov/articles/PMC5856597/ — source calibration complications and frequency-domain characterizations.
4. Core [UniformTube](../../../src/morphoacoustics/acoustics/uniform_tube.py) — inherited 1D lossless equation, not duplicated here.
5. [EL-R1 audit A1](https://github.com/ryonakayama234/morphoacoustics/blob/research/el-r1-ear-port-20261022/docs/research/listener-r1/AUDIT-AMENDMENT-A1.md) — total vs incident pressure, area/load coupling, f=0 distinction.
6. [ASMR workspace PR #155](https://github.com/ryonakayama234/morphoacoustics/pull/155) — metadata-only package proposal, NOT Core main.
