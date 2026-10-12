# OG-0 amendment 01 — boundary separation and independent wave oracle

**Written 2026-10-12, AFTER exploratory OG-0 implementation and CI results.**
**Status: proposed; independent reviewers have not signed off.**
This is a visible correction to [og0-preregistration.md](./og0-preregistration.md), not a claim to have preregistered outcomes before observing them.

## A. Why an amendment is required

The original protocol conflated (i) the ideal pressure-release downstream boundary `p_out=0`, used to calculate finite-tube input impedance, with (ii) a nonzero through-power test at that same terminal. Its mean power is identically `0.5 Re(p_out Conjugate[U_out])=0`, so a nonzero-power outlet assertion would be invalid. Existing OG-0 code actually uses separate matched-outlet and pressure-release cases; the protocol was inconsistent.

For **pressure-release** retain `p_B,out=0`, `Z_B,out=0`, only for the input impedance fixture at 733 Hz. Its zero mean *terminal* power is an expected result, not proof of a nonzero-power transmission channel. For **nonzero junction-power conservation**, set `p_B,out=Zc,B U_B,out`, with `U_B,out=1e-6 m³/s` for the 733 Hz fixture. `Zc,B = rho c / S_B`. Retain separate markers for the two different load conditions.

## B. An independent wave scattering benchmark, distinct from inverse matrix composition

In the fixed global A→B axial direction use a **unit incident pressure wave** at A.out, `a=1 Pa` (optionally multiply by fixed complex `a=1+0.4j Pa` to test phasor handling). Let `ZA=rho c/SA`, `ZB=rho c/SB`; define reflected pressure wave `r a` in A and forward transmitted pressure wave `t a` in B. Enforce `a(1+r)=a t` and `a(1-r)/ZA=a t/ZB`. These TWO wave boundary equations are separate from transfer-matrix multiplication and yield

- `r=(ZB-ZA)/(ZA+ZB)=-1/3` for the fixed mismatch.
- `t=2 ZB/(ZA+ZB)=2/3` (pressure amplitude ratio, NOT transmitted power fraction).
- `R=|r|²=1/9`, `T=ZA |t|²/ZB=8/9`; `R+T=1` for lossless matched/semi-infinite downstream.
- For `a=1 Pa`, `P_inc=|a|²/(2ZA)=3.644314868804665e-7 W`, `P_refl=4.049238743116294e-8 W`, `P_trans=3.239390994493035e-7 W` (Wolfram symbolic wave solution), with `P_inc-P_refl=P_trans`.

For `theta_A=2 pi f LA/c`, `theta_B=2 pi f LB/c`, use **independent analytic traveling-wave propagation** rather than the experimental graph's inverse matrix to set expected A.in pressure/volume velocity:

```
B.out = (t a exp(-i theta_B), t a exp(-i theta_B) / ZB)
A.in expected pressure = a (exp(+i theta_A) + r exp(-i theta_A))
A.in expected volume U = a (exp(+i theta_A) - r exp(-i theta_A)) / ZA
```

Apply the actual validated `A.out→B.in` experimental graph's `transfer_matrix(f)` to the imposed B.out traveling-wave state and compare with these independent A.in formulas at `[80,250,400,733,1200,2000,4000] Hz` and `a=1+0.4j Pa`. Normalize the complex two-vector by `(|a|, |a|/ZA)`; maximum absolute normalized error candidate threshold `1e-11`. The equal-area case separately gives `r=0,t=1`. This explicitly tests the full graph against a **wave-oracle family**, not only a single 733Hz reference or self-inverse junction reconstruction.

## C. Deliberately wrong junction negative control

A mistaken `J_wrong=diag(1, SA/SB)` acts as if **particle** rather than **volume** velocity were conserved. Since the correct ideal massless series junction is `J=I` in (p,U), this incorrect J must FAIL the traveling-wave oracle. In mismatched fixture at 733Hz, Wolfram found a max scaled incident-wave state discrepancy approximately **0.5861352498** when normalized by `(|a|, |a|/ZA)` for the complex incident amplitude `a=1+0.4j`. A test must reject `J_wrong` with a large margin, e.g. normalized discrepancy `>0.1`; it also must accept the unmutated graph within `1e-11`. The test therefore demonstrates *sensitivity to a concrete physical interface error*, not merely that two forms of the same matrix agree. A preliminary calculation reported 0.6312869839 when scaling with unit pressure rather than |a|; the fully specified normalization above gives 0.5861352498 and was verified by re-running the checked-in Wolfram source. The exact magnitude is diagnostic, not itself a model universal constant.

## D. Decision rules and chronology

- The original OG-0 Python tests and CI were **exploratory** and remain immutable historical evidence.
- The amended tests and subsequent CI verify that the *corrected experimental specification* is consistently implemented; they are **controlled regression checks on already known fixtures**, not independent preregistered confirmation data.
- Conditions/tolerances are **candidates** until external numerical-physics and code reviewers approve them. Do not silently tune after results. A later actual prospective scientific test requires a separately recorded new protocol, unobserved geometry/frequency/load fixture or independent measurement, reviewer signoff *before* that test, and separately tracked evidence.
- Independent reviewers must examine power sign conventions, passivity, 1D plane-wave validity range (especially high frequencies), number/type of physically valid ports, invalid-vs-unsupported distinctions, units, immutable identity/provenance, and error near pressure-release poles.
- Only after reviews and head CI can the **experiment-only** code be considered for main merge. Main merge is **not** promotion to the public Core acoustics/preparation API, and does **not** prove arbitrary graphs, wall motion, FSI, glottal source or voice generation.
