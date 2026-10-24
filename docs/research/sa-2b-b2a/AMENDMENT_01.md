# B2-A pre-test clarification A1 — distinguish INTERNAL reflections from LIP reflection
Date: 2026-10-25 JST, appended BEFORE B2-A test implementation and empirical runs. This DOES NOT rewrite GATE_A.md.

The frozen Gate A G2 phrase "Closed-mouth reflected first source-return tick 2N" from the uniform B1 model is ambiguous for a *nonuniform 16-section* tube. Internal impedance discontinuities necessarily cause early reflections at the source; forbidding those is physically incorrect and would reject genuine anatomy.

**Correct physical observable:** compare two identical initial states, bodies, source impulse, and interior junctions, with only mouth termination changed:
- mouth closed (+1) versus matched (0), and/or closed versus pressure-release (-1).
- the **difference** of the source-return pressure traces is identically zero through tick 2N-1, and first nonzero at tick 2N. This isolates the first LIP-origin reflection.
- the UNDIFFERENCED source-return trace is allowed (and must be measured) to show earlier echoes from internal section changes. Uniform all-same-area control must first return only at 2N for closed end. Matched nonuniform tube is not reflection-free because the 15 internal boundaries still reflect. Do not weaken the first lip incident support constraint: lip incoming a_lip remains exactly zero for ticks < N.

Gate 7 negative controls explicitly require preservation of these earlier anatomical echoes and unequal-area reflection signs. No physical tolerances or required scientific measurements change; only distinguish two separate reflection paths. Record the original ambiguous condition and this prospective interpretation in RESULTS. If a future reviewer disagrees that this is the physically valid observable, HOLD pending review instead of silently adjusting.

Addendum regarding G6: spectrum transfer at 2600Hz must meet B0 physical ka <=0.8 using that exact body's lip radius, otherwise explicitly exclude that case with declared negative control. Other f gates remain unchanged.
