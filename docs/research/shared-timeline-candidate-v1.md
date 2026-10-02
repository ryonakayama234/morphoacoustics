# Shared timeline candidate v1

Issue: #28

## Purpose

This document records the first compiler-local candidate for sharing timing semantics between CoordinationPlan and ProsodyPlan.

It is deliberately **not** a new universal physical-domain API.

The candidate tests one narrow architectural claim:

> pronunciation-derived semantic anchors can be shared by motor coordination and prosodic intent, while absolute seconds remain a compiled result and solver/body state remains outside both plans.

The intended pipeline is:

~~~text
Pronunciation structure / fixture
        ↓
semantic anchor IDs
        ↓
ResolvedTimeline
   ┌───────────────┴───────────────┐
   ↓                               ↓
CoordinationPlan               ProsodyPlan
   ↓                               ↓
Gesture event times          resolved symbolic cues
   └───────────────┬───────────────┘
                   ↓
           compile_shared_timeline
                   ↓
              GestureScore
~~~

## Why this is in integration/

Gesture and GestureScore remain the physical-kernel-facing motor contracts.

The candidate types in morphoacoustics.integration.shared_timeline are compiler-side representations. They may evolve or be rejected without changing the universal domain schema.

This preserves the project boundary:

~~~text
creative / linguistic semantics
        ↓
integration compiler
        ↓
task-level GestureScore
        ↓
physical realization
~~~

## Anchor semantics

A semantic anchor has a stable string ID and provenance.

Examples:

~~~text
utterance.start
segment.s3.onset
mora.m2.onset
accentual_phrase.ap1.end
~~~

ResolvedAnchor additionally carries time_s, but that object is already a **resolved compiler timeline**. The symbolic plans do not store their own absolute event times.

This distinction is intentional:

- semantic identity is stable across recompilation;
- absolute seconds may change with pace, duration rules, or later pronunciation compilation;
- both prosody and coordination can continue to point at the same semantic event.

## CoordinationPlan

CoordinationPlan contains equality constraints between gesture events and either:

- a semantic anchor; or
- another gesture event.

Examples:

~~~text
A.onset  = utterance.start + 0.08 s
A.offset = A.onset + 0.18 s
B.onset  = A.offset - 0.06 s
B.offset = B.onset + 0.18 s
~~~

The compiler resolves these relations as a weighted equality graph.

The graph is solved from the known semantic anchors. Therefore a purely relative cycle with no path to any anchor is invalid rather than silently being assigned t=0.

Contradictory equalities are also invalid.

## Experiment 011 reproduction

The candidate can represent both preregistered Experiment 011 conditions without body-specific information.

Sequential:

~~~text
A: 0.08–0.26 s
B: 0.26–0.44 s
~~~

Overlap:

~~~text
A: 0.08–0.26 s
B: 0.20–0.38 s
~~~

The only change is the relative relation for B.onset:

~~~text
sequential: B.onset = A.offset
overlap:    B.onset = A.offset - 0.06 s
~~~

The compiler tests require the same result when gesture inventory order, timing-constraint order, or anchor tuple order is reversed.

## ProsodyPlan

ProsodyPlan remains symbolic.

Candidate event kinds are:

- BOUNDARY
- PROMINENCE
- DURATION_SCALE
- EFFORT
- VOICING

Each event references a semantic anchor and a scalar value.

The plan deliberately does **not** contain:

- raw F0 trajectories;
- waveform samples;
- LF-family parameters;
- body IDs;
- solver state;
- section indices.

For example:

~~~text
boundary(ap1.end, strength=0.8)
duration_scale(ap1.end, 1.15)
prominence(m2.onset, 0.5)
~~~

Compilation resolves these cues onto the same timeline used by gesture-event timing, but does not yet realize them into F0, amplitude, duration, or phonation trajectories. That realization remains a later source/prosody compiler concern.

## Diagnostics

Candidate compilation is explicit rather than corrective.

Current diagnostic classes include:

- DUPLICATE_GESTURE_ID
- UNKNOWN_GESTURE
- UNKNOWN_ANCHOR
- UNRESOLVED_EVENT
- CONTRADICTORY_TIMING
- INVALID_GESTURE_WINDOW

Unknown references are not guessed. Contradictory timing is not averaged. Unanchored relative timing is not silently zero-based.

## Determinism

The candidate compiler version is:

~~~text
shared-timeline-candidate/v1
~~~

Compilation canonicalizes traversal/output ordering so equivalent input order produces the same GestureScore and resolved event sequence.

This is compiler determinism, not a claim that future pronunciation compilation will preserve identical absolute seconds across compiler versions.

## Scope boundary

This candidate does not establish:

- a complete Japanese prosodic grammar;
- a production-ready intonation model;
- phase-oscillator Task Dynamics;
- general articulator competition;
- a source-control API;
- a new GestureScore schema;
- Studio-facing controls.

It is sufficient only if it can support:

1. Experiment 011 sequential/overlap timing;
2. the planned Experiment 014 shared semantic anchors;
3. explicit invalid diagnostics;
4. deterministic compilation;
5. continued separation from body/solver/acoustic coordinates.

## Next gate

If this candidate survives #28, Experiment 014 can use the same anchor IDs for:

~~~text
CoordinationPlan:
  gesture event relation -> semantic anchor

ProsodyPlan:
  boundary/prominence/duration intent -> same semantic anchor
~~~

Only after that research result should any larger compiler or production representation be promoted.
