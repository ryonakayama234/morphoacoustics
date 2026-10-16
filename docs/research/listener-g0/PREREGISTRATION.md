---
id: EL-G0-PREREG
status: FROZEN_BEFORE_EXECUTION
parent: "PR #83 / EL-H01, EL-H02 / Issue #113"
implementation_scope: EXPERIMENT_ONLY
production_api_change: false
---

# EL-G0 — 事前登録（独立音源による左右受音の解析基準系）

## Why this gate exists
ListenerSpec/InteractionScene を公開型として先取りせず、まず「同一の既知音源と二つの受音点から、幾何だけで説明できる左右受音差」を検証する。Speaker solver や Studio への依存は置かない。親研究 [PR #83](https://github.com/ryonakayama234/morphoacoustics/pull/83) は parked のままで、その G1/G2 の人体妥当性を主張しない。

## Hypothesis and competing nulls
H-EL-G0: 3D 自由空間の理想点モノポールであれば、距離 r の受音複素圧力は
p(r,f)=i 2π f ρ Q(f) exp(-i 2π f r/c)/(4πr)。
同じ Q、ρ、f なら、受音点間のレベル比は 20 log10(rL/rR) [dB] (R/L)、伝搬遅延差は (rR-rL)/c [s] (R-L) となる。**これは既知理論の実装・符号・単位・座標の基準テストであり、耳介や人体の新物理を検証する試験ではない。**

Null A: 2点が対称配置で音源が正中 → R-L の差 0。
Null B: 音源を x 軸方向に鏡映 → R-L の符号反転（両側の距離が交換）。

## Frozen fixture and units
- Cartesian world coordinates [m]: L=(-0.09, 0, 0), R=(+0.09, 0, 0)
- center S=(0, 0.20, 0) m; offset S=(+0.12, 0.20, 0) m; mirrored S=(-0.12, 0.20, 0) m
- c=343 m/s; ρ=1.2 kg/m³; source complex volume velocity Q=1.0e-6 m³/s; f = 1000 Hz
- R-L delay sign: tR-tL; R/L level sign: 20 log10(|pR|/|pL|)
- Receiver is **two ideal point pressure probes**, not an eardrum microphone, blocked-canal HRTF, human auditory nerve model or morphological pinna.

## Frozen numerical gates (no tuning after results)
1. Centered: |Δt_R-L| < 1e-12 s; |ΔL_R/L| < 1e-12 dB.
2. Offset: rL=0.29 m; rR=sqrt(0.0409) m = 0.20223748416156684 m; Δt_R-L = -0.2558673931149656 ms; ΔL_R/L = +3.1307268779057047 dB. Tolerance < 1e-9 in the **displayed units** (ms, dB), and < 1e-12 m in distances.
3. Mirroring x: signs reverse for Δt and ΔL within 1e-12 of paired values in original units.
4. Every calculated complex pressure finite; invalid (nonpositive f, c, ρ; zero distance; nonfinite data) rejected explicitly.
5. Stored records contain inputs, output observation name, SI units, frequency, model ID, source identity, assumptions, and code provenance.

## Limits / separate future gates
G0 cannot establish physical pinna/ear-canal filtering or 1 cm/soft-contact accuracy. G1 needs geometry variation compared against rigid/no-pinna null; G2 needs distance-resolved measured HRTF with valid measurement range. Contact/source generation, wet films, cartilage conduction, energy accounting and ASMR psychophysics require other gates. No silent playback-gain or HRTF replacement.

## Decision rule
Numerical success -> **PROVISIONAL_ANALYTIC_BASELINE**, never morphology validity or production adoption. Failure -> preserve evidence, fix with explicit amendment and rerun. Independent review needed before promoting any contract.

## Sources
- [PR #83 INDEX / 70 Research gates](https://github.com/ryonakayama234/morphoacoustics/blob/docs/embodied-listener-research-20261011/docs/research/embodied-listener/70-research-gates.md)
- [Existing research parent R-NV0 / Issue #53](https://github.com/ryonakayama234/morphoacoustics/issues/53)
- [Wolfram acoustic PDE models](https://reference.wolfram.com/language/guide/AcousticPDEModels.html)
