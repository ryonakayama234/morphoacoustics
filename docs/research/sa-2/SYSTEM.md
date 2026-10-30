# SA-2A — SYSTEM: one aperture, one boundary, one receiver law

Reference: uniform normal piston velocity on a circular disk embedded in an infinite rigid baffle. This is the FLANGED circular-aperture analytic oracle, NOT the unflanged open tube, human face, animal beak, near-field mouth microphone or generic head radiation.

With exp(+i omega t) phasor convention and outgoing exp(-i k r), area S=pi*a², U=S*v, k=omega/c, x=ka, fluid density rho, c sound speed, acoustic volume-flow impedance Zc=rho*c/S [Pa*s/m³]:

Zrad/Zc = 1-J1(2x)/x + i H1(2x)/x,
R(x)≈x²/2, X(x)≈8x/(3*pi), x→0.

J1 = Bessel function of order one; H1 = Struve function of order one. The expression originates as **MECHANICAL** piston radiation impedance F/v = rho*c*S*(R+iX). The acoustic pressure/volume-flow impedance p/U = (F/S)/(v*S) = rho*c/S*(R+iX). F/v and p/U differ by S²: never conflate them.

Plane-wave 2-port prepared tract at the same lip port:
[p_g,U_g]^T = [A,B;C,D]*[p_lip,U_lip]^T,
p_lip=Zrad*U_lip,
U_lip/U_g = 1/(C*Zrad + D),
Zin = (A*Zrad+B)/(C*Zrad+D).

Exterior far field uses the identical baffled piston:
p(r,theta)/U_lip = (i omega rho/(2*pi*r))*exp(-i*k*r)*D(theta),
D(theta)=2*J1(x*sin(theta))/(x*sin(theta)), D(0)=1.
The field radiates into the FORWARD HEMISPHERE ONLY. It is not the legacy full-space 4*pi monopole used in Exp009, and a single r/theta pressure sample is not acoustic power.

Pport = 1/2 Re(Zrad)*|U_lip|².
Pfield = r²/(2*rho*c) * integral_forward_hemisphere |p(r,theta)|² dOmega
       = pi*r²/(rho*c) * integral_0^(pi/2) |p(r,theta)|² sin(theta) dtheta.
With U=1 m³/s complex peak phasor (calibration only), the normalized power identity is R(x)=x²/2 * integral_0^(pi/2) D(theta)² sin(theta) dtheta.

Independent near-port reference: Rayleigh double area integral using overlap area of two radius-a disks. In dimensionless separation t=d/(2a),
Zrad/Zc = (4*i*x/pi)*integral_0^1 [acos(t)-t*sqrt(1-t²)]*exp(-2*i*x*t) dt.
This numerically checks both R and X without calling Bessel/Struve from the tested formula; still derived for SAME circular baffle family, not empirical validation of biological anatomy.

Legacy comparator: Exp009 ZL=0.05 rho*c/A_lip, outgoing monopole with 4*pi angular normalization and independent observer law. Not a coherent same-geometry replacement and not secretly modified in SA-2A. Current Exp009 lossy matrix is used only for frozen-body frequency-domain port evaluation.

SA-2A may evaluate the actual prepared CC-A2 M0 geometry via exact SV-1 preflight; no imaginary M1 fallback. The analytic exact baffled piston formula is defined for all real x but coupling to 1D plane waves is restricted to declared experimental ka≤0.8 and frequencies with a valid 1D cross-section interpretation. Receiver examples must explicitly state far-field assumptions; use pure farfield asymptotic receiver at r=1.0m for numeric demonstration and do not claim real 1m microphone calibration. The reactive lip load is frequency-dependent; a naive IFFT or STFT multiplication is NOT yet a causal physically verified boundary for VF-1.

Sources:
COMSOL baffled piston rayleigh integral, power and far-field: https://doc.comsol.com/6.3/doc/com.comsol.help.models.aco.baffled_piston_radiation/baffled_piston_radiation.html
Engineering acoustics reference, piston impedance formula: https://catalogimages.wiley.com/images/db/pdf/9781119851059.excerpt.pdf
Independent Rayleigh disk integral background: https://backend.orbit.dtu.dk/ws/files/52443965/ris_r_536.pdf
Titze 2008 source-filter coupling: https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/
