# B0 — frozen independent wave oracle, before RP1 Gate B implementation

Date: 2026-11-04 JST. **Generated after D0 registration and after Gate A code; BEFORE new RP1 Core-matrix Gate B coupler code.**

- Preregistered D0 science protocol Git commit: `a33c8c68879f732cd830b2caab6b8024b5322297`.
- Frozen 16-row JS complex travelling-wave oracle: Git blob `81286d0a2b7ea26cf33ce65d0eb98be6df47b607`, path `experiments/045_el_rp1_receiver_port/b0_wave_oracle_16.json`.
- Independently authored JS source: Git blob `20ccd339fb55883082ff349d0ff4affddbc676fd`, path `experiments/045_el_rp1_receiver_port/rebuild_b0.mjs`.
- Source equation: forward entrance wave `A=ps/[(1+rs)+(1-rs)*Gamma*exp(-2ikL)]`; reflected entrance wave `B=A*Gamma*exp(-2ikL)`; `p0=A+B`, `u0=(A-B)/Zc`, `pL=A*exp(-ikL)*(1+Gamma)`, `uL=A*exp(-ikL)*(1-Gamma)/Zc`.
- Gamma=(Zt-Zc)/(Zt+Zc), rs=Zs/Zc, Zc=rho*c/area; separate source-resistor and terminal-power accounting.
- One row has exactly 15 columns in a known order; **reject shortened/longer rows before any zip comparison**. Use exact JSON metadata/parameter checks and pinned Git blob hash.
- No training/fit, unsealed empirical data, measured KU100 HRIR, real-ear hypothesis or perceptual scoring. "Frozen reference" means independently calculated **synthetic** 1D numbers, not blinded measurement evidence.
- R2 old 18 Wolfram + 24 ECMAScript rows remain on their historical PRs without rewriting.

## B0 state
`ORACLE_FROZEN / GATE_B_COUPLER_NOT_IMPLEMENTED_AT_B0`. The commit containing this note and oracle must predate the new Python coupler; tests must authenticate its exact Git blob against this documented value.

Rebuild from this source (when Node.js is available):

```bash
node experiments/045_el_rp1_receiver_port/rebuild_b0.mjs > /tmp/el-rp1-b0-rebuilt.json
cmp experiments/045_el_rp1_receiver_port/b0_wave_oracle_16.json /tmp/el-rp1-b0-rebuilt.json
```
