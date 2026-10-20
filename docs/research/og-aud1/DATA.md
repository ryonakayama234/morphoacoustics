# OG-AUD1 / DATA — Proposed organ graph and Take boundary

> 2026-10-20. **CANDIDATE contract only; not an official schema or live API.** [SYSTEM](./SYSTEM.md) · [EXPERIMENT](./EXPERIMENT.md) · [Core #130](https://github.com/ryonakayama234/morphoacoustics/issues/130) · [Studio #20](https://github.com/ryonakayama234/morphoacoustics-studio/issues/20).

## Keep six distinct objects

```mermaid
flowchart LR
  CH["CharacterSpec | creative identity"] --> SEL["Exact preset selection"]
  BP["GraphBlueprint | persistent organs, ports, junction, boundary"] --> P["PreparedBranch3 | resolved immutable body"]
  SEL --> P
  P --> RUN["SourceProgram U(t) | execution input"]
  RUN --> ST["Calculated p/U state; Pa, m³/s"]
  ST --> OBS["Raw observation + diagnostics"]
  OBS --> TAKE["Studio immutable Take | artifacts + provenance"]
```

- **Persistent physical Blueprint** (Core owner): OG-4 schema `og4.passive.branch3.v1` and *its complete exact-key, exact-capability contract* remain authoritative. The names A/B/C, `A.in,A.out,B.in,B.out,C.in,C.out`, zero-volume J with law `ideal.branch3.p_u`, source and matched B/C loads are physical identifiers, not UI positions. Section length/area, medium, orientation, law ID, module revisions and source/load references affect the prepared identity. No semantic "nose" or "tongue" assertion.
- **Read-only Studio diagram** (Studio owner): positions, coordinates, collapsed panels, icons and colors cannot affect Core's prepared-graph identity/digest. No unvalidated inferred physical connection from visual lines.
- **Prepared graph** (Core owner): the existing OG-4 immutable `PreparedBranch3`, backend ID, exact Blueprint digest, preparation digest and capability; revalidate rather than trusting a supplied digest. Morphology provenance is distinct from acoustic time state.
- **SourceProgram** (candidate, Core owner): canonical 48,000 samples/s finite input **volume-flow** samples U(t) in m³/s (not signal gain, microphone pressure or LF amplitude without dimension). Frozen source id/revision and sample content SHA-256; deterministic phase/envelope and initial rest assumptions; exact source-plane `A.in`. No source substitution across the A/B experiment.
- **Physical observation** (candidate, Core owner): `p_A.in(t)` raw Pa array; corresponding source U(t); per-port complex pressure/volume-flow on frozen oracle anchors, passivity and condition/accuracy diagnostics; band, time, buffer and solver revision. Pa/flow must not be confused with playback PCM.
- **Creator Take** (Studio owner): immutable content-addressed raw pressure, source, labeled `MONITOR_PRESSURE_NON_RADIATED` playback WAV, typed result and exact Core body+source+code/solver provenance; persist success only after complete checks.

## Minimal human-inspectable candidate request (NOT a normative v1 schema)

```json
{
  "candidate_kind": "og-aud1/physical-monitor/v0-proposal",
  "character_id": "character-demo",
  "body_preset": {
    "id": "graph-small-C",
    "revision": "1",
    "graph_schema": "og4.passive.branch3.v1"
  },
  "source_ref": {
    "id": "og-aud1-fixed-volume-flow",
    "revision": "candidate",
    "port": "A.in",
    "unit": "m3/s"
  },
  "observation": {
    "kind": "source-port-pressure-monitor",
    "port": "A.in",
    "unit": "Pa",
    "band_hz": [0, 4000],
    "sample_rate_hz": 48000
  }
}
```

**Only a conceptual handoff**, not copy/paste valid input for any current API. Design review must settle source timing/length, exact identifier spelling and revision pinning, hash canonicalization, window/padding, frequency-grid and anti-alias requirements before publication. The second preset selects C area 0.0006m²; first 0.00015m². Do not treat labels themselves as physical values: resolve exact OG-4 Blueprint and verify digest.

## Response/record inventory proposal

| Field / artifact | Owner / rule |
|---|---|
| result status & typed refusal | Core; invalid request != unsupported backend != numerical failure != genuine gesture infeasibility != execution failure |
| graph schema + organ IDs/revisions + typed ports & J law | Core canonical; Studio snapshot for display |
| `blueprint_digest`, `preparation_digest`, solver/source/code pinned SHA | Core only; checked at Studio trust boundary |
| U(t) [m³/s], p(A.in,t) [Pa] raw, time grid | Core; exact array length, endian and dtype must be frozen |
| per-port complex p [Pa], U [m³/s], mean power [W] and residuals | Core scientific evidence; oracle-compatible |
| spectral band, FFT/window/pad and monitor plane | Core; compulsory to interpret pressure and alias artifacts |
| WAV 48 kHz mono PCM16, separate playback normalization scale | Core emission / Studio checked; never marketed as calibrated free-field |
| SHA-256 for input/physics/PCM + final receipt | Core creates; Studio verifies and archives only after all checks |
| Character, script/direction context, Take name, comparison, UX diagram layout | Studio; not part of physics digest |

## Refusal and backward compatibility

- Retain OG-4 `Branch3Error` `INVALID / UNSUPPORTED / NUMERICALLY_UNRESOLVED` semantics. A malformed graph is INVALID; structurally lawful but unverified frequencies/bodies and arbitrary ports are UNSUPPORTED; ill-conditioned physics is NUMERICALLY_UNRESOLVED. Job crash is FAILED. This slice makes no promise of articulated gesture `INFEASIBLE`: do **not** misuse that status for a bad graph, unknown preset or source.
- Result receipt must be the final atomic marker, stored only after all raw/PCM checks and hashes. Never write accepted partial artifacts or an immutable success Take for refusals. No fallback to CC-A2, static WAV, guessed radiation or extrapolated branch.
- Do not modify historical CC-A2 / X2a Takes, v0/v1 Performance Contract schemas or their exact trusted code checkouts. A future interface receives **a new version/capability label**; Studio consumes Core-authoritative schema/receipt and does not invent JS-side canonical digests.

## Gate A audit addendum — proposed A/B pair provenance (2026-10-20)

[Physics/UX review details](./GATE_A_REVIEW.md). **Candidate only.** Do not confuse a graph's immutable physical identity with a pair's downstream audition metadata. A proposed `AuditionPairReceipt` (not yet a published contract) references two exact body/preparation digests, the **same source samples/hash**, two raw pressure hashes, a single playback-gain rule and numeric scale, each WAV hash, fixed sample rate and band, and the scientific check results. The pair-level gain is a *presentation transform* and must not mutate raw Pa, SI units, source, geometry or the Core body digest.

**Atomicity question for review:** for pairwise shared gain, validate **both** physical results before producing/accepting paired playable Takes; on one failure preserve no *successful pair* and no fallback. Specify staged temporary artifact cleanup and crash-recovery semantics before changing CC-A2's adopted immutable Take store. Individually peak-normalized WAVs would obscure cross-body absolute pressure ratio; a separate loudness-matched perceptual comparison requires an explicit condition label. Read-only Studio graph position, branch B/C *length* edits under matched loads, and UI gain have no physical impact on this specific monitored transfer.

### Numerical variable scaling versus physical units (Experiment 043 preflight)

The [Wolfram global-system preflight](../../../experiments/043_og_aud1_preflight/RESULTS.md) uses a **dimensionless numerical conditioning policy**, not new persisted physics units. It solves for `(p, q=Z_ref U)` where `p,q` are both in Pa, `Z_ref=1,372,000 Pa·s/m³` is declared, and reports `U=q/Z_ref` back in **m³/s**. A future independent test must compare the physical original `p/U` and conservation/power in SI, not treat q as volume flow. Matrix condition depends on this declared scaling and is not directly comparable to an unscaled mixed-unit condition number. This numerical-science evidence remains an **experiment-local** record, not a published Studio result field.

## Experimental 044 — new sample/receipt implementation, not adopted schema

[Executed exploratory manifest and hashes](../../../experiments/044_og_aud1_monitor/RESULTS.md) were generated using a standalone `experiments/044_og_aud1_monitor/monitor.py` source (code SHA256 in receipt). Typed conceptual relation remains `fixed graph params + prescribed 48000x float64 U(t) [m³/s] → new complete-grid Zin(f) → 48000x raw p(A.in,t) [Pa] → pair-shared 0.8 peak gain → two 48000-frame PCM16 WAVs`. Input and output pressure are distinct, auditable byte arrays (NPY). Each generated file has a SHA256; manifest is written after staged artifacts. **No `PreparedBranch3` verified digest or CC-A2 `PerformanceRequest` is asserted by this experiment-local output**, and no Studio immutable Take has been written. Run manifest carries source/signal/reference-plane, graph dimensions, numeric-band policy and environment versions; it is not a substitute for a future trusted versioned contract.


## Experiment 045: causal six-port evidence boundary (research only)

~~~mermaid
flowchart LR
 B["Fixed A/B/C/J body recipe; immutable selected C area"] --> P["Derived Z0, r, tau"]
 U["Fixed analytic U(t) [m³/s]"] --> S["Causal delayed-echo six-port p/U states"]
 P --> S
 S --> Raw["raw p(A.in,t) [Pa], raw U(t) [m³/s]"]
 S --> Audit["signed junction flow, outlet power and echo-tail bound"]
 Raw --> Derive["single A/B gain → PCM16 monitor WAV"]
 Audit --> Receipt["manifest + SHA256; research only"]
 Derive --> Receipt
 Receipt -. "after scientific and security gates only" .-> Take["Future Studio immutable Take"]
~~~

The [Experiment 045 runner](../../../experiments/045_og_aud1_causal_monitor/causal_monitor.py) creates a *separate* experimental manifest schema (og-aud1.causal.experiment.v0), not an adopted Contract v1 extension. The source is the exact finite-time analytical flow program shared with Experiment 044. Two allowed C areas and J law are fixed. Observations include 48kHz 1s raw source U and raw A.in pressure p as separate little-endian float64 NPY, two PCM16 mono WAVs, a **pair-shared** playback gain, physical/FFT-independent echo settings, six-port conservation diagnostics, code version hash and per-file SHA-256. The six-port traces are internal computational diagnostic states, not claimed persisted complete port wavefields. Source input is not acoustic gain or glottal physical actuation; p(A.in) is not receiver SPL. Immutable output directory is staged and receipt written last. No Studio Take acceptance, no published prepared-body identity, and no relaxation of exact-ref trust policy.
