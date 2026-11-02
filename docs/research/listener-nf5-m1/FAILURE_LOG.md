# FAILURE_LOG — independent negative and blocker ledger
## Preserved historical findings
- NF3 PR257: final C2 0/155 available positions, INDETERMINATE; geometric validity guard must not be weakened to improve paper coverage.
- NF4 PR261: C4 242/344 acceptance below 80%; ILD C4 2.34171 vs B3 2.06708 dB; bootstrap [-0.83938,+0.10474] dB; both folds failed, 500–2000Hz worse; posthoc B0 1.53527dB on accepted. Reusing opened SCUT final would invalidate new blind confirmation.
- NF5 G0-A2: rights edition conflict, shared Data.Delay [1,2] and short 128 tap FIR. No inference of absent absolute propagation times or physical time origin from metadata alone.
## M1 negative controls to record
Wrong archive hash; duplicate direction/zero radius; coordinate pole/az wrap misassignment; inconsistent four shells; same angular final direction in training different radius; insufficient spatial blocks; 5° buffer violation; low-band unqualified; common vs ear-specific gain/time; phase/real FIR failure; hidden IR read; false-green CI/no pipefail; rights/plane ambiguity; zero support. Any failure will be appended with code SHA, reproducer and classification, without rewriting passed historical gates.
