# VF-1B2 C1-R0 — SYSTEM / exact sealed power reference
For length L_g=0.010 m, depth ell=0.010 m, base half-gap h0=0.00020 m, two outward moving coordinates x_L and x_U, shape basis phi_L=1-z/L_g, phi_U=z/L_g:
A(z,t)=2 ell [h0 + phi_L x_L + phi_U x_U], V(t)=2 ell L_g h0 + ell L_g(x_L+x_U)=V0+g(x_L+x_U), g=ell L_g [m2]. A(z,t)>0 is required for all z, not just positive V.
Sealed and *uniform* gas, no throughflow: M_g=rho0 V0 constant. Isentropic p_abs(V)=P0 (V0/V)^gamma, rho(V)=rho0 V0/V. Gases do not have an independent axial flow mode in this idealized lumped limit. External tissue pressure P_ext= P0, absolute Pa.
Two tissue coordinates: M diag(m_L,m_U), damping D diag(d_L,d_U), K=[[k_L+k_c,-k_c],[-k_c,k_U+k_c]]. Equations:
 dx_i/dt = v_i; m_i dv_i/dt = g[p_abs(V)-P_ext] - (Kx)_i - d_i v_i.
In uniform pressure the two forces are exactly equal; antisymmetric aerodynamic force is ZERO. It is a mathematical negative control, not a proposed mechanism for phonation.
Define internal gas E_g(V)=P0*V0/(gamma-1)*(V0/V)^(gamma-1) [J] (arbitrary additive constant). dE_g/dt= -p_abs dV/dt. Elastic+kinetic E_t=1/2 v^TMv+1/2 x^TKx. Define relative total invariant H = E_g(V)-E_g(V0) + E_t + P_ext(V-V0), to include external pressure boundary work explicitly.
Exact law: dH/dt = - d_L v_L^2 - d_U v_U^2. Thus H(t)+ integral_0^t d_i v_i^2 dt = H(0). When D=0, H must remain constant. No artificial energy injection or negative damping.
Independently compare fluid p(V), gas mass, and H from raw saved x(t),v(t) not by importing solver routines. Pressure-gradient separate *analytic oracle only*: p_g(z)=b+a z/L -> F_L=ell L (b+a/3), F_U=ell L (b+2a/3); F_L-F_U=-ell L a/3. A gradient does not arise dynamically in this sealed model.
No SFI/p'U' port in this exercise. Spatial FV, nonzero mean flow, reservoir enthalpy and genuine phonation are **not implemented** and remain separate staged dependencies.
Studio V2 ADR: Character/Inspector own future organ parameter edit refs; Motion task/drive intent; Scene speaker/listener; bottom Take Dock only valid audio; Research Drawer hidden receipts. All Studio code and V2 registry remain untouched.
