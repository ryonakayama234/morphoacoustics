# VM-1B Gate A — independent 16-section loaded complex transfer

**2026-10-26 JST / PROSPECTIVE, RESEARCH ONLY, not adopted.** Parent [#200](https://github.com/ryonakayama234/morphoacoustics/issues/200), [VM-1 #196](https://github.com/ryonakayama234/morphoacoustics/issues/196), independently held [VM-1A Draft #198](https://github.com/ryonakayama234/morphoacoustics/pull/198), [Foundation #199](https://github.com/ryonakayama234/morphoacoustics/issues/199). Studio UI is **FROZEN / NO EDIT**; future UI expansion requires a stop and proposal.

## Physical question / claims
- H1: an **independently constructed frequency-domain transmission matrix** for frozen 16-section M0/M1 predicts the **entire complex** mouth pressure/flow and inlet impedance of the *separate* native-time waveguide under ideal matched termination. Independent propagation reference must resolve actual unequal tube areas, not only a uniform delay.
- H2: using the **declared discrete B0 state equation**, the matrix with an exact discrete admittance predicts the 0.30 s transient DFT within a bounded finite-record residual; extending to 0.60 s reduces truncation bias. This independently checks two mathematical implementations of the **same assumed B0 boundary law**, NOT whether that law correctly models real mouth radiation.
- H3: increasing cells/section 2→4→8 approaches the continuous-time limit of the specified B0 shunt resistance+inertance for fixed f=100,600 Hz, without inventing tissue damping.
- H4: a wrong outlet law (matched substituted for B0), a wrong p/U coupling or a corrupted frozen geometry **must not** be granted B0-pass status. All B0 and matched quantities must retain correct named observer/units.

## Frozen physics and excitation
- From exact [Experiment028 frozen_reference.json](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/028_task_field_morphology_transfer/frozen_reference.json), Git blob SHA-1 `7810dfbb72cb6c41af007db6e9d51c58cad9a522`: 16 identical /a/ cross-section areas for M0/M1, each M0 section 0.010 m / M1 section 0.011 m.
- Air density `rho=1.21 kg/m3`, speed `c=343 m/s`; impedance `Z_j=rho*c/A_j` [Pa·s/m3]. No wall losses, no articulator motion, no vocal oscillator, no receiver, no far-field sound.
- One native-tick positive **injected volume** `V=1e-13 m3`: at time index zero `U_in[0]=V/dt` [m3/s], all later zero; `fs=c*cells_per_section/section_length`, `dt=1/fs`. Zero physical initial state and contiguous session.
- Fixed native record duration 0.30 s for both terminations and M0/M1 n=2; B0 also 0.60 s for finite-window test. `N=ceil(duration*fs)`, nearest bin to requested `f={100,600} Hz`; report exact actual bins and offsets. FFT uses e^(-iωt) convention, meaning complex p/U reference has propagation phase `exp(-iω L/c)`.

## Independent frequency-domain model
For each fixed tube section length `L_j`, `k=2πf/c`, phase `φ_j=k L_j`, the two-port state convention **inlet pressure/forward flow** equals:
```text
[p_in]   [ cos(phi)        i Z_j sin(phi)] [p_out]
[U_in] = [ i sin(phi)/Z_j  cos(phi)      ] [U_out]
```
Chain 16 sections **in anatomical order** to get `T=[[A,B],[C,D]]`. This calculation MUST NOT import `scatter_pressures`, `PassiveWaveguideSession`, or prior VM-1A transfer code.

At the outlet `U_out=Y_L p_out`, so:
```text
H_pU=p_out/U_in=1/(C+D*Y_L)     [Pa s/m3]
H_U =U_out/U_in=Y_L/(C+D*Y_L)   [dimensionless]
Z_in=p_in/U_in=(A+B*Y_L)/(C+D*Y_L) [Pa s/m3]
```
Ideal matched `Y_L=1/Z_last`.

For **existing B0 discrete boundary**, `a` is outgoing-to-port incident pressure, `q_n=q_{n-1}+dt*p_n/m` is inertance flow state, `p_n=(2a_n-Z_last*q_{n-1})/(1+Z_last/R+Z_last*dt/(2m))`. Since `U_n=(2a_n-p_n)/Z_last=q_(n-1)+p_n/R+dt*p_n/(2m)`, it follows that the exact phasor load admittance is:
```text
Y_B0(z)=1/R + dt/(2m)*(1+z^-1)/(1-z^-1)
       =1/R - i*dt/(2m)*cot(pi*f*dt)
m=8*rho*r/(3*pi*A_last), tau=3*pi*r/(16*c), R=m/tau,
r=sqrt(A_last/pi)
```
For finite `f>0` below Nyquist. This is a **discrete shunt R + inertance model**; don't mistake it for the impedance of a measured human mouth or a series RL element. Its continuous-time limit is `1/R + 1/(i*2πf*m)`.

## Prospective scientific gates, before confirmatory CI
- **G0** exact source geometry blob and all positive SI model parameters / distinct B0 and matched; refuse nonfinite, DC, Nyquist and unsupported cells/time.
- **G1** compare separate 0.30 s native waveguide (n=2) DFT at both bins to independent reference for all three complex port transfers, both bodies matched and B0: normalized complex relative error <= `1e-9` matched; <= `2e-3` B0. Error tolerance accounts for **truncated impulse response**, not claimed biological uncertainty. Retain actual complex phase, no magnitude-only pass.
- **G2** B0 0.60 s record produces smaller/equal complex error for each evaluated port/frequency vs 0.30 s and max relative error <= `1e-5`. No zero padding as a substitute for longer physics simulation.
- **G3** analytical n=2,4,8 B0 admittance/matrix at exact 100/600 Hz converges in complex absolute relative error toward independently derived continuous-time B0 admittance; n8 error < n4 < n2 in these prespecified test conditions. This validates *discretization behavior*, not 3D radiation.
- **G4** 0 input gives 0 native response; corrupted body hash rejected; wrong termination label cannot be silently substituted; passive energy ledger exact existing tolerance; incompatible expected port units rejected.
- **G5** report exact source/body/code hashes, native clock, record length, three complex quantity errors, false-law negative controls, and an explicit `INDETERMINATE_REAL_RADIATION`, `VOICE_NO_GO_UNCHANGED`.

**Transparency:** Preliminary local algebra/prototype sanity checks were performed before this design record and informed finite-window engineering tolerances; these are prospective for *GitHub confirmatory implementation/CI*, **not** a blind empirical preregistration. No historical VM-0/VM-1A selectivity numbers will be hard-coded as pass targets.

Next hypotheses require independent empirical or high-fidelity B0 physical reference, passive wall loss, active source-load coupling and radiated receiver. Failures must be retained, not rewritten as passes.