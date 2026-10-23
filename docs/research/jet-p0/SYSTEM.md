# JET-P0 — SYSTEM

**Scope**: a prescribed glottal aperture trajectory -> Bernoulli jet -> *candidate* source-local stochastic closure -> existing Core CC-A2 M0 prepared static 1D tract -> actual raw pressure -> one-common-gain listening WAV. Research-only; not tissue/airflow bidirectional FSI.

~~~mermaid
flowchart TD
    D[Future Studio: Character and acting Direction] -. planned only .-> G[Glottal-state control candidate]
    G --> A[Prescribed aperture trajectory A_g(t)]
    P[Subglottal pressure ΔP] --> Q[Bernoulli flow Q = Cd A sqrt(2ΔP/ρ)]
    A --> Q
    Q --> J[Jet Reynolds and correlation scale]
    J --> N[Source-local gated stochastic closure Q prime]
    Q --> S[Volume-velocity source Q plus Q prime]
    N --> S
    B[Prepared Core CC-A2 M0@1 rest body] --> R[Existing Exp042/023 static acoustic render]
    S --> R
    R --> RAW[Raw physical outlet pressure Pa]
    RAW --> AUD[Single common playback gain, WAV]
    AUD -. future opt-in after gates .-> L[Studio VA-L0 masked audition / verified Take]
~~~

### Authority
The aperture phase is **prescribed**; not the calculated displacement of real mass-spring vocal folds. The Bernoulli relation computes source mean volume flux from the specified pressure and area. Noise is modeled as a bounded *hypothesis* about unresolved jet microdynamics at the source, **not a measured constitutive law**. Its correlation bandwidth scales with computed jet speed over declared length. 1000 Reynolds gating is a falsifiable model choice, NOT a universal physical turbulence boundary. Re, gap, length and Cd are not fitted to a real character.

No waveform-to-waveform EQ/crossfade/vocoder. The pressure is obtained by a fresh actual Core acoustics calculation on the frozen prepared body. The listening WAV has a **single common amplitude scale**, distinctly downstream of physical pressure and retained separately. No pressure change if the model refuses a nonfinite/negative control.

### Current / prospective boundary
- **Exists on main:** versioned prepared M0 /a/-like path and LF single sustained physical Take (SV-1); Studio two-body CC-A2.
- **This branch:** alternative prescribed jet research source; no Studio import, no graph modification.
- **Possible later:** add opt-in, versioned physical source-port control after independent numeric and listening gates. Until then Studio MUST NOT present this as established voice quality or a new body variation.

### Dependencies
A frozen CC-A2 prepared M0 via SV-1 `_validated_context()` is required; use source preflight unchanged. Exp042's `_render()` is reused to generate new pressure samples. If the upstream version differs or does not bind, fail without fabricated Take. SMC (`packages/speech-motor-compiler/`) and ASMR (`asmr/`) are completely independent, disabled in this experiment.

### After-run boundary (2026-10-23; retrospective)
Physical Core rendering succeeded but source-noise→acoustic response did **not** pass the predeclared high-band criterion. See [failure audit](FAILURE_AUDIT_20261023.md) and the explicit future coupled-system sketch in [Voice Lab roadmap](VOICE_LAB_ROADMAP.md). The JET-P0 forward source is not yet a finite-impedance acoustic feedback loop.
