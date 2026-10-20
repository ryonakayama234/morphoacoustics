# DATA — admission contract / frozen evidence boundaries

Status: **conceptual acceptance requirements, NOT current public schema**.

~~~mermaid
flowchart LR
 CH["Studio Character, Script/Direction"] --> SEL["Exact fixed graph preset ID/revision"]
 BLUE["Core GraphBlueprint: A,B,C typed ports, J law, loads"] --> PRE["Core prepared digest + capability + trusted revision"]
 SEL --> PRE
 SRC["Fixed source U(t) SI & source bytes hash"] --> OBS["Core newly calculated p/U states"]
 PRE --> OBS
 OBS --> TRACE["Signed per-port SI + time/energy/oracle diagnostics"]
 OBS --> RAW["Raw p(A.in) Pa"]
 RAW --> WAV["Pair-shared playback gain, 48k mono PCM16"]
 TRACE --> RECEIPT["Versioned verified receipt, artifact hashes, code SHA"]
 WAV --> RECEIPT
 RECEIPT --> VERIFY["Studio independent validation & immutable pair commit"]
 VERIFY --> TAKES["Two Takes + Character context + body diff + replay"]
~~~

## Six distinct identities

1. Creator's Character/Script/Direction and viewer layout: Studio-owned; no acoustic numerical values invented in presentation.
2. GraphBlueprint: explicit schema/revisions/port types, geometry SI, fixed J orientation law, medium, matched B/C boundary and source-port declaration: Core-owned; not free topology.
3. PreparedGraph / PreparedBranch3: Core recomputes valid blueprint digest, preparation digest and approved backend capability; caller cannot assert a magic digest string to skip validation.
4. SourceProgram: SI volume-flow U(t), 48000 Hz, 48000 float64 real samples, deterministic finite-time program, exact source plane A.in, persisted exact byte hash; not glottal pressure, script interpretation or sound gain.
5. PhysicalObservation: p(A.in,t) raw Pa + all signed p/U port evidence, echo count/tail bound, causal start, power budget, model condition; no conflation of internal monitor with emitted/listener pressure.
6. AuditionPair + Studio Takes: one pairwise shared scale and two distinct PCM16 WAVs, separate source/raw/PCM SHA256, record of exact Core commit, reference body digests, format/endian/frame count, immutable content references, request/response version, no unverified artifacts.

## Strict trust / negative controls

Do NOT directly adopt current Experiment045 research manifest as a public Studio response: it lacks verified PreparedBranch3 digest/strict new capability and the Core checkout commit as a proven execution identity. A standalone code-file SHA256 and self-declared body settings do not meet trust. Permit only a clean exact-head pinned Core runner; no caller-supplied executable command, arbitrary destination, path traversal, symbolic-link escape or untrusted returned URLs. Validate before archive: exact schema, hashes/lengths/source byte identity, body binding, finite SI values, PCM format, computed gain, fixed source/monitor plane. On one failure, pair commit is atomic **no playable Takes**. Ignore no unsupported fallback to OG-4's 8-point snapshots, CC-A2 serial-body renderer, a precomputed WAV or a fabricated phasor interpolation.

Decision taxonomy: \`INVALID\` (malformed), \`UNSUPPORTED\` (lawful graph/out-of-scope source or body), \`NUMERICALLY_UNRESOLVED\` (failed conservation/precision), \`FAILED\` (execution/trust/archive error). Use \`INFEASIBLE\` only for actual physically unrealizable task-level gestures, not an invalid graph.

Code and manifest hashes alone cannot demonstrate source-provenance authenticity. When promoting to Core, receipt must bind exact commit + body digest and permit independent re-evaluation. Review should test hash corruption, altered body revision, stale checkout, swapped A/B pressure, modified source sample, wrong normalization, unsupported state, empty/missing artifact, malicious paths, read-only viewer coordinate mutation and reloaded historical Take semantics.
