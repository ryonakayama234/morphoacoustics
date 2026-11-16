# EL-NF2 — decision log

**D0 (2026-10-30):** Adopt static measured-domain relative receiver task, entire-direction holdout, nested joint direction/distance holdout, B0/B1/C1, explicit engineering gates and uncertainty caveat. C2 out of v1.0 gate until independently preregistered. Use simple method B1 by default if C1 advantage is unsupported. Carry physical frame and receiver plane as provenance, not invented anatomical identity.

**Risk A:** 49 directions only; test may have insufficient supported coverage or high direction sparsity. Stop/INDETERMINATE if valid final directions <8. Do not expand angular threshold after inspecting test acoustic scores.

**Risk B:** Strongly correlated frequency/distance samples. Bootstrap entire direction cluster; do not treat individual band/distance as independent human heads.

**Risk C:** Data refer to a single artificial head and unresolved receiver port. Do not infer generalized embodied hearing, personal physiology, eardrum pressure, contact or subjective ASMR.

**Risk D:** Static HRIR interpolation != moving-source acoustic renderer. Future motion physics separately gated.

**Adoption:** No main / Core / ASMR runtime / Studio integration until full independent science review, numerical and physical boundary audits and explicit release decision.


**D3 (2026-10-30):** [Actual measured run 41050468955](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41050468955) passed original-MD5 integrity, synthetic and mutation tests, measured evaluator and evidence arithmetic audit, but frozen G3 outcome is **REVISE_OR_REJECT**. Final median ILD C1 1.921281 dB vs direct B1 2.751612 dB (-30.18%), but 95% direction-cluster CI B1−C1 [-0.0878,1.4184] dB includes zero; B0 better than C1 in heldout S1 and validation. **No adoption, no posthoc threshold changes, no final-fold algorithm tuning.** Numeric evidence artifact 12974606905 archived.

**D3 implementation audit:** Explicitly limit claimed support to the implemented 45-degree nearest-training-point guard plus radial bounds; prereg phrase "convex local angular cap" is not fully verified, so a genuine interpolation-hull validity certificate remains OPEN. Additionally, author-written arithmetic auditing is not external scientific review. Any successor must prereg a *new independent dataset or holdout*, not rebrand current final test as newly unseen.

**D4:** G4/G5 remain PENDING. A future deliberate choice between B0/B1/C1 or an entirely new C2 must be based on independent evidence and a separate adoption RFC, not this negative v1.0 gate.
