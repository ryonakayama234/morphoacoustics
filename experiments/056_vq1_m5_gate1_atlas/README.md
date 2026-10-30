# Research-only M5 Figure 2B two-reader pressure-atlas gate

This is **a source-metrology candidate generator**, not scientific validation of digitized wall pressure. The checked-in `source_manifest.json` has **NO** original Figure2B bytes, **NO** digitizer measurements, and **NO** qualified pressure samples. Default `run.py` returns an explicit `SOURCE_IMAGE_NOT_ACQUIRED` research HOLD. Code is intentionally independent of proposed unmerged PRs #218, #220, #239, #241.

## Run (Linux/bash / WSL2)

```bash
cd experiments/056_vq1_m5_gate1_atlas
python -m unittest discover -p 'test_*.py' -v
VQ1_M5_TEST_OUTCOME=success python run.py --out /tmp/vq1_m5_gate1.json
cat /tmp/vq1_m5_gate1.json
```

A future externally sourced figure + two independently annotated readers may be supplied with:
```bash
VQ1_M5_TEST_OUTCOME=success python run.py --input validated_source_manifest.json --figure /path/to/original_figure_bytes --out /tmp/atlas_candidate.json
```
**Note:** A SHA256 for the provided image verifies internal byte identity, NOT that it is genuinely Figure2B from Fulcher et al. A candidate status **always** requires independent manual source audit, including original DOI/figure identity, legend, axis readings, x/y unit scaling, and resolution. The tool will not issue `S1_PRESSURE_ATLAS_QUALIFIED`.

## Physical constraints
- Source Figure2B uses `D=p0-p_i`, jet-adhered FW versus separated NFW, physical case d=.02cm / reported DeltaP=10cmH2O; pressure cannot be inferred from TableI Q or calculated Fig4.
- Pixel/axis bounding controls are synthetic for unit tests. Two analysts are declared independent by IDs; code cannot verify their real-world independence. Interval overlap by itself is *not* proof of figure authenticity.
- Separate pressure-drop D from tissue-backside reference and virtual-work force. A common backside reference cannot be assumed for different walls. S2/S3/G1-D and voice are always HOLD/NO_GO.
- The code takes original figure bytes but never commits or redistributes source imagery. Source permissions remain with the publication.
- Runner archives STOP receipt for malformed data and RED tests. Do not set external CI test-outcome to success if tests failed.

Read [SYSTEM](../../docs/research/vq1-m5-gate1-source-atlas/SYSTEM.md), [DATA](../../docs/research/vq1-m5-gate1-source-atlas/DATA.md), [EXPERIMENT](../../docs/research/vq1-m5-gate1-source-atlas/EXPERIMENT.md).