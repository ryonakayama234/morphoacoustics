# OG-5 Gate A — preregistration and narrow design contract (2026-10-16 JST)

**STATE: DRAFT DESIGN / NOT RATIFIED / NO CORE IMPLEMENTATION / NOT ADOPTED.**
Tracks [#109](https://github.com/ryonakayama234/morphoacoustics/issues/109). Base: Core main af10985f180f7b9a8f1dbca269c1133bc1a94c0a, which includes merged OG-4 PR #108. A Gate-A reviewer must freeze disputed thresholds, error precedence and schema details before any separate Gate-B production implementation. No historical OG-3/OG-4 ABI changes, voice/WAV/FSI/Studio integration or automatic merge are authorized by this design.

## 1. Causal architecture and fixture

~~~mermaid
flowchart LR
  Src["prescribed flow / A.in"] --> A["Tube A"]
  A --> J1(("J1: ideal 3-port"))
  J1 --> B["Tube B"]
  J1 --> C["Tube C"]
  B --> J2(("J2: ideal 3-port"))
  J2 --> D["Tube D"]
  J2 --> E["Tube E"]
  C --> LC["C load"]
  D --> LD["D matched"]
  E --> LE["E matched"]
~~~

Five separate rigid, uniform, lossless, small-signal **1D tubes** A/B/C/D/E; exactly two massless, zero-volume ideal acoustic three-port junction relations, J1=(A.out,B.in,C.in), J2=(B.out,D.in,E.in). This is a connected, **acyclic, fixed** directed reference arrangement (not one-way wave propagation). It does not represent living nasality, phonation or a graph of arbitrary topology. Graphical wires only represent physical connectivity if a typed, oriented law is validated.

~~~mermaid
flowchart TD
  BP["Semantic GraphBlueprint (versioned)"]
  VAL["validate: types / units / coverage / orientation"]
  CAP["capability: exact OG-5 bounded family"]
  PREP["immutable PreparedGraph + identities"]
  EQ["20x20 complex coupled solver, scaled"]
  OBS["all 10 endpoints p,U + powers + diagnostics"]
  REF["independent Wolfram recursion + negative controls"]
  BP --> VAL --> CAP --> PREP --> EQ --> OBS
  OBS --> REF
  VAL -->|INVALID| F["typed refusal; no partial observation"]
  CAP -->|UNSUPPORTED| F
  EQ -->|NUMERICALLY_UNRESOLVED| F
~~~

Core owns validity, simulation physics, snapshot and diagnostics. Studio may consume a later approved contract but OG-5 is NOT a creator-facing graph UI. A three-port is a **single multi-port physical law**; it must not be implemented as three unbound pairwise wires.

## 2. Exact physical conventions

- Phasors are **peak**, with time dependence exp(+i omega t); f>0 Hz, omega=2 pi f rad/s.
- Each tube has reference flow U positive from its inlet to its outlet, measured in **m^3/s**, and pressure perturbation p in **Pa**. Flow is **not particle velocity** m/s.
- Uniform tube length L [m], cross-section A [m^2], c=343 [m/s], rho=1.2 [kg/m^3] throughout. Zc=rho*c/A [Pa s/m^3], theta=2*pi*f*L/c.
- At every tube, [p_in,U_in]^T = T [p_out,U_out]^T where T={{cos(theta),i Zc sin(theta)},{i sin(theta)/Zc,cos(theta)}}. This convention fixes all signs.
- Junction J1: p_A.out=p_B.in=p_C.in and U_A.out=U_B.in+U_C.in. J2: p_B.out=p_D.in=p_E.in and U_B.out=U_D.in+U_E.in. For generic orientation this is sum of outward-signed U=0.
- Input: U_A.in=10^-6 (1+0.4 i)*scale m^3/s, scale in {1,0.5,-1}; it is not a prescribed pressure source.
- Terminations: D.out and E.out matched to their OWN Zc. C.out matched or closed (U_C.out=0). No explicit infinite-impedance sentinel; no silent fallback.
- Mean acoustic power in reference direction for each endpoint: 0.5 Re(p Conjugate(U)) [W]. For ideal lossless network P_A.in=P_C.out+P_D.out+P_E.out. Closed C carries zero mean terminal power; its acoustic reactive field can be nonzero.

**Equation budget** = 10 tube equations (two per tube) + 6 ideal junction equations + 1 prescribed source equation + 3 load equations = **20 complex equations for 20 complex endpoint states** (p,U at inlet and outlet of all five tubes).

## 3. Registered fixture and case generation (proposal pending Gate A review)

| Organ | L [m] | A [m^2] |
| --- | ---: | ---: |
| A | 0.08 | 0.0003 |
| B | 0.09 | 0.0003 |
| C | 0.06 | {0.00015, 0.0003, 0.0006} |
| D | 0.07 | 0.0003 |
| E | 0.05 | 0.0006 |

Frequencies [80,250,400,733,997,1200,2000,4000] Hz, C loads [matched,closed], source scales [1,0.5,-1]. Cartesian product **3 x 8 x 2 x 3 = 144 positive candidate cases**; collection order irrelevant to graph identity; requested frequency sequence and duplicate occurrences remain relevant to an observation identity. Gate A *has not executed these 144 cases* and cannot assert they are all supported/nonsingular yet. Review may reject/adjust a condition with an explicitly dated protocol amendment **before Gate B**, retaining this original proposal.

**Exploratory evidence only:** [Gate A Wolfram receipt](./og5-gate-a-wolfram-receipt.md) and [self-contained code](./og5-gate-a-oracle.wl) compute three 733-Hz cases independently by global 20x20 and recursive impedance/full-port propagation. They are not a preregistered blind test or production implementation. In particular, the first unscaled Wolfram Solve produced a conditioning warning; scaled calculations succeeded. The first all-port comparison attempt generated rule-replacement errors due to an incorrect AssociationThread construction; corrected by using Thread[vars -> vector], with original failure documented, not erased.

## 4. Independence, normalization and planned accept/reject tests

The Gate B Core backend must build/solve a **global coupled** 20x20 complex linear system using unchanged UniformTube primitives. Normalize with fixed positive Uref=1e-6 m^3/s, Zref=rho*c/0.0003 [Pa s/m^3], Pref=Zref*Uref [Pa], and dimensionless P=p/Pref, Q=U/Uref. Apply finite/nonfinite checks to every coefficient and result. Do not use least-squares, hidden regularization, unapproved model substitutions, or fallback to OG-4.

The **independent Wolfram comparator** must NOT import production matrices or solver code: combine C/D/E input impedances backward via parallel admittances at J2 then J1, and propagate pressure/flow through each tube with its inverse transfer matrix. Compare every one of the 20 complex normalized endpoint values; comparing the source port alone is insufficient. The comparator itself must be inspected by a separate critical reviewer.

Proposed numerical acceptance thresholds (NOT FROZEN pending scientific Gate A review):
1. Full-port normalized discrepancy max over 20 values (and frequencies/cases) <= 1e-10, scale denominator max(1,max reference |P| or |Q|).
2. Normalized per-junction pressure/flow conservation <= 1e-10. Mean power relative residual <= 1e-10, scale by max(|P_in|,1e-18 W). Inspect tube-wise lossless power too.
3. Normalized matrix 2-norm condition number <= 1e10, scaled backward residual <= 1e-12; otherwise return NUMERICALLY_UNRESOLVED atomically. The condition cap and numerical floor require reviewer justification before freezing; *small backward residual does not guarantee small forward error*.
4. Malformed / duplicated / dangling / wrong-direction / wrong-kind / wrong-unit input deterministically INVALID, after structural checks. Well-formed but out-of-bounds topology or numeric fixture UNSUPPORTED; supported but singular/ill-conditioned computation NUMERICALLY_UNRESOLVED. INFEASIBLE reserved for future actuation/task feasibility, not acoustic numeric faults; infrastructure failure FAILED at job level. No digest, partial observation, partial cache or masquerading success after a failed frequency.
5. Wrong junction flow sign, using particle velocity instead of volume flow, wrong terminal impedance, flipped directed port, geometry/revision mutation, source change, orphan port, wrong number of junctions, well-formed cycle, malformed+unsupported dual-error precedence, counterfeit snapshot, and unchanged-layout-only identity control MUST have explicit negative outcomes. Nondegenerate area C=0.00015 and f=733 Hz avoids equal-area false-law camouflage. Wrong-law mutations must disagree with independent full-port oracle or fail the physical laws, not merely exercise code branch coverage.
6. Python 3.11, 3.12, 3.13 + mypy, existing OG-3 and OG-4 frozen public acceptance and a genuine live X2a preservation check if affected; two clean evidence runs against same exact HEAD, source checksum, raw artifacts + SHA sidecars + independent artifact re-read, inspector/reviewer context disclosure.

## 5. Candidate strict schema and serialized objects (experiment-local proposal)

Do NOT retrofit OG-3 fixed2 or OG-4 branch3 ABI. Candidates for a **separate** API under morphoacoustics_graph.tree5, subject to Gate A review:

- GraphBlueprint schema=og5.passive.tree5.v1: organs as individually revised explicit SI pipe modules, each with exactly inlet and outlet acoustic.p_u typed ports; junctions with IDs, law ideal.branch3.p_u, *ordered* port refs; source and typed C/D/E loads, medium. Only the named A-E and exact J1/J2 connections plus bounded physical fixture are supported; syntactically valid graph permutations canonicalize but preserve semantic port orientation.
- PreparedTree5: frozen independently copied canonical blueprint, explicit port-to-unknown map, backend_id, capability, blueprint_digest, preparation_digest. Recompute binding on export/restore; no deserializing NumPy/pickle solver state, no forgeable hash accepted as authenticity.
- Observation v1: exact requested frequency sequence; 10 named endpoint IDs in documented order A.in,A.out,...,E.out; each endpoint peak complex pressure_pa and volume_flow_m3_s (complex serialized as exact {real,imag}), mean_power_w, f-by-f diagnostics (cond2, backward residual, both junction residuals, terminal power defect); immutable observation_digest. No measured state in morphology.
- Canonical identity: strict finite binary64 SI numbers excluding bool, normalize ±0, explicit versions/domain separation, IDs/revisions and source separated from effective products, terminal kind distinct even if acoustically equal, order-independent organ and junction collections but ordered per-junction ports; UI canvas coordinates, timestamps, local file paths and workflow run IDs excluded from physical hashes. Observation digests include order-sensitive requested frequencies. Final byte encoding/golden vectors/error codes must be ratified *before Gate B*; do not claim that OG-4 hashes can be reused.

Backend implementation must refuse old valid OG-3/OG-4 snapshots/schemas without automatic migration; INVALID malformed legacy input takes precedence over UNSUPPORTED valid legacy version. Reject unknown physical Port kinds rather than coercing them. Exact API function names, JSON limits, error precedence and numerical parameter bounds are a Gate A design-review item, not silently fixed by implementation.

## 6. Work allocation and decision gates

~~~mermaid
flowchart TD
  A["Gate A: docs-only physical/schema/oracle preregistration"] --> RA{"independent design review?"}
  RA -->|approved and frozen| B["Gate B: distinct Draft PR, isolated Core backend"]
  RA -->|amend| A
  B --> T["exact HEAD Python/Wolfram 144-case + mutations + regression"]
  T --> RC{"Gate C: critical physics + API + reproducibility audit"}
  RC -->|passed| L["SUPPORTED_LIMITED: merge with pinned receipt"]
  RC -->|not enough| I["INCONCLUSIVE: remain draft"]
  RC -->|falsified| R["REJECT: record counterexample"]
~~~

- Gate A: THIS PR docs-only (no src/tests/workflow or Studio changes): frozen candidate graph, full equations, independent Wolfram executable, future thresholds and negative controls, diagrams/data/ledger/execution synchronized.
- Gate B: new separate **Draft** PR only after explicit Gate-A review; new Core module, contract, tests, generated raw evidence and CI. Record failed attempts, preserve historical baseline fixtures.
- Gate C: separate scope-critical review; exact HEAD and post-merge attestation; only qualified LIMITED adoption, never a general plug-and-play physics claim.
- Parallel creator path: Core CC-A1 draft PR #101 -> Studio CC-A2 issue #14 is independent, never blocked by OG-5.

## 7. Sources and review checkpoints

Normative baseline: [OG-4 API v1](./og4-branch3-api-v1.md), [adopted OG-4 implementation](../../src/morphoacoustics_graph/branch3.py), [graph program](./organ-graph-program.md), [data contract](./organ-graph-data-candidate.md), [execution](./organ-graph-execution-plan.md), [scientific ledger](./organ-graph-experiment-ledger.md). The older documents contain historical pre-merge OG-4 statements; this proposal does not rewrite history and distinguishes current merged PR #108 from legacy text. Tube transfer and impedance conventions must be reviewed against the implemented UniformTube and OG-4 numerical sign choices, independently of any idealized Wolfram derivation.


### Chronological post-filing experiment note (2026-10-16 JST; not a Gate A ratification)

At the first proposal commit, the 144-case sweep had not run. It was then executed **from that exact committed Wolfram source** (blob d0fd961fdfcc6eae0a263d8e17aba87ba60db8b4): 144 cases evaluated, maximal 20-state recursive/global discrepancy 5.682202313875164e-48, maximum observed scaled condition number 223.7427248146314, terminal power balance zero at **14-digit reported precision**. Three deliberately wrong laws were separately solved at 733 Hz and rejected by full-port comparison, including a **wrong positive-real C impedance that passes energy conservation**. See [chronologically appended receipt](./og5-gate-a-wolfram-receipt.md) and [negative-control source](./og5-gate-a-negative-controls.wl). These are post-filing *discovery runs*, **not independent Core verification, not blind frozen tests, and not Gate A approval**. Exact raw 144 case-level archival remains open.


### Evidence provenance and archival scope (follow-up after the first protocol commit)

All 144 numerical *summary records* now exist as a versioned [case JSON archive](./og5-gate-a-cases-144-exploratory.json) plus [SHA-256 sidecar](./og5-gate-a-cases-144-exploratory.json.sha256). Verified unique fixture count, finite values and 10^-10 displayed power threshold after re-reading the GitHub file. The exact Git blob is 273d6f374eea1db42db527a926ccc86cb7bee1f6 and archive SHA-256 is 8ca71a44a9f6b7562469cff51acc4ab395d7b5144b0bd617c161e7854889ae7b. See [receipt](./og5-gate-a-wolfram-receipt.md). **Full complex p/U per case was compared but not stored** in this early summary archive; do not infer otherwise. Bounded-error numeric thresholds, schema, negative-test coverage and Gate A ratification remain open to critical review.
