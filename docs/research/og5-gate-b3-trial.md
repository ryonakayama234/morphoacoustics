# OG-5 Gate B3 — independent Core/full-port evidence candidate

**State: B3 IMPLEMENTATION TRIAL / NOT ADOPTED.** PR #112. A1 frozen acceptance remains authoritative; this file is a live experiment receipt and workflow instruction, not a Gate C scientific decision.

## What is being checked

Two **separate Wolfram 15.0.1 methods**, a 20×20 coupled global complex equation solve and passive impedance recursion/full endpoint reconstruction, generated and archived 144 immutable case-input/output bundles in \`og5-b3-oracle-00.json\` through \`07.json\`. Each shard has 18 named cases and complete 10 endpoint complex \`p\` and \`U\` results for **both** algorithms. Their source is \`og5-gate-b3-independent-oracle.wl\`; no production Core imports. The evaluation stage separately ran all 144 before archiving.

\`\`\`mermaid
flowchart LR
  S["Validated Blueprint (5 tubes / 2 junctions)"] --> P["Core prepare_tree5"]
  P --> R["Core response (20 complex values)"]
  W["Independent Wolfram global 20x20"] --> F["8 frozen JSON shards / 144 cases"]
  I["Independent Wolfram scalar impedance recursion"] --> F
  R --> Q["B3 fail-closed scorer"]
  F --> Q
  Q --> E["144 raw case receipts + 8 wrong-law controls"]
  E --> T["Two exact-HEAD CI artifacts (different runners)"]
  T --> C["Gate C critical scientific / data review — NOT AUTOMATIC"]
\`\`\`

**Frozen acceptance:** 144/144 no omissions; for each case and **each** Wolfram reference, max over 10 ports of \`abs(p-p_ref)/1.372 Pa\` and \`abs(U-U_ref)/1e-6 m³/s\` ≤1e-10. Scorer independently verifies power reconstruction, scaled junction diagnostics ≤1e-10, scaled matrix residual ≤1e-12, condition2 ≤1e4, zero power at closed port, positive source power, physical identity and exact ordered port names. Eight prescribed wrong-law/output mutants must differ >1e-6 or return an explicit valid numeric refusal. No waveform or anatomy claim.

Archived independent Wolfram generation summary: **144/144 cases, ten p/U port pairs each**, max global-vs-recursion normalized discrepancy \`2.602356456953343e-14\`, max recursive power defect \`3.0408037606009796e-15\`, max branch flow defect \`2.711828597234095e-15\`. These are **reference-only**, not a Core-versus-Wolfram pass.

## Reproducible machine procedure

After installing \`pip install -e '.[dev]'\` on a checked-out exact candidate HEAD, run:

\`\`\`bash
HEAD="$(git rev-parse HEAD)"
python checks/check_og5_gate_b3.py --expected-head "$HEAD" --output-dir /tmp/og5-b3-evidence
\`\`\`

The dedicated \`.github/workflows/og5-gate-b3-independent.yml\` uses the PR's **head SHA**, not GitHub's synthetic PR merge commit, with two isolated workers \`a\` and \`b\`. Each stores 144 raw Core+oracle case outputs, eight control outcomes, metrics, versioned source/oracle SHA256, Git HEAD, workflow run identifiers, and per-file checksum sidecars. A comparison job requires the full receipts to be byte-for-byte identical and checks all sidecar hashes. Failure does not satisfy adoption.

The scorer uses the real \`prepare_tree5().response()\` public candidate path; it never supplies Wolfram states to the physical solver. The mutation harness injects changes only into the Core linear-system rows or Core's reported endpoint identity, leaving the oracle pinned. It reverts each injection after one case.

## Documentation/ABI and limitations

\`\`\`mermaid
flowchart TD
  BP["GraphBlueprint: revisioned body + load + source"] --> V["Shape, refs, topology, capability"]
  V --> PP["Immutable PreparedTree5 / preparation digest"]
  PP --> OBS["Full Observation: 10 port IDs, p/U/power/metrics"]
  OBS --> HASH["Observation identity + outer SHA-bound raw evidence"]
  HASH --> C["Gate C review"]
  UI["Studio layout"] -. "not in physical hashes" .-> BP
\`\`\`

The gate does not support arbitrary graph topologies, 3D anatomy, FSI, active motor gestures, biological speaking, WAV, Studio body editing or release of generalized Character Creator. It reuses the **frozen** A1 Blueprint/Snapshot/Observation types, stable INVALID/UNSUPPORTED/NUMERICALLY_UNRESOLVED, and all existing B2 refusal fixtures; new B3 JSON records are *outer scientific evidence*, not an ABI extension. Prior OG-3/OG-4, Exp028/029 and original X2a physical smoke must be reaudited separately on final exact HEAD.

**Gate C remains required:** examine actual CI logs, both raw archives and checksum identities, historic negative run evidence, numerical laws and API security/reproducibility; disclose shared assistant context; record LIMITED/INCONCLUSIVE/REJECT before merge. An unverified PR cannot claim a new supported Core feature.
