# RESULTS — existing evidence only; audit decision HOLD

**2026-10-20 exploratory audit of current exact PR #134 head \`8ee5c04adefedbcba902c17435eac3b020e7c10e\`**. This record follows existing experimental results, so it **cannot** be called a prospective confirmatory Gate B. All independent external signatures remain pending.

## GitHub

[Core experimental PR #134](https://github.com/ryonakayama234/morphoacoustics/pull/134) is a Draft stacked on #132; no peer reviews yet. [Workflow 39434179523](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39434179523) completed successfully with both Python 3.11 and Python 3.13; at the checked exact head OG-3 / OG-4 / SV-1 and general tests workflows were also successful. Pass means engineering regressions in tested environments, not scientific adoption. Studio [#20](https://github.com/ryonakayama234/morphoacoustics-studio/issues/20) remains an unimplemented runtime; [Studio Draft #21](https://github.com/ryonakayama234/morphoacoustics-studio/pull/21) is docs-only.

## Wolfram: a freshly assembled 12-state full-port 16-case audit

Independently solve 12 complex p and q = Z_ref U port variables for A.in/A.out/B.in/B.out/C.in/C.out with three propagation pairs, pressure continuity twice, signed volume-flow balance once, both matched terminations, one A.in U source. Exact 16 previously visible exploratory cases: C area \`{.00015,.00060}\` m² × f \`{0,80,233,733,997,1801,2801,4000}\` Hz.

- Max rel complex global-vs-analytic Z_in error: **5.616671087228337e-16**
- Max absolute signed J volume-flow residual: **4.577529034063484e-22 m³/s**
- Max relative input/output mean power mismatch: **3.888492353255547e-16**
- Min Re Z_in: **457333.3333333334 Pa·s/m³** (>0)
- Symbolic independent derivation validates \`1-r^2=(1+r)^2*Z0/Z_J\` and \`Re Zin = Z0(1-r^2)/(1+r^2-2 r cos(theta))\` for real |r|<1 and positive impedances.
- The separate [oracle script](oracle_global_16.wl) records an independently assembled equation formulation. It shares the ideal 1D physics assumptions with Python; it is not measurement of a real biological voice or truly independent peer review.

## Findings by class

**GREEN (exploration):** restricted network model and causal-delay mathematics are coherent across tested conditions; passive, right-sign J balance; 2-body numerical difference with same source. **AMBER (blocking for physical adoption):** known-case rather than fresh prospectively reserved oracle, no signed science security review, narrow self-consistency tests, source/alias/frequency error budget not fully approved, no output prepared-body digest verified or versioned trusted adapter. **RED/NOT DONE (for requested E2E):** no actual Studio branch3 Perform→new immutable paired Take→restart replay or creator auditory pilot. Never label as a FAILED test when simply not implemented; instead track \`NOT_RUN\`.

**Decision now: \`HOLD_ADOPTION\`.** Keep experiment-only Drafts separate. Proposed future Gate A/B values in [EXPERIMENT](EXPERIMENT.md) are candidates, explicitly not thresholds retroactively used to pass this experiment.
