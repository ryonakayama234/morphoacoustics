# DATA — acoustic state, clocks, ports and provenance

Frozen body: L=0.16 m, A_mouth=0.000804247719318987 m², rho=1.21 kg/m³, c=343 m/s. This is uniform calibration, not CC-A2 M0's 16 varying areas. Physical clocks derived from 10mm/n with integer n=2,4,8: 68600/137200/274400 Hz. Cross-clock 48k observer and active source coupling NOT_IMPLEMENTED. Physical tube T_one_way=L/c seconds (reference only as an analytical oracle).

State: forward and backward FIFOs of length N=16*n, each pressure samples in Pa. At the spatially matched cell locations p(Pa)=a+b; U(m³/s)=(a-b)/Zc; B0 stored q(m³/s) and inertance M(Pa*s²/m³). No wave-synthesis surrogate state.

Each archived 2D trace column: time_s, U_in_m3_s, a_source_pa, b_source_pa, a_lip_pa, b_lip_pa, p_in_pa, p_lip_pa, U_lip_m3_s, E_duct_j, E_B0_j, source_work_j, outlet_dissipation_j, delta_total_E_j, energy_residual_j. Energy residual is delta-total - source-work + dissipated. Values are raw, signed SI; no inferred listener loudness.
Archive contains closed / pressure_release / matched / b0 driven port traces and wavefront controls, plus first 4N samples of long B0 impulse measurements at all three physics clocks. Manifest records SHA256 of each .npy, physical clocks, empirical complex transfer errors, arrival ticks, loss and energy ledger; CI_EVIDENCE records Git commit/ref/run. Exact source SHA and independent byte recheck required. A short impulse excerpt is NOT sufficient alone to reproduce low-frequency transfer; full simulation code+seed+duration+manifest do that, and future archival upgrade should store an adequate long tail if storage permits.

Previous data in B1 Draft #178 and original FAILED gate remain immutable. No scientific B1 certification until evidence audit.