# EXPERIMENT — prospective hypotheses (NO RESULTS YET)
Gate-A conditions are frozen in [GATE_A.md](GATE_A.md) before implementation.

H1 / continuity and energy: with zero inlet, empty state gives identically zero traces. With initially excited closed tube and no inlet, acoustic energy is conserved. With matched or B0 lip, no energy is created; the B0 inertance stores and returns wave energy.

H2 / time of flight: a 0.16 m tube has continuous one-way L/c = 0.0004664723032 s; at 48k this is 22.39067055 samples. The algorithm must not silently replace the tube by a 16-sample delay. Finite-volume space-time dispersion is measured and labeled as error, not as tissue behavior.

H3 / wave transfer: the independent continuum lossless tube two-port and B0 analytic impedance give the reference inlet-flow→lip-pressure complex transfer:
 H(f)=1/[i sin(kL)/Zc + cos(kL)/Zload(f)],
 Zload(f)=M*(i2πf)/(1+tau*(i2πf)).
Check phase as well as magnitude; separately derive closed-closed lowest resonance f1=c/(2L)=1071.875 Hz and its converging discrete counterpart. The mathematical ideal is not experimental microphone truth.

H4 / B0 reuse: unmodified B0.step(a) must reproduce the boundary's p, U, reflected b, q_next and stored/dissipated energy for the incident wave computed by the coupled duct. This is a local compatibility assertion, not a full physical biological validation.

Negative controls: invalid A,L,rho,c,fs or nonfinite inlet -> fail closed; bad R/M cannot be tuned independently; out-of-domain ka>0.8 for SA-2A comparison excluded. A high-pass post-EQ or white-noise brightness replacement does not satisfy H1-H4.

Scientifically distinct future hypotheses: B2 actual 16-section M0 at fixed shape and mouth load; B3 finite physical vocal source; VF-1 self-excitation; Studio A/B voice quality and durable character identity. All NOT_RUN under B1.

Evidence status as of preregistration: NOT_RUN / NO NUMERICAL RESULTS / NO CI CLAIM / NO MAIN MERGE.
