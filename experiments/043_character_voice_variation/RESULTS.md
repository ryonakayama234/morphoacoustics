# Experiment 043 — execution ledger

## 2026-10-30: numerical pilot executed; no voice-quality adoption

**Disposition: NUMERICAL_PILOT_ONLY / NOT_ADOPTED.**

The first full four-case physical audio generator run succeeded. It is evidence
that **two controlled physical interventions reach different modeled pressure
observations**, not evidence that a human can recognize four distinct
characters, that the voices sound natural, or that new biomechanics were
validated.

### Exact execution provenance

- Workflow: [exp043 physical run 41058978291](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41058978291)
- Executed source HEAD: `dece94151715ee06e2d272db8e4f1c70c65725a9`
- Python: 3.11.17; NumPy: 2.4.6, pinned baseline research dependencies.
- Structural + full-physics test: **3 passed**.
- Fresh second execution and independent saved-buffer verification: **PASS**.
- Four pressure arrays: 24,000 finite samples each; WAVs: mono PCM16, 48 kHz,
  0.5 s; source and playback gain fixed across all conditions.
- [Full research evidence artifact 12978197071](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41058978291/artifacts/12978197071)
- ZIP SHA256 (observed GitHub upload log):
  `6f95f9be9b07073524f74aac5c65775866bc533158bd034c74df5889a70fd503`
- Source float64 array SHA256 observed in this Linux CI run:
  `724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc`;
  historical Exp028 warns source byte hashes can differ by SIMD/NumPy path,
  so this digest is **environment-scoped**, not a universal model invariant.

### Quantitative observation (one fixed source; common gain)

| Body | Schedule | Physical total length | Raw RMS Pa | Raw peak Pa |
| --- | --- | ---: | ---: | ---: |
| M0 | reference | 0.160 m | 0.0020636981 | 0.0054092544 |
| M0 | late constriction | 0.160 m | 0.0020570986 | 0.0053673065 |
| M1 | reference | 0.176 m | 0.0021470601 | 0.0055688209 |
| M1 | late constriction | 0.176 m | 0.0021396342 | 0.0055235622 |

Each of the four raw-pressure SHA256 digests differs; see the uploaded
`receipt.json` for the complete exact digests. The listening PCM uses one
common `161.61410350724196` scaling factor for all four (derived from the
maximum absolute raw pressure across conditions), **not** per-Take loudness
matching and not a physically varied vocal effort. All four passed the
nonfinite/length/WAV/hash checks. A changed RMS or hash alone does not establish
perceptually meaningful speaker identity or better sound.

### Causal controls and limitations

- M1 only lengthens all 16 sections by 10%, leaving rest areas unchanged.
- Timing variation moves only task #2 onset from 0.15 to 0.19 s and leaves
  its 0.35 s offset, targets and final area state unchanged.
- Fresh output comes from existing time-varying task realization and modeled
  acoustic response, not crossfading or equalizing previously generated WAV.
- Not a source-filter bidirectional dynamic FSI solver; not material or
  muscle-specific character control; no arbitrary text-to-speech.
- No voice naturalness, phonetic identification, across-utterance character
  consistency or blinded listener result was measured.
- Neither CVI-1 Gate B nor Studio `Character` / `Motion` integration was
  claimed or modified; voice-quality HOLDs remain in force.

### Remaining release gates

1. Check actual four WAVs against the same-condition existing baseline for
   new audible artifacts, with uncertainty and honest provenance.
2. Independent science/code audit of the model reuse and intervention
   semantics; a passing workflow is not independent physical validation.
3. If the creator finds real creative value, separately propose a versioned
   domain/API integration and Studio V2 slot implementation for agreement.
4. Preserve original output receipts and append any negative result instead
   of relaxing this experiment's meaning after hearing it.

This pilot remains on a Draft PR and is not a new adopted character or voice
generation capability.
