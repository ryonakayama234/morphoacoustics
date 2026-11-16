# FAILURE_LOG — append-only failures and scope blockers

## F0 — registered limitations, not observed implementation failures (2026-11-04)
- Pressure-only fixed-termination response is non-identifying for changed receiver load (analytic counterexample).
- HRTF/reference-plane matching alone does not prove a calibrated pressure–volume-flow two-port.
- KU100/NF5 physical endpoint, timing, compensation, source method and rights questions remain separate blocked qualification work (PR #280).
- EL-R2-S1 18+24 synthetic numerical comparisons are not measured human ear validation.
- Research code and CI not yet executed as of registration.
- No independent human auditory-science review performed.

Subsequent bugs, negative results, failed Actions and corrections must be appended here with original failing input and reproduction location; do not delete this section.

## F1 — Gate B first CI reproduction failure (2026-11-04 JST)
- First full Gate B CI head `b152a5cb59e33c642eba03fef9a9e62055838eb4`: [push run 41787476209](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787476209) and [PR run 41787482020](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41787482020) both FAILED on Python 3.11 and 3.12 at exact bytewise `cmp` of independently regenerated Node.js JSON versus the original frozen B0 output (first reported differing byte 2494, line 105). The job stopped **before** Gate B Python numerical tests. This is **not** a passed physics experiment and not evidence that the source/receiver model is accurate or inaccurate.
- Scientific distinction: original B0 Git blob SHA `81286d0a2b7ea26cf33ce65d0eb98be6df47b607` remains unchanged and authenticated. JavaScript runtimes may differ in last floating-point digits for trigonometric calculations, so a cross-runtime byte-exact decimal JSON check is stricter than preregistered numerical physics acceptance; exact binary identity remains mandatory for the stored original archive, not for independently regenerated floating outputs.
- Remediation in next implementation commit: enforce complete 16x15 schema, immutable physical parameters, row/order checks and each component's **pre-registered E2 tolerances**, plus strong mutations that exceed them. No threshold relaxation, no rewritten original oracle, no original D0 editing. Re-evaluate both runtime and numerical tests at new exact head.
