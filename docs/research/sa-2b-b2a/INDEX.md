# B2-A — prepared anatomical 16-section passive propagation

**Status: IMPLEMENTED / GATE_PENDING INDEPENDENT CI AND RAW ARCHIVE AUDIT.** No claim of B2-A scientific pass until exact-run CI evidence, source SHA and rehash verification are appended to RESULTS.

Based on verified uniform B1b Draft #181, itself on B1 Draft #178 and B0 Draft #176. No main merge. Owner authorized implementation and requested third-party '@codex review' on GitHub if available. PR review response (if any) must be inspected before final adoption.

- [GATE_A.md](GATE_A.md): prospective frozen B2-A scientific gate, committed BEFORE any code.
- [AMENDMENT_01.md](AMENDMENT_01.md): before tests; distinguishes *early anatomic junction echoes* from *lip-sourced round trip*.
- [SYSTEM.md](SYSTEM.md): scattering equations, physical-clock contract, static-body limitations.
- [DATA.md](DATA.md): prepared source, body provenance, SI numerical state, raw artifacts.
- [EXPERIMENT.md](EXPERIMENT.md): independent oracles, negative controls and scientific disposition.
- [RESULTS_20261025.md](RESULTS_20261025.md): to be created ONLY after actual CI audit.

Implementation: experiments/053_b2a_anatomical_waveguide/run.py, independent_audit.py and tests/test_experiment_053_sa2b_b2a.py. Both actual frozen prepared CC-A2 M0/ M1 /a/ and M0 frozen /i/ are inputs. Source/model differences remain inspectable; no arbitrary EQ. Scientific status is independent from software CI status; failed runs remain recorded.

**Not supported**: nonuniform section lengths within one body, changing section boundaries during simulation, tissue mechanics, nonserial topology, nasal side branches, physically energy-preserving source/output 48k resampling, VF-1 feedback, naturalness, production performance.