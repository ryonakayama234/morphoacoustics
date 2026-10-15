# OG-3 Gate B — minimal public fixed two-port candidate (2026-10-15)

**IMPLEMENTATION CANDIDATE / DRAFT / NOT ADOPTED.**
Parent [Core #100](https://github.com/ryonakayama234/morphoacoustics/issues/100); physical design [Gate A PR #102](https://github.com/ryonakayama234/morphoacoustics/pull/102), X2a isolation [#103](https://github.com/ryonakayama234/morphoacoustics/issues/103). This separate implementation PR **stacks on the Gate A design branch**, NOT on main; no merge or independent reviewer approval implied. The code may change after automated CI/independent critique.

## System, data and physics

```mermaid
flowchart TD
 B["OrganGraphBlueprint: 2 named organs + 2-port junction, exact revisions"] --> V["validate_graph: SI + port type/orientation, graph connectivity"]
 V --> C["prepare_graph: fixed2 capability only"]
 C --> P["PreparedPhysicalGraph: 2 retained UniformTube nodes; identity/digests"]
 P --> O["observe_transfer: unloaded 2x2 complex T on explicit grid"]
 O --> R["Immutable observation: frequencies, 4 re/im pairs each, digests"]
 C -. "valid unsupported branch or mixed medium" .-> U["UNSUPPORTED"]
 V -. "invalid topology, SI, wiring" .-> I["INVALID"]
```

- Code in `src/morphoacoustics/physical/organ_graph.py` and `src/morphoacoustics/preparation/graph.py`, **direct subpackage imports**; no old initializer or old acoustic primitive changes; no runtime imports of Experiment039. Only fixed passive lossless **serial two-node** topology is computed. Legal three-port graph validation stays valid then returns `UNSUPPORTED` for this backend.
- `[p_in,U_in]=T_A*T_B[p_out,U_out]`, `e^(+iωt)`, `Z=ρ c/A` [Pa s/m³]. Complex normalized output `S T S^-1`, `S=diag(1,Z_A)`. Ideal p and **volume flow U** continuity at serial zero-volume junction. No waveform, flow excitation or glottal dynamics. `matched` and `pressure_release` are only provenance/terminal metadata for an **unloaded two-port**; the full complex T does not depend on which is recorded.
- Candidate identities: `blueprint_digest` hashes sorted *named* organ/junction collections, oriented edge ordering, exact versions/physical SI parameters encoded as big-endian binary64 hex, source/load/termination and schema. `preparation_digest` adds backend/version/port mapping; `observation_digest` adds ordered frequency bytes (with normalized signed zero) and real/imag binary64 values. Core authoritative; **no Python/JavaScript cross-runtime byte verification claimed yet**. Snapshots must roundtrip exact prep digest.
- Explicit requests: nonempty 1-D **at most 4096** finite numerical frequency points in `0..4000 Hz`. >4000 Hz `UNSUPPORTED`; negative/NaN/Inf/wrong shape `INVALID`; `-0.0` normalized to `+0.0` before evaluation and hash. The 4 kHz cap is an engineering *capability window*, **not scientific validation of every frequency/body**: OG-2 frozen scientific comparisons cover only seven specified points.
- Status: `INVALID` for ill-formed/ill-typed graph, `UNSUPPORTED` for recognized backend capability absent, `NUMERICALLY_UNRESOLVED` for nonfinite computed matrix. `INFEASIBLE` remains reserved for task-level motor realization outside this API; `FAILED` is the job/runtime outcome. No fabricated WAV on failure.

## Validation contract — **not acceptance evidence until CI/artifacts exist**

- Clean-room `tests/test_prepared_graph_public.py` imports only `src/morphoacoustics/` plus separately reads the immutable OG-2 Wolfram JSON **as oracle data**, never imports experiment Python.
- Compare full complex normalized 7-frequency matrix to `experiments/039_og2_prepared_graph/wolfram/og2_oracle.json` with `≤1e-10`, equal-area A+B vs one 0.17-m tube `≤1e-10`, lossless flux `T†JT≈J`, and negative false particle velocity connection.
- Test port/ID/units, disconnected graph, valid unsupported branch, exact B-only revisions/physics/digest, reordered organ collection digest identity, snapshotted reconstruction, terminal-invariant *unloaded* T, shape/frequency and ±0.0 identity.
- Source-freeze: `limited_live.py` adds **only two new explicitly hash-pinned files**:
  - `physical/organ_graph.py` Git blob `ea72548dd3fb771436dbfe0980ae5ab5ed3e9b17`
  - `preparation/graph.py` Git blob `405fb65ce65118b86384896e3406871da9408528`
  All **23 old pins and original source blobs remain unchanged**, original unknown-file/tamper failure tests must continue to pass. This manifest change only makes the audit aware of new physically isolated source; true preflight X2a smoke **must still be demonstrated**.
- Require full 3.11/3.12/3.13 CI, mypy, exact PR head, direct re-evaluation of Wolfram/clean output. Genuine X2a audited-NumPy 2.4.6 two-Take 0.5s WAV+physical trace with immutable sha256 artifacts remains a **blocking unverified gate**, not implied by generic pytest.
- Independent numerical and code/API review required; correlated AI feedback is not independent human acceptance. This PR is draft and must not merge or be declared publicly adopted even on green CI.

## Future Studio contract

Studio sends named graph/revision + explicit physical selection through a separately versioned adapter. No UI canvas coordinates, Character narrative, Script/Direction or generated audio enters Core blueprint digest. No Studio changes in this PR.
