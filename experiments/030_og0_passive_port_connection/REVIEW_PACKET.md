# OG-0 reviewer packet — experiment-only merge gate

**Status: REVIEW HANDOFF ONLY · author-side audit · no independent approvals · NOT ADOPTED.**

- Parent: [#90](https://github.com/ryonakayama234/morphoacoustics/issues/90); independent review tracker: [#93](https://github.com/ryonakayama234/morphoacoustics/issues/93).
- [Protocol PR #91](https://github.com/ryonakayama234/morphoacoustics/pull/91) + [transparent amendment 01](https://github.com/ryonakayama234/morphoacoustics/blob/research/og0-prereg/docs/research/og0-amendment-01.md) (both written/updated before or after exploratory results as transparently stated).
- [Implementation PR #92](https://github.com/ryonakayama234/morphoacoustics/pull/92); baseline main \`8868df1188443fc4523533c6cb0bb9cd72995c32\`; verified prior CI head \`b3173705901d633da5a36aebbbe657a32c0e9c65\`, [Actions run 38255137148](https://github.com/ryonakayama234/morphoacoustics/actions/runs/38255137148) passed Python 3.11/3.12/3.13 + typecheck. **Always inspect current PR head at review time**, and reconfirm its CI.
- Original frozen *pre-implementation numerical oracle* (not independently accepted protocol): \`tests/scientific/oracles/og0_wolfram.json\`; the *post-exploratory* wave oracle: \`tests/scientific/oracles/og0_wave_amendment01_wolfram.json\`. Reproducible Wolfram code \`wolfram/og0_oracle.wl\`.
- Files of interest: \`port_network.py\`, \`run.py\`, \`tests/test_experiment_030_og0.py\`, \`README.md\`, \`RESULTS.md\`.

## Precisely bounded claim that MAY be accepted after independent review

Two immutable, separately identified rigid lossless constant-area **one-dimensional** tube organs are connected through a validated acoustic \`A.out→B.in\` port edge. For a zero-length **ideal one-dimensional** junction sharing the same medium, pressure \(p\) [Pa] and signed **volume velocity** \(U\) [m³/s] are continuous in the common axial coordinate. Transfer of \((p,U)\) over this ideal junction is \(J=I\), and the serial transfer is \(T_A T_B\). The characteristic impedances \(\rho c/S\) differ when cross-sectional areas differ, producing plane-wave scattering. Time convention \(e^{+i\omega t}\). This is a verification of the **selected idealized mathematical model**, not its agreement with 3D tube discontinuities in nature.

Excluded: general graphs, multiple edges/branches, 3D fields, evanescent-mode/end-correction physics, noncircular shape, moving walls, FSI, acoustic source/glottis, phonation, emitted sound, Studio and public production Core API. No \`src/\` contract changes are proposed.

## Author-side independent mathematical cross-check (NOT a reviewer signoff)

1. **Traveling-wave interface conditions** — unit pressure incidence: \`1+r=t\`, \`(1-r)/ZA=t/ZB\`. For \(S_A=0.0003\), \(S_B=0.0006\) m², \(\rho=1.2\), \(c=343\), find \`ZA=1,372,000\`, \`ZB=686,000\` Pa·s/m³, \`r=-1/3\`, pressure \`t=2/3\`, \`R=1/9\`, \`T=8/9\`. **Pressure transmission \(t\) is not power transmission \(T\).**
2. **Distinct numerical check** — post-exploratory wave oracle imposes \(a=1+0.4i\) Pa and evaluates inlet state from traveling waves, not inverse matrix roundtrip. Wolfram independently found the incorrect **particle-velocity-continuity mutation** \`J_wrong=diag(1,S_A/S_B)\` gives max normalized inlet state error \`0.5861352498274852\` at 733 Hz, while the ideal wave representation is equal to high numerical precision. Candidate mutation kill threshold \`>0.1\`, correct transfer error \`<1e-11\`. Explicitly distinguish these from a prospective preregistration.
3. **Pressure-release vs matched outlet** — pressure-release \`p_B,out=0\` ⇒ \`0.5 Re(p Conjugate(U))=0\` at that **terminal**; use for 733-Hz finite-tube input impedance. Nonzero transmitted real power requires a **different** matched terminal with \`p_B,out=ZB U_B,out\`. A former protocol contradiction was corrected in amendment 01 after initial exploratory CI, without hiding the chronology.
4. **Extra independent lossless-passivity identity** (analytic **review aid**, not an added preregistered gate): for a lossless transfer \`T={{A,B},{C,D}}\` with \`Det[T]=1\` and a passive complex downstream load \`ZL\`, \`Zin=(A ZL+B)/(C ZL+D)\` and \`Re[Zin]=Re[ZL]/Abs[C ZL+D]^2 >= 0\` when \`Re[ZL]>=0\`. Using \(Z_L=Z_B(0.6+0.35i)=411600+240100i\) Pa·s/m³ at 733 Hz, Wolfram gives \(Z_{\rm in}\approx1,228,425.27113075+141,951.79050393i\) Pa·s/m³; both computations of \(\mathrm{Re}\,Z_{\rm in}\) agree to high precision. An independent physicist should verify applicability, units, and signs before relying on this.
5. **Conditional circular-duct modal limit** (illustrative, NOT part of the area-only model): for a *rigid circular* tube the first non-planar cutoff is \(f_c=c\,j'_{1,1}/(2\pi\sqrt{S/\pi})\), \(j'_{1,1}\approx1.84118378134\). At \(S=3\) cm² cutoff \(\approx10,285.51\) Hz, at \(S=6\) cm² \(\approx7,272.95\) Hz. At 4 kHz the first evanescent-mode axial **amplitude decay lengths** are \(\approx5.76\) mm and \(\approx8.99\) mm for the respective *uniform circular cross sections*. **Below cutoff does not imply absence of these modes near a sharp 3D discontinuity**, and area alone does not fix circular shape.

## Primary acoustics sources for the physical scope warning

- Rienstra & Hirschberg, *An Introduction to Acoustics*, [Fundamentals of Duct Acoustics](https://citeseerx.ist.psu.edu/document?doi=035a3a0c530196dd9b2d7344b5b18b5f2288e2f7&repid=rep1&type=pdf), rigid cylindrical duct mode cutoff and below-cutoff evanescent behavior (Section 4).
- Peat (1988), [*The acoustical impedance at discontinuities of ducts in the presence of a mean flow*](https://www.sciencedirect.com/science/article/pii/0022460X88903537), *Journal of Sound and Vibration* 127(1), 123–132: discontinuity-induced evanescent waves and effective impedance.
- [*A re-expansion method for determining the acoustical impedance and the scattering matrix for the waveguide discontinuity problem*](https://pmc.ncbi.nlm.nih.gov/articles/PMC2933254/) (2010): at a duct step, plane waves alone can miss the local evanescent acoustic impedance.

These sources delimit scope; they do **not** experimentally validate this specific implementation.

## Independent review assignments and decision record (leave EMPTY until genuine reviewers act)

### Physics/numerics — reviewer not assigned

- [ ] Derive sign/units/scattering/power without copying the experiment solver, review source and two oracle datasets and the Wolfram script.
- [ ] Judge whether exact ideal-1D junction is a sufficient and correctly bounded claim; expressly consider modal cutoff and local evanescent effects.
- [ ] Examine passivity equation and prospective-vs-post-exploratory status; reject unsupported real-tract assertions.
- [ ] Submit review under **own GitHub identity** with verdict, objections, and exact reviewed commit SHA.

### Code/API — reviewer not assigned

- [ ] Audit immutable organ/port and edge validation, invalid-vs-unsupported rules, negative controls and graph identity.
- [ ] Check that the traveling-wave oracle kills the wrong-junction mutation, and that the power continuity roundtrip alone is not treated as independent physics proof.
- [ ] Confirm no production \`src/\` or Studio changes; inspect pinned code/oracle hashes and newest CI.
- [ ] Submit review under **different GitHub identity from the physics reviewer and implementation author**, with verdict and exact SHA.

### Decision rule

- **Before review:** keep PRs Draft, research conclusion \`NOT_ADOPTED\`, no main merge.
- If accepted, first resolve all review objections, confirm revised PR head CI, document a **research-only** decision on #90, then consider merging approved experimental docs/tests; do **not** promote code into \`src/\` as a consequence.
- If a prospective confirmatory experiment is required, reviewers must approve a separately versioned protocol and previously unseen fixture(s) *before executing them*. Existing amended checks on known fixtures are **controlled regression only**.
- The implementer/assistant, CI, or symbolic software must **never impersonate third-party reviewers** or fill their checkboxes.
