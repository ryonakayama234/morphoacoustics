# Experiment 045 — causal six-port organ-graph monitor

**Research-only Draft. NO physical Gate B, NO adopted Core/Studio capability.**

This adds an explicitly causal pressure-monitor calculation for the same fixed 3-duct graph of Core [OG-AUD1 #130](https://github.com/ryonakayama234/morphoacoustics/issues/130), stacked on [Experiment 044](../044_og_aud1_monitor/README.md). Experiment 044's ideal 4kHz FFT cut is formally acausal. This follow-on avoids that cut by evaluating the actual delayed reflection series of the *same ideal lossless matched-load model*.

## Organ-node and typed junction diagram

~~~mermaid
flowchart LR
 U["Input U(t), m³/s"] --> A["A: L=8cm S=3cm²"]
 A --> J(("J: p equal; U conserved"))
 J --> B["B: L=9cm S=3cm²"]
 J --> C["C: L=6cm S=1.5 or 6cm²"]
 B --> L1["Matched load"]
 C --> L2["Matched load"]
 A -. "monitor p(A.in), Pa" .-> W["48k mono WAV (NON-RADIATED)"]
~~~

Ports A.in/A.out, B.in/B.out, C.in/C.out carry signed pressure [Pa] and **volume flow** [m³/s]. Drawn connector lines are not sufficient to define physical compatibility; Core must validate junction type/law and actual body prep before a future Studio contract.

For Z0 = rho*c / S_A, round-trip tau=2L_A/c, and downstream parallel impedance Z_J=(1/Z_B+1/Z_C)^-1, the reflection r=(Z_J-Z0)/(Z_J+Z0). The causal solution is:

p(A.in,t) = Z0 [U(t) + 2 SUM_{k>=1} r^k U(t-k*tau)]

The runner evaluates 48 **analytically delayed** echoes (subsample fractional delay, no sample rounding). It checks conservative omitted-tail pressure, exact zero before source onset, six-port continuity, signed flow and integrated source-to-terminations energy. For the limited prescribed smooth source the resulting pair PCM16 WAVs agree byte-for-byte with Experiment 044: same audible example, stronger causal interpretation; **not** a new human voice.

## Run (WSL2/Linux)

~~~bash
python -m pip install numpy
cd experiments/045_og_aud1_causal_monitor
python -m unittest -v test_causal_monitor.py
python causal_monitor.py /tmp/og-aud1-045-run1
python causal_monitor.py /tmp/og-aud1-045-run2
sha256sum /tmp/og-aud1-045-run{1,2}/raw_U_m3_s.npy
~~~

Each destination must be unused. The output is one immutable manifest and two derived monitor WAVs plus raw SI source/pressure arrays. Source is shared and WAV uses **one shared playback scale**, never per-take peak normalization. Neither terminal produces exterior radiation.

## Experimental limits

No generic graph editing, area sweep beyond exactly 2 fixed C areas, source-filter feedback, tissue/FEM, realistic vocal fold, character dialog, radiation, true receiver model, calibrated SPL or user-visible adopted Take. The signed-power calculation depends on matched terminations and the full 1s record. This is exploratory; **scientific preregistration, independent review and Studio exact-SHA trusted integration remain open**.

Related searchable records: [SYSTEM](../../docs/research/og-aud1/SYSTEM.md) · [DATA](../../docs/research/og-aud1/DATA.md) · [EXPERIMENT](../../docs/research/og-aud1/EXPERIMENT.md) · [Results](RESULTS.md).
