# OD-3 A0 amendment — source SHA portability and receipt integrity
Date: 2026-11-02 JST. **Prospective amendment after failed audit**, never pretend this was frozen in original preregistration 2092805.

## Cross-run SHA discrepancy, not hidden
- Previous OD-2 Actions run 41325182878: source LF100 SHA256 4d075fd89958ff481507661ea43e4602ed5fe72b0104bc897685b1f696abf529.
- First OD-3 Actions run 41381823153: same code-defined LF100 source, current SHA 724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc; native source/geometry/pressure model passed.
- Added strict comparison against earlier runner's exact SHA after seeing this discrepancy: Actions run 41382450478 **FAILED SOURCE_MISMATCH**; preserve historical red run.
- On run 41382577413, physically re-ran UNMODIFIED OD-2 suite on the SAME runner as OD-3. It produced source SHA 724412c20... and passed all original source/shape/M0 quantized acoustic regression. Its six shape contrasts were near older results at floating-point roundoff. This supports the interpretation of differing low bits across independently provisioned numerical environments, though original LF100 array bytes were not archived for a cross-machine samplewise error proof.
- New gate: TWO source generations in same process must have exactly matching raw float64 SHA; unmodified OD-2 in same CI job must report EXACT same source SHA and task-plan SHA as OD-3; G0 source/geometry/acoustic regression against inherited Exp029 remains enforced; entire source code inventory still pinned. Keep each-run SHA in receipt. Do NOT assert universal cross-CPU byte equality from NumPy version alone. No source law, body, coordinate, G0/G1 or acoustic observer changed. Cross-run byte-portability now NOT ESTABLISHED.
- CI 41382731990 demonstrates same-run OD-2/OD-3 exact source and task plan identity and all physical/replay/adversarial gates.

## Code-review P2 repair
Codex first review at SHA 3ec5c8b identified one-ULP raw pressure forgery: changing Pa and manifest file SHA inside replay tolerance passed because saved sample SHA was not compared with the scientific decision raw Pa receipt. New implementation independently validates native float64 sample SHA against the trusted rederived decision plus the preexisting 1e-12 physics replay tolerance; explicit one-ULP + forged manifest test refuses. The initial green remains historical and is not a proof of this new audit gate. Changes c322000 and 7429210, final dedicated CI 41382731990 passed.

## Unchanged acceptance
Only existing OD-2 bodies, frozen Exp027/029 3-task field and genuine 1D pressure source. Only task1 onset and offset delayed by +0.020s for G1. No wave processing, physical model rewrite, Studio UI, production API, human voice or ASMR claim. Original design freeze is immutable; this is an auditable amendment.
