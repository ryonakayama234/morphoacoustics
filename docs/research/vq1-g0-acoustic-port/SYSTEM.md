# VQ-1 G0-P SYSTEM — research-only same-tick inlet port

Status: PRE-IMPLEMENTATION PREREGISTRATION (2026-10-28 JST); no new solver run at registration. Source base: Core main `727b11ecf103f5c087cfcb820bdec11f883e7c03`. Creator delegated experimental implementation after design Draft #237. This child study has no production public API, Studio UI, glottal tissue, moving duct, or SFI branch import.

## Boundary & actual source semantics
Existing `PassiveWaveguideSession.step(U)` in `src/morphoacoustics_waveguide/passive_waveguide.py` implements a fixed static 1D serial FIFO acoustic waveguide. Each native tick: incident backward inlet pressure is the pre-shift first item `backward[0][0]` [Pa]. `Z0=rho*c/A0` [Pa*s/m3], `h=length/(c*cells_per_section)` [s]. Its source boundary is `a=b+Z0 U`; hence `p=a+b=2b+Z0 U` [Pa], `source_work=h*p*U` [J]. The port is oriented U>0 **into the tract**.

This is exactly a *discrete* boundary, not continuous-time midpoint acoustic impedance. This module MUST use the actually native h; it MUST NOT substitute the research SFI-2/3 midpoint backend at 48k. The only trusted Core step is `PassiveWaveguideSession.step()`; leave it unchanged.

## Research architecture

```mermaid
flowchart LR
  B["Prepared fixed 1D tract + native h"] --> W["Core PassiveWaveguideSession"]
  W --> S["G0 research snapshot\ntick + immutable native state fingerprint + b"]
  S --> P["pure peek(snapshot,U)\np=2b+Z0U, W=h pU"]
  P --> C["commit_once(snapshot,U)\nvalidate freshness then actual Core step"]
  C --> E["independent oracle + signed energy audit"]
  E -. "G1 static wall pressure is a different model" .-> G["G1-S measured pressure reference (HOLD here)"]
```

The adapter lives in `experiments/054_vq1_g0_port/port.py` and deliberately reads private FIFO state, marked **version-pinned experimental only**. Its snapshot fingerprints every wave FIFO, B0 q, complete immutable config representation, native tick and session ownership; later direct out-of-band mutation must cause a stale-state refusal. Snapshot/peek never calls `step`, advances FIFO, changes B0 q, or rewinds. `commit_once` validates the exact captured state and uses one existing `step()`; the Core step already precomputes candidates before committing live state. Research API explicitly single-threaded; a production concurrency-safe interface would need its own approval. No generic solver graph, moving duct, source-wall power, or Studio UI.

## Scientific separation
G0 tests **only** same-tick p/U port, failure atomicity, deterministic state and passive acoustic power. The port is not a tissue force. The subsequent G1-S static measured M5 pressure/geometry identification and G1-D moving-wall force/work remain separate conditional research gates. A G0 PASS gives no voice, self-oscillation or creator GO. Source and receiver are still absent.
