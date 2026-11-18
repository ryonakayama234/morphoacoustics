# BODYMAP-B2-RUNMANIFEST-20261113-01 — executor ADDENDUM-02

Scientific evaluation count at freeze: **0/15**. Owner GO and supervisor ADDENDUM-01 apply unchanged.

- Scientific Core checkout: exact clean 0bb60cc227d231ec1cb67b701a849172ed92164b, separate from this evidence checkout.
- Runner: study_runner.py SHA-256 **0b6f627cee27074848b00580dfc656a0507048da7599a30017b3ad3954049b0b**. Frozen by this commit BEFORE scientific execution.
- Three input hashes verified: original e662141d1f79c7f1bb3663acdd33e476e2c949bf757fcf734a97005ede27aca8; aux 884ca8de62840b3e41b0204872936ae696504d308b1b16394893c1889d759d22; ADDENDUM-01 6214dba2532d1b567ac1876cabbf84429ffdc42bed26fecf5ef5ef21fffb581f.
- Python 3.11.18; both frozen locks installed with --require-hashes --only-binary=:all: (uv pip frontend, 14 distributions). NumPy 2.4.6 / SciPy 1.17.1 / mpmath 1.4.1. PYTHONPATH includes pin/src.
- M0 readback digest and all 16 cells match; LF consumed source SHA-256 724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc; DFT a33c54be89317bbd09bd7e07a85f4306260d7a13623318fff2054a54630076d1.
- Eight KNOWN_ENGINEERING_DATA cases reproduce registered tolerances with unchanged reviewer acceptance code. Original report FAIL is preserved: its only failed aggregate is mutations_candidate_probes, because SWAP-GEOM-PORT uses uniform U6. Following supervisor acceptance comment 6826724845, supplementary M0 probe refuses PHYSICAL_IDENTITY_MISMATCH. No scientific code edit or threshold relaxation.
- Run exactly 12 primary and 3 independent-process repeated null cases once, followed by 9 negative families once using M0 for port reversal. No retries after partial results.
- Save arrays (complex128 preserves Re/Im), source buffer/DFT, projected spectrum, native f64 pressure, internal states, coefficients, power integrals, pack/0, receipts and stdout/stderr. Stop preserves partial outputs and journal.
- 60 minute wall cap includes engineering start (engineering/stderr.log creation timestamp) and study/self-check. No new cases or sweeps. Source remains RECOMPUTED pending independent same-run chain review; full_verified_source_state UNKNOWN.
- Executor diagnostics only: final independent 15-case oracle adjudication and acceptance belong to supervisor after submission. IMPLEMENTATION_CONFORMANCE UNRESOLVED and EFFECT UNKNOWN until then.
