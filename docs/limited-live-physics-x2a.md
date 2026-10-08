# X2a — first limited live physical utterance (Core #69)

**Status:** experimental integration adapter for exactly one previously audited
task-field /a/→/i/-like transition. Studio may display it as **「あい（実験発声）」**,
but that is a *restricted text-to-fixture mapping*, **not** verified Japanese
phonetic identification. This is a checkout-local, headless CLI, not TTS and
not a web server.

## Supported input

The API here is **integration-local** `morpho-live/v1`, **not** Performance
Contract v0. The future Studio service maps the creative
`PerformanceRequest` into this validated pronunciation fixture; it must
not pass arbitrary text or `Direction` through as physical commands.

```json
{
  "schema_version": "morpho-live/v1",
  "pronunciation_id": "v3a-a-to-i-like/v1",
  "body_id": "v3c-M_plus/v1",
  "segment_id": "s1",
  "text": "あい",
  "seed": 0
}
```

Exactly **one** segment is accepted; the single `segment_id` is an opaque
nonempty identifier. The only exposed body is the V3c `M_plus` PreparedMorphology;
the only source is `lf_fixed`; the only seed is `0`; the only supported
creative `direction` is absent or an empty object. Unsupported combinations
return `SUCCEEDED + UNSUPPORTED` with a diagnostic and **no audio**.
Malformed requests **including invalid JSON or UTF-8 request files**
return `SUCCEEDED + INVALID`. A runtime/preflight error is instead `FAILED`.
An **already-existing output directory is always an execution error**, even
when the request is unsupported or invalid: no previous Take bytes can be
mistaken for the current result. Those distinctions must survive the Studio adapter.

## Reproduction on WSL2/Linux

Run from a **full source checkout** of
[morphoacoustics](https://github.com/ryonakayama234/morphoacoustics).
The adapter verifies the adopted Experiment 029 and Experiment 028 runners'
Git blobs, the pinned Experiment 028 frozen manifest and **all recorded
transitive experiment/acoustic source-file SHA-256 digests before dynamically
importing an experiment module**; it then runs the upstream scientific
preflight and Wolfram-oracle checks. It refuses to run if any adopted source
or gate differs. The frozen source preflight now pins the Git-blob identity of
**all 23 other Python files in `src/morphoacoustics/`** (including domain,
preparation, physical, simulation, and eagerly imported package initializers)
and rejects newly added or removed Python package files. This complements
Experiment 028's transitive experiment manifest and Experiment 029's frozen
oracles. The integration adapter `limited_live.py` is reviewed through the
PR/CI revision rather than recursively self-hashed. Any intentional package
refactor must re-audit this frozen research execution boundary before changing
pins; do not silently recapture an oracle from modified code.

This is a scientific reproducibility boundary for a trusted
checkout, not a sandbox for arbitrary malicious Python dependencies. Python
initializes package modules before running a `python -m` entry point; thus this
guard executes **before dynamic experiment loading** but does not promise to
prevent every Python import of untrusted checkout files. External dependencies
and their installation integrity are outside the source manifest. It deliberately requires **NumPy 2.4.6**, matching the
audited experiment, and does not read stored experiment WAVs.

```bash
python -m pip install 'numpy==2.4.6'
python -m pip install -e '.[dev]'

cat > limited-live-request.json <<'JSON'
{
  "schema_version": "morpho-live/v1",
  "pronunciation_id": "v3a-a-to-i-like/v1",
  "body_id": "v3c-M_plus/v1",
  "segment_id": "s1",
  "text": "あい",
  "seed": 0
}
JSON

python -m morphoacoustics.integration.limited_live \
  --request limited-live-request.json --output-dir live-take-001
python -m morphoacoustics.integration.limited_live \
  --request limited-live-request.json --output-dir live-take-002
pytest -q checks/test_limited_live_smoke.py tests/test_limited_live_policy.py
```

Always supply a **new, nonexistent output directory**: overwriting a Take is
forbidden. A successful execution generates 3 new local files and a result
manifest: `audio.wav` (48 kHz, 16-bit mono, 24,000 frames), `raw_pressure_pa.npy`
(unmodified acoustic pressure in Pa), `physical_trace.csv` (selected
10-ms-aligned task activations and physical areas), `result.json`.
The audio is playback-normalized to peak 0.90; never treat that WAV as a
pressure measurement. The manifest records SHA-256 digests for each artifact,
input/seed/fixture/compiler identities, the frozen task-plan SHA-256, NumPy
version, acoustic call count (102) and experimental ancestry.

Each valid call invokes the physical and acoustic model **again**. Two
identical requests in a fixed environment must produce identical playback-WAV
and trace digests despite separate run directories; a new Take/run ID belongs
to the orchestration layer and is **not** the content digest. Float64
least-significant bits may change between environments. Therefore the
scientific gate compares the full 24,000-sample waveform quantized at
1e-9 Pa against the adopted
`dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e`
signature. The raw float64 hash is **diagnostic**, not a cross-platform
identity guarantee. PCM16 file equality across environments is not
automatically certified by that quantized scientific gate.

## Failure and no-fallback semantics

A PreparedMorphology reachability preflight happens before source/physical/
acoustic synthesis. Experiment 029's `M_minus` test body is deliberately
**not exposed** as a creator-selectable body: attempting its body ID in the
CLI is `UNSUPPORTED`. The dedicated scientific smoke exercises `M_minus`
directly at the adopted capability layer, verifying
`INFEASIBLE`, `LOCATION_UNREACHABLE` on task 1, no physical endpoint,
no acoustic waveform, and **zero acoustic transfer calls**.
A limit violation is not fixed by clipping or fallback synthesis.

## Evidence, integration boundary and pending work

- [V3a PR #63](https://github.com/ryonakayama234/morphoacoustics/pull/63):
  frozen task-space continuous transition.
- [V3b PR #65](https://github.com/ryonakayama234/morphoacoustics/pull/65):
  limited unchanged-task morphology transfer.
- [V3c PR #68](https://github.com/ryonakayama234/morphoacoustics/pull/68):
  frozen reachability/no-fallback and quantized acoustic signature.
- [Core Issue #69](https://github.com/ryonakayama234/morphoacoustics/issues/69):
  headless live execution entrypoint.
- [Studio Issue #11](https://github.com/ryonakayama234/morphoacoustics-studio/issues/11):
  local HTTP transport, content-addressed storage, immutable Take, persistence,
  Performance Contract v0 bridge, playback/download and UI.

The scientific reachability limit is **experiment-local**, not an established
biological articulator limit. This work does **not** verify blind human vowel
identity, arbitrary Japanese speech, different actors, emotion, arbitrary
morphology or production TTS. The parent V3 #33 retains independent human
observation/PHONETIC_TRANSFER evaluation; it need not be misreported as closed
to use this narrowly adopted computational baseline.

### Review checklist

- [ ] CI scientific smoke actually executes the physical transfer 102 times
      for each of two fresh takes and compares their digests.
- [ ] M_minus remains audio-less with zero acoustic transfer calls.
- [ ] Foreign body/text/Direction and stale output cannot silently succeed.
- [ ] Test/review results, scientific limits and source revision are recorded
      before the Draft PR is marked ready.
