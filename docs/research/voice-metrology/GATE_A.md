# VM-0 Gate A — Voice Metrology, preregistered before analyzer code

Date: 2026-10-25 JST. Scope: diagnosis-only. Current physics/Studio HOLD #193/#31 cannot be merged or promoted by passing these tests.

## What was wrongly certified?
Prior gates measured byte/provenance integrity, finite-speed wave transfer, algebraic energy closure and valid PCM/WAV. None measured humanlike phonation or even transfer function shape of the tract. The monitored waveform is p_mouth [Pa] at a boundary, NOT a physically modeled far-field microphone or Listener.

## Five distinct measurement/acceptance axes (do not collapse into one score)
1. TRACEABILITY: exact Core commit, source/body/observer identity, SI units, raw sources, native p/U, observer p, PCM, sampling clocks, transform version. Return INVALID on mismatch.
2. PHYSICAL VALIDITY: analytic/independent numerical propagation, energy, boundary impedance, reflectance, wave speed, convergence, and correctly named location. Previous PASS of energy residual does not mean resonance Q or formant spectra are correct.
3. SOURCE/TRACT/RECEIVER: physically separate source flow and flow derivative, broadband tract transfer H(f), resonant peaks and -3 dB linewidth/Q, attenuation and radiation, calibrated ear/receiver. Missing glottal feedback, wall work/loss and external receiving field must be UNMODELED, never passed.
4. VOICE CANDIDACY: only compare against a PREDECLARED task and matched physically interpretable reference, including frequency/temporal coverage and vowel structure. No universally valid one-number voice score; extreme harmonic concentration is diagnostic, not proof of a voice-quality threshold.
5. CREATOR BINARY: after prior gates, ask creator a single framed question: GO / NO-GO for the specified voice milestone. No requirement to describe buzziness, phonetic defects or design fixes.

## Immutable CI fixture used to validate first measurement instrument
Archived real physics M0/M1 GitHub Actions artifact: https://github.com/ryonakayama234/morphoacoustics/actions/runs/40181810529/artifacts/12594024942
Core historical candidate source commit 8d4a62c6a75394309ef0b18f72cc06f81f265331; source full SHA-256 15e7309ec7cce300a4d45f0c5149f6b4ac9490fc3ae0625ea4e1825b4834ea9d.
M0 length 0.16m, native 68600Hz; M1 length 0.176m, native 62363.6363Hz. Both 16 sections n2, identical sampled source, 100Hz LF prescribed FLOW, 0.25s, output 48k mono PCM16 fixed 8 Pa/full-scale, mouth p not far-field.
First fixed spectral window: 0.05 <= t < 0.20 seconds, exactly 15 periods at F0=100Hz. Remove mean, FFT bin centers exact harmonics 100,200,...8000Hz; normalize squared magnitudes within harmonics 1..80. For each trace record per-harmonic fractions, 600Hz fraction, 100:600 relative dB, fraction of total AC FFT power explained by those harmonics. NOT a standalone naturalness score.
Before analyzer code: M0 p_monitor sixth share ~0.21788; M1 sixth share ~0.96871. Input sixth share ~0.0002885 in BOTH. M1 source 600Hz relative 100Hz is -34.91 dB, output +19.84dB, difference +54.75 dB. Derived from CI artifact, NOT linked to local creator UUID mapping. Flag output anomaly at physical mouth port before resampling; DO NOT infer faulty wavelength resonance without an independent impulse/sweep test.

## Independent controls to be implemented in ordered phases
A. Measurement algorithm: pure 100Hz sinusoid, pure 600Hz sinusoid, mixed tones with known energy, silence => undefined/NOT_MEASURED instead of NaN or false GO; SHA/WAV tampering and mismatched body/source rejected.
B. Source-only: harmonic envelope, periodic DC flow, derivative spectrum, release/attack and applied flow boundary. No modeled self-oscillating fold = source-tract feedback absent, not healthy.
C. Tract-only: separate small-signal delta/impulse/sweep U source into physically passive model; measure p_mouth/U_in, p_in/U_in, U_mouth/U_in magnitude/phase, resonant frequencies, bandwidth/Q and decay. Compare independent transfer-matrix/uniform-tube reference where identical boundary applies; do NOT deduce transfer poles solely from a 100Hz harmonic sample.
D. One-factor counterfactual: same exact source/observation and geometry except length, then only wall damping, then only radiation; preregister change and direction. Same-task controlled baseline before claiming improvement.
E. Receiver and future phonation: independently validated radiation propagation and calibrated Listener reference required for microphone/ear SPL, full source-tract feedback and dynamic tissue treated as explicitly missing until present.

## Validation / uncertainty / comparison
Use measurement-method version, units, reference frequency grid/window, independent truth/control stimulus, numeric precision, uncertainty and tolerance predeclared from numerical error/reference distributions. Different body, source, observer or moving/ static task gives INCOMPARABLE for old-new quality tests; the observed M0/M1 comparison is a *body perturbation* test, not a new-vs-old benchmark.
Do not set arbitrary 600Hz fraction or clinical CPP / HNR normative threshold after inspecting this example. A pure sine has excellent periodicity; that does not certify voice. ASHA recommends validated instrumentation and CPP for clinical contexts, NOT a voice-likeness threshold for simulator mouth port.
Creator's local Takes 05e8d69a-5e9b-4d5f-bb7d-3961d9674022 and 9801d385-9085-498f-87ff-9d2f3980b598 remain UUIDs without verified matching artifacts: do NOT label either M0/M1.

## References
- Titze, JASA 2008 nonlinear source-tract coupling: https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/
- Vocal-tract wall mechanical impedance influences resonance linewidth: https://pmc.ncbi.nlm.nih.gov/articles/PMC4490178/
- ASHA voice acoustic protocol and instrument validity: https://pubs.asha.org/doi/10.1044/2018_AJSLP-17-0009
- NIST TN1297: define method, uncertainty and valid comparators: https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-d4-measurand-defined-measurement-method
- NIST TN1900 measurement model/uncertainty: https://www.nist.gov/publications/simple-guide-evaluating-and-expressing-uncertainty-nist-measurement-results