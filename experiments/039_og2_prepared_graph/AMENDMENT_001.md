# OG-2 erratum 001 — dimensionless p/U matrix convention (disclosed post-implementation)

Date: 2026-10-13 JST. Protocol's original pre-implementation commit: `857d84b465aaf2057589edc8cf3e491bef7ee695`. Frozen independent Wolfram numerical oracle committed before Python implementation as `d42939b34d6a296c4e9dafb9f0c769353a4e2ce7`; first Python implementation commit: `6e25761b6a40b8d6d14074885435f53c4a3c0432`.

## Discovered flaw

During private algebra/numerical cross-check following implementation, before opening the first OG-2 PR, the written protocol and initial Python scaling used `D=diag(1,Zref)`, `D^-1 T D`. For an acoustic state `[p,U]`, where pressure is Pa and volume flow is m³/s, this is the **wrong similarity direction** if the intended dimensionless observation is `[p,Zref*U]`.

## Corrected definition (without retroactive preregistration claim)

Let `S=diag(1,Zref)`, `Zref=rho*c/S_A`. Then
`[p,Zref*U]_{in} = (S T S^-1)[p,Zref*U]_{out}`.
Thus **correct normalized transfer = `S T S^-1`**, with dimensionless top-right `i (Zsection/Zref) sin(phi)` and lower-left `i (Zref/Zsection) sin(phi)`.

This formula already underlay the original independently evaluated Wolfram matrix **values** (the `rel=S_A/S_section` oracle), so the numerical oracle table and the preregistered tolerances **were not adjusted to fit Python**. Only the similarity-transform text/metadata and the corresponding Python observation/test code were corrected. Preserve the original commits as the historical record; amended measurements are *controlled regression* rather than independent blind prospective confirmation.

## Consequences and reviewers

- The physical law `p_A,out=p_B,in`, `U_A,out=U_B,in`, the identity ideal junction, fixed fixtures and tolerances are unchanged.
- Each failing gate must still fail; the dimensional normalization must be reviewed independently.
- Do not upgrade the evidence claim from `PROVISIONAL_NUMERICAL_PASS / REVIEW_PENDING / NOT_ADOPTED` on account of this repair.
- If an independent reviewer requires a prospectively untouched protocol, rerun a new separately preregistered replication; this amendment alone does not count as that replication.
