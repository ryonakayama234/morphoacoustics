# Scientific tests

Scientific tests encode model-level expectations that should survive refactors and backend changes.

Planned hypotheses include:

- Changing tract length while holding the source fixed changes resonance structure.
- Changing source F0 while holding tract geometry fixed does not directly redefine tract resonances.
- The same task-level gesture may produce different morphology-specific state trajectories.
- An unreachable gesture can produce `INFEASIBLE` rather than a fabricated sound.
- Different fidelity backends can be compared on the same morphology/gesture inputs.

These tests should use tolerances and clearly state which behavior is expected to be backend-independent and which behavior is an approximation of a particular fidelity level.
