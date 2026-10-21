# SMC-2 EXPERIMENTS — frozen preregistration and evidence log

**2026-10-22 JST, BEFORE SMC-2 implementation.** Status: INTERNALLY_PREREGISTERED; NOT independently reviewed, NOT confirmed, NOT adopted. Keep any failures and amend protocols prospectively with a new revision, never rewrite original hypotheses after tests.

## Hypotheses and falsifiers
H1 composition: 'あい','いあ','あいあい','いあい' share a phoneme-level dictionary; each fully mapped node retains exact code-point span and stable ordinal ID. Falsifier: whole-word fixture branches, source loss, divergent output in two same-input runs.
H2 partial: 'おはよう','ありがとう' give explicit unknown motor mapping; 'よう'/'とう' include contextual-phonology ambiguity, 'あ、い。' preserves boundary, 'お早う' does not invent reading, '' invalid. Falsifier: any unresolved input generates full executable coordination or silent substitution.
H3 time: with p=1, first 0.08–0.26s, second 0.20–0.38s, third 0.32–0.50s, fourth 0.44–0.62s; relation residual tolerance 1e-9s. p=2 halves each absolute time; p=0.5 doubles it. Falsifier: timing/order permutation changes normalized solution, contradiction silently succeeds, or Wolfram reference mismatch beyond 1e-9s.
H4 no physics leakage: planner changes zero `src/morphoacoustics/` files, zero Performance Contract / Studio files, produces no physical `GestureScore`, simulated pressure or WAV. Falsifier: a runtime fallback claims physical audio or packages a body/solver coordinate as universal motor intent.

## Matched fixtures / controls / negatives
- Valid only symbolic: 'あい', 'いあ', 'あいあい', 'いあい'; fixed segment_id `s1`; pace 1.0; deterministic comparison.
- Pace intervention: 'あい' pace 0.5 vs 1 vs 2, hold script, compiler revision, inventory and timeline origin fixed. Measure scaled event times only, not quality/natural speech.
- Partial: 'おはよう', 'ありがとう', 'あ、い。'; invalid: 'お早う', '', unknown emoji/katakana, blank segment ID, nonstring text, nonfinite/out-of-range pace.
- Negative reference: contradiction for B.ONSET both A.OFFSET and A.OFFSET-0.06; preexisting `compile_shared_timeline` must diagnose invalid in synthetic test only. Also unknown ID/unanchored event and reversed input constraint order.
- No synthetic phoneme `/h/`, `/t/`, `/ɾ/`, `/g/` physical gesture; no place of articulation inferred from a character.

## Independent Wolfram rational oracle (existing inherited Exp011 timing)
Exact (no numerical phonetics): `d=9/50; overlap=3/50; t0=2/25;` four onsets `{2/25,1/5,8/25,11/25}`, offsets `{13/50,19/50,1/2,31/50}`. Pairwise overlap each `3/50`; overlap/window=1/3. Incompatible equality system has no solution. This numerical oracle was evaluated with Wolfram before code; actual checker source to be committed as `wolfram-oracle.wl` in implementation revision. Existing SMC-1 used this timing policy; this does NOT independently validate language or coordination physiology.

## Procedure / stop conditions
1. Gate A: independent review of declared assumptions/protocol pending; freeze this commit before executing new SMC-2 tests. A software pilot following this internal registration is not an independently preregistered scientific confirmation.
2. Gate B: standalone package only; tests for deterministic serialization, source trace, graph node cardinality, timing/provenance, refusal, body/physics leakage. Capture exact SHA, Python versions, CI failures and corrections.
3. Gate C: rerun independent Wolfram oracle; whole Core suite, mypy, OG3/OG4/SV1 existing checks at exact new PR head; independent scientific/code review separately. No sound from this Gate.
4. Gate D: no adoption until explicit independent review and decision: GO_LIMITED_SYMBOLIC, REVISE, MORE_DATA or REJECT.

## Evidence ledger
- Entry A0: 2026-10-22; authored registration, 4 docs; Wolfram `{2/25,1/5,8/25,11/25}` / `{13/50,19/50,1/2,31/50}`, 3/50 overlap, contradiction False. Independent peer audit PENDING. Code not yet implemented at registration.

## Entry B0 — submitted implementation, no claimed PASS
Standalone research code + lexical, phoneme-granularity, partial input, source offsets, time scale, inherited synthetic timing, contradiction, deterministic receipt tests submitted. Added Python 3.11/3.12/3.13 / mypy / full pytest workflow. CI status and independent review **PENDING** at initial submission; no physical simulation, natural pronunciation, audio, or adoption gate completed.

## Entry B1 — initial exact-code SHA evidence and semantic correction
Prior code-bearing SHA `718d0f122833727102938f000494a0c158f0ff8f` passed: SMC-2 3.11/3.12/3.13 + mypy/full pytest [run 39625566343](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39625566343), existing Core [39625566295](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39625566295), OG3 [39625566344](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39625566344), OG4 [39625566323](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39625566323), SV1 [39625566536](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39625566536). All success on same SHA. Independent Wolfram repeat: exact onset/offset/overlap/unsatisfiable contradictory pair all True. Scientific independent review: PENDING. No inference of naturalness or physical speech.

During self-review, `PRECEDES` was found ambiguous: it could wrongly imply gestures cannot overlap. Refinement: rename to `LEXICAL_NEXT` and add unknown-ID/unsupported-Unicode crossing negatives. This new implementation revision must pass fresh exact-HEAD CI. Initial CI success must not be silently attributed to revised HEAD.

## Entry B2 — exact-SHA automated evidence, 2026-10-22 JST
**Code-bearing SHA:** `a8e41fb65abd2aee5c19cc3fb413fa25370cea08` after lexical-edge correction / extra negative tests. GitHub check-runs API reports 20/20 `success` (push and PR checks overlap). Five distinct workflows all SUCCESS for this SHA:
- [SMC-2 symbolic research / Python 3.11/3.12/3.13 + mypy + research and full pytest](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39626061640)
- Full Core tests and typecheck: exact-SHA check runs SUCCESS (action URL is not asserted here).
- OG3, OG4 and SV1: check-runs for code-bearing SHA all SUCCESS. Exact action identifiers retrievable from Actions for that commit.
- **Independent Wolfram Language check:** rational windows and overlaps, contradictory equality UNSAT; `True` for onset/offset/overlap/conflict; pace/2 and pace×2 symbolically verified. Mathematical event scheduling only, not phonetic realism.

**Interpretation:** bounded computational implementation is technically supported for declared fixture set. No body realizer, physics WAV, naturalness, general Japanese support, Studio user testing, independent code/science peer review or scientific adoption. Next Gate: independent design and claim audit, potential additional unseen holdout before decision. Keep PR Draft, do not merge or close #11.
