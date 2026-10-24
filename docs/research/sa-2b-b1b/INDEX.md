# B1b — independent local passive acoustic propagation (research)
Status: IMPLEMENTATION_IN_RESEARCH; verification/independent audit pending.
Parent: [B1 issue #177](https://github.com/ryonakayama234/morphoacoustics/issues/177). Stacked upon B1 Draft #178 / B0 Draft #176, not main.
Gate A2 was committed first: [GATE_A2_LOCAL_WAVEGUIDE.md](../sa-2b-b1/GATE_A2_LOCAL_WAVEGUIDE.md), commit ef7d74cbbafeca5113db9e4b34bbb0d220b228c4.
See [SYSTEM](SYSTEM.md), [DATA](DATA.md), [EXPERIMENT](EXPERIMENT.md), [RESULTS](RESULTS_20261024.md) (add after actual CI).
Executable: experiments/052_b1b_local_waveguide/run.py; test: tests/test_experiment_052_sa2b_b1b.py; workflow: sa-2b-b1b.yml.
The official Core interface, Studio, SMC and ASMR are untouched. A PASS never proves natural voice, true M0 shape, or native 48k physically coupled source/observer. The old B1 global implicit model stays an independent comparison and an archived experimental reference; production candidate selection requires documented transition.