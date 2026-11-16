# DATA — operational measurands, interventions, typed record proposal

**Research-only observation envelope v0; not a Core/ASMR public JSON Schema.** The numerical fixture and reference-oracle values in PR #158 are frozen; this document clarifies information needed for an honest implementation without changing them.

## What is actually measured
The primary "measurement" is a **computed complex steady-state solution of a synthetic 1D acoustical circuit** at named ports, compared to an independent traveling-wave calculation. No microphone, tissue, human participant, room, hearing sensation, ASMR stimulus or physiological measurement is involved.

| Class | Variables / units | Interpretation |
|---|---|---|
| Exogenous | ps (Pa complex); Zs,Zt (Pa·s/m³ real absolute); L (m), A (m²), rho (kg/m³), c_air (m/s), f (Hz) | fixed/assigned intervention and fixture |
| Solved | p0,pL (Pa complex); U0,UL (m³/s complex) | total port states in the specified linear model |
| Derived | Zc,Zin (Pa·s/m³ complex as applicable), Gamma_in, H_drive/H_canal/H_total, kL, rs,rt | *functions* of solved/assigned values, not independent empirical measurements |
| Energy | Pdrive, Pentrance, Pterminal, Ploss_source (W) plus r_source,r_tube (W) | active power accounting, positive f only |
| Diagnostic | oracle component errors, numeric condition indicator, null/contrast checks, software/provenance IDs | verification of implementation/reproducibility, not physiology |

## Frozen main factorial (do not replace)
A = {3e-5,6e-5} m²; L = {0.020,0.025,0.030} m; f = {1000,3000,7000} Hz: exactly **18 cases**.
rho=1.21 kg/m³, c_air=343 m/s, ps=(1+0i) Pa peak; Zs=13,834,333.333333334 and Zt=27,668,666.666666668 Pa·s/m³ fixed **absolutely** for every row. Comparison is a paired model counterfactual within one circuit fixture. No biological claim.

## Proposed record types and no ambiguous scalar coercion
~~~json
{
  "schema_version": "el-r2-s1.gateb.research-observation.v0-proposed",
  "status": "RESEARCH_ONLY",
  "fixture_id": "frozen-gate-a-row-id",
  "source_reference_plane": "SOURCE_EQUIVALENT",
  "entrance_plane": "CANAL_ENTRANCE",
  "terminal_plane": "TERMINAL_SIDE",
  "phasor": "peak_exp_plus_iwt",
  "positive_U": "entrance_to_terminal",
  "frequency_hz": 3000,
  "geometry": {"length_m": 0.025, "area_m2": 0.00003},
  "source": {"ps_pa": [1.0, 0.0], "zs_pa_s_m3": 13834333.333333334},
  "termination": {"zt_pa_s_m3": 27668666.666666668},
  "solved": {
    "p0_pa": ["real", "imag"],
    "u0_m3_s": ["real", "imag"],
    "pL_pa": ["real", "imag"],
    "uL_m3_s": ["real", "imag"]
  },
  "derived": {
    "h_total_complex": ["real", "imag"],
    "h_drive_complex": ["real", "imag"],
    "h_canal_complex": ["real", "imag"],
    "gamma_in_complex": ["real", "imag"]
  },
  "energy_W": {
    "drive": "number", "entrance": "number",
    "terminal": "number", "source_loss": "number",
    "source_residual": "number", "tube_residual": "number"
  },
  "input_outcome": "VALID|INVALID|UNSUPPORTED|NUMERICALLY_UNRESOLVED",
  "science_verdict": "PASS|FAIL|INDETERMINATE|NOT_RUN",
  "provenance": {
    "core_commit": "sha", "experiment_commit": "sha",
    "wolfram_oracle_blob": "f89ccf20cb60019c4487873a13af678e983beb6b",
    "wolfram_source_blob": "fa8c2112f36f2b7119d40e8125e4d979ba091eef",
    "fixture_digest": "sha256", "implementation_digest": "sha256",
    "runtime_versions": {}, "test_run_url": "optional"
  }
}
~~~
Above is an illustrative **field/units contract**, NOT a sample of executed numeric results: strings "real"/"imag"/"number" are placeholders and MUST be replaced by finite JSON numbers on implementation; no fake data should pass validation. For zero-drive supplemental controls, H ratios must be null with an explicit undefined reason, NOT 0, infinity or NaN. Record raw complex components as ordered [real,imag], SI units in names, and fixed plane IDs. Do not treat a render-normalized audio WAV as a Pa sample.

## Candidate domain and refusal taxonomy
Gate A DATA offered 0.01<=L<=0.05 m; 1e-5<=A<=1e-4 m²; 0<f<=8000 Hz; finite positive rho,c,real Zt>0,real Zs>=0, complex finite ps, and bounded small-signal pressure ratio as **proposed engineering guardrails**, NOT anatomical truth. Gate B implementation must accept/reject these definitions explicitly after review and document why. No quietly inserted clipping, damping, coercion or solver fallback. For real positive load/source, physical uniqueness follows passivity; numerically unresolved refers to floating-point conditioning, not a physical resonance "failure".

- INVALID: missing/ambiguous unit, malformed shape, nonfinite numeric, negative A or L, inconsistent planes, unsupported mixing of p0 prescription with finite ps/Zs.
- UNSUPPORTED: well-formed but excluded scope (complex/reactive load, nonuniform tube, out-of-range dimensions/frequency, contact, 3D/real biological interpretation).
- NUMERICALLY_UNRESOLVED: nominally supported input where stable finite solution/condition cannot be established with declared precision.
- INFEASIBLE: **not applicable**, because no motor command or body feasibility question is solved.

Input outcome is separate from scientific verdict. A numerical mismatch on valid input must be scientific FAIL, not quietly recast as UNSUPPORTED.

## Identifiability and future empirical measurement
Holding ps,Zs,Zt fixed **in a model** identifies only this equivalent-circuit counterfactual. It does not isolate real anatomy from middle-ear changes nor guarantee an identical external acoustic incident field. Future Gate C must register (i) actual probe source calibration / leakage / evanescent-mode uncertainty; (ii) microphone/probe physical plane; (iii) open/blocked canal or SOFA HRTF reference and normalization; (iv) measured uncertainty and model discrepancy. None can be inferred from Gate B algebra.

Literature boundary: [Nørgaard et al. 2018, source calibration parallel components](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856597/); [Nørgaard et al. 2022, calibration-waveguide geometry](https://pmc.ncbi.nlm.nih.gov/articles/PMC8807002/).
