# OG-0 results — provisional research only

## Amendment 01 — post-exploratory controlled regression (2026-10-12)

On commit `9510c0cdf341a131546050deeb1f00b458ac09df`, the amended GitHub Actions PR workflow [run 38254916672](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38254916672) **succeeded** across Python 3.11/3.12/3.13 pytest and mypy typecheck. Python 3.11 output reports **113 passed**, including **13 OG-0 parameterized targeted cases** (8 original + 5 amendment cases). The [push workflow run 38254911628](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38254911628) also passed.

The updated runner checks an analytic incident/reflected/transmitted wave oracle across the seven frequencies `[80,250,400,733,1200,2000,4000] Hz`; a deliberately WRONG junction `J=diag(1,SA/SB)` must be rejected by that independent wave oracle; and ideal pressure-release terminal mean power must vanish, in contrast to the separate nonzero-power matched termination. A changed model/runner/oracle file SHA or numerical environment changes the runner's reproducibility identity.

The checked-in [Wolfram source](./wolfram/og0_oracle.wl) was re-evaluated after the amendment. It independently returned `r=-1/3`, pressure transmission `t=2/3`, `R=1/9`, `T=8/9`, `a=1+0.4j Pa` at A.out and A.in at 733 Hz approximately `(-0.151276473874+1.299323190050i) Pa`, `(2.92135096243e-7+6.12420284707e-7i) m³/s`. It found the **correct** wave construction agrees with the transfer model to high precision, whereas **incorrect particle-velocity continuity** produces normalized A.in state discrepancy `0.5861352498274852` at 733 Hz under scale `(|a|,|a|/ZA)`, far beyond the gate `0.1`.

**Chronology and claim limitation:** Both Wolfram wave-oracle fixtures and the amended boundary-condition criteria were added *after* the exploratory OG-0 CI outcomes and are **not preregistered prospective scientific confirmation**. [Protocol amendment 01](https://github.com/ryonakayama234/morphoacoustics/blob/research/og0-prereg/docs/research/og0-amendment-01.md) explicitly records this. These CI outcomes only support the **amended regression checks**. Independent physics/numerical and code/API signoff still missing; adoption decision stays **NOT ADOPTED**.

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
