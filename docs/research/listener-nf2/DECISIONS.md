# EL-NF2 — decision log

**D0 (2026-10-30):** Adopt static measured-domain relative receiver task, entire-direction holdout, nested joint direction/distance holdout, B0/B1/C1, explicit engineering gates and uncertainty caveat. C2 out of v1.0 gate until independently preregistered. Use simple method B1 by default if C1 advantage is unsupported. Carry physical frame and receiver plane as provenance, not invented anatomical identity.

**Risk A:** 49 directions only; test may have insufficient supported coverage or high direction sparsity. Stop/INDETERMINATE if valid final directions <8. Do not expand angular threshold after inspecting test acoustic scores.

**Risk B:** Strongly correlated frequency/distance samples. Bootstrap entire direction cluster; do not treat individual band/distance as independent human heads.

**Risk C:** Data refer to a single artificial head and unresolved receiver port. Do not infer generalized embodied hearing, personal physiology, eardrum pressure, contact or subjective ASMR.

**Risk D:** Static HRIR interpolation != moving-source acoustic renderer. Future motion physics separately gated.

**Adoption:** No main / Core / ASMR runtime / Studio integration until full independent science review, numerical and physical boundary audits and explicit release decision.
