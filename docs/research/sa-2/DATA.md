# SA-2A — DATA & provenance (before execution)
State: NOT_RUN, input units and oracle cases frozen here.

Calibration air rho=1.21 kg/m³, c=343 m/s. Test piston radius a=0.010 m, S=pi*a² m², and x=ka in [0, 0.005, 0.02, 0.1, 0.25, 0.55, 0.8]. Also radius 0.005m (geometry sensitivity) at selected same physical frequencies (200, 1000, 3000Hz) with per-case x screening. Denote farfield r=1m, theta=0deg (on-axis) and 60deg.

Main body: prepared/rest CC-A2 M0 /a/-like tube from experiments/042_sv1_sustained_vowel/run.py::_validated_context(). Actual outlet radius a=sqrt(A_lips/pi), NEVER substitute the calibration a=0.010m for true M0 if different. Record outlet area and all section area/length digest. A second audited body is optional and must be genuinely bound; otherwise mark UNAVAILABLE.

Variables: f [Hz], a [m], S [m²], k [rad/m], x=ka [1], U_in and U_lips [m³/s], p_g/p_lip/p_observer [Pa], Zrad/Zin [Pa*s/m³], frequency transfer p_observer/U_in [Pa*s/m³], p/U complex reference signs, energy [W]. Record phase, full complex values (NPY real/imag), branch/source/CI SHA and all artifact hashes. Store both Bessel/Struve analytic and independent Rayleigh-overlap-quadrature R/X values, and hemispherical farfield power quadrature.

No fake 0.5s voice, no raw-Pa WAV, no listening gain: SA-2A is frequency-domain calibration. No post-EQ, no fitted turbulence, no altered JET-P0 20% threshold or fabricated lip biomechanics. Future SA-2B must preserve 4 frozen original JET source NPY SHA and existing SA-1 results in a separate run and preregistration.

Archive: manifest.json (schema=research.sa2a.v0, exact git commit via CI_EVIDENCE, legacy comparator, model limits, math gates, pass/fail, arrays SHA256), calibration table CSV, complex frequency-domain NPYs, a human-readable RESULTS.md only after actual CI. Real biological limits explicitly unverified.
