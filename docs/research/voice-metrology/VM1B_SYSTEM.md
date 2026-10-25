# VM-1B physical system and evidence ownership

**Research-only; no Core main, Studio UI, SMC, ASMR, held Voice/WG2 PR, or Take changes.** Proposed foundation programme [#199](https://github.com/ryonakayama234/morphoacoustics/issues/199).

```mermaid
flowchart LR
  BODY["Frozen /a/ M0/M1 16-section bodies"] --> FREQ["Independent frequency transfer matrices T1..T16"]
  BODY --> NATIVE["Adopted PassiveWaveguideSession n=2"]
  LAW["Declared matched / discrete B0 shunt R+inertance"] --> FREQ
  LAW --> NATIVE
  PULSE["SI one-tick input volume"] --> NATIVE
  FREQ --> CMP["Complex physical-port compare: HpU,Zin,HU"]
  NATIVE --> DFT["Separate native p_in/U_in/p_mouth/U_mouth DFT 0.30/0.60s"]
  DFT --> CMP
  CMP --> EVID["Gate results, exact hashes and limitations"]
  EVID -. "research evidence, no UI write" .-> CORE["Core Foundation #199"]
```

**Two independent algorithm paths but shared physical assumptions:** frequency-domain 2×2 section transfer and exact phasor shunt-B0 derivation versus per-tick scattering/queue dynamics. The two paths share constants, geometry, *assumed* B0 R/m and ideal-flow source. Their agreement is a strong **software/numerical consistency** test, not independent evidence that the B0 circuit is a correct physical mouth radiation law.

Physical port `p_mouth,U_mouth` is the 1D mouth-boundary effort/flow pair, **not** a receiver pressure, sample-rate postprocessor, audience audio or listener sound. The source is a **prescribed physical flow**, not self-sustained vocal-fold oscillation. No gain/F0/formant quality inference.

Future extension principle: typed p/U ports and matched provenance are needed for an eventual swappable organ model, but no generic graph-to-WAV solver or universal model ABI is being introduced by this research. The accepted Studio Character/Motion/Scene canvas layout is protected; when UI expansion is necessary, **stop and submit an explicit proposal first**.