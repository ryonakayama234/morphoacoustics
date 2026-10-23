# SA-1 — SYSTEM (prospective design)

## Actual inherited code
- Existing fixed prepared CC-A2 M0 /a/-like body from experiments/042_sv1_sustained_vowel/run.py
- experiments/023_static_vowel_calibration/run.py::render_static uses experiments/012_source_renderer_artifacts/run.py::frame_render with overlapping Hann-windowed frames, fixed hop and preroll.
- experiments/009_fixed_tract_waveform/run.py::lossy_transfer_matrix, outlet_volume_velocity_transfer and far_field_pressure_transfer implement current experiment-local acoustic approximation.
- src/morphoacoustics/acoustics/uniform_tube.py supplies a separate lossless transfer-matrix reference.
- Experiment 047 in JET-P0 draft prescribes glottal flow; there is no current finite-source-impedance or true self-oscillating vocal tissue.

## Causal ports

~~~mermaid
flowchart LR
    I[Glottal U_in: m3/s] --> T[Tube transfer T_U]
    T --> O[Lip U_out: m3/s]
    O --> R[Monopole radiation R_obs]
    R --> P[Observer p_obs: Pa]
    T -. 2-port matrix .-> G[Computed inlet p_g: Pa]
    O -. declared load .-> L[Computed lip p_lips: Pa]
    B[Body geometry] --> T
    Z[Boundary Z_L] --> T
~~~

For frequency f, [p_in,U_in] = [[A,B],[C,D]] [p_lips,U_lips], with p_lips=Z_L U_lips.
T_U = U_lips/U_in = 1/(C Z_L + D)
Z_in = p_in/U_in = (A Z_L+B)/(C Z_L+D)
R_obs = (j omega rho/(4 pi r)) exp(-j omega r/c)
P_obs = U_in T_U R_obs.

The actual Exp009 termination is Z_L=0.05 rho c/A_lips, a CONSTANT resistive surrogate, and its observer is an approximate free-field monopole at r=0.20m. Its deliberately frequency-proportional radiation magnitude can weight higher frequencies; that alone is not an implementation defect. The source-to-output chain has not been independently validated as a physically consistent lip radiation boundary.

## Instrumentation boundary
Compute U_lips and acoustic port pressures analytically from the existing 2-port matrix as explicitly labeled RECONSTRUCTIONS; do not falsely describe them as direct measurements of unimplemented fluid-structure states. Retain real existing frame_render pressure as separate sampled data. Use matching frame/window/operator when comparing sampled outputs; the 2-pass STFT is NOT assumed equivalent to a 1-pass product transfer.

Pressure p has units Pa; volume flow U has units m3/s; acoustic impedance p/U has units Pa s/m3. Acoustic power requires pressure and volume flow AT THE SAME PORT, e.g. half Re(p U*) for consistent peak phasors. Do not equate observer Pa2 with inlet acoustic energy. Positive passive impedances can still exhibit local large flow-velocity resonance ratios.

VF-1 will later close the loop with finite glottal impedance and tissue dynamics, not an arbitrary equalizer. That feedback is not part of SA-1.

Scientific grounding:
Titze 2008 https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/
Wolfe et al 2009 https://pmc.ncbi.nlm.nih.gov/articles/PMC2689615/
Levine-Schwinger 1948 https://doi.org/10.1103/PhysRev.73.383
Titze-Palaparthi 2018 https://pmc.ncbi.nlm.nih.gov/articles/PMC5948106/
