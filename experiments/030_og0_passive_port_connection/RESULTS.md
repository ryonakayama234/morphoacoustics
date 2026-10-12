# OG-0 results — provisional research only

## GitHub validation (real repository)

On head `1ed8dad5a4ded0e7e4861cb439e9fe40a21a3a31`, the standard GitHub Actions **pull_request workflow** [run 38218919000](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38218919000) completed **successfully**. All Python 3.11, 3.12, 3.13 pytest jobs and the mypy typecheck job succeeded. The real-repository test suite includes the **8 targeted OG-0 tests**, including the experiment runner launched as a subprocess and a physically reversed edge-order contrast.

The equivalent [push workflow run 38218914661](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38218914661) also succeeded with the same four jobs. These outcomes establish integration/CI success for that commit, **not** independent physical/scientific adoption.

## Independent numerical check

The source file [wolfram/og0_oracle.wl](./wolfram/og0_oracle.wl) was fetched from this Draft branch and evaluated by the Wolfram Language service. It independently reproduced the ~504.41176 Hz fundamental, pressure reflection -1/3, reflected/transmitted power fractions 1/9 and 8/9, mismatched 733-Hz impedance -3.027514900845341e6 j Pa·s/m³, and matched outlet junction pressure, volume flow and nonzero real power. Wolfram internally used high precision; its matrix-composition roundoff is lower than the earlier machine-double snapshot recorded in `og0_wolfram.json`, not a changed physical model. Original pre-implementation oracle: [og0_wolfram.json](../../tests/scientific/oracles/og0_wolfram.json).

Earlier local debugging passed six targeted tests against a minimal reconstruction of the existing Fidelity-0 interfaces. The **real GitHub CI supersedes** that smoke test for actual repository integration.

## Remaining barriers

- [x] Experimental code, typed port validation, independent oracle, negative controls and provenance.
- [x] GitHub integration tests for Python 3.11/3.12/3.13 plus typecheck.
- [x] Rerun checked-in Wolfram source in Wolfram Language.
- [ ] Independent *physical/numerical* scientific reviewer signs off equations, sign conventions, tolerances, 1D limitations and conservation checks.
- [ ] Independent *code/API* reviewer audits validation paths, unchanged production contracts, and failure taxonomy.
- [ ] Preregistration [#91](https://github.com/ryonakayama234/morphoacoustics/pull/91) accepted/frozen; new protocol version required if revised after inspecting outcomes.
- [ ] Research decision formally recorded on parent [issue #90](https://github.com/ryonakayama234/morphoacoustics/issues/90).

**Status: PROVISIONAL_NUMERICAL_PASS / NOT INDEPENDENTLY REVIEWED / NOT ADOPTED.** This does not demonstrate arbitrary graphs, branches, tissue FSI or actual sound synthesis.
