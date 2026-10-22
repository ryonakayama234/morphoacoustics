# SMC-3 EXPERIMENTS — frozen Gate A test plan

Preregistered from [#162](https://github.com/ryonakayama234/morphoacoustics/issues/162), before new package code. Artificial tasks G1–G3 are mathematical probes, NOT observed human motor gestures.

## H1: representational expressivity
Input: P1/P2 + G1/G2/G3; edges {(P1,G1),(P1,G2),(P2,G2),(P2,G3)}.
Expected: 2 units, 3 **distinct** task IDs, 4 associations, no duplicated G2 node, STRUCTURALLY_VALID. Falsifier: shared G2 copied or missing association.

## H2: exact scheduling and lexical independence
Input task windows (seconds) G1 [2/25,13/50], G2 [1/5,33/100], G3 [29/100,27/50]; durations respectively 9/50,13/100,1/4. Event equality edges supply exact start/end and common anchor. Consecutive overlap 3/50 and 1/25. Never enforce phoneme lexical order as nonoverlap. Falsifier: float rounding or forced sequential timing.
Independent Wolfram evaluator check on 2026-10-22: `{{2/25,13/50},{1/5,33/100},{29/100,27/50}}` → overlaps `{3/50,1/25}`.

## H3: contradiction / missing endpoint
Input 1: same event forced to two unequal rational times 29/100 and 8/25 → INVALID, CONTRADICTORY_TIMING.
Input 2: coupling to missing task, invalid event name or invalid lag type → INVALID.
Input 3: OFFSET equal/before ONSET when both resolved → INVALID.
Falsifier: any silently accepted contradictory or unknown reference.

## H4: provenance / no unauthorized synthesis
Input: unknown character and absent pronunciation unit must remain undecoded; invalid source span or source empty → INVALID; unassociated unit/task → INVALID. No physical score, audio or body fields. Changing input source changes digest; reordering equivalent relations should not change canonical digest.

## H5: package and regressions
Run from clean root: editable install in isolated Python environment (3.11+), package pytest, mypy, existing root pytest; static check no imported Core runtime. Inspect exact HEAD GitHub checks including OG3/OG4/SV1 where available. Failures and skipped experiments must be recorded without conflating software with physical/phonetic validation.

## Decision criteria
GO_LIMITED_SYMBOLIC only after clean software checks and independent design reviewer; else REVISE/MORE_DATA/REJECT. Real pronunciation, physiology, perception, and cross-body execution have separate gates. No `main` merge in this work package.
