---
id: EL-REFERENCES
title: "Evidence / limits reference ledger"
status: RESEARCH_CANDIDATE
priority: PARKED
implementation_authorized: false
reviewed_as_of: 2026-10-11
---

# References — information sources and claim limits

各参照は「何を支持するか」「何を支持しないか」を一緒に保存する。最新の外部検証が必要なら再確認する。研究の仮説と実験的な知見は別物である。

## Internal

### REF-ARCH
[Architecture](../../architecture.md)、[Invariants](../../invariants.md)、[Model assumptions](../../model-assumptions.md)。Supports: 現行の5段因果、solver capability、source/receiver境界、失敗状態。Does not support: listener接触モデルの実装。

### REF-RNV
[Nonvocal/nearfield candidate](../nonvocal-oral-nearfield-candidate-v0.md)、[Issue #53](https://github.com/ryonakayama234/morphoacoustics/issues/53)。Supports: 非発声音/接触音候補、receiver transfer、非音響観測の責務分離。Does not support: ASMR音の再現精度やwet-contact solver完成。

### REF-SFI3
[Issue #82: SFI-3](https://github.com/ryonakayama234/morphoacoustics/issues/82)。Supports: 声門—固定声道の連成エネルギー検証研究計画。Does not support: 二身体連成がproduction化されたとの解釈。

## External acoustics

### REF-NF-DATA
Yu, Wu, Liu, Xie, 2018, Near-field head-related transfer-function measurement and database of human subjects. [DOI 10.1121/1.5027019](https://doi.org/10.1121/1.5027019)、[PubMed](https://pubmed.ncbi.nlm.nih.gov/29604722/)。Supports: 56人、距離0.2–1.0mの被験者HRTF測定。Does not support: 1cm/接触・柔軟な耳の変形時の性能。

### REF-NF-FDTD
Prepeliţă et al., 2020, Numerical simulations of near-field head-related transfer functions: Magnitude verification and validation with laser spark sources. [DOI 10.1121/10.0001409](https://doi.org/10.1121/10.0001409)。Supports: rigid head replicaの特定条件での近接場wave-model/HRTF magnitude validation（報告された範囲内）。Does not support: 生体口耳接触・濡れ・音源非線形全般・全位相の同等精度。

### REF-HRTF-MESH
[Mesh2HRTF official](https://www.mesh2hrtf.org/) と[GitHub](https://github.com/Any2HRTF/Mesh2HRTF)。Supports: 頭と耳の形状からBEM散乱を計算する方法とソフトウェア。Does not support: 二体contact FSIをそのまま解く機能。

### REF-SOFA
[SOFA official](https://www.sofacoustics.org/)。Supports: AES69に基づくHRTF等の空間音響データ交換。Does not support: 任意SOFAの測定面、1cm、接触条件、個人適合。必ずconvention / reference planeを見る。

## Cartilage / material

### REF-CC-REVIEW
Hosoi et al., 2019, Cartilage conduction as the third pathway for sound transmission. [DOI 10.1016/j.anl.2019.01.005](https://doi.org/10.1016/j.anl.2019.01.005)。Supports: cartilage-air等の軟骨伝導経路の学術整理。Does not support: 柔らかい口から耳への直接接触で同じ効率。

### REF-CC-PATH
Nishimura et al., 2014, Cartilage conduction efficiently generates airborne sound in the ear canal. [DOI 10.1016/j.anl.2014.08.001](https://doi.org/10.1016/j.anl.2014.08.001)、[PubMed](https://pubmed.ncbi.nlm.nih.gov/25199744/)。Supports: 耳介軟骨刺激の空気伝導経路に関する実験。Does not support: 舌/唇接触の音量や効果。

### REF-CC-HARDNESS
Vibrational and Acoustical Characteristics of Ear Pinna Simulators That Differ in Hardness (2021). [PubMed PMID 34287225](https://pubmed.ncbi.nlm.nih.gov/34287225/)。Supports: 硬さの異なる耳介模型での振動/音圧測定。Does not support: すべての人体軟骨の構成則決定。

## Numerical model references

### REF-WOLFRAM-ACOUSTICS
[Wolfram time-domain acoustics](https://reference.wolfram.com/language/PDEModels/tutorial/Acoustics/AcousticsTimeDomain)、[AcousticImpedanceValue](https://reference.wolfram.com/language/ref/AcousticImpedanceValue.html)、[AcousticNormalVelocityValue](https://reference.wolfram.com/language/ref/AcousticNormalVelocityValue.html)。Supports: 波動PDEと独立した境界条件/音源項の設計。Does not support: 湿潤接触や耳の物性値の生理学的検証。

Wolfram numerically checked (2026-10-11): c=343m/sとして理想的な1/4波長共鳴c/(4L)はL=25/30/35mmに対し3430/2858.3/2450 Hz。実耳道の予測ではない。r=1cmのkr=2πfr/cは1/5/10kHzで0.183/0.916/1.832。EL-H05のspring-damper identityは記号的に確認したが、人体での検証ではない。

## Maintenance

追加時にsource ID、著者/年/DOI、観測条件、supports、does not support、対応EL-H番号、確認日、dataset・再配布条件を明示する。論文結果を使って測定範囲外へ暗黙に外挿しない。
