# CC-B1 exploratory 16-section rest-area intervention
**Status: EXPERIMENTAL / NO Gate A ratification / NOT SCIENTIFICALLY ADOPTED / NO NEW PRODUCTION API / NO STUDIO FEATURE.**

Core #141; Studio #25. Physically edits exactly **zero-based section 0** of the exact Experiment023 /a/-like 16×10mm prepared baseline, with rest cross-section area ratios 0.90, 1.00 and 1.10. **All other geometry, source and three-task movement are unchanged.**

This research-only runner reuses the source-pinned Experiment029/028 path via `tools/cc_a2_live.py` without changing existing CC-A2 or X2a, and reproduces the CC-A2 M0 quantized pressure oracle as a null/control.

Independent [Wolfram oracle](wolfram/cc_b1_exploratory_16section.wl) uses the published /a/ diameter array in glottis→lips order, the task field's log-diameter kernels, a manually assembled 16-tube ideal transfer matrix and pressure-release outlet. It gives **5Hz-grid input-impedance peaks** of the baseline and edited physical states: not a new broadband time-domain model, not a mouth-radiation model, and not proof of voice naturalness.

## Reproduce (after checking out the exact Core source branch)
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install 'numpy==2.4.6'
pip install -e '.[dev]'
python -m pytest -v tests/test_cc_b1_pilot.py
python experiments/cc_b1_rest_area_pilot/run.py --output-dir /tmp/cc-b1-new-output
```
Outputs: 3 new float64 Pa NPYs, three **pair-shared-gain** 48kHz mono PCM16 research preview WAVs, and decision.json (written last). Preview PCM is normalized using ONE gain across all 3 bodies; raw pressure remains unchanged, and normalized playback is not calibrated SPL. The runner refuses an existing output directory, wrong audited numpy, source revision drift, incompatible geometry, unapproved ratio and mismatched reference. **This is not a real Studio Take**.

Primary checks: exact same frozen source and GestureScore, unchanged 15 other rest areas, full-time section-0 ratio preservation at selected times, unchanged baseline quantized waveform, independent 3-peak oracle within 7.5Hz of 5Hz-grid exploratory predictions, actual new raw Pa difference above a numerical floor and no unexpected instability. These are preliminary exploratory thresholds and shall **not** be relabeled prospective confirmatory Gate B.

Before Core API and Studio are considered, Gate A must be independently reviewed/frozen for a genuinely prospective trial (including new holdout grid/metric, security/units/version binding and time-varying solver accuracy); then conduct new Gate B separately. A subjective listening gate, voice-likeness and creative-usefulness gate are still required. See [Core SYSTEM](../../docs/research/cc-b1-tract-edit/SYSTEM.md), [DATA](../../docs/research/cc-b1-tract-edit/DATA.md), [EXPERIMENT](../../docs/research/cc-b1-tract-edit/EXPERIMENT.md).
