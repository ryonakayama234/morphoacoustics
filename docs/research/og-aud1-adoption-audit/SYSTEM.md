# SYSTEM — acceptance graph, physical vs creator boundaries

Status: **AUDIT PROPOSAL / Gate A unsigned / E2E not done**. This is not an implemented Studio architecture.

~~~mermaid
flowchart TD
 UI["Studio: Character + validated preset A/B + fixed performance task"] --> RQ["Exact capability/version request"]
 VIEW["Read-only A-J-(B,C) node/port diagram"] --- UI
 RQ --> VAL["Core: validate typed ports/J, snapshot, source, capability"]
 VAL --> PRE["PreparedBranch3 and recomputed immutable body digest"]
 PRE --> SOL["Validated causal 3-duct matched outlet solver"]
 SRC["Prescribed U(t), m³/s, fixed source ID/hash"] --> SOL
 SOL --> P["All port p[Pa]/U[m³/s] + physics diagnostics"]
 P --> RAW["Raw p(A.in,t) Pa + source U(t)"]
 RAW --> PAIR["Shared gain; two labeled non-radiated PCM16 monitor WAVs"]
 PAIR --> TRUST["Studio: exact Core SHA, schema, size, hashes, SI/format, path verifier"]
 TRUST --> TAKE["Atomic immutable verified research Take pair"]
 TAKE --> AUD["One-shot A/B listening + reload/restart + causal body diff"]
 VAL --> REJECT["INVALID / UNSUPPORTED / NUMERICALLY_UNRESOLVED / FAILED"]
 REJECT --> NONE["No playable Take; no fallback"]
~~~

## Physics / source plane

Nodes A,B,C are fixed ducts; J is a **typed 3-way acoustic.p_u junction**, not merely three canvas lines. Pressure is continuous at J, and signed volume flow obeys U_A.out=U_B.in+U_C.in. Both distal terminations are mathematically matched and absorb waves without physical exterior radiation. A volume-flow source U(t) is prescribed at A.in and p(A.in,t) is an **internal pressure observation**, not a microphone signal.

Three-duct ideal line model: Z_i=rho*c/S_i; Z_J=(1/Z_B+1/Z_C)^(-1); r=(Z_J-Z_A)/(Z_J+Z_A), tau=2L_A/c; p(A.in,t)=Z_A[U(t)+2 Sum_{k>=1}r^k U(t-k*tau)]. The source is a fixed analytical stimulus, not a task-level motor program physically realized from a Script. No claims of glottal feedback, articulatory motion, speech, mouth radiation, listener stereo, 3D body or subjective naturalness.

## Review and release state machine

~~~mermaid
flowchart LR
 E["Exp043–045: exploratory"] --> A{"Gate A: independent prospective protocol signature?"}
 A -->|No| H["HOLD"]
 A -->|Yes| B{"Gate B: *new* confirmatory Core + independent numerical/security audit?"}
 B -->|No| H
 B -->|Yes| C["GO_LIMITED_CORE possible; new pinned API"]
 C --> D{"Gate C: real Studio fresh Take, verification and restart?"}
 D -->|No| H
 D -->|Yes| F{"Gate D: independent creator review + explicit E2E decision?"}
 F -->|No| H
 F -->|Yes| G["GO_LIMITED_E2E"]
~~~

All decisions are bound to **exact commit SHAs**. Review failures and threshold amendments are indexed with time and new prospective test sets. Never let a CI-green or Wolfram-match bypass independent review. Keep all PRs draft/no merge until their applicable gate decision. A real domain reviewer must independently sign physics and a separate security/API reviewer must sign trust. Shared AI agents cannot certify their own independence.
