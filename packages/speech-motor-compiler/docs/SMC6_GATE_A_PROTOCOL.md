# SMC-6 Gate A — frozen bounded temporal-network research protocol

**Protocol-first status:** prospective fixtures and semantic decisions, no SMC-6 tests/source at this commit. Owner [#219](https://github.com/ryonakayama234/morphoacoustics/issues/219). Inherits SMC-5 exact gated research HEAD `894d2f0d68169e7f794d78be729057b3b31d6017` via design A0 HEAD `23134784a96a08ad899bf711bf70702f6159508b`; all are stacked and unmerged. Historical RED #180 is untouched. All numbers are **synthetic mathematical scenarios** and no physiology is established.

## Frozen design resolutions (A0 D09)
- **Origin/clock:** exact local rational seconds, explicit fixed origin t0=0 and explicit per-scenario finite horizon T (0<T<=10 seconds), not an external physiological clock. Task events 0<=ONSET<OFFSET<=T; closed STN duration constraint OFFSET-ONSET>=epsilon, where epsilon is an explicit exact positive rational.
- **Result status:** `SAT_UNIQUE` if every event has a singleton feasible interval; `SAT_NONUNIQUE` otherwise; `UNSAT` for contradictory constraints; `REJECTED` for invalid/untrusted shape; `INDETERMINATE` if independent reference unavailable. A SAT witness, selected by earliest-event canonical potential, is mathematical only—not natural motor timing.
- **Duplicate provenance:** require unique constraint IDs; different IDs with identical inequalities remain separate evidence in the scenario and digest; solver may process both (no silent provenance dedup). Exact same ID repeated is rejected, even if values agree.
- **Authentication/replay:** only freshly recompile *bytes* through the existing SMC-5 `compile_wire` ingress; no trusted caller-supplied `CompileResult`, `SymbolicPlan`, altered SHA or mutable graph. Sidecar recomputes and records canonical request SHA, plan digest, candidate digest, original SMC-5 event-table/anchor/coupling timing digest, scenario digest, math algorithm revision and witness digest; no public ABI. Caller must give mode and versioned scenario ID. Replay means identical bytes canonicalized by SMC-5 and identical scenario semantics yield identical research digest/result. Caller-supplied source/receipt snapshots are forbidden.
- **COMPATIBILITY lane:** import *every* SMC-5 exact anchor/coupling and the **resolved exact event timetable** as L=U constraints, so no range may move an event. Any contradictory new range is UNSAT, not a partial replacement. Confirm exact old timetable.
- **RESEARCH_OVERRIDE lane:** caller must supply exact literal replacement policy `SMC5_EXACT_TIMING_REPLACED_FOR_SYNTHETIC_STUDY` and nonblank rationale. Original exact timing is explicitly excluded (but hashed in receipt), never silently widened; task IDs/goals/selected pronunciation identity are kept. A new scenario digest identifies a **different experiment**, not the old SMC-5 timing result.
- **Research data and limits:** finite conjunctive difference bounds L<=t_to-t_from<=U as exact Python `Fraction` (not float/int/bool) with numerator/denominator bounded in magnitude to 10^9, maximum 12 unique tasks and 96 extra constraints. Every event endpoint must be from authenticated unique SMC-5 tasks, or the explicit origin. No disjunction, soft preference, task dynamics, inferred reading, organs, source, air pressure, frequency or WAV. Existing SMC-3/5 modules and `__init__` unchanged.
- **Phase semantics:** ONSET/OFFSET are *symbolic Task-active markers*, not articulator trajectories, acoustic events or oscillator phase. The diagnostic ratio (onset delta / duration) must not be called phase.

## Hypotheses and falsifiers (pre-source)
- **H0 exact legacy:** COMPATIBILITY produces exactly each original SMC-5 event and unchanged original source digests, including after adding redundant constraints; moving any original event is a failure.
- **H1 expressive freedom:** override represents finite non-singleton feasible event regions; zero-width when fully pinned. Claiming one witness is the only/natural solution is a failure.
- **H2 soundness:** every witness satisfies all hard constraints with **exactly zero** violation; explicit contradiction has UNSAT and no witness; negative-cycle certificate has strictly negative sum.
- **H3 joint overlap:** witness overlap and full feasible-set min/max overlap must be distinct, with extrema computed over *jointly feasible event schedules*, not marginal window products.
- **H4 provenance:** only fully authenticated SMC-5 bytes give a model; canonical semantic permutation of unordered constraints does not alter study identity; source/timing changes cannot preserve scenario identity; explicit shared Task appears once.
- **H5 intervention:** addition of hard constraints cannot enlarge the feasible set; changed constraint bounds and zero-overlap alternative produce traceable distinct scenario and measurement.
- **H6 fail-closed:** malformed Fraction, nonfinite/oversized, fake task IDs, duplicate IDs, absent override rationale, invalid wire, unsupported constraint type, missing anchors/origin or unbounded horizon are rejected; no physical body fields and no false schedule.

## Frozen synthetic reference fixtures (all independent of phonetics)
Take T=3/5 seconds, epsilon=1/100. Task G1: s1=0, e1=3/10. Task G2: 9/50<=s2<=11/50, e2-s2=19/100.
- T01 SAT_NONUNIQUE; s2=[9/50,11/50], e2=[37/100,41/100]; achievable overlap O12=[2/25,3/25]. Earliest witness s2=9/50 gives 3/25.
- T02 additional s2=9/50: SAT; overlap=3/25.
- T03 additional s2=11/50: SAT; overlap=2/25.
- T04 separate G2 onset 3/10: SAT with overlap=0; study identity differs.
- T05 T01 + s2>=7/20: UNSAT with verified negative cycle; no witness.
- T06 T01 + e2=s2: UNSAT because epsilon>0.
- T07 compatibility: SMC-5 validated fixture yields identical resolved timeline, zero width, unchanged candidate and source digest.
- T08 compatibility + a bound conflicting with inherited exact time: UNSAT, never widened.
- T09 override requires named timing replacement, immutable source timing digest and distinct study digest.
- T10 shuffle extra constraint declaration order (not source pronunciation order): same canonical study/result digest.
- T11 shared task associated with multiple supplied units has one start/end pair; compare only unique task IDs.
- T12 duplicate constraint ID, forged endpoint, disjunction or cross-type bounds: typed rejection, no witness.
- T13 missing/negative/zero horizon, unbounded event or invalid/float/NaN rational: reject/indeterminate, never assume zero silently.
- T14 adding a consistent inequality never increases any per-event feasible width; record changed windows and overlap.
- T15 independent oracle disagreement or unverified negative-cycle evidence: MORE_DATA/REVISE; preserve counterexample.

## Exact reference, method and gates
1. Record this protocol commit **before** adding tests. Commit tests without source to an independent subsequent commit and preserve observed RED failure (absence of `temporal_stn` module), not merely expected RED.
2. Implement a bounded STN with exact Fraction graph difference edges, independent reference for tiny cases (closed-form T01-T06 plus secondary independent checking), Bellman-Ford/Floyd-Warshall consistent shortest paths and explicit negative-cycle evidence. For overlap minima/maxima enumerate the 2x2 start/end ordering partitions, enforce each order in the STN, and optimize exact event differences under the **same joint constraints**; allow zero when no overlap feasible.
3. Validate malformed input and limits before any graph calculation; reject with explicit stage/code and never partial schedules. Serializing hashes must preserve separate legacy and new study identities. All decisions, changes and individual source SHAs go in append-only RESULTS.
4. Run isolated package pytest and strict mypy on Python 3.11/3.12/3.13, existing Core regressions where available; request an exact-HEAD `@codex review` for software audit (not linguistic/physical quality).
5. **GO_LIMITED_FORMAL** only if T01–T15 or their explicitly documented realizable subfixtures pass with exact reference, no unresolved P1/P2 software defect and verified CI at final SHA. Otherwise `REVISE`/`MORE_DATA`. Even a GO is synthetic time-algebra only; no public MotorScore ABI, Studio editor, Core model changes, phonetic validity, naturalness or main merge.

This frozen protocol supplements A0 documents without rewriting their original hypotheses. New revisions require an additive amendment with source SHA, *not* silent edits to this document.
